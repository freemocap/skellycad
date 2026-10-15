"""Manifest selection and matched-part export shared by eye-tracker projects.

Species geometry and camera poses stay in the species design. FreeCAD imports
are deferred so manifest checks can also run in ordinary Python.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    checkpoint = (ROOT / manifest['native_checkpoint']).resolve()
    if not checkpoint.is_relative_to(ROOT):
        raise ValueError('Checkpoint must be within SkellyCAD')
    if hashlib.sha256(checkpoint.read_bytes()).hexdigest() != manifest['native_sha256']:
        raise ValueError('Selected checkpoint hash mismatch')
    return manifest, checkpoint


def open_selected(path):
    import FreeCAD as App
    manifest, checkpoint = load_manifest(path)
    doc = App.openDocument(str(checkpoint))
    if 'label' in manifest:
        doc.Label = manifest['label']
    if doc.Revision.RevisionID != manifest['revision']:
        raise ValueError('Checkpoint revision differs from manifest')
    for name in manifest['parts'].values():
        obj = doc.getObject(name)
        if obj is None or not obj.Shape.isValid() or len(obj.Shape.Solids) != 1:
            raise ValueError(f'Invalid or missing matched part: {name}')
    return manifest, doc


def export_selected(path, validate):
    import Part
    import MeshPart
    manifest, doc = open_selected(path)
    validate(doc)
    out = (ROOT / manifest['print_directory']).resolve()
    if not out.is_relative_to(ROOT / 'generated'):
        raise ValueError('Print exports must be under generated/')
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': manifest['revision'], 'native_sha256': manifest['native_sha256'],
              'units': 'mm', 'linear_deflection_mm': .03, 'angular_deflection_rad': .15, 'files': {}}
    for label, roles in manifest['print_groups'].items():
        objects = [doc.getObject(manifest['parts'][role]) for role in roles]
        shapes = []
        for obj in objects:
            placed = obj.Shape.copy()
            placed.Placement = obj.getGlobalPlacement()
            shapes.append(placed)
        shape = Part.makeCompound(shapes) if len(shapes) > 1 else shapes[0]
        mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=.03, AngularDeflection=.15, Relative=False)
        filename = f"{manifest['revision']}-{label}.stl"
        mesh.write(str(out / filename))
        report['files'][filename] = {'expected_shells': len(objects), 'native_volumes_mm3': [o.Shape.Volume for o in objects]}
    (out / 'export.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out)
    return report
