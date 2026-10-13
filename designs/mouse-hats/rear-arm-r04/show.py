"""Side-by-side route review; offsets only affect this inspection document."""
from pathlib import Path
import sys,json
import FreeCAD as App
import FreeCADGui as Gui
import Part,Mesh
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
for p in [HERE,HERE.parent/'model',HERE.parent/'print-test-r03']:sys.path.insert(0,str(p))
import rear_sweep,ribbon_carrier_features,socket_revision_features
OUT=ROOT/'generated/mouse-hats/rear-arm-r04'
old=App.openDocument(str(ROOT/'generated/mouse-hats/print-test/r03/print-in-place-review.FCStd'))
doc=App.newDocument('RearRibbonOptions');doc.Label='R04 rear ribbon sweep - R03 / A / B comparison'
for key,offset,color in [('R03',30,(.65,.67,.7)),('A',0,(.23,.72,.82)),('B',-30,(.92,.62,.25))]:
    if key=='R03':shape=old.Carrier.Shape.copy()
    else:
        source=App.openDocument(str(OUT/('r04'+key.lower()+'-carrier.FCStd')));shape=source.RibbonClearanceCarrier.Shape.copy()
    group=doc.addObject('App::Part','Option'+key);group.Label={'R03':'R03 - current rear arm','A':'R04A - V5-guided sweep','B':'R04B - extra 1.25 mm ribbon space'}[key]
    for name,s,c in [('Carrier',shape,color),('Holder',old.Holder.Shape,(.66,.45,.81)),('Clip',old.ClipReference.Shape,(.85,.4,.35))]:
        ob=doc.addObject('Part::Feature',key+name);ob.Shape=s.copy();group.addObject(ob)
        ob.ViewObject.ShapeColor=c;ob.ViewObject.LineColor=(.12,.16,.19)
    group.Placement.Base=App.Vector(0,offset,0)
    label=doc.addObject('App::Annotation','Label'+key);label.LabelText=[group.Label];label.Position=App.Vector(-5,offset-6,-14)
    label.ViewObject.TextColor=(.1,.15,.18);label.ViewObject.FontSize=14
# Legacy reference can be toggled for A without contaminating manufacturing exports.
v5=doc.addObject('Mesh::Feature','V5RearReference');v5.Label='V5 rear mesh - optional A overlay'
v5.Mesh=Mesh.Mesh(str(ROOT/'generated/mouse-hats/arms/v5-shell-4.stl'))
v5.ViewObject.ShapeColor=(.25,.8,.3);v5.ViewObject.Transparency=65;v5.ViewObject.Visibility=False
App.setActiveDocument(doc.Name);doc.recompute()
up=App.Vector(0,1,0);normal=App.Vector(-1,0,0)
Gui.activeDocument().activeView().setCameraOrientation(App.Rotation(up.cross(normal),up,normal,'ZXY').Q)
Gui.activeDocument().activeView().fitAll();doc.saveAs(str(OUT/'rear-arm-options.FCStd'))
