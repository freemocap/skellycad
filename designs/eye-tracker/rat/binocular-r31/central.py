"""Build the uncapped two-sided carrier and retain the R30 stem interface."""
from pathlib import Path
import sys,json,hashlib,zipfile
import numpy as np
import FreeCAD as A,Part
R=Path.cwd();S=R/'designs/eye-tracker/rat/binocular-r31';O=R/'generated/eye-tracker/rat/binocular-r31'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world
cfg=json.loads((S/'recipe.json').read_text());m=cfg['source'];assert hashlib.sha256((R/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256']
def pose(t):return A.Placement(A.Matrix(*np.asarray(t).ravel().tolist()))
def moved(s,t):
 s=s.copy();s.Placement=pose(t).multiply(s.Placement);return s
T=np.array(cfg['mount_to_skull']);src=A.openDocument(str(R/m['native_checkpoint']));d=A.openDocument(str(O/'placement.FCStd'))
tray=world(src.RetainedPCBTray).transformed(pose(T).inverse().toMatrix());finished=world(src.FinishedCarrier).transformed(pose(T).inverse().toMatrix())
upper=tray.common(Part.makeBox(40,30,60,A.Vector(-15,7.5,-30)))
stem=finished.common(Part.makeBox(20,15,12,A.Vector(-5,-7.5,-6)))
bridge=Part.makeBox(2.8,7.5,5.0,A.Vector(2.0,5.0,-2.5))
trays=[moved(upper,np.array(v['board_transform'])) for v in cfg['sides'].values()]
central=stem.multiFuse([bridge,*trays]).removeSplitter()
for side,rec in cfg['sides'].items():
 relief=Part.makeBox(1.,4.5,3.2,A.Vector(5.18706399647303,10.53,16.4));central=central.cut(moved(relief,np.array(rec['board_transform']))).removeSplitter()
 s=Part.Shape();s.read(str(O/(side+'-JST_4pin.brep')));b=s.BoundBox;central=central.cut(Part.makeBox(b.XLength+.4,b.YLength+.4,b.ZLength+.4,A.Vector(b.XMin-.2,b.YMin-.2,b.ZMin-.2))).removeSplitter()
report={'units':'mm','cut_plane_mount_y_mm':7.5,'bridge_box_origin_mm':[2,5,-2.5],'bridge_box_size_mm':[2.8,7.5,5.],'valid':central.isValid(),'solids':len(central.Solids),'stem_preserved_difference_mm3':stem.cut(central).Volume,'components':{}}
for side in cfg['sides']:
 for name in ['PCB','JST_4pin']:
  s=Part.Shape();s.read(str(O/(side+'-'+name+'.brep')));report['components'][side+name]=central.common(s).Volume
 print(side,'tray valid',trays[list(cfg['sides']).index(side)].isValid(),flush=True)
print(report,flush=True)
assert central.isValid() and len(central.Solids)==1 and report['stem_preserved_difference_mm3']<1e-6
assert all(v<1e-6 for v in report['components'].values())
o=d.addObject('Part::Feature','CentralCarrier');o.Shape=moved(central,T)
for side,s in zip(cfg['sides'],trays):s.exportBrep(str(O/(side+'-tray.brep')))
central.exportBrep(str(O/'central.brep'));stem.exportBrep(str(O/'stem.brep'));(O/'central-validation.json').write_text(json.dumps(report,indent=2));d.recompute();p=O/'central-carrier.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
A.closeDocument(d.Name);A.closeDocument(src.Name);print('CENTRAL_SAVED')


