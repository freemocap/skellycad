"""Simple Ultra Skelly mock-up: the 1 inch square spine tube, the neck drive and the skull.

Body frame: origin on the floor below the spine, +X forward, +Y the skeleton's left, +Z up,
millimetres. Dimensions are planning estimates from mockup.json. The head frame H
(anatomy/README.md) is drawn at the eye sockets. Run live in the project FreeCAD window:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py mockup --run r001

or headless with the pinned FreeCAD Python: `... bin/python.exe -B designs/ultraskelly/src/mockup.py --run r001`.
"""
import argparse
import json
import math
from pathlib import Path

import FreeCAD as App
import Part

import cadkit

HERE = Path(__file__).resolve().parent
V = App.Vector
BONE, STEEL, DARK, RED, GREEN, BLUE = ((0.93, 0.9, 0.8), (0.55, 0.57, 0.6), (0.15, 0.15, 0.17),
                                       (0.85, 0.1, 0.1), (0.1, 0.65, 0.2), (0.15, 0.35, 0.9))


def ellipsoid(center, semi_axes):
    shape = Part.makeSphere(1.0)
    scale = App.Matrix()
    scale.scale(*semi_axes)
    shape = shape.transformGeometry(scale)
    shape.translate(V(*center))
    return shape


def shell(center, semi_axes, wall):
    return ellipsoid(center, semi_axes).cut(ellipsoid(center, [a - wall for a in semi_axes]))


def surface_x(center, semi_axes, y, z):
    """Front (+X) surface of an ellipsoid at (y, z)."""
    (cx, cy, cz), (a, b, c) = center, semi_axes
    return cx + a * math.sqrt(1 - ((y - cy) / b) ** 2 - ((z - cz) / c) ** 2)


def skull(p):
    s = p['skull']
    w = s['wall']
    outer = ellipsoid(s['cranium_center'], s['cranium_semi_axes']).fuse(
        ellipsoid(s['face_center'], s['face_semi_axes']))
    inner = ellipsoid(s['cranium_center'], [a - w for a in s['cranium_semi_axes']]).fuse(
        ellipsoid(s['face_center'], [a - w for a in s['face_semi_axes']]))
    body = outer.cut(inner)
    eye, nose = s['eye_socket'], s['nose_hole']
    cutters = [Part.makeCylinder(eye['diameter'] / 2, 200, V(0, side * eye['spacing'] / 2, eye['height']), V(1, 0, 0))
               for side in (1, -1)]
    cutters.append(Part.makeCylinder(nose['diameter'] / 2, 200, V(0, 0, nose['height']), V(1, 0, 0)))
    cranium_bottom = s['cranium_center'][2] - s['cranium_semi_axes'][2]
    cutters.append(Part.makeCylinder(s['neck_hole_diameter'] / 2, 60, V(0, 0, cranium_bottom - 20)))
    return body.cut(Part.makeCompound(cutters)).removeSplitter()


def head_frame(p):
    """Landmarks L, R and origin O of the head frame on this estimated skull."""
    s, eye = p['skull'], p['skull']['eye_socket']
    x = surface_x(s['cranium_center'], s['cranium_semi_axes'], eye['spacing'] / 2, eye['height'])
    return {'L': [x, eye['spacing'] / 2, eye['height']], 'R': [x, -eye['spacing'] / 2, eye['height']],
            'O': [x, 0.0, eye['height']]}


def arrow(origin, direction, length=60, radius=2.0):
    shaft = Part.makeCylinder(radius, length * 0.8, V(*origin), direction)
    tip = Part.makeCone(radius * 2.5, 0, length * 0.2, V(*origin) + direction * (length * 0.8), direction)
    return shaft.fuse(tip)


def build(doc, p):
    tube, drive, body = p['spine_tube'], p['neck_drive'], p['body']
    side, wall = tube['outside'], tube['wall']
    length = tube['top'] - tube['bottom']
    spine = Part.makeBox(side, side, length, V(-side / 2, -side / 2, tube['bottom'])).cut(
        Part.makeBox(side - 2 * wall, side - 2 * wall, length + 2, V(-side / 2 + wall, -side / 2 + wall, tube['bottom'] - 1)))
    cadkit.add(doc, 'SpineTube', spine, STEEL, label='Spine tube, 1 in square (25.4 mm)')
    bx, by, bz = drive['block']
    cadkit.add(doc, 'NeckDrive', Part.makeBox(bx, by, bz, V(-bx / 2, -by / 2, tube['top'])), DARK,
               label='Neck drive: pan and tilt servos (estimated)')
    cadkit.add(doc, 'ServoPost', Part.makeCylinder(drive['post_diameter'] / 2, drive['post_top'] - tube['top'] - bz,
                                                   V(0, 0, tube['top'] + bz)), (0.8, 0.8, 0.82), label='Servo post into the skull')
    cadkit.add(doc, 'Skull', skull(p), BONE, label='Skull (estimated life size)')
    jaw = p['skull']['jaw']
    cadkit.add(doc, 'Jaw', ellipsoid(jaw['center'], jaw['semi_axes']), BONE, label='Jaw')
    bar = body['shoulder_bar']
    cadkit.add(doc, 'Shoulders', Part.makeBox(bar['depth'], bar['width'], bar['thickness'],
                                              V(-bar['depth'] / 2, -bar['width'] / 2, bar['height'] - bar['thickness'] / 2)),
               BONE, label='Shoulder bar')
    rib = body['ribcage']
    cadkit.add(doc, 'Ribcage', shell(rib['center'], rib['semi_axes'], 4), BONE, 75, label='Ribcage (transparent)')
    px, py, pz = body['pelvis']['size']
    pelvis_top = body['pelvis']['height'] + pz / 2
    cadkit.add(doc, 'Pelvis', Part.makeBox(px, py, pz, V(-px / 2, -py / 2, pelvis_top - pz)), BONE, label='Pelvis')
    waist = body['waist_drive']
    cadkit.add(doc, 'WaistDrive', Part.makeCylinder(waist['diameter'] / 2, tube['bottom'] - pelvis_top, V(0, 0, pelvis_top)),
               DARK, label='Waist drive (motor turns the torso)')
    r = body['limb_diameter'] / 2
    legs = [Part.makeCylinder(r, pelvis_top - pz, V(0, s * body['leg_spacing'] / 2, 0)) for s in (1, -1)]
    arms = [Part.makeCylinder(r, bar['height'] - body['arm_bottom'], V(0, s * bar['width'] / 2, body['arm_bottom']))
            for s in (1, -1)]
    cadkit.add(doc, 'Limbs', Part.makeCompound(legs + arms), BONE, 40, label='Arms and legs (placeholders)')
    cadkit.add(doc, 'Floor', Part.makeCylinder(300, 5, V(0, 0, -5)), (0.8, 0.8, 0.8), 60, label='Floor')
    frame = head_frame(p)
    origin = frame['O']
    for name, direction, color in (('HeadX', V(1, 0, 0), RED), ('HeadY', V(0, 1, 0), GREEN), ('HeadZ', V(0, 0, 1), BLUE)):
        cadkit.add(doc, name, arrow(origin, direction), color, label=f'Head frame +{name[-1]}')
    return frame


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--run', required=True, help='new run name under generated/ultraskelly/mockup/')
    args = parser.parse_args(argv)
    source = HERE / 'mockup.json'
    params = json.loads(source.read_text(encoding='utf-8'))
    folder = cadkit.run_folder('mockup', args.run)
    cadkit.close_saved_runs(folder.parent)
    doc = App.newDocument('UltraSkellyMockup')
    frame = build(doc, params)
    doc.recompute()
    native = folder / 'ultraskelly-mockup.FCStd'
    native_sha = cadkit.save_verified(doc, native)
    cadkit.write_report(folder / 'build-report.json', {
        'part': 'mockup', 'run': args.run, 'units': 'mm', 'parameters_sha256': cadkit.sha256(source),
        'native': {'path': native.name, 'sha256': native_sha}, 'head_frame_landmarks_mm': frame,
        'status': 'Planning mock-up from estimates; not a measured model of the robot.'})
    if App.GuiUp:
        cadkit.present(doc, 'isometric')
    else:
        App.closeDocument(doc.Name)
    print(json.dumps({'saved': str(native), 'head_frame_origin_mm': [round(v, 1) for v in frame['O']]}))


if __name__ == '__main__':
    main()
