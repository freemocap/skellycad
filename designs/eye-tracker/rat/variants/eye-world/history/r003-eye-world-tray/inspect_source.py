from pathlib import Path
import json,sys,numpy as np
import FreeCAD as A,Part
R=Path.cwd();O=R/'generated/eye-tracker/rat/eye-world-tray-r03';S=R/'designs/eye-tracker/rat';m=json.loads((S/'lowered-cameras-r43/review.json').read_text());d=A.openDocument(str(R/m['native_checkpoint']));c=json.loads((S/'lowered-cameras-r43/recipe.json').read_text());T=np.array(c['mount_to_skull']);H=T@np.array(c['sides']['Left']['head'])
def world(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s
for name in ['CentralCarrier','FinishedCarrier','Lefteye_primary_Holder']:
 s=world(d.getObject(name));print(name,s.Volume,s.BoundBox,flush=True)
 if name=='Lefteye_primary_Holder':
  s=s.transformed(A.Matrix(*np.linalg.inv(H).ravel().tolist()));s.exportBrep(str(O/'source-holder-head.brep'));print('HEAD',s.BoundBox,flush=True)
  for i,f in enumerate(s.Faces):
   print(i,type(f.Surface).__name__,round(f.Area,3),tuple(round(v,3) for v in f.CenterOfMass),f.BoundBox,flush=True)
 else:s.exportBrep(str(O/(name+'.brep')))
A.closeDocument(d.Name)
