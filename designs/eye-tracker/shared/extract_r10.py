"""One-time extraction of reusable R10 geometry from the frozen mouse baseline.

Run in FreeCAD. Normal assembly builds consume the extracted assets, not this
script or the original complete-assembly checkpoint.
"""
from pathlib import Path
import hashlib
import json
import FreeCAD as App
import Part

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MOUSE = HERE.parent / 'mouse'
SOURCE = MOUSE / 'checkpoints/MH-T3-EYE-R10.FCStd'
SOURCE_HASH = '8bc7974226c8df0892f3c174f46bc34318605ea2ab5ab697c71a745af0d88111'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert sha(SOURCE) == SOURCE_HASH
    destinations = [HERE / 'cameras/pupil-core-eye-inherited/camera.json',
                    HERE / 'mounts/r10-monocular/mount.json', MOUSE / 'anatomy.json']
    if any(p.exists() for p in destinations):
        raise RuntimeError('Extracted library already exists; create a new revision instead of overwriting it.')
    src = next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName).resolve() == SOURCE), None)
    if src is None:
        src = App.openDocument(str(SOURCE))
    assets = []

    def save_shape(folder, filename, shape):
        path = folder / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        shape.exportBrep(str(path))
        reread = Part.Shape()
        reread.read(str(path))
        assert reread.isValid()
        assert abs(reread.Volume - shape.Volume) < 1e-6
        record = {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}
        assets.append(record)
        return record

    camera_folder = HERE / 'cameras/pupil-core-eye-inherited'
    pcb = src.ApproxPCB.Shape.copy()
    pcb_origin = App.Vector(pcb.BoundBox.XMin, pcb.BoundBox.YMin, pcb.BoundBox.ZMin)
    pcb.translate(-pcb_origin)
    camera = {'id': 'pupil-core-eye-inherited', 'label': 'Pupil Core eye camera — inherited fit reference',
              'units': 'mm', 'frame': 'PCB envelope minimum corner; axes parallel to recovered R10 XYZ',
              'hardware_revision': None,
              'limitations': ['PCB and lens datum are inherited approximations, not a manufacturer camera CAD model.',
                              'Sensor, lens, connector and ribbon dimensions remain unverified.'],
              'pcb_envelope': save_shape(camera_folder, 'pcb-envelope.brep', pcb),
              'pcb_envelope_size_mm': [pcb.BoundBox.XLength, pcb.BoundBox.YLength, pcb.BoundBox.ZLength]}
    destinations[0].write_text(json.dumps(camera, indent=2) + '\n')

    mount_folder = HERE / 'mounts/r10-monocular'
    # Preserve the actual accepted geometry: the old protected-tray helper has
    # extra historical material, so intersect it with the final carrier first.
    tray = src.T3ProtectedTray.Shape.common(src.Carrier.Shape).removeSplitter()
    supports = src.Carrier.Shape.cut(tray).removeSplitter()
    rebuilt = tray.fuse(supports).removeSplitter()
    delta = rebuilt.cut(src.Carrier.Shape).Volume + src.Carrier.Shape.cut(rebuilt).Volume
    assert rebuilt.isValid() and len(rebuilt.Solids) == 1 and delta < 1e-6
    mount = {'id': 'r10-monocular', 'label': 'R10 tray, ribbon-loop supports and adjustable holder',
             'compatible_cameras': [camera['id']], 'units': 'mm', 'frame': 'Recovered R10 assembly XYZ',
             'pcb_placement': {'translation_mm': list(pcb_origin), 'rotation_xyzw': [0, 0, 0, 1]},
             'lens_datum_mm': list(src.LensDatum.Shape.CenterOfMass),
             'sightline_vector_mm': list(src.EyeTarget.Shape.CenterOfMass - src.LensDatum.Shape.CenterOfMass),
             'geometry_method': 'Fuse the extracted tray/mount region and ribbon-support/socket region; copy matched parts.',
             'limitations': ['The arm route and internal holder pose are the fixed R10 preset.',
                            'These regions fuse into one printed carrier; they are not separate printable parts.',
                            'Reposition a complete camera station rigidly; changing internal aim requires a new validated mount preset.'],
             'parts': {'tray': save_shape(mount_folder, 'tray.brep', tray),
                       'supports': save_shape(mount_folder, 'supports-and-socket.brep', supports)},
             'checks': {'holder_gap_mm': src.Carrier.Shape.distToShape(src.Holder.Shape)[0],
                        'cap_contact_mm3': src.Carrier.Shape.common(src.Cap.Shape).Volume}}
    for name in ('Holder', 'Cap', 'Clip', 'UpperCatch', 'UpperRail', 'SideLedge'):
        mount['parts'][name] = save_shape(mount_folder, name + '.brep', src.getObject(name).Shape)
    destinations[1].write_text(json.dumps(mount, indent=2) + '\n')

    anatomy_doc = App.newDocument('MouseAnatomySource')
    anatomy_doc.Label = 'Mouse anatomy — inherited R10 registration'
    for name in ('Skull', 'Eye1', 'Eye2'):
        old = src.getObject(name)
        obj = anatomy_doc.addObject('Mesh::Feature', name)
        obj.Mesh = old.Mesh.copy()
        obj.Placement = old.Placement
        obj.ViewObject.ShapeColor = old.ViewObject.ShapeColor
    anatomy_doc.recompute()
    anatomy_path = MOUSE / 'references/skull/anatomy-r10.FCStd'
    anatomy_doc.saveAs(str(anatomy_path))
    App.closeDocument(anatomy_doc.Name)
    anatomy_asset = {'path': anatomy_path.relative_to(ROOT).as_posix(), 'sha256': sha(anatomy_path)}
    assets.append(anatomy_asset)
    anatomy = {'units': 'mm', 'frame': mount['frame'], 'mesh_checkpoint': anatomy_asset,
               'meshes': ['Skull', 'Eye1', 'Eye2'],
               'eye_target_mm': list(src.EyeTarget.Shape.CenterOfMass),
               'eye_target_status': 'Inherited eye-surface proxy, not a verified pupil landmark',
               'baseplate': save_shape(MOUSE / 'inputs', 'baseplate-r10.brep', src.Baseplate.Shape)}
    destinations[2].write_text(json.dumps(anatomy, indent=2) + '\n')
    lineage = {'source_checkpoint': SOURCE.relative_to(ROOT).as_posix(), 'source_sha256': SOURCE_HASH,
               'extracted_assets': assets, 'carrier_recomposition_difference_mm3': delta,
               'note': 'Immutable extracted geometry. Normal builds need no R09/R10 whole-assembly checkpoint.'}
    (HERE / 'r10-extraction.json').write_text(json.dumps(lineage, indent=2) + '\n')
    print('R10_LIBRARY_EXTRACTED')


if __name__ == '__main__':
    main()
