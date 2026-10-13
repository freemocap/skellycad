"""Current T3 assembly with a lower rear-arm root and a shorter loop."""
from pathlib import Path
import hashlib,json,sys,math
import FreeCAD as App,FreeCADGui as Gui,Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/compact-arm-r04';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(HERE.parent/'model'));sys.path.insert(0,str(HERE.parent/'rear-arm-r11'))
from attachment_arm_features import geometry,unit
from options_root_edges import tray_edges
s=json.loads((HERE/'settings.json').read_text());source=ROOT/s['source_checkpoint']
assert hashlib.sha256(source.read_bytes()).hexdigest()==s['source_sha256']
assert hashlib.sha256((HERE/'socket-source.brep').read_bytes()).hexdigest()==s['socket_source_sha256']
src=next((d for d in App.listDocuments().values() if Path(d.FileName)==source),None) or App.openDocument(str(source))
camera=Gui.getDocument(src.Name).activeView().getCameraOrientation()
shift=App.Vector(*s['joint_shift_mm']);data=[s['rear_data'],s['top_data']]
for d in data:
 d['socket_center_mm']=list(App.Vector(*d['socket_center_mm'])+shift)
 d.update(attachment_radius_mm=2.65,socket_lead_mm=1.,socket_width_mm=3.,socket_thickness_mm=2.2)
rear=data[0];rear['sections']=41
rear['arm'].update(root_mm=s['root_mm'],root_handle_mm=s['root_handle_mm'],socket_handle_mm=s['socket_handle_mm'],root_width_mm=s['root_width_mm'],root_thickness_mm=s['root_thickness_mm'])
rear['arm']['radial_direction']=list(App.Rotation(unit(rear['socket_axis']),s['attachment_angle_deg']).multVec(unit(rear['arm']['radial_direction'])))
arm,_,_,path,twist=geometry(rear,s['body_width_mm'],s['body_thickness_mm'])
top=geometry(data[1],3.,1.8)[0]
socket=Part.Shape();socket.read(str(HERE/'socket-source.brep'));socket.translate(shift)
n=unit(rear['socket_axis']);c=App.Vector(*rear['socket_center_mm'])
collar=Part.makeCylinder(s['collar_radius_mm'],3,c+n*2.4,n).cut(Part.makeCylinder(1.45,3,c+n*2.4,n))
socket=socket.fuse(collar).removeSplitter()
# Remove only the old rear-root protrusion from the saved T3 tray region.
root_trim=Part.makeBox(53.70677424482636,4.5,3.5,App.Vector(-50,10.3,14.5))
tray=src.T3ProtectedTray.Shape.cut(root_trim).removeSplitter()
carrier=tray.fuse(top).fuse(socket).fuse(arm).removeSplitter();carrier.check(True)
assert carrier.isValid() and len(carrier.Solids)==1
print('basic fusion',carrier.Volume,flush=True)
# The saved T3 tray already includes the original top-root junction blend.
carrier=carrier.makeFillet(.2,tray_edges(carrier,*data,which='rear'))
print('root fillets',carrier.Volume,flush=True)
edges=[]
for edge in carrier.Edges:
 if len(edge.Vertexes)!=2:continue
 points=[v.Point-c for v in edge.Vertexes]
 if all(abs((v-n*v.dot(n)).Length-s['collar_radius_mm'])<1e-5 and 2.8-1e-5<=v.dot(n)<=5+1e-5 for v in points):edges.append(edge)
assert len(edges) in [8,10],len(edges)
carrier=carrier.makeFillet(.3,edges)
shoulder=[e for e in carrier.Edges if hasattr(e.Curve,'Radius') and abs((e.CenterOfMass-c).dot(n)-2.4)<1e-5 and 2.4<e.Curve.Radius<2.5]
assert len(shoulder)==1
carrier=carrier.makeFillet(.2,shoulder)
carrier=carrier.cut(Part.makeSphere(2+s['ball_clearance_mm'],App.Vector(*s['ball_center_mm']))).removeSplitter()
carrier.check(True);assert carrier.isValid() and len(carrier.Solids)==1
doc=App.newDocument('CompactArmR04');doc.Label='MH-T3-EYE-R04 — lower root / compact rear curve'
for old in src.Objects:
 if old.TypeId=='Part::Feature':
  o=doc.addObject('Part::Feature',old.Name);o.Shape=(carrier if old.Name=='Carrier' else tray if old.Name=='T3ProtectedTray' else carrier.cut(tray) if old.Name=='EyeRibbonArms' else old.Shape.copy());o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
 elif old.TypeId=='Mesh::Feature':
  o=doc.addObject('Mesh::Feature',old.Name);o.Mesh=old.Mesh.copy();o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
for name,shape in [('NewRearArm',arm),('NewRearPath',path),('PreviousCarrier',src.Carrier.Shape)]:
 o=doc.addObject('Part::Feature',name);o.Shape=shape;o.Visibility=False
info=doc.addObject('App::FeaturePython','Revision');info.addProperty('App::PropertyString','RevisionID');info.RevisionID='MH-T3-EYE-R04'
report=dict(revision='MH-T3-EYE-R04',units='mm, mm3',valid=carrier.isValid(),solids=len(carrier.Solids),volume_mm3=carrier.Volume,new_root_mm=s['root_mm'],old_root_mm=[4.10677424482636,12.550767,16.7662968498585],new_path_length_mm=path.Length,old_loop_plus_extension_length_mm=42.43753,new_arm_xmin_mm=arm.BoundBox.XMin,old_arm_xmin_mm=-16.2579,holder_gap_mm=carrier.distToShape(doc.Holder.Shape)[0])
for name in ['Holder','Clip','Baseplate','ApproxPCB','Cap']:
 report[name+'_overlap_mm3']=carrier.common(doc.getObject(name).Shape).Volume
 report[name+'_baseline_overlap_mm3']=src.Carrier.Shape.common(src.getObject(name).Shape).Volume
for name in ['UpperCatch','UpperRail']:report[name+'_missing_mm3']=src.getObject(name).Shape.cut(carrier).Volume
report['optical_obstruction_mm']=carrier.common(doc.OpticalAxis.Shape).Length
assert max(report[n+'_overlap_mm3'] for n in ['Holder','Clip','Baseplate','ApproxPCB'])<1e-6
assert abs(report['Cap_overlap_mm3']-report['Cap_baseline_overlap_mm3'])<1e-6
assert report['UpperCatch_missing_mm3']<1e-6 and report['UpperRail_missing_mm3']<1e-6
assert report['optical_obstruction_mm']<1e-6
report['rearward_reach_old_mm']=3.70677424482636-report['old_arm_xmin_mm']
report['rearward_reach_new_mm']=3.70677424482636-report['new_arm_xmin_mm']
report['rearward_reach_reduction_percent']=100*(1-report['rearward_reach_new_mm']/report['rearward_reach_old_mm'])
holes=[f for f in carrier.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-2)<1e-8 and abs(f.Surface.Axis.x)>0.999]
assert len(holes)==2
report['tray_holes_retained']=True
(HERE/'validation.json').write_text(json.dumps(report,indent=2))
doc.Carrier.Visibility=True
for name in ['T3ProtectedTray','EyeRibbonArms','UpperCatch','UpperRail','ApproxPCB']:doc.getObject(name).Visibility=False
doc.recompute();Gui.activeDocument().activeView().setCameraOrientation(camera.Q);Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(OUT/'MH-T3-EYE-R04.FCStd'))
print(json.dumps(report,indent=2))
