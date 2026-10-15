from pathlib import Path
import FreeCAD as A,Part,Mesh
r=Path.cwd();o=r/'generated/eye-tracker/mouse/nasal-camera-r15';d=A.openDocument(str(o/'ET-MOUSE-NASAL-R15.FCStd'));rib=d.RibbonCandidate.Shape
for n in ['RetainedPCBTray','RetainedSocket','UpperSupport','RearRibbonGuard','FinishedCarrier']:
 s=d.getObject(n).Shape;c=rib.common(s);print(n,c.Volume, c.BoundBox if c.Volume else '',flush=True)
