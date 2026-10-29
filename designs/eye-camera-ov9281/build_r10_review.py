"""Recheck native correspondence and assemble a read-only R10 board overview."""
import collections,hashlib,json,math,shutil,subprocess,sys
from pathlib import Path
import pcbnew as p
from validate_r05 import netlist,findpad,xy,v,connected
from build_r10_planes import connectivity
from audit_interconnect import checked_inputs
from copper_retention import retention

ROOT=Path(__file__).resolve().parents[2];DESIGN=Path(__file__).resolve().parent
SRC=ROOT/'generated/ov9281-r10-balanced-04';OUT=ROOT/'generated/ov9281-r10-review-02';CLI=Path(sys.executable).with_name('kicad-cli.exe')
assert not OUT.exists();manifest=json.loads((SRC/'checkpoint.json').read_text())
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for f in manifest['files']:assert sha(SRC/f['path'])==f['sha256']
checked_inputs();OUT.mkdir()
for entry in manifest['files']:
    source=SRC/entry['path'];target=OUT/entry['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
(OUT/'checks').mkdir(exist_ok=True)
expected=netlist(OUT/'source-netlist.xml');boards={};summary={};count=0;components={};copper={}
for name in ['controller','head','flex-study']:
    b=p.LoadBoard(str(OUT/(name+'.kicad_pcb')));boards[name]=b
    for f in b.GetFootprints():
        for q in f.Pads():
            key=(f.GetReference(),q.GetNumber())
            if name!='flex-study' and key in expected:assert q.GetNetname()==expected[key];count+=1
            elif name!='flex-study':assert not q.GetNetname(),key
    assert all(len(g)==1 for g in connectivity(b).values())
    report=OUT/'checks'/(name+'-drc.json');subprocess.run([str(CLI),'pcb','drc','--format','json','--output',str(report),str(OUT/(name+'.kicad_pcb'))],capture_output=True,check=True);d=json.loads(report.read_text());assert not d['violations'] and not d['unconnected_items']
    summary[name]={'footprints':len(list(b.GetFootprints())),'unconnected_items':0,'violations_by_type':{},'copper_layers':b.GetCopperLayerCount(),'native_thickness_mm':b.GetDesignSettings().GetBoardThickness()/1e6}
    rows=[]
    for f in b.GetFootprints():
        side='F' if f.GetLayer()==p.F_Cu else 'B';points=[]
        for item in f.GraphicalItems():
            if isinstance(item,p.PCB_SHAPE) and item.GetLayer()==(p.F_CrtYd if side=='F' else p.B_CrtYd):points.extend([item.GetStart(),item.GetEnd()])
        if not points:continue
        xs=[q.x/1e6 for q in points];ys=[-q.y/1e6 for q in points]
        rows.append({'reference':f.GetReference(),'value':f.GetValue(),'side':side,'xy_mm':[f.GetPosition().x/1e6,-f.GetPosition().y/1e6],'angle_deg':f.GetOrientationDegrees(),'bounds_xy_mm':[min(xs),min(ys),max(xs),max(ys)]})
    components[name]=rows
    area=(32*20 if name=='controller' else 14*14 if name=='head' else 35.3*12.5);copper[name]=[]
    for layer in ([p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu] if name!='flex-study' else [p.F_Cu]):
        row=retention(b,layer,area);copper[name].append(row)
        if name!='flex-study':assert row['retention_fraction']>.6,(name,row)
assert count==471,count
for i in range(1,25):
    connected(boards['flex-study'],'J301',i,'J302',i)
    x,y=xy(findpad(boards['head'],'J201',i).GetPosition());fx,fy=xy(findpad(boards['flex-study'],'J302',i).GetPosition());assert math.dist((76-y,1.25+x),(fx+29.2,fy+2))<1e-6
    assert abs(xy(findpad(boards['controller'],'J102',i).GetPosition())[1]-(.5+(i-1)*.5+2))<1e-6
subprocess.run([str(CLI),'sch','erc','--exit-code-violations','--output',str(OUT/'checks/erc.rpt'),str(OUT/'camera.kicad_sch')],capture_output=True,check=True)
assembly=p.BOARD();assembly.SetCopperLayerCount(6);assembly.GetDesignSettings().SetBoardThickness(p.FromMM(.541));nets={}
for b in boards.values():
    for q in b.GetPads():
        n=q.GetNetname()
        if n and n not in nets:net=p.NETINFO_ITEM(assembly,n);assembly.Add(net);nets[n]=net
for name,angle,off in [('controller',0,(50,50)),('head',270,(126,51.25)),('flex-study',0,(79.2,52))]:
    b=boards[name]
    for original in b.GetFootprints():
        assignments={q.GetNumber():q.GetNetname() for q in original.Pads()};f=p.FOOTPRINT(original);assembly.Add(f);f.Rotate(v(0,0),p.EDA_ANGLE(angle,p.DEGREES_T));f.Move(v(*off))
        for q in f.Pads():
            if assignments[q.GetNumber()]:q.SetNet(nets[assignments[q.GetNumber()]])
    for original in list(b.GetTracks())+list(b.Zones()):
        item=p.Cast_to_ZONE(original.Duplicate(False)) if isinstance(original,p.ZONE) else original.Duplicate();assembly.Add(item);item.Rotate(v(0,0),p.EDA_ANGLE(angle,p.DEGREES_T));item.Move(v(*off));item.SetNet(nets[original.GetNetname()])
    for original in b.GetDrawings():
        if isinstance(original,p.PCB_SHAPE):item=original.Duplicate();assembly.Add(item);item.Rotate(v(0,0),p.EDA_ANGLE(angle,p.DEGREES_T));item.Move(v(*off))
name='OV9281-P4-R10-assembly';p.SaveBoard(str(OUT/(name+'.kicad_pcb')),assembly)
for board in list(boards)+[name]:
    subprocess.run([str(CLI),'pcb','export','svg','--layers','F.Cu,B.Cu,F.Fab,Edge.Cuts','--mode-single','--fit-page-to-board','--exclude-drawing-sheet','--output',str(OUT/(board+'.svg')),str(OUT/(board+'.kicad_pcb'))],capture_output=True,check=True)
hashes={n:sha(OUT/n) for n in ['head.kicad_pcb','controller.kicad_pcb','flex-study.kicad_pcb','camera.kicad_sch',name+'.kicad_pcb']}
result={'revision':'OV9281-P4-R10','fabrication_ready':False,'source_checkpoint':str(SRC),'rigid_board_pad_net_checks':count,'assembled_pin_alignment_checks':24,'flex_contact_paths_verified':24,'schematic_erc_errors':0,'schematic_erc_warnings':0,'boards':summary,'inner_copper_retention':copper,'sha256':hashes,'assembly_limit':'Composite overview only; mixed rigid/flex stackups remain authoritative in the three separate boards.'}
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'component-reservations.json').write_text(json.dumps({'native_sha256':hashes,'boards':components,'scope':'Native courtyard XY and side only; component height remains an explicit mechanical assumption.'},indent=2)+'\n');print(json.dumps(result,indent=2))
