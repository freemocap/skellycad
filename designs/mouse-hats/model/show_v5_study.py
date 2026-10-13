"""Separate aligned mesh study; CURRENT parts are never replaced here."""
import os,json
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Mesh
ROOT=Path(os.environ['CAD_PLAYGROUND_ROOT'])
OUT=ROOT/'generated/mouse-hats/arms'
report=json.loads((OUT/'registration.json').read_text())
doc=App.newDocument('V5ArmsStudy')
doc.Label='STUDY — V5 arms and camera pose — provisional alignment'
colors=[(.9,.5,.2),(.7,.4,.9),(.25,.7,.9),(.3,.9,.4),(.9,.3,.5),(1,0,0)]
names=['Camera holder','Socket','PCB tray + stem','Rear U-shaped arm','Top bent arm','Loose two-triangle patch (hidden)']
for entry,color in zip(report['components'],colors):
    i=entry['id'];obj=doc.addObject('Mesh::Feature',f'V5Shell{i}')
    obj.Label=f"{i:02d} — {names[i-1]} — V5 mesh"
    obj.Mesh=Mesh.Mesh(str(OUT/f'v5-shell-{i}.stl'))
    obj.ViewObject.ShapeColor=color;obj.ViewObject.DisplayMode='Flat Lines'
    if i==6:obj.Visibility=False
source=next((d for d in App.listDocuments().values() if d.getObject('CleanedTrayAndMount')),None)
if source is None:
    import runpy
    api=runpy.run_path(str(ROOT/'designs/mouse-hats/model/build_mount.py'));api['load_modules']()
    source=App.openDocument(str(ROOT/'generated/mouse-hats/model/tray-cleanup/cleaned-tray.FCStd'))
reference=doc.addObject('Part::Feature','CurrentTrayReference')
reference.Shape=source.CleanedTrayAndMount.Shape.copy()
reference.Label='CURRENT tray — fixed alignment comparison (toggle visibility)'
reference.ViewObject.ShapeColor=(.8,.8,.8);reference.ViewObject.Transparency=70
reference.Visibility=False
doc.recompute();Gui.activeDocument().activeView().viewIsometric();Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(OUT/'v5-arms-study.FCStd'))
