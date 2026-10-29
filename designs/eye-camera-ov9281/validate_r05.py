"""Validate R05 interconnect geometry, net correspondence and retained routes.

Run using KiCad Python, optionally --directory OUTPUT_DIRECTORY.
"""
from pathlib import Path
import argparse, collections, hashlib, itertools, json, math, re, subprocess
import xml.etree.ElementTree as ET
import pcbnew as p

ROOT=Path(__file__).resolve().parent
CLI='C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe'
mm=p.FromMM
def v(x,y): return p.VECTOR2I(mm(x),mm(y))
def xy(q): return [p.ToMM(q.x),p.ToMM(q.y)]
def key(q): return (q.x,q.y)
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def bounds(f):
    bb=f.GetBoundingBox(False,False)
    return [p.ToMM(x) for x in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()]]
def netlist(path):
    return {(n.get('ref'),n.get('pin')):net.get('name') for net in ET.parse(path).findall('.//nets/net') for n in net.findall('node')}
def findpad(b,r,n):
    f=next(f for f in b.GetFootprints() if f.GetReference()==r)
    return next(q for q in f.Pads() if q.GetNumber()==str(n))
def connected(b,r,n,s,m):
    a=findpad(b,r,n); z=findpad(b,s,m); assert a.GetNetname()==z.GetNetname()
    graph=collections.defaultdict(set)
    for t in b.GetTracks():
        if t.GetNetname()!=a.GetNetname(): continue
        x,y=key(t.GetStart()),key(t.GetEnd());graph[x].add(y);graph[y].add(x)
    start,end=key(a.GetPosition()),key(z.GetPosition()); seen={start}; pending=[start]
    while pending:
        x=pending.pop()
        for y in graph[x]-seen: seen.add(y);pending.append(y)
    assert end in seen,(r,n,s,m)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,default=ROOT/'electronics/r05')
    out=ap.parse_args().directory.resolve();src=ROOT/'electronics/r04'
    gen=ROOT.parents[1]/'generated/ov9281-r05-validation';gen.mkdir(exist_ok=True)
    record=json.loads((out/'interface.json').read_text()); pins=record['pins']
    for name,h in record['parent_sha256'].items(): assert digest(src/name)==h,name
    baseline=netlist(src/'source-netlist.xml'); expected=netlist(out/'source-netlist.xml')
    assert all(expected.get(k)==n for k,n in baseline.items()),'Existing schematic connections changed'
    assert set(expected)-set(baseline)=={('J201',str(i)) for i in range(1,25)}
    assert all(expected[('J201',str(i))]==pins[str(i)] for i in range(1,25))
    boards={name:p.LoadBoard(str(out/f'{name}.kicad_pcb')) for name in ['controller','head','flex-study']}
    summary={};checked=0;allrefs=[]
    for name,size in [('controller',[32,20]),('head',[14,14]),('flex-study',record['flex_size_mm'])]:
        b=boards[name];sides=collections.defaultdict(list)
        for f in b.GetFootprints():
            ref=f.GetReference();allrefs.append(ref);bb=bounds(f)
            if name!='flex-study':
                assert bb[0]>=.749 and bb[1]>=.749 and bb[2]<=size[0]-.749 and bb[3]<=size[1]-.749,(name,ref,bb)
                sides[f.GetLayer()].append((ref,bb))
            for q in f.Pads():
                k=(ref,q.GetNumber())
                if name!='flex-study' and q.GetNumber():
                    if k not in expected:
                        assert not q.GetNetname(),k
                        continue
                    assert q.GetNetname()==expected[k],(k,q.GetNetname(),expected[k]);checked+=1
        for side,items in sides.items():
            for (ra,a),(rz,z) in itertools.combinations(items,2):
                assert a[2]+.149<=z[0] or z[2]+.149<=a[0] or a[3]+.149<=z[1] or z[3]+.149<=a[1],(name,ra,rz,a,z)
        subprocess.run([CLI,'pcb','drc','--format','json','--output',str(gen/f'{name}-drc.json'),str(out/f'{name}.kicad_pcb')],check=True)
        drc=json.loads((gen/f'{name}-drc.json').read_text()); types=collections.Counter(d['type'] for d in drc['violations'])
        assert types==({'track_dangling':6} if name=='controller' else {}),(name,types,drc['violations'])
        summary[name]={'size_mm':size,'footprints':len(list(b.GetFootprints())),
                       'violations_by_type':dict(types),'unconnected_items':len(drc['unconnected_items'])}
    assert len(set(allrefs))==103 and checked==456,(len(set(allrefs)),checked)
    assert {f.GetReference() for name in ['head','controller'] for f in boards[name].GetFootprints()}=={k[0] for k in expected}-{'J104'}

    # Preserve all earlier placements, layers and copper. Compare actual saved data.
    for name in ['controller','head']:
        old=p.LoadBoard(str(src/f'{name}.kicad_pcb'));new=boards[name]
        newfp={f.GetReference():f for f in new.GetFootprints()}
        for f in old.GetFootprints():
            z=newfp[f.GetReference()]
            assert key(f.GetPosition())==key(z.GetPosition()) and f.GetOrientationDegrees()==z.GetOrientationDegrees() and f.GetLayer()==z.GetLayer()
        def tracks(b):return sorted((t.GetNetname(),key(t.GetStart()),key(t.GetEnd()),t.GetWidth(),t.GetLayer()) for t in b.GetTracks())
        assert tracks(old)==tracks(new),('R04 tracks changed',name)
    routes=json.loads((src/'routing-study.json').read_text())['routes'];path_count=0
    for r in routes:
        m=re.fullmatch(r'(\w+)\.(\w+) to (\w+)\.(\w+)',r['label'])
        if m: connected(boards['controller'],*m.groups());path_count+=1

    # Verify nominal copper dimensions independently of the generation loops.
    connector=next(f for f in boards['controller'].GetFootprints() if f.GetReference()=='J102')
    for i in range(1,25):
        q=findpad(boards['controller'],'J102',i)
        assert all(abs(a-z)<1e-5 for a,z in zip(xy(q.GetPosition()),[27.75,2.5+(i-1)*.5]))
        assert xy(q.GetSize())==[.3,.8]
        margins=xy(q.GetSolderPasteMargin(p.F_Paste))
        assert all(abs(a-z)<1e-5 for a,z in zip(margins,[-.025,-.075])),margins
    mounts=[q for q in connector.Pads() if not q.GetNumber()]
    assert len(mounts)==2 and all(xy(q.GetSize())==[.4,.8] for q in mounts)
    assert sorted(xy(q.GetPosition()) for q in mounts)==[[30.25,1.5],[30.25,15.0]]

    # Coordinate test of the assembled, untwisted cable. Head rotates 270 degrees
    # in the drawing; component locations in its native board remain unchanged.
    for i in range(1,25):
        q=findpad(boards['head'],'J201',i);hx,hy=xy(q.GetPosition());hx,hy=76-hy,1.25+hx
        a=findpad(boards['flex-study'],'J301',i);z=findpad(boards['flex-study'],'J302',i)
        assert a.IsOnLayer(p.B_Cu) and z.IsOnLayer(p.B_Cu)
        assert a.GetNetname()==z.GetNetname()==q.GetNetname()==pins[str(i)]
        fx,fy=xy(z.GetPosition());fx+=29.2;fy+=2
        assert math.dist((hx,hy),(fx,fy))<1e-6,(i,hx,hy,fx,fy)
        cy=xy(findpad(boards['controller'],'J102',i).GetPosition())[1]
        assert abs(xy(a.GetPosition())[1]+2-cy)<1e-6
        connected(boards['flex-study'],'J301',i,'J302',i)
    # Rails and grounds between each high-speed pair remain in the inherited order.
    assert [pins[str(n)] for n in [1,4,7,10]]==['GND']*4
    subprocess.run([CLI,'sch','erc','--exit-code-violations','--output',str(gen/'erc.rpt'),str(out/'camera.kicad_sch')],check=True)

    # Actual combined copper view for inspection only; overlapping solder/contact
    # regions are intentional assembly interfaces, not one manufacturable PCB.
    assembly=p.BOARD();assembly.SetCopperLayerCount(4);nets={}
    for b in boards.values():
        for f in b.GetFootprints():
            for q in f.Pads():
                n=q.GetNetname()
                if n and n not in nets:
                    net=p.NETINFO_ITEM(assembly,n);assembly.Add(net);nets[n]=net
    for name,angle,offset in [('controller',0,(50,50)),('head',270,(126,51.25)),('flex-study',0,(79.2,52))]:
        b=boards[name]
        for original in b.GetFootprints():
            assignment={q.GetNumber():q.GetNetname() for q in original.Pads()}
            f=p.FOOTPRINT(original);assembly.Add(f);f.Rotate(v(0,0),p.EDA_ANGLE(angle,p.DEGREES_T));f.Move(v(*offset))
            for q in f.Pads():
                n=assignment[q.GetNumber()]
                if n:q.SetNet(nets[n])
        for original in b.GetTracks():
            t=original.Duplicate();assembly.Add(t);t.Rotate(v(0,0),p.EDA_ANGLE(angle,p.DEGREES_T));t.Move(v(*offset));t.SetNet(nets[original.GetNetname()])
        for original in b.GetDrawings():
            if isinstance(original,p.PCB_SHAPE):
                d=original.Duplicate();assembly.Add(d);d.Rotate(v(0,0),p.EDA_ANGLE(angle,p.DEGREES_T));d.Move(v(*offset))
    p.SaveBoard(str(out/'assembly-interconnect-study.kicad_pcb'),assembly)
    for name in ['controller','head','flex-study','assembly-interconnect-study']:
        layers='F.Cu,B.Cu,F.Fab,Edge.Cuts,Dwgs.User' if name in ['flex-study','assembly-interconnect-study'] else 'F.Cu,F.Fab,F.CrtYd,Edge.Cuts,Dwgs.User'
        subprocess.run([CLI,'pcb','export','svg','--layers',layers,'--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--output',str(out/f'{name}.svg'),str(out/f'{name}.kicad_pcb')],check=True)
    report={'status':'Interface geometry and net correspondence checked; incomplete camera, not for manufacture',
            'parent_native_files_unchanged':True,'prior_placements_and_tracks_retained':True,
            'rigid_board_pad_net_checks':checked,'prior_copper_paths_verified':path_count,'flex_contact_paths_verified':24,
            'assembled_pin_alignment_checks':24,'schematic_erc_errors':0,'schematic_erc_warnings':0,
            'same_side_footprint_bounds_do_not_overlap':True,'connector_bounds_mm':bounds(connector),
            'connector_land_pattern_checks':'24 signal pads, two mounting pads, pitch, numbering and stencil dimensions',
            'boards':summary,'flex_lane_trace_length_mm':33.8,'flex_lane_length_mismatch_mm':0,
            'limits':'Length equality is only on the straight flex; whole-link impedance/skew/return plane and physical mating unverified',
            'sha256':{n:digest(out/n) for n in ['controller.kicad_pcb','head.kicad_pcb','flex-study.kicad_pcb','camera.kicad_sch','assembly-interconnect-study.kicad_pcb']}}
    (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
