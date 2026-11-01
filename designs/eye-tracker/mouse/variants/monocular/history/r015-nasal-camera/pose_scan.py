from pathlib import Path
import json,numpy as np
import FreeCAD as A,Part,Mesh
R=Path.cwd();S=R/'designs/eye-tracker/mouse/nasal-camera-r15';b=json.loads((S/'baseline.json').read_text());e=json.loads((S.parent/'landmark-eyes-r04/placement.json').read_text());v=A.Vector(*e['eyes'][0]['axis_world']);c=A.Vector(*e['eyes'][0]['center_world_mm']);old=A.Vector(*b['axis']['origin']);direction=A.Vector(*b['axis']['direction']);nasal=A.Vector(*np.array(e['skull_basis_columns'])[:,0]);start=old+nasal*2.5;ideal=c+v*((old-c).dot(v));m=json.loads((S.parent/'landmark-eye-placement-r14/review.json').read_text());d=A.openDocument(str(R/m['native_checkpoint']));holder=d.eye_primary_Holder.Shape.copy();holder.Placement=d.eye_primary_Holder.getGlobalPlacement();tray=d.RetainedPCBTray.Shape
for f in [0,.1,.2,.3,.4,.5,.6,.7,.8,1]:
 p=start*(1-f)+ideal*f;aim=c-p;aim.normalize();rot=A.Rotation(direction,aim);D=A.Placement(p-rot.multVec(old),rot);h=holder.copy();h.Placement=D.multiply(h.Placement);print(f,'angle',aim.getAngle(-v)*180/np.pi,'holdertray',h.common(tray).Volume,'gap',h.distToShape(tray)[0],flush=True)
