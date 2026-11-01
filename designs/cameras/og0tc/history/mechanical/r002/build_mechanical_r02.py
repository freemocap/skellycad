"""OC0TC integrated-optics packaging concept plus unmodified selected Pupil reference.
Geometry is envelope-only; see integration/r02/design.json for assumptions.
"""
from pathlib import Path
import sys,json,hashlib
import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore,QtWidgets
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
sys.path.insert(0,str(ROOT/'designs/eye-tracker'))
from shared.camera import add_camera,selected_model
OUT=BASE/'mechanical/r02'
if (OUT/'oc0tc-usb-comparison.FCStd').exists(): raise SystemExit('Preserve R02; create a new revision.')
Gui.showMainWindow();Gui.getMainWindow().hide()
app=QtWidgets.QApplication.instance();app.setQuitOnLastWindowClosed(False)
result=1

def run():
    global result
    try:
        model=selected_model() # Verifies native checkpoint and every physical part hash.
        doc=App.newDocument('OC0TC_USB_Concept_R02')
        group=doc.addObject('App::Part','NewCamera');group.Label='OC0TC integrated optics / R02 / 58 x 14 mm'
        parts=[]
        def add(name,shape,color,scope):
            o=doc.addObject('PartDesign::Feature',name);o.Shape=shape;o.ViewObject.ShapeColor=color
            o.addProperty('App::PropertyString','Evidence').Evidence=scope;group.addObject(o);parts.append(o);return o
        add('MainPCB',Part.makeBox(20,14,.8),(.15,.45,.25),'20 x 14 x 0.8 mm design envelope; no routed electronics')
        add('Flex',Part.makeBox(30,4,.15,App.Vector(20,5,.325)),(.95,.65,.1),'30 x 4 mm illustrative flex; terminations and stackup unverified')
        add('HeadPCB',Part.makeBox(8,8,.8,App.Vector(50,3,0)),(.15,.45,.25),'8 x 8 mm design envelope')
        add('OC0TCModule',Part.makeBox(3,3,1.7,App.Vector(52.5,5.5,.8)),(.12,.12,.15),'Integrated optics module: published 1.7 mm height; 3 x 3 mm XY is reserved space, not package dimensions')
        add('CX3',Part.makeBox(10,10,1.7,App.Vector(3,2,.8)),(.15,.15,.17),'Published 10 x 10 x 1.7 mm package envelope; BGA escape not implemented')
        add('JSTEnvelope',Part.makeBox(5,5.6,3,App.Vector(15,4.2,.8)),(.9,.9,.85),'Conservative design allowance; not verified manufacturer geometry')
        add('PowerAllowance',Part.makeBox(2.4,10,1,App.Vector(.3,2,.8)),(.4,.45,.5),'Space allowance only; regulator parts and thermal budget unresolved')
        add('FlashAllowance',Part.makeBox(5,4,.8,App.Vector(5,5,-.8)),(.2,.2,.2),'Underside space allowance only; flash package not selected')
        for y in [3.2,9.8]:
            add('IRLEDEnvelope'+str(y).replace('.','_'),Part.makeBox(1,1,.5,App.Vector(53.5,y,.8)),(.8,.75,.65),'1 mm LED allowance; current driver, output and thermal design pending')
        axis=doc.addObject('Part::Feature','NewOpticalAxis');axis.Shape=Part.makeLine(App.Vector(54,7,2.5),App.Vector(54,7,7))
        axis.ViewObject.LineColor=(.1,.7,.9);axis.ViewObject.LineWidth=3;group.addObject(axis)
        axis.addProperty('App::PropertyString','Evidence').Evidence='Module top-center reference normal; actual optical datum and close-focus performance unverified'
        reference=add_camera(doc,name='PupilReference')
        rotation=App.Rotation(App.Vector(0,0,1),-90)
        shapes=[]
        for obj in reference.PhysicalParts:
            sh=obj.Shape.copy();sh.Placement=App.Placement(App.Vector(),rotation).multiply(sh.Placement);shapes.append(sh)
        bb=Part.makeCompound(shapes).BoundBox
        reference.Placement=App.Placement(App.Vector(-bb.XMin,27-bb.YMin,-bb.ZMin),rotation)
        doc.recompute()
        physical=Part.makeCompound([o.Shape for o in parts]);b=physical.BoundBox
        assert abs(b.XLength-58)<1e-6 and abs(b.YLength-14)<1e-6
        assert all(o.Shape.isValid() for o in parts)
        assert not any('Barrel' in o.Name or 'Holder' in o.Name for o in parts)
        assert all(a.Shape.common(b.Shape).Volume < 1e-7 for i,a in enumerate(parts) for b in parts[i+1:])
        report={'revision':'OC0TC-USB-CONCEPT-R02','units':'mm','envelope_mm':[b.XLength,b.YLength,b.ZLength],
                'all_new_solids_valid':True,'reference_checkpoint':model['revision'],
                'reference_hashes_verified':True,'full_pinout_available':False,'routed':False,
                'physical_fit_verified':False,'optics_verified':False,'bridge_sensor_compatibility_verified':False,
                'separate_lens_parts':False,'module_xy_verified':False,'module_height_mm':1.7}
        Gui.setActiveDocument(doc.Name);view=Gui.getDocument(doc.Name).activeView();view.viewAxonometric();view.fitAll()
        doc.saveAs(str(OUT/'oc0tc-usb-comparison.FCStd'))
        Part.export(parts,str(OUT/'oc0tc-usb-envelope.step'))
        view.saveImage(str(OUT/'comparison.png'),1400,900,'White')
        reference.Visibility=False;view.viewAxonometric();view.fitAll()
        view.saveImage(str(OUT/'concept.png'),1400,700,'White')
        (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report));result=0
        App.closeDocument(doc.Name)
    finally:app.quit()
QtCore.QTimer.singleShot(0,run);app.exec();sys.exit(result)
