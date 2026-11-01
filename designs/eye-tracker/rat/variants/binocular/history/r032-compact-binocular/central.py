"""Replace paired tray backs and tall bridge with a short shared windowed spine."""
from pathlib import Path
import sys,json,hashlib,zipfile
import numpy as np
import FreeCAD as A,Part
R=Path.cwd();S=R/'designs/eye-tracker/rat/compact-binocular-r32';O=R/'generated/eye-tracker/rat/compact-binocular-r32';P=S.parent/'binocular-r31';PO=R/'generated/eye-tracker/rat/binocular-r31'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
cfg=json.loads((P/'recipe.json').read_text());source=json.loads((P/'review.json').read_text());oldT=np.array(cfg['mount_to_skull']);T=oldT.copy();T[2,3]-=2
m=cfg['source'];assert hashlib.sha256((R/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256'];src=A.openDocument(str(R/m['native_checkpoint']));d=A.openDocument(str(O/'lowered.FCStd'))
def pose(t):return A.Placement(A.Matrix(*np.asarray(t).ravel().tolist()))
def moved(s,t):
 s=s.copy();s.Placement=pose(t).multiply(s.Placement);return s
tray=world(src.RetainedPCBTray).transformed(pose(oldT).inverse().toMatrix());finished=world(src.FinishedCarrier).transformed(pose(oldT).inverse().toMatrix())
# Retain the front catches and edge ledges, removing both thick tray back walls.
retention=tray.common(Part.makeBox(20,30,60,A.Vector(5.08706399647303,7.5,-30)))
stem=finished.common(Part.makeBox(20,14.4,12,A.Vector(-5,-7.5,-6)))
spine=Part.makeBox(1.2,11.1,36.2,A.Vector(2.68706399647303,6.5,-18.1770758806404))
for z in [-13.5,2.0]:spine=spine.cut(Part.makeBox(2,5.5,11.5,A.Vector(2.3,9,z)))
trays=[];records={}
for side,old in cfg['sides'].items():
 B=np.array(old['board_transform']);B[1,3]=-1.;B[0,3]+=(-1.4 if side=='Right' else 1.4);delta=B@np.linalg.inv(np.array(old['board_transform']));trays.append(moved(retention,B))
 components={}
 for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001']:
  s=world(src.getObject(n)).transformed(pose(oldT).inverse().toMatrix())
  s=moved(s,B if n in ['PCB','JST_4pin'] else np.array(old['head_delta']))
  components[n]=s;s.exportBrep(str(O/(side+'-'+n+'.brep')))
 cam=d.getObject(side+'Camera');cam.Placement=pose(T);cam.PhysicalParts[0].Shape=Part.makeCompound([components['PCB'],components['camera_pcb']]);cam.PhysicalParts[2].Shape=Part.makeCompound([components[n] for n in ['JST_4pin','IR_LED','IR_LED_001']])
 records[side]={**old,'board_transform':B.tolist()}
central=stem.multiFuse([spine,*trays]).removeSplitter()
for side,rec in records.items():
 B=np.array(rec['board_transform']);relief=Part.makeBox(1.,4.5,3.2,A.Vector(5.18706399647303,10.53,16.4));central=central.cut(moved(relief,B)).removeSplitter()
 s=Part.Shape();s.read(str(O/(side+'-JST_4pin.brep')));b=s.BoundBox;central=central.cut(Part.makeBox(b.XLength+.4,b.YLength+.4,b.ZLength+.4,A.Vector(b.XMin-.2,b.YMin-.2,b.ZMin-.2))).removeSplitter()
prior=world(d.CentralCarrier).transformed(pose(T).inverse().toMatrix());report={'units':'mm','shared_spine_thickness_mm':1.2,'board_back_gap_mm':1.2,'board_drop_mount_y_mm':5,'old_central_volume_mm3':prior.Volume,'new_central_volume_mm3':central.Volume,'volume_reduction_percent':100*(1-central.Volume/prior.Volume),'old_central_mount_y_max_mm':prior.BoundBox.YMax,'new_central_mount_y_max_mm':central.BoundBox.YMax,'valid':central.isValid(),'solids':len(central.Solids),'intersections_mm3':{}}
assert central.isValid() and len(central.Solids)==1;assert central.Volume<prior.Volume*.8
for side in records:
 for n in ['PCB','JST_4pin']:
  s=Part.Shape();s.read(str(O/(side+'-'+n+'.brep')));v=central.common(s).Volume;report['intersections_mm3'][side+n]=v;assert v<1e-6,(side,n,v)
base=world(d.Baseplate).transformed(pose(T).inverse().toMatrix());report['intersections_mm3']['Baseplate']=central.common(base).Volume;assert report['intersections_mm3']['Baseplate']<1e-6
assign(d.CentralCarrier,moved(central,T));central.exportBrep(str(O/'central.brep'));stem.exportBrep(str(O/'stem.brep'))
# Remove obsolete carrier and support geometry; new supports are built in the next stage.
for name in ['FinishedCarrier','RightUpperSupport','RightLowerSupport','LeftUpperSupport','LeftLowerSupport']:d.removeObject(name)
recipe={**cfg,'revision':'ET-RAT-COMPACT-BINOCULAR-R32','source':source,'geometry_lineage_r30':m,'mount_to_skull':T.tolist(),'board_back_gap_mm':1.2,'board_raise_mount_y_mm':-1.,'world_lowering_mm':2.,'sides':records,'central_design':'One 1.2 mm windowed spine with retained opposing catches and short original stem interface'}
(S/'recipe.json').write_text(json.dumps(recipe,indent=2));(S/'central-validation.json').write_text(json.dumps(report,indent=2));d.recompute();p=O/'compact-central.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
A.closeDocument(d.Name);A.closeDocument(src.Name);print(json.dumps(report,indent=2))
