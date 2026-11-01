"""Build the R05 physical interconnect draft beside R04 using KiCad Python.

Connector lands: [@hiroseFh34Drawing]. This is not a fabrication release.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess
import xml.etree.ElementTree as ET
import pcbnew as p
from extract_head import children
import build_r02 as sch

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'electronics/r04'
CLI = 'C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe'
CONNECTOR = 'Hirose_FH34SRJ_24S_0.5SH_R05'
LAND = 'Flex_Solder_24_P0.5_R05'
mm = p.FromMM
def v(x, y): return p.VECTOR2I(mm(x), mm(y))
def xy(q): return [p.ToMM(q.x), p.ToMM(q.y)]
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def line(parent, a, z, layer, width=.05, footprint=False):
    d = p.PCB_SHAPE(parent) if footprint else p.PCB_SHAPE()
    d.SetShape(p.SHAPE_T_SEGMENT); d.SetStart(v(*a)); d.SetEnd(v(*z))
    d.SetLayer(layer); d.SetWidth(mm(width)); parent.Add(d)

def box(parent, bounds, layer, footprint=False):
    x,y,X,Y = bounds
    for a,z in [((x,y),(X,y)),((X,y),(X,Y)),((X,Y),(x,Y)),((x,Y),(x,y))]:
        line(parent,a,z,layer,footprint=footprint)

def footprint(board, ref, value, name):
    f = p.FOOTPRINT(board); board.Add(f)
    f.SetReference(ref); f.SetValue(value); f.SetFPID(p.LIB_ID('Camera', name))
    f.SetAttributes(p.FP_SMD); f.Reference().SetVisible(False); f.Value().SetVisible(False)
    return f

def pad(f, number, x,y,w,h, net=None, layer=p.F_Cu, paste=True):
    q = p.PAD(f); q.SetNumber(str(number)); q.SetAttribute(p.PAD_ATTRIB_SMD)
    q.SetShape(p.PAD_SHAPE_RECT); q.SetPosition(v(x,y)); q.SetSize(v(w,h))
    ls=p.LSET(); ls.AddLayer(layer); ls.AddLayer(p.F_Mask if layer==p.F_Cu else p.B_Mask)
    if paste: ls.AddLayer(p.F_Paste if layer==p.F_Cu else p.B_Paste)
    q.SetLayerSet(ls); f.Add(q)
    if net: q.SetNet(net)
    return q

def clone(source):
    old = p.LoadBoard(str(source)); b=p.BOARD(); b.SetCopperLayerCount(4)
    b.GetDesignSettings().SetBoardThickness(mm(.6)); nets={}
    for name in {q.GetNetname() for f in old.GetFootprints() for q in f.Pads()}:
        if name:
            n=p.NETINFO_ITEM(b,name); b.Add(n); nets[name]=n
    for original in old.GetFootprints():
        assignment={q.GetNumber():q.GetNetname() for q in original.Pads()}
        f=p.FOOTPRINT(original); b.Add(f)
        for q in f.Pads():
            name=assignment[q.GetNumber()]
            if name: q.SetNet(nets[name])
    for original in old.GetTracks():
        t=original.Duplicate(); b.Add(t); t.SetNet(nets[original.GetNetname()])
    for original in old.GetDrawings():
        if not isinstance(original,p.PCB_SHAPE): continue
        # Remove obsolete reservation rectangles, retaining the actual board outline.
        if original.GetLayer()!=p.Edge_Cuts:
            if source.stem=='controller': continue
            if min(xy(original.GetStart())[1],xy(original.GetEnd())[1])>=12: continue
        d=original.Duplicate(); b.Add(d)
    return b,nets

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True)
    out=ap.parse_args().output.resolve()
    if out.exists(): raise SystemExit('Use a new output directory; preserve prior revisions.')
    # Check the selected saved R04 native files before deriving another revision.
    parent=json.loads((SRC/'validation.json').read_text())['sha256']
    for name in ['controller.kicad_pcb','head.kicad_pcb','camera.kicad_sch']:
        assert digest(SRC/name)==parent[name], ('Changed R04 source',name)
    out.mkdir(parents=True)
    for name in ['Camera.pretty','Camera.kicad_sym','fp-lib-table','sym-lib-table',
                 'camera.kicad_pro','controller.kicad_pro','head.kicad_pro',
                 'LICENSE-Antmicro','LICENSE-Espressif-library.md']:
        if (SRC/name).is_dir(): shutil.copytree(SRC/name,out/name)
        else: shutil.copy2(SRC/name,out/name)
    pinout={node.get('pin'):net.get('name') for net in ET.parse(SRC/'source-netlist.xml').findall('.//nets/net')
            for node in net.findall('node') if node.get('ref')=='J102'}
    assert set(pinout)=={str(i) for i in range(1,25)}

    # Preserve the existing circuit; give J102 a physical footprint and add J201.
    source=(SRC/'camera.kicad_sch').read_text(encoding='utf-8')
    blocks=list(children(source))
    for i,b in enumerate(blocks):
        if b.startswith('(symbol ') and sch.prop(b,'Reference')=='J102':
            b=b.replace('HEAD HARNESS / logical only','FH34SRJ-24S-0.5SH(99)')
            b=re.sub(r'(\(property "Footprint" )"[^"]*"',r'\1"Camera:'+CONNECTOR+'"',b)
            blocks[i]=b
    sch.PARTS.clear()
    sch.add('J201','Connector_Generic','Conn_01x24','HEAD / soldered flex',265,225,
            {k:n.lstrip('/') for k,n in pinout.items()},'Camera:'+LAND)
    source='(kicad_sch\n'+'\n'.join(blocks+sch.PARTS)+'\n)\n'
    source=source.replace('R02 / OV9281 + ESP32-P4X connected draft','R05 / OV9281 + ESP32-P4X interconnect draft')
    (out/'camera.kicad_sch').write_text(source,encoding='utf-8')
    subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','--output',str(out/'source-netlist.xml'),str(out/'camera.kicad_sch')],check=True)

    b,nets=clone(SRC/'controller.kicad_pcb')
    for name in set(pinout.values()):
        if name not in nets:
            n=p.NETINFO_ITEM(b,name); b.Add(n); nets[name]=n
    f=footprint(b,'J102','FH34SRJ-24S-0.5SH(99)',CONNECTOR)
    # Component-side land-pattern view, cable exits +Y. Drawing EDC3-159714-05,
    # sheets 1,2,4: pin 1 at +5.75; E=13.1, F=13.9; body A=14, contact span B=11.5.
    for i in range(1,25): pad(f,i,5.75-(i-1)*.5,0,.3,.8,nets[pinout[str(i)]])
    for x in [-6.75,6.75]: pad(f,'',x,2.5,.4,.8)
    box(f,[-7,-1.05,7,2.75],p.F_Fab,True)
    box(f,[-7.25,-1.3,7.25,3.15],p.F_CrtYd,True)
    # Stencil is reduced per Hirose: signal apertures .25 x .65, mounting tabs unchanged.
    for q in f.Pads():
        if q.GetNumber():
            q.SetLocalSolderPasteMargin(mm(.005)); q.SetLocalSolderPasteMarginRatio(-.1)
    p.FootprintSave(str(out/'Camera.pretty'),f)
    f.SetOrientationDegrees(90); f.SetPosition(v(27.75,8.25))
    b.BuildConnectivity(); p.SaveBoard(str(out/'controller.kicad_pcb'),b)

    h,hnets=clone(SRC/'head.kicad_pcb')
    for name in set(pinout.values()):
        if name not in hnets:
            n=p.NETINFO_ITEM(h,name); h.Add(n); hnets[name]=n
    f=footprint(h,'J201','SOLDER FLEX / 24 contacts',LAND)
    for i in range(1,25): pad(f,i,-5.75+(i-1)*.5,0,.3,1.5,hnets[pinout[str(i)]],paste=False)
    box(f,[-6,-.95,6,.95],p.F_CrtYd,True)
    p.FootprintSave(str(out/'Camera.pretty'),f)
    f.SetPosition(v(7,12.25)); h.BuildConnectivity(); p.SaveBoard(str(out/'head.kicad_pcb'),h)

    # Straight flex coupon. Both exposed contact sets are B.Cu, facing the rigid
    # PCB top surfaces. These are connectivity-study traces, not impedance-qualified.
    flex=p.BOARD(); flex.SetCopperLayerCount(2)
    flex.GetDesignSettings().SetBoardThickness(mm(.1)); fnets={}
    for name in set(pinout.values()):
        n=p.NETINFO_ITEM(flex,name); flex.Add(n); fnets[name]=n
    length=35.3; width=12.5
    box(flex,[0,0,length,width],p.Edge_Cuts)
    for ref,cx in [('J301',.75),('J302',34.55)]:
        f=footprint(flex,ref,'FLEX CONTACTS / B.Cu','Flex_Contacts_R05')
        for i in range(1,25): pad(f,i,0,-5.75+(i-1)*.5,1.5,.3,fnets[pinout[str(i)]],p.B_Cu,False)
        f.SetLayer(p.B_Cu)
        if ref=='J301': p.FootprintSave(str(out/'Camera.pretty'),f)
        f.SetPosition(v(cx,6.25))
    for i in range(1,25):
        t=p.PCB_TRACK(flex); t.SetStart(v(.75,.5+(i-1)*.5)); t.SetEnd(v(34.55,.5+(i-1)*.5))
        t.SetWidth(mm(.15)); t.SetLayer(p.B_Cu); t.SetNet(fnets[pinout[str(i)]]); flex.Add(t)
    # Connector stiffener extent is nominal 2.5 mm; not the bendable body thickness.
    box(flex,[0,0,2.5,width],p.Dwgs_User)
    flex.BuildConnectivity(); p.SaveBoard(str(out/'flex-study.kicad_pcb'),flex)
    project=json.loads((out/'controller.kicad_pro').read_text())
    project['board']['design_settings']['rules']['min_copper_edge_clearance']=0
    (out/'flex-study.kicad_pro').write_text(json.dumps(project,indent=2)+'\n')
    (out/'flex-study.kicad_dru').write_text('''(version 1)
(rule "Flex body edge clearance" (constraint edge_clearance (min 0.25mm)))
(rule "Exposed terminal fingers reach cut edge"
 (condition "A.Type == 'Pad'") (constraint edge_clearance (min -0.05mm)))
''')

    record={'revision':'OV9281-P4-R05','units':'mm','status':'Physical interface and straight flex connectivity study; not for fabrication',
            'parent_sha256':{n:parent[n] for n in ['controller.kicad_pcb','head.kicad_pcb','camera.kicad_sch']},
            'pins':pinout,'connector':'FH34SRJ-24S-0.5SH(99)','head_attachment':'J201 solder lap; custom lands, assembly process unqualified',
            'connector_xy':[27.75,8.25],'connector_rotation_deg':90,'connector_height_mm':1,
            'connector_fpc_tip_thickness_mm':.3,'connector_fpc_tip_thickness_tolerance_mm':.03,
            'flex_body_thickness_mm':.1,'flex_body_thickness_note':'Provisional envelope only; no selected stackup',
            'flex_size_mm':[length,width],'flex_origin_in_controller_frame_mm':[29.2,2],
            'head_transform':{'rotation_deg':270,'translation_mm':[76,1.25]},
            'board_gap_mm':30,'flat_assembly_length_mm':76,
            'mating':'Bottom-contact mode; flex B.Cu faces rigid-board F.Cu. Pin n connects to pin n; no twist.',
            'sources':['hiroseFh34Product','hiroseFh34Drawing','hiroseFh34Catalog'],
            'limits':['Rigid-board routing incomplete','Flex ground contacts not yet bonded to a continuous reference plane',
                      'No impedance, power-drop, bend-life or solder-joint qualification','No mass estimate or physical mating test',
                      'Connector footprint and cable orientation require independent pre-fabrication review',
                      'Tip corner radius, coverlay, stiffener adhesive and fabrication tolerances not fully modeled',
                      'Optics and LED driver remain unfinished']}
    (out/'interface.json').write_text(json.dumps(record,indent=2)+'\n')
    print(out)

if __name__=='__main__': main()
