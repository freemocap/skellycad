import FreeCAD as A,Part,json,hashlib
from pathlib import Path
r=Path.cwd();out=r/'generated/eye-tracker/mouse/ribbon-fixed-r03';m=json.loads((r/'designs/eye-tracker/mouse/active-model.json').read_text());assert hashlib.sha256((r/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256']
d=A.openDocument(str(r/'generated/eye-tracker/mouse/camera-fit-r01/mouse-camera-fit-r01.FCStd'))
s=json.loads((r/'designs/mouse-hats/b-flared-loop-r07/settings.json').read_text());p=r/'designs/mouse-hats/b-flared-loop-r07/socket-source.brep';assert hashlib.sha256(p.read_bytes()).hexdigest()==s['socket_source_sha256']
socket=Part.Shape();socket.read(str(p));shift=A.Vector(*s['joint_shift_mm']);socket.translate(shift);n=A.Vector(*s['rear_data']['socket_axis']);c=A.Vector(*s['rear_data']['socket_center_mm'])+shift
mask=socket.fuse(Part.makeCylinder(s['collar_radius_mm'],3,c+n*2.4,n));carrier=d.getObject('eye_primary_Carrier').Shape
retained=carrier.common(mask).removeSplitter();assert retained.isValid() and len(retained.Solids)==1
retained.exportBrep(str(out/'retained-socket.brep'));print('socket',retained.Volume,retained.BoundBox)
for name in ['eye_primary_Carrier','RibbonRouteGuide']:
 if d.getObject(name):d.removeObject(name)
tray=Part.Shape();tray.read(str(r/'designs/eye-tracker/shared/mounts/r10-monocular/tray.brep'))
# The historical tray mask excludes small lower-body markings. Preserve those too.
remnants=carrier.cut(tray.fuse(retained)).Solids
for fragment in remnants:
 if fragment.BoundBox.ZMax<8:tray=tray.fuse(fragment)
removed=carrier.cut(tray.fuse(retained))
assert len(removed.Solids)==2, 'Expected exactly the two connecting arms'
for name,sh in [('RetainedPCBTray',tray),('RetainedSocket',retained)]:o=d.addObject('Part::Feature',name);o.Shape=sh
base=A.openDocument(str(r/m['native_checkpoint']));checks={}
for name in ['eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','skull_mount_Baseplate']:
 a=d.getObject(name).Shape;b=base.getObject(name).Shape;checks[name]=a.cut(b).Volume+b.cut(a).Volume;assert checks[name]<1e-8
report={'checkpoint':m['native_checkpoint'],'sha256':m['native_sha256'],'unchanged_shape_symmetric_differences_mm3':checks,'socket_outside_baseline_mm3':retained.cut(carrier).Volume,'socket_mask_missing_mm3':carrier.common(mask).cut(retained).Volume,'socket_mask_source':str(p.relative_to(r)),'socket_mask_source_sha256':s['socket_source_sha256'],'sensor_pose':{'translation':list(d.getObject('MeasuredSensorHead').Placement.Base),'quaternion_xyzw':list(d.getObject('MeasuredSensorHead').Placement.Rotation.Q)},'removed_arm_components':len(removed.Solids),'removed_arm_volumes_mm3':[sh.Volume for sh in removed.Solids],'ribbon_status':'unsolved; no ribbon displayed'}
(out/'fixture-validation.json').write_text(json.dumps(report,indent=2));A.closeDocument(base.Name);d.recompute();d.saveAs(str(out/'mouse-fixed-cradle-r03.FCStd'));d.Label='Mouse fixed cradle R03 - only arms removed';d.save()
print(json.dumps(report,indent=2))
