"""Add editable recovered centerlines to the V5 study, leaving CURRENT untouched."""
from pathlib import Path
import json,sys,os
import FreeCAD as App
import FreeCADGui as Gui
import Part
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
from path_features import ArmPath
ROOT=Path(os.environ['CAD_PLAYGROUND_ROOT']);OUT=ROOT/'generated/mouse-hats/arms'
data=json.loads((OUT/'recovered-paths.json').read_text())
doc=App.getDocument('V5ArmsStudy')
if doc is None:doc=App.openDocument(str(OUT/'v5-arms-study.FCStd'))
for name,arm,shell in [('RearArmPath','rear',4),('TopArmPath','top',5)]:
    obj=doc.getObject(name)
    if obj is None:
        obj=doc.addObject('Part::FeaturePython',name)
        ArmPath(obj,[s['center_mm'] for s in data['arms'][arm]['sections']])
    obj.Label=arm.title()+' arm — editable recovered centerline (not solid)'
    obj.ViewObject.Proxy=0;obj.ViewObject.LineColor=(1.0,1.0,0.15);obj.ViewObject.LineWidth=5
    obj.Visibility=True
    doc.getObject('V5Shell'+str(shell)).ViewObject.Transparency=65
axis=doc.getObject('SocketAxis') or doc.addObject('Part::Feature','SocketAxis')
c=App.Vector(*data['socket_spheres'][0]['center_mm'])
n=App.Vector(*data['socket_axis_from_inner_to_outer_center'])
axis.Shape=Part.makeLine(c-n*4,c+n*7)
axis.Label='Measured socket axis — axial roll not yet resolved'
axis.ViewObject.LineColor=(1,1,1);axis.ViewObject.LineWidth=3
doc.recompute();App.setActiveDocument(doc.Name)
Gui.Selection.clearSelection();Gui.Selection.addSelection(doc.RearArmPath)
doc.save()
Gui.activeDocument().activeView().saveImage(str(OUT/'recovered-paths.png'),1100,850,'Current')
