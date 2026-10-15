"""Validate a composed assembly against the frozen mouse high-water mark."""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[3]


def compare_mouse_baseline(assembly):
    import FreeCAD as App
    reference = assembly.config['baseline']
    path = ROOT / reference['checkpoint']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == reference['sha256']
    existing = next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName).resolve() == path), None)
    baseline = existing or App.openDocument(str(path))
    try:
        station = next(c for c in assembly.manifest['camera_instances'] if c['id'] == reference['camera_instance'])
        names = {name: station['objects'][name] for name in ('Carrier', 'Holder', 'Cap', 'Clip')}
        names['Baseplate'] = station['baseplate_object']
        report = {'baseline': 'MH-T3-EYE-R10', 'revision': assembly.config['revision'], 'parts': {}}
        for role, name in names.items():
            rebuilt, original = assembly.document.getObject(name).Shape, baseline.getObject(role).Shape
            delta = rebuilt.cut(original).Volume + original.cut(rebuilt).Volume
            assert rebuilt.isValid() and len(rebuilt.Solids) == 1, role
            assert delta < 1e-6, (role, delta)
            assert abs(rebuilt.Area - original.Area) < 1e-5, role
            volume_delta = abs(rebuilt.Volume - original.Volume)
            assert volume_delta < 1e-3, (role, volume_delta)
            report['parts'][role] = {'symmetric_difference_mm3': delta, 'volume_mm3': rebuilt.Volume,
                                     'volume_integration_difference_mm3': volume_delta}
        for name in ('Skull', 'Eye1', 'Eye2'):
            a, b = assembly.document.getObject(name), baseline.getObject(name)
            assert a.Mesh.Topology == b.Mesh.Topology and a.Placement == b.Placement, name
        for name in ('LensDatum', 'OpticalAxis'):
            a, b = assembly.document.getObject(station['objects'][name]).Shape, baseline.getObject(name).Shape
            assert len(a.Vertexes) == len(b.Vertexes), name
            assert max((v.Point - w.Point).Length for v, w in zip(a.Vertexes, b.Vertexes)) < 1e-6, name
        carrier = assembly.document.getObject(station['objects']['Carrier']).Shape
        baseplate = assembly.document.getObject(station['baseplate_object']).Shape
        assert carrier.common(baseplate).Volume < 1e-6
        report.update(passed=True, anatomy_unchanged=True, sightline_unchanged=True,
                      checkpoint_unchanged=hashlib.sha256(path.read_bytes()).hexdigest() == reference['sha256'])
        return report
    finally:
        if existing is None:
            App.closeDocument(baseline.Name)


def _world_shape(obj):
    shape = obj.Shape.copy()
    shape.Placement = obj.getGlobalPlacement()
    return shape


def validate_selected(doc, manifest):
    """Check complete matched parts before exporting a selected assembly."""
    for station in manifest['camera_instances']:
        parts = {role: _world_shape(doc.getObject(name)) for role, name in station['objects'].items()}
        carrier = parts['Carrier']
        for role in ('UpperCatch', 'UpperRail'):
            assert parts[role].cut(carrier).Volume < 1e-6, role
        for role in ('Holder', 'ApproxPCB', 'Clip'):
            assert carrier.common(parts[role]).Volume < 1e-6, role
        assert carrier.common(_world_shape(doc.getObject(station['baseplate_object']))).Volume < 1e-6
