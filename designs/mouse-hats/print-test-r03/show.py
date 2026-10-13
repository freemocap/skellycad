"""Show current R03 assembled print unit and a separate socket section."""
from pathlib import Path
import sys
import FreeCAD as App
import FreeCADGui as Gui
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent/'model'))
import socket_revision_features
OUT=ROOT/'generated/mouse-hats/print-test/r03'
assembly=App.openDocument(str(OUT/'print-in-place-review.FCStd'))
for o in assembly.Objects:
    o.ViewObject.Visibility=o.Name in ['Carrier','Holder','ClipReference']
for name,color in [('Carrier',(.23,.72,.82)),('Holder',(.66,.45,.81)),('ClipReference',(.87,.67,.28))]:
    o=assembly.getObject(name);o.ViewObject.ShapeColor=color;o.ViewObject.LineColor=(.12,.16,.19)
assembly.Label='PRINT TEST R03 - stronger socket roots / 0.332 mm measured gap'
normal=App.Vector(1,.5,1);normal.normalize();up=App.Vector(0,1,0)
Gui.activeDocument().activeView().setCameraOrientation(App.Rotation(up.cross(normal),up,normal,'ZXY').Q)
Gui.activeDocument().activeView().fitAll();assembly.save()
# A bounded cross section makes the print-in-place gap inspectable without
# changing the actual geometry or moving the ball relative to the socket.
center=App.Vector(12.139962388488971,4.892484895319452,24.37007035179014)
region=Part.makeSphere(6,center)
cut=Part.makeBox(40,80,80,App.Vector(center.x,-30,-10))
section=App.newDocument('R03SocketSection');section.Label='R03 - socket cross section (inspection only)'
for name,color in [('Carrier',(.23,.72,.82)),('Holder',(.66,.45,.81))]:
    obj=section.addObject('Part::Feature',name+'Section')
    obj.Shape=assembly.getObject(name).Shape.common(region).cut(cut)
    obj.ViewObject.ShapeColor=color;obj.ViewObject.LineColor=(.12,.16,.19)
section.recompute()
Gui.activeDocument().activeView().setCameraOrientation(App.Rotation(App.Vector(0,0,-1),App.Vector(0,1,0),App.Vector(1,0,0),'ZXY').Q)
Gui.activeDocument().activeView().fitAll();section.saveAs(str(OUT/'socket-section.FCStd'))
App.setActiveDocument(assembly.Name)
