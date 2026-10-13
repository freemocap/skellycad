"""Build an eye-tracker assembly from camera, mount and animal configuration.

The public entry point is build_assembly(config_path, output_dir=None). It
validates references before building and returns the document and export
manifest. Camera count, role, hardware choice and rigid placement are data.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import math
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


@dataclass
class Assembly:
    document: object
    manifest: dict
    config: dict


def _id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z][a-z0-9_-]*', value):
        raise ValueError(f'Invalid library or instance identifier: {value!r}')
    return value


def _asset(record):
    path = (ROOT / record['path']).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Asset must be within the repository')
    if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
        raise ValueError(f'Asset hash mismatch: {record["path"]}')
    return path


def _pose(data):
    import FreeCAD as App
    t, q = data['translation_mm'], data['rotation_xyzw']
    if len(t) != 3 or len(q) != 4 or not all(math.isfinite(x) for x in [*t, *q]):
        raise ValueError('Placement needs three finite millimetre coordinates and an XYZW quaternion')
    if abs(sum(x*x for x in q) - 1) > 1e-6:
        raise ValueError('Placement quaternion must have unit length')
    return App.Placement(App.Vector(*t), App.Rotation(*q))


def _shape(asset):
    import Part
    shape = Part.Shape()
    shape.read(str(_asset(asset)))
    if not shape.isValid():
        raise ValueError(f'Invalid library geometry: {asset["path"]}')
    return shape


def _hardware(camera, mount):
    """Compose printable parts from frozen geometric regions in their kit frame."""
    parts = {name: _shape(asset) for name, asset in mount['parts'].items()}
    carrier = parts.pop('tray').fuse(parts.pop('supports')).removeSplitter()
    if not carrier.isValid() or len(carrier.Solids) != 1:
        raise ValueError('Tray and supports must form one valid printed carrier')
    parts['Carrier'] = carrier
    parts['ApproxPCB'] = _shape(camera['pcb_envelope'])
    parts['ApproxPCB'].Placement = _pose(mount['pcb_placement']).multiply(parts['ApproxPCB'].Placement)
    for name in ('Holder', 'Cap', 'Clip'):
        if len(parts[name].Solids) != 1:
            raise ValueError(f'{name} must be one printable solid')
    # These checks travel with the mount, independent of animal placement.
    for name in ('UpperCatch', 'UpperRail'):
        if parts[name].cut(carrier).Volume > 1e-6:
            raise ValueError(f'Mount lost {name}')
    for name in ('Holder', 'Clip', 'ApproxPCB'):
        if carrier.common(parts[name]).Volume > 1e-6:
            raise ValueError(f'Mount interferes with {name}')
    if abs(carrier.distToShape(parts['Holder'])[0] - mount['checks']['holder_gap_mm']) > 1e-6:
        raise ValueError('Holder clearance differs from the selected mount preset')
    if abs(carrier.common(parts['Cap']).Volume - mount['checks']['cap_contact_mm3']) > 1e-6:
        raise ValueError('Matched cap contact differs from the selected mount preset')
    return parts


def build_assembly(config_path, output_dir=None):
    import FreeCAD as App
    import FreeCADGui as Gui
    import Part

    config_path = Path(config_path).resolve()
    config = json.loads(config_path.read_text())
    if config['schema_version'] != 1 or config['units'] != 'mm':
        raise ValueError('Expected assembly schema 1 with millimetre units')
    if not config['cameras']:
        raise ValueError('An eye tracker requires at least one camera instance')
    anatomy_path = (config_path.parent / config['anatomy']).resolve()
    if not anatomy_path.is_relative_to(ROOT):
        raise ValueError('Anatomy must be within the repository')
    anatomy = json.loads(anatomy_path.read_text())
    _asset(anatomy['mesh_checkpoint'])
    baseplate_shape = _shape(anatomy['baseplate'])
    base_ids = [_id(b['id']) for b in config['baseplates']]
    camera_ids = [_id(c['id']) for c in config['cameras']]
    if len(set(base_ids + camera_ids)) != len(base_ids + camera_ids):
        raise ValueError('Camera and baseplate instance identifiers must be unique')
    resolved = []
    cache = {}
    for instance in config['cameras']:
        if instance['role'] not in ('eye', 'world'):
            raise ValueError('Camera role must be eye or world')
        if instance['baseplate'] not in base_ids:
            raise ValueError('Camera references an unknown baseplate instance')
        camera_id, mount_id = _id(instance['camera']), _id(instance['mount'])
        camera = json.loads((HERE / 'cameras' / camera_id / 'camera.json').read_text())
        mount = json.loads((HERE / 'mounts' / mount_id / 'mount.json').read_text())
        if camera['id'] != camera_id or mount['id'] != mount_id or camera_id not in mount['compatible_cameras']:
            raise ValueError('Camera and mount preset are incompatible')
        key = (camera_id, mount_id)
        if key not in cache:
            cache[key] = _hardware(camera, mount)
        resolved.append((instance, camera, mount, cache[key], _pose(instance['placement'])))
    base_poses = [_pose(b['placement']) for b in config['baseplates']]
    anatomy_pose = _pose(config['anatomy_placement'])

    doc = App.newDocument('EyeTrackerAssembly')
    doc.Label = config['label']
    manifest = {'revision': config['revision'], 'status': 'Built assembly; application-specific validation required',
                'parts': {}, 'print_groups': {}, 'camera_instances': [],
                'assembly_config': config_path.relative_to(ROOT).as_posix(), 'units': 'mm'}
    try:
        def group(name, label):
            obj = doc.addObject('App::DocumentObjectGroup', name)
            obj.Label = label
            return obj

        def add(parent, name, label, shape, pose, color, visible=True):
            obj = doc.addObject('Part::Feature', name)
            obj.Label = label
            placed = shape.copy()
            placed.Placement = pose.multiply(placed.Placement)
            obj.Shape = placed
            obj.ViewObject.ShapeColor = color
            obj.Visibility = visible
            parent.addObject(obj)
            return obj

        anatomy_group = group('Anatomy', config['species'].title() + ' anatomy — reference only')
        mesh_path = _asset(anatomy['mesh_checkpoint'])
        existing = next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName).resolve() == mesh_path), None)
        source = existing or App.openDocument(str(mesh_path))
        try:
            for name in anatomy['meshes']:
                original = source.getObject(name)
                obj = doc.addObject('Mesh::Feature', name)
                obj.Mesh = original.Mesh.copy()
                obj.Placement = anatomy_pose.multiply(original.Placement)
                obj.ViewObject.ShapeColor = original.ViewObject.ShapeColor
                anatomy_group.addObject(obj)
        finally:
            if existing is None:
                App.closeDocument(source.Name)
        target = Part.makeSphere(.25, App.Vector(*anatomy['eye_target_mm']))
        add(anatomy_group, 'EyeTarget', 'Inherited eye-surface target (approx.)', target, anatomy_pose, (1., .6, .1))
        bases = group('Baseplates', 'Animal mounting baseplates')
        for instance, pose in zip(config['baseplates'], base_poses):
            role = instance['id'] + '_Baseplate'
            obj = add(bases, role, instance['label'], baseplate_shape, pose, (.75, .65, .35))
            manifest['parts'][role] = obj.Name
            manifest['print_groups'][instance['id'] + '-baseplate'] = [role]
        colors = {'Carrier': (.2, .75, .8), 'Holder': (.62, .45, .8), 'Cap': (.85, .65, .2), 'Clip': (.85, .65, .2)}
        for instance, camera, mount, shapes, pose in resolved:
            ident = instance['id']
            station = group('Camera_' + ident, instance['label'] + ' — ' + camera['label'])
            station.addProperty('App::PropertyString', 'CameraRole').CameraRole = instance['role']
            station.addProperty('App::PropertyString', 'CameraProfile').CameraProfile = instance['camera']
            station.addProperty('App::PropertyString', 'MountPreset').MountPreset = instance['mount']
            objects = {}
            for name, shape in shapes.items():
                obj = add(station, ident + '_' + name, name if name != 'ApproxPCB' else 'PCB envelope (approx.)', shape,
                          pose, colors.get(name, (1., .6, .1)), name in ('Carrier', 'Holder', 'Clip'))
                objects[name] = obj.Name
                if name in colors:
                    manifest['parts'][ident + '_' + name] = obj.Name
            lens = App.Vector(*mount['lens_datum_mm'])
            direction = App.Vector(*mount['sightline_vector_mm'])
            for name, shape in [('LensDatum', Part.makeSphere(.25, lens)), ('OpticalAxis', Part.makeLine(lens, lens + direction))]:
                obj = add(station, ident + '_' + name, 'Inherited ' + name + ' guide (approx.)', shape, pose, (1., .6, .1))
                obj.ViewObject.LineColor = (1., .2, .1)
                objects[name] = obj.Name
            manifest['camera_instances'].append({'id': ident, 'role': instance['role'], 'camera': instance['camera'],
                'mount': instance['mount'], 'objects': objects, 'baseplate_object': manifest['parts'][instance['baseplate'] + '_Baseplate']})
            for label, names in [('carrier-and-holder', ['Carrier', 'Holder']), ('matching-cap', ['Cap']), ('camera-clip', ['Clip'])]:
                manifest['print_groups'][ident + '-' + label] = [ident + '_' + name for name in names]
        revision = doc.addObject('App::FeaturePython', 'Revision')
        revision.addProperty('App::PropertyString', 'RevisionID').RevisionID = config['revision']
        doc.recompute()
        App.setActiveDocument(doc.Name)
        Gui.activeDocument().activeView().viewAxonometric()
        Gui.activeDocument().activeView().fitAll()
        if output_dir is not None:
            output_dir = Path(output_dir).resolve()
            if not output_dir.is_relative_to(ROOT / 'generated'):
                raise ValueError('Fresh builds must be under generated/')
            output_dir.mkdir(parents=True, exist_ok=True)
            native = output_dir / (config['revision'] + '.FCStd')
            doc.saveAs(str(native))
            manifest.update(native_checkpoint=native.relative_to(ROOT).as_posix(), native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),
                            print_directory=(output_dir / 'print').relative_to(ROOT).as_posix())
            (output_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        return Assembly(doc, manifest, config)
    except Exception:
        App.closeDocument(doc.Name)
        raise
