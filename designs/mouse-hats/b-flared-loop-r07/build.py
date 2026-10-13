"""B-selected plugward flare, on the complete R06 assembly. Dimensions mm."""
from pathlib import Path
import copy,hashlib,json,sys,math
import FreeCAD as App,FreeCADGui as Gui,Part
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
for p in [HERE,HERE.parent/'model',HERE.parent/'rear-arm-r11']:sys.path.insert(0,str(p))
from assembly_geometry import build_geometry
s=json.loads((HERE/'settings.json').read_text());source=ROOT/s['source_checkpoint']
assert hashlib.sha256(source.read_bytes()).hexdigest()==s['source_sha256']
assert hashlib.sha256((HERE/'socket-source.brep').read_bytes()).hexdigest()==s['socket_source_sha256']
src=App.openDocument(str(source))
carrier,arm,path=build_geometry(copy.deepcopy(s),src,HERE/'socket-source.brep')
# Replay B through the same construction with zero flare for exact comparison.
bs=copy.deepcopy(s);bs['plugward_flare_deg']=0
bc,ba,bp=build_geometry(bs,src,HERE/'socket-source.brep')
def remove_text(shape,name,x,normal):
 tool=Part.Shape();tool.read(str(HERE.parent/'loop-options-r05'/(name+'Emboss.brep')))
 outside=Part.makeBox(100,200,200,App.Vector(x-100 if normal<0 else x,-100,-100))
 return shape.cut(tool.common(outside)).removeSplitter()
clean=remove_text(carrier,'Carrier',3.70677424482636,-1)
font=Path('C:/Windows/Fonts/arialbd.ttf')
groups=Part.makeWireString('B2',str(font.parent)+'/',font.name,3.5)
face=Part.makeCompound([Part.makeFace(g,'Part::FaceMakerBullseye') for g in groups])
face.scale(3.5/face.BoundBox.YLength);b=face.BoundBox;face.translate(App.Vector(-(b.XMin+b.XMax)/2,-(b.YMin+b.YMax)/2,0))
mat=App.Matrix();mat.A11=0;mat.A12=0;mat.A13=-1;mat.A21=0;mat.A22=1;mat.A23=0;mat.A31=1;mat.A32=0;mat.A33=0
face=face.transformGeometry(mat);face.translate(App.Vector(3.75677424482636,13.2,0))
mark=face.extrude(App.Vector(-.45,0,0))
carrier=clean.fuse(mark).removeSplitter();carrier.check(True)
assert carrier.isValid() and len(carrier.Solids)==1
cap=remove_text(src.Cap.Shape,'Cap',10.2870639964732,1)
doc=App.newDocument('PlugwardLoopR07');doc.Label='MH-T3-EYE-R07 — B2 plugward ribbon loop'
skip={'PreviousCarrier','NewRearArm','NewRearPath','EyeRibbonArms'}
for old in src.Objects:
 if old.Name in skip:continue
 if old.TypeId=='Part::Feature':
  o=doc.addObject('Part::Feature',old.Name);o.Shape=carrier if old.Name=='Carrier' else cap if old.Name=='Cap' else old.Shape.copy();o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
 elif old.TypeId=='Mesh::Feature':
  o=doc.addObject('Mesh::Feature',old.Name);o.Mesh=old.Mesh.copy();o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
for name,shape in [('NewRearArm',arm),('NewRearPath',path),('PreviousBArm',ba),('PreviousBPath',bp),('EyeRibbonArms',carrier.cut(doc.T3ProtectedTray.Shape))]:
 o=doc.addObject('Part::Feature',name);o.Shape=shape;o.Visibility=False
info=doc.addObject('App::FeaturePython','Revision');info.addProperty('App::PropertyString','RevisionID');info.RevisionID='MH-T3-EYE-R07'
report={'revision':info.RevisionID,'source_sha256':s['source_sha256'],'units':'mm, mm3, degrees','selected_arm':'B','printed_label':'B2','root_flare_toward_plug_deg':s['plugward_flare_deg'],'lens_side_angle_to_plate_deg':90+s['plugward_flare_deg'],'plug_side_angle_to_plate_deg':90-s['plugward_flare_deg'],'previous_B_path_length_mm':bp.Length,'new_path_length_mm':path.Length,'previous_B_rearward_extent_mm':3.70677424482636-ba.BoundBox.XMin,'new_rearward_extent_mm':3.70677424482636-arm.BoundBox.XMin,'max_centerline_plugward_shift_mm':max(bp.Curve.value(i/1000).z-path.Curve.value(i/1000).z for i in range(1001)),'root_center_at_plate_mm':[3.70677424482636,s['root_mm'][1],s['root_mm'][2]],'carrier_valid':True,'carrier_solids':1}
for name in ['Holder','Clip','Baseplate','ApproxPCB','Cap']:
 report[name+'_overlap_mm3']=carrier.common(doc.getObject(name).Shape).Volume
 assert abs(report[name+'_overlap_mm3']-src.Carrier.Shape.common(src.getObject(name).Shape).Volume)<1e-6
for name in ['UpperCatch','UpperRail']:
 assert src.getObject(name).Shape.cut(carrier).Volume<1e-6
report['holder_gap_mm']=carrier.distToShape(doc.Holder.Shape)[0]
assert abs(report['holder_gap_mm']-.33316465223866576)<1e-6
assert carrier.common(doc.OpticalAxis.Shape).Length<1e-6
report['optical_axis_clear']=True
doc.recompute();App.setActiveDocument(doc.Name)
rotation=App.Rotation(App.Vector(0,0,1),App.Vector(1,0,0),App.Vector(0,1,0),'ZXY')
Gui.activeDocument().activeView().setCameraOrientation(rotation.Q);Gui.activeDocument().activeView().fitAll()
checkpoint=ROOT/'designs/mouse-hats/current/checkpoints/MH-T3-EYE-R07.FCStd'
doc.saveAs(str(checkpoint))
(HERE/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
