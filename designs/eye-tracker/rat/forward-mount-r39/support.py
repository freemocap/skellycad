from pathlib import Path
import sys,json,zipfile,numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/forward-mount-r39';O=R/'generated/eye-tracker/rat/forward-mount-r39';cfg=json.loads((S/'recipe.json').read_text());T=np.array(cfg['mount_to_skull']);inv=np.linalg.inv(T)
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
def pose(t):return A.Placement(A.Matrix(*np.asarray(t).ravel().tolist()))
def moved(s,t):return s.transformed(pose(t).toMatrix())
def local(o):return moved(world(o),inv)
def load(stage):return A.openDocument(str(O/(stage+'.FCStd')))
def obstacles(d):
 out={}
 for p in O.glob('*.brep'):
  if p.stem=='central' or p.stem.endswith('RetainedSocket'):continue
  s=Part.Shape();s.read(str(p));out[p.stem]=s
 return out
def save(d,stage,report):
 d.recompute();p=O/(stage+'.FCStd');d.saveAs(str(p))
 with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
 (O/(stage+'.json')).write_text(json.dumps(report,indent=2));A.closeDocument(d.Name)
