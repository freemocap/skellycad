from pathlib import Path
import FreeCAD as A,FreeCADGui as G
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'generated/mouse-hats/pcb-retention-study/height-geometry/with-catch/numeric-labels'
d=A.newDocument('NumericCatchLabels')
for letter,dy in [('H',0),('T',-25)]:
 s=A.openDocument(str(p/('R11B-'+letter+'-numeric-catch.FCStd')))
 for name,dz in [('Carrier',0),('Cap',-55)]:
  sh=s.getObject(name).Shape.copy()
  if name=='Cap':sh.rotate(A.Vector(),A.Vector(0,1,0),180)
  sh.translate(A.Vector(0,dy,dz))
  o=d.addObject('Part::Feature',letter+name);o.Shape=sh;o.ViewObject.ShapeColor=(.25,.7,.8) if letter=='H' else (.9,.65,.25)
 A.closeDocument(s.Name)
A.setActiveDocument(d.Name);d.recompute()
n=A.Vector(-1,0,0);u=A.Vector(0,1,0)
G.activeDocument().activeView().setCameraOrientation(A.Rotation(u.cross(n),u,n,'ZXY').Q)
G.activeDocument().activeView().fitAll()
d.saveAs(str(p/'numeric-label-review.FCStd'))
