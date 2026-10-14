"""Verify the selected camera checkpoint and its assembly import contract."""
from pathlib import Path
import json
import sys
import itertools
import FreeCAD as App

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'designs/eye-tracker'))
from shared.camera import add_camera, selected_model, checked_asset

model = selected_model()
for kind in ('exports', 'validation'):
    for record in model[kind].values():
        checked_asset(record)
checked_asset(model['lens_source'])
bad = dict(model['native_checkpoint'], sha256='0' * 64)
try:
    checked_asset(bad)
except ValueError:
    pass
else:
    raise AssertionError('Corrupt camera assets must be rejected')

source = App.openDocument(str(checked_asset(model['native_checkpoint'])))
doc = App.newDocument('SelectedCameraValidation')
first = add_camera(doc, 'First')
pose = App.Placement(App.Vector(12, -4, 9), App.Rotation(App.Vector(1, 0, 0), 35))
second = add_camera(doc, 'Second', pose)
assert first.Name != second.Name and len(first.PhysicalParts) == 4
for obj, name in zip(first.PhysicalParts, model['parts']):
    baseline = source.getObject(name).Shape
    assert obj.Shape.cut(baseline).Volume + baseline.cut(obj.Shape).Volume < 1e-7
    assert obj.ExportForPrinting and obj.Shape.isValid()
for obj in [first.PhysicalParts[0], first.PhysicalParts[3]]:
    for solid in obj.Shape.Solids:
        assert abs(solid.BoundBox.ZMin) < 1e-9
        assert abs(solid.BoundBox.ZMax - .25) < 1e-9
for a, b in itertools.combinations(first.PhysicalParts, 2):
    assert a.Shape.common(b.Shape).Volume < 1e-7
whole = first.PhysicalParts[0].Shape
for obj in first.PhysicalParts[1:]:
    whole = whole.fuse(obj.Shape)
assert whole.isValid() and len(whole.Solids) == 1
assert not first.OpticalAxis.ExportForPrinting
assert not first.SensorFrame.ExportForPrinting
assert (first.OpticalAxis.SensorCenter - source.OpticalAxis.SensorCenter).Length < 1e-9
assert (first.OpticalAxis.Origin - source.OpticalAxis.Origin).Length < 1e-9
assert (second.OpticalAxis.getGlobalPlacement().multVec(second.OpticalAxis.Origin)
        - pose.multVec(first.OpticalAxis.Origin)).Length < 1e-9
assert (second.SensorFrame.getGlobalPlacement().Base
        - pose.multVec(first.OpticalAxis.SensorCenter)).Length < 1e-9
assert (second.OpticalAxis.getGlobalPlacement().Rotation.multVec(second.OpticalAxis.Direction)
        - pose.Rotation.multVec(first.OpticalAxis.Direction)).Length < 1e-9
out = ROOT / 'generated/verification/camera'
out.mkdir(parents=True, exist_ok=True)
(out / 'validation.json').write_text(json.dumps({
    'revision': model['revision'], 'passed': True, 'asset_hashes_verified': True,
    'corrupt_hash_rejected': True, 'checkpoint_geometry_equivalent': True,
    'coplanar_substrate': True, 'exclusive_material_regions': True,
    'connected_assembly': True, 'two_instances_and_transformed_datum': True,
    'physical_fit_verified': False,
}, indent=2) + '\n')
print('SELECTED_CAMERA_OK')
