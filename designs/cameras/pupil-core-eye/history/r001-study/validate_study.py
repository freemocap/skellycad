"""Run with the pinned FreeCAD Python; writes independent geometry verification."""
import json, math
import FreeCAD as A, Part
import camera_study as c

d=A.newDocument('CameraStudyValidation')
root,flex=c.create_camera(d,'TestCamera',90)
original_volumes={o.Name:o.Shape.Volume for o in flex.Head.Group}
checks=[]
for angle in (0,1,45,90,120,180):
    flex.BendDegrees=angle;d.recompute()
    L,w,t=flex.FreeLength.Value,flex.Width.Value,flex.Thickness.Value
    expected,end,rot,r=c.ribbon_shape(L,w,t,angle)
    assert flex.Shape.isValid() and len(flex.Shape.Solids)==1
    assert abs(flex.Shape.Volume-L*w*t)<1e-6
    assert (flex.Head.Placement.Base-end).Length<1e-9
    assert (flex.Head.Placement.Rotation.multVec(A.Vector(0,1,0))-rot.multVec(A.Vector(0,1,0))).Length<1e-9
    assert all(abs(o.Shape.Volume-original_volumes[o.Name])<1e-9 for o in flex.Head.Group)
    checks.append({'bend_degrees':angle,'volume_mm3':flex.Shape.Volume,'valid':True})
path=c.OUT/'reopen-test.FCStd';d.saveAs(str(path));A.closeDocument(d.Name)
d=A.openDocument(str(path));flex=d.getObject('TestCameraRibbon');flex.BendDegrees=65;d.recompute()
assert flex.Shape.isValid() and (flex.Head.Placement.Base-c.ribbon_shape(L,w,t,65)[1]).Length<1e-9
A.closeDocument(d.Name)
# Rebuild static export from the saved GUI study, excluding datum axes and groups.
d=A.openDocument(str(c.OUT/'camera-flex-study-r01.FCStd'))
solids=[]
for o in d.Objects:
    if o.TypeId in ('PartDesign::Feature','PartDesign::FeaturePython') and not o.Label.startswith('Optical direction'):
        shape=o.Shape.copy();shape.Placement=o.getGlobalPlacement();solids.append(shape)
assert len(solids)==21
compound=Part.makeCompound(solids);compound.exportStep(str(c.OUT/'camera-flex-study-r01.step'))
step=Part.Shape();step.read(str(c.OUT/'camera-flex-study-r01.step'))
assert step.isValid() and len(step.Solids)==21
assert abs(step.Volume-compound.Volume)<1e-5
A.closeDocument(d.Name)
report={'passed':True,'recompute_checks':checks,'reopened_editable':True,'STEP_solid_count':len(step.Solids)}
(c.OUT/'verification.json').write_text(json.dumps(report,indent=2))
p=c.OUT/'validation.json';data=json.loads(p.read_text());data['solid_count']=21;p.write_text(json.dumps(data,indent=2))
print(json.dumps(report,indent=2))
