from pathlib import Path
import FreeCAD as A,Part,Mesh,MeshPart
r=Path.cwd();d=A.openDocument(str(r/'generated/eye-tracker/mouse/nasal-camera-r15/ET-MOUSE-NASAL-R15.FCStd'));m=MeshPart.meshFromShape(Shape=d.FinishedCarrier.Shape,LinearDeflection=.03,AngularDeflection=.12,Relative=False);pairs=m.getSelfIntersections();print('pairs',len(pairs));print(pairs);print([[m.Facets[i].Points for i in row[:2]] for row in pairs[:2]])

