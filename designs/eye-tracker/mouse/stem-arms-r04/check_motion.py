from pathlib import Path
import json
import FreeCAD as A,Part
r=Path.cwd();out=r/'generated/eye-tracker/mouse/stem-arms-r04';d=A.openDocument(str(out/'mouse-stem-arms-r04.FCStd'));j=json.loads((r/'designs/mouse-hats/b-flared-loop-r07/settings.json').read_text());pivot=A.Vector(*j['ball_center_mm'])
parts=[d.getObject(n).Shape.copy() for n in ['eye_primary_Holder','eye_primary_Clip']]
for o in d.getObject('MeasuredSensorHead').Group:
 if hasattr(o,'Shape'):sh=o.Shape.copy();sh.Placement=o.getGlobalPlacement();parts.append(sh)
assembly=Part.makeCompound(parts);arms=Part.makeCompound([d.getObject(n).Shape for n in ['UpperSupport','RearRibbonGuard']]);rows=[]
for i,axis in enumerate([A.Vector(1,0,0),A.Vector(0,1,0),A.Vector(0,0,1)]):
 for angle in [-10,10]:
  sh=assembly.copy();sh.rotate(pivot,axis,angle);row={'axis':'XYZ'[i],'angle_deg':angle,'new_arm_overlap_mm3':sh.common(arms).Volume,'new_arm_clearance_mm':sh.distToShape(arms)[0]};rows.append(row);print(row,flush=True)
(out/'motion-samples.json').write_text(json.dumps({'scope':'Six rigid camera/cradle rotations against new arms only; ribbon not deformed or re-solved. Not a continuous motion envelope.','samples':rows},indent=2))
