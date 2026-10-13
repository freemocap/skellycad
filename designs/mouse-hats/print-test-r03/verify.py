"""Checks specific to R03's socket edits, including unchanged mating regions."""
from pathlib import Path
import sys,json,math
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
for p in [HERE,HERE.parent/'model',HERE.parent/'print-test',HERE.parent/'reconstruction/baseplate',HERE.parent/'reconstruction/main_carrier']:sys.path.insert(0,str(p))
import socket_revision_features,attachment_arm_features,arm_finish_features,stem_blend_features,retention_features,mount_features,carrier_features
OUT=ROOT/'generated/mouse-hats/print-test/r03'
doc=App.openDocument(str(OUT/'carrier.FCStd'));feature=doc.StrongerClearanceCarrier
assembly=App.openDocument(str(ROOT/'generated/mouse-hats/print-test/r02/print-in-place-review.FCStd'))
def isolated(s):
 t=Part.Shape();t.importBrepFromString(s.exportBrepToString());return t
def common(a,b):return isolated(a).common(isolated(b),0)
def difference(a,b):return isolated(a).cut(isolated(b),0)
a=doc.LongerPCBRetainers.Shape;b=feature.Shape
added=difference(b,a);removed=difference(a,b)
p=json.loads(doc.RearArm.DesignJSON);center=App.Vector(*p['socket_center_mm']);axis=App.Vector(*p['socket_axis'])
# Whole features that must remain fixed: old PCB/stem stock and neck opening below local Z=-1.29.
trayloss=common(removed,doc.TrayReference.Shape).Volume
mouth=Part.makeCylinder(3.7,10,center-axis*11.29,axis)
mouthchange=common(added,mouth).Volume+common(removed,mouth).Volume
bore=Part.makeCylinder(1.45,3,center+axis*2.4,axis)
ballgap=b.distToShape(assembly.Holder.Shape)[0]
report={'valid':b.isValid(),'solids':len(b.Solids),'added_mm3':added.Volume,'removed_mm3':removed.Volume,
 'net_added_mm3':b.Volume-a.Volume,'minimum_holder_separation_mm':ballgap,
 'holder_overlap_mm3':common(b,assembly.Holder.Shape).Volume,
 'cap_overlap_R02_mm3':common(a,assembly.CapReference.Shape).Volume,
 'cap_overlap_R03_mm3':common(b,assembly.CapReference.Shape).Volume,
 'baseplate_overlap_mm3':common(b,assembly.BaseplateReference.Shape).Volume,
 'original_tray_material_removed_mm3':trayloss,'lower_neck_opening_change_mm3':mouthchange,
 'insert_bore_obstruction_mm3':common(b,bore).Volume}
# Sample bowl wall along 120 radial rays; this is not a global minimum thickness proof.
u=axis.cross(App.Vector(1,0,0));u.normalize();v=axis.cross(u);thickness=[]
for polar in [60,75,90,105,120]:
 for az in range(0,360,15):
  t=math.radians(polar);q=math.radians(az);d=axis*math.cos(t)+(u*math.cos(q)+v*math.sin(q))*math.sin(t)
  line=Part.makeLine(feature.BallCenter,feature.BallCenter+d*6)
  intersection=line.common(b)
  thickness.extend(e.Length for e in intersection.Edges if e.Length>1e-5)
report['sampled_bowl_radial_wall_min_mm']=min(thickness)
assert report['valid'] and report['solids']==1 and ballgap>=.3
assert report['holder_overlap_mm3']<1e-7 and report['baseplate_overlap_mm3']<1e-7
assert abs(report['cap_overlap_R03_mm3']-report['cap_overlap_R02_mm3'])<1e-7
print(json.dumps(report,indent=2),flush=True)
assert trayloss<1e-7 and mouthchange<1e-7 and report['insert_bore_obstruction_mm3']<1e-7
b.check(True)
# Reopen and demonstrate clearance is a real parameter, then restore.
vol=b.Volume
feature.BallClearance=.30;doc.recompute();feature.Shape.check(True)
assert feature.Shape.Volume>vol
feature.BallClearance=.35;doc.recompute();assert abs(feature.Shape.Volume-vol)<1e-6
report['reopen_clearance_edit_restore_passed']=True
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))


