"""Import actual KiCad STEP and build a separate bench mounting study.

Run with the pinned FreeCAD bundled Python. Connector/cable shapes are explicit
clearance envelopes, not manufacturer models or eye-camera geometry.
"""
from pathlib import Path
import hashlib
import argparse
import json
import sys
import FreeCAD as App
import Part
import FreeCADGui as Gui
from PySide import QtWidgets, QtCore

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--board-step',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
OUT=args.output.resolve()
if OUT.exists():
    raise SystemExit('Use a new output directory; preserve reviewed revisions.')
OUT.mkdir(parents=True)
STEP=args.board_step.resolve(strict=True)
Gui.showMainWindow(); Gui.getMainWindow().hide()

app=QtWidgets.QApplication.instance()
app.setQuitOnLastWindowClosed(False)
exit_code=1
def run():
    global exit_code
    try:
        doc=App.newDocument('CameraInterfaceR02')
        def add(name,shape,color):
            obj=doc.addObject('PartDesign::Feature',name); obj.Shape=shape
            obj.ViewObject.ShapeColor=color
            return obj
        shape=Part.Shape(); shape.read(str(STEP))
        pcb=add('ImportedKiCadBoard',shape,(.1,.42,.23))
        pcb.addProperty('App::PropertyString','SourceSHA256').SourceSHA256=hashlib.sha256(STEP.read_bytes()).hexdigest()
        pcb.addProperty('App::PropertyString','Scope').Scope='Actual board-only KiCad STEP; copper omitted; nominal PCB 1.6 mm'
        
        tray=Part.makeBox(32,36,2,App.Vector(-1,-35,-3))
        for x,y in [(2.5,-2.5),(27.5,-2.5),(2.5,-31.5),(27.5,-31.5)]:
            tray=tray.fuse(Part.makeCylinder(2,1,App.Vector(x,y,-1)))
            tray=tray.cut(Part.makeCylinder(1.1,4,App.Vector(x,y,-3)))
        for x in [-1,30.3]:
            tray=tray.fuse(Part.makeBox(.7,36,5,App.Vector(x,-35,-1)))
        tray=tray.removeSplitter()
        holder=add('BenchTray',tray,(.3,.4,.7))
        holder.addProperty('App::PropertyString','Scope').Scope='Teaching dimensions, mm; 0.3 mm side gap; screw hardware and print fit untested'
        envelopes=[]
        for i,y in enumerate([-10.5,-30.5],1):
            env=add('ConnectorEnvelope'+str(i),Part.makeBox(21.6,4.5,1.9,App.Vector(4.2,y,1.6)),(.85,.8,.6))
            env.addProperty('App::PropertyString','Scope').Scope='Approximate clearance box, not a manufacturer STEP model'
            envelopes.append(env)
            cable=add('RibbonEnvelope'+str(i),Part.makeBox(16,8 if i==1 else 12,.3,App.Vector(7,y-(8 if i==1 else 12),2.3)),(.8,.4,.12))
            cable.addProperty('App::PropertyString','Scope').Scope='Illustrative route; not vendor cable geometry or minimum bend-radius validation'
            envelopes.append(cable)
        doc.recompute()
        report={'units':'mm','source_step_sha256':hashlib.sha256(STEP.read_bytes()).hexdigest(),
                'board_bbox_mm':[shape.BoundBox.XLength,shape.BoundBox.YLength,shape.BoundBox.ZLength],
                'native_geometry_valid':all(o.Shape.isValid() for o in doc.Objects),
                'board_tray_intersection_mm3':shape.common(tray).Volume,
                'envelope_tray_intersections_mm3':{o.Name:o.Shape.common(tray).Volume for o in envelopes},
                'physical_fit_tested':False,'camera_optics_included':False}
        assert report['native_geometry_valid']
        assert report['board_tray_intersection_mm3'] < 1e-6
        assert all(v<1e-6 for v in report['envelope_tray_intersections_mm3'].values())
        Gui.setActiveDocument(doc.Name)
        view=Gui.getDocument(doc.Name).activeView()
        view.viewAxonometric(); view.fitAll()
        doc.recompute(); doc.saveAs(str(OUT/'camera-interface-assembly.FCStd'))
        Part.export([pcb,holder]+envelopes,str(OUT/'camera-interface-assembly.step'))
        view.saveImage(str(OUT/'preview.png'),1200,900,'White')
        (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report))
        App.closeDocument(doc.Name)
        Gui.getMainWindow().close()
        exit_code=0
    finally:
        app.quit()
QtCore.QTimer.singleShot(0,run)
app.exec()
sys.exit(exit_code)
