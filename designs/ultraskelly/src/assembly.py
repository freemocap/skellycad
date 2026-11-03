"""Ultra Skelly mock-up with the electronics shelf clamped on its spine tube, for clearance review.

The shelf frame (mount.json) is placed on the mock-up's spine axis at --shelf-z (mm above the
floor). Gaps are reported against the mock-up's estimated shoulders, neck drive and skull, so
they are planning numbers, not measurements. Run live:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py assembly --run r001
"""
import argparse
import json
from pathlib import Path

import FreeCAD as App

import cadkit
import mockup
import mount

HERE = Path(__file__).resolve().parent


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--run', required=True, help='new run name under generated/ultraskelly/assembly/')
    parser.add_argument('--shelf-z', type=float, default=1620.0, help='plate underside height above the floor, mm')
    args = parser.parse_args(argv)
    folder = cadkit.run_folder('assembly', args.run)
    cadkit.close_saved_runs(folder.parent)
    doc = App.newDocument('UltraSkellyAssembly')
    body = json.loads((HERE / 'mockup.json').read_text(encoding='utf-8'))
    mockup.build(doc, body)
    before = {o.Name for o in doc.Objects}
    mount.build(doc, json.loads((HERE / 'mount.json').read_text(encoding='utf-8')))
    added = [o for o in doc.Objects if o.Name not in before]
    for obj in added:
        if obj.Label.startswith('Spine tube'):
            doc.removeObject(obj.Name)  # the mock-up already has the tube
            continue
        obj.Placement.Base.z += args.shelf_z
    doc.recompute()
    shelf = [o for o in doc.Objects if o.Name not in before and hasattr(o, 'Shape') and o.Shape.Solids]
    top = max(o.Shape.BoundBox.ZMax for o in shelf)
    bottom = min(o.Shape.BoundBox.ZMin for o in shelf)
    drive = body['spine_tube']['top']
    shoulders = body['body']['shoulder_bar']['height'] + body['body']['shoulder_bar']['thickness'] / 2
    jaw_bottom = body['skull']['jaw']['center'][2] - body['skull']['jaw']['semi_axes'][2]
    gaps = {'shelf_bottom_to_shoulder_top': round(bottom - shoulders, 1), 'shelf_top_to_neck_drive': round(drive - top, 1),
            'shelf_top_to_jaw_bottom': round(jaw_bottom - top, 1), 'shelf_z': args.shelf_z,
            'shelf_top_z': round(top, 1)}
    native = folder / 'assembly.FCStd'
    native_sha = cadkit.save_verified(doc, native)
    cadkit.write_report(folder / 'build-report.json', {
        'part': 'assembly', 'run': args.run, 'units': 'mm', 'native': {'path': native.name, 'sha256': native_sha},
        'gaps_mm': gaps, 'status': 'Planning check against mock-up estimates, not the robot.'})
    if App.GuiUp:
        cadkit.present(doc, 'right')
    else:
        App.closeDocument(doc.Name)
    print(json.dumps({'saved': str(native), 'gaps_mm': gaps}))


if __name__ == '__main__':
    main()
