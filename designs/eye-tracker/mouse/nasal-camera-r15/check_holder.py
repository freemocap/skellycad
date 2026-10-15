from pathlib import Path
import FreeCAD as A,Part,Mesh
r=Path.cwd();d=A.openDocument(str(r/'generated/eye-tracker/mouse/nasal-camera-r15/ET-MOUSE-NASAL-R15.FCStd'));h=d.eye_primary_Holder.Shape.copy();h.Placement=d.eye_primary_Holder.getGlobalPlacement()
for n in ['RetainedPCBTray','RetainedSocket','UpperSupport','RearRibbonGuard']:
 s=d.getObject(n).Shape;print(n,s.common(h).Volume,flush=True)
