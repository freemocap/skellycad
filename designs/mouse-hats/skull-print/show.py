"""Run in pinned FreeCAD GUI after build.py; show the actual exported color parts."""
from pathlib import Path
import FreeCAD as App,FreeCADGui as Gui,Mesh
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-print'
d=App.newDocument('SkullBaseplatePrint');d.Label='PRINT — Skull, eyes, embedded current baseplate — 1:1'
for n,c in [('Skull',(.86,.8,.63)),('Eyes',(1.,1.,1.)),('PupilCornea',(.08,.08,.08)),('Mount',(.125,.66,.74))]:
 o=d.addObject('Mesh::Feature',n);o.Mesh=Mesh.Mesh(str(OUT/(n+'.stl')));o.ViewObject.ShapeColor=c
d.recompute();Gui.activeDocument().activeView().viewIsometric();Gui.activeDocument().activeView().fitAll()
d.saveAs(str(ROOT/'designs/mouse-hats/skull-print/SkullBaseplatePrint.FCStd'))
Gui.activeDocument().activeView().saveImage(str(OUT/'preview.png'),1200,1000,'Current')
print(d.Name)
