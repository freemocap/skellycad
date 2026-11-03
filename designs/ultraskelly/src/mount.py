"""Spine-tube shelf for UltraSkelly's electronics, with the cut-down OMT case and the PCA9685.

One printed plate clamps to the 1 inch square spine tube with a collar and two M3 set screws.
The community OMT Pi 5 case, shortened in the CAD to open its top, screws to the plate with the Pi's own
M2.5 screws. Bosses hold the PCA9685 beside the case, and slot pairs anchor zip ties. Shelf
frame and parameters are in mount.json. Run live in the project FreeCAD window:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py mount --run r001
"""
import argparse
import json
import math
from pathlib import Path

import FreeCAD as App
import Part

import cadkit
import case_view
import hardware_view
import vendor

HERE = Path(__file__).resolve().parent
V = App.Vector
PLATE_COLOR, CASE_COLOR, STEEL = (0.95, 0.55, 0.15), (0.88, 0.88, 0.9), (0.55, 0.57, 0.6)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def rounded_plate(x0, x1, y0, y1, r, z0, z1):
    plate = box(x0, x1, y0, y1, z0, z1)
    vertical = [e for e in plate.Edges if abs(e.tangentAt(e.FirstParameter).z) > 0.99]
    return plate.makeFillet(r, vertical)


def case_matrix(p, z0):
    """Pi-origin case coordinates to the shelf frame: rotate about Z, then move onto the plate."""
    m = App.Matrix()
    m.rotateZ(math.radians(p['case']['rotation_deg']))
    m.move(V(*p['case']['pi_origin'], z0))
    return m


def moved(shape, matrix):
    """Rigidly moved copy; keeps exact geometry, unlike transformGeometry."""
    shape = shape.copy()
    shape.transformShape(matrix)
    return shape


def cut_case(height):
    """OMT case body in Pi-origin coordinates, cut at a wall height; cached as BREP."""
    source = vendor.path('omt-case-3mf')
    cached = vendor.CACHE / 'omt-case-3mf' / f'case-cut-{height:g}.{vendor.sha256(source)[:12]}.brep'
    if cached.exists():
        return Part.read(str(cached))
    mesh = vendor.mesh_3mf('omt-case-3mf')['Pi Case v11.step']
    mesh.translate(*case_view.CASE_TO_PI)
    shape = Part.Shape()
    shape.makeShapeFromMesh(mesh.Topology, 0.01)
    solid = Part.makeSolid(shape)  # one face per mesh triangle; refining took minutes for little gain
    b = solid.BoundBox
    result = solid.common(box(b.XMin - 5, b.XMax + 5, b.YMin - 5, b.YMax + 5, b.ZMin - 1, height))
    assert result.isValid() and len(result.Solids) == 1, 'case cut is not one valid solid'
    cached.parent.mkdir(parents=True, exist_ok=True)
    result.exportBrep(str(cached))
    return result


def pi_to_shelf(p, x, y):
    angle = math.radians(p['case']['rotation_deg'])
    ox, oy = p['case']['pi_origin']
    return (ox + x * math.cos(angle) - y * math.sin(angle), oy + x * math.sin(angle) + y * math.cos(angle))


def pca_holes(p):
    q = p['pca9685']
    angle = math.radians(q['rotation_deg'])
    return [(q['origin'][0] + hx * math.cos(angle) - hy * math.sin(angle),
             q['origin'][1] + hx * math.sin(angle) + hy * math.cos(angle)) for hx, hy in q['holes_local']]


def plate(p, case_box):
    pl, col, t = p['plate'], p['collar'], p['plate']['thickness']
    half = p['tube']['outside'] / 2 + p['tube']['clearance']
    solids = [rounded_plate(*pl['x'], *pl['y'], pl['corner_radius'], 0, t),
              box(-half - col['wall'], half + col['front_wall'], -half - col['wall'], half + col['wall'], 0, col['height'])]
    lip, off = p['lip'], p['lip']['offset']
    x0, x1, y0, y1 = case_box.XMin - off, case_box.XMax + off, case_box.YMin - off, case_box.YMax + off
    g, w, top = lip['corner_gap'], lip['wall'], t + lip['height']
    solids += [box(x0 - w, x0, y0 + g, y1 - g, t, top), box(x1, x1 + w, y0 + g, y1 - g, t, top),
               box(x0 + g, x1 - g, y0 - w, y0, t, top), box(x0 + g, x1 - g, y1, y1 + w, t, top)]
    q = p['pca9685']
    solids += [Part.makeCylinder(q['boss_diameter'] / 2, q['boss_height'], V(x, y, t)) for x, y in pca_holes(p)]
    cutters = [box(-half, half, -half, half, -1, col['height'] + 1),
               box(*p['vent_window']['x'], *p['vent_window']['y'], -1, t + 1)]
    cs = p['case_screws']
    for x, y in (pi_to_shelf(p, hx, hy) for hx, hy in case_view.HOLES):
        cutters += [Part.makeCylinder(cs['clearance'] / 2, t + 2, V(x, y, -1)),
                    Part.makeCylinder(cs['counterbore'] / 2, cs['counterbore_depth'] + 1, V(x, y, -1))]
    cutters += [Part.makeCylinder(q['pilot'] / 2, t + q['boss_height'] + 2, V(x, y, -1)) for x, y in pca_holes(p)]
    ts = p['tie_slots']
    for xc, yc in ts['centers'].values():
        for dx in (-ts['spacing'] / 2, ts['spacing'] / 2):
            cutters.append(box(xc + dx - ts['width'] / 2, xc + dx + ts['width'] / 2, yc - ts['length'] / 2, yc + ts['length'] / 2, -1, t + 1))
    ss = p['set_screws']
    for z in ss['heights']:
        cutters.append(Part.makeCylinder(ss['clearance'] / 2, col['front_wall'] + 4, V(half - 2, 0, z), V(1, 0, 0)))
        cutters.append(box(ss['nut_slot_x'], ss['nut_slot_x'] + ss['nut_slot'], -ss['nut_flats'] * 0.58, half + col['wall'] + 1,
                           z - ss['nut_flats'] / 2, z + ss['nut_flats'] / 2))
    body = solids[0].fuse(solids[1:]).cut(Part.makeCompound(cutters)).removeSplitter()
    return Part.Solid(body.Solids[0]) if len(body.Solids) == 1 else body


def inside(shape, x, y, z):
    return shape.isInside(V(x, y, z), 1e-6, True)


def validate(p, part, case_shape):
    """Geometry checks only; printed fit, screw grip and clamp strength are untested."""
    assert part.isValid() and len(part.Solids) == 1, 'plate is not one valid solid'
    t, half = p['plate']['thickness'], p['tube']['outside'] / 2 + p['tube']['clearance']
    assert not inside(part, 0, 0, t / 2) and not inside(part, half - 0.05, half - 0.05, 20), 'tube passage blocked'
    assert inside(part, -half - 0.5, 0, 20) and inside(part, half + 0.5, 3.5, 5), 'collar wall missing'
    for z in p['set_screws']['heights']:
        assert not inside(part, half + 1.5, 0, z) and not inside(part, p['set_screws']['nut_slot_x'] + 1.5, 10, z)
    for x, y in (pi_to_shelf(p, hx, hy) for hx, hy in case_view.HOLES):
        assert not inside(part, x, y, t - 0.5) and inside(part, x + 2.2, y, t - 0.5), 'case screw hole wrong'
    for x, y in pca_holes(p):
        assert not inside(part, x, y, t + 2) and inside(part, x + 2.2, y, t + 2), 'PCA9685 boss wrong'
    clash = part.common(case_shape).Volume
    assert clash < 1e-3, f'plate intersects the case by {clash:.3f} mm3'
    box_ = part.BoundBox
    return {'valid': True, 'volume_mm3': round(part.Volume, 1),
            'bounds_mm': [[round(box_.XMin, 2), round(box_.YMin, 2), round(box_.ZMin, 2)],
                          [round(box_.XMax, 2), round(box_.YMax, 2), round(box_.ZMax, 2)]],
            'case_clash_mm3': round(clash, 4)}


def build(doc, p):
    t = p['plate']['thickness']
    m = case_matrix(p, t)
    case_shape = moved(cut_case(p['case']['cut_height']), m)
    part = plate(p, case_shape.BoundBox)
    checks = validate(p, part, case_shape)
    cadkit.add(doc, 'ShelfPlate', part, PLATE_COLOR, label='Shelf plate with tube collar (print)')
    cadkit.add(doc, 'CaseCut', case_shape, CASE_COLOR, 30, label=f"OMT case cut to {p['case']['cut_height']} mm (print)")
    z = case_view.stack_heights()
    stack = [('Pi5', vendor.shape('pi5-step'), z['pi_z'], hardware_view.PCB_GREEN),
             ('AIHat', hardware_view.ai_hat(), z['ai_hat_bottom'], hardware_view.PCB_GREEN),
             ('MotorHat', vendor.shape('motor-hat-step'), z['motor_hat_bottom'], hardware_view.HAT_BLUE)]
    for name, shape, dz, color in stack:
        cadkit.add(doc, name, moved(hardware_view.placed(shape, 0, 0, dz), m), color, label=name)
    q = p['pca9685']
    pca = hardware_view.placed(vendor.shape('pca9685-step'), *q['origin'], t + q['boss_height'], q['rotation_deg'])
    cadkit.add(doc, 'PCA9685', pca, hardware_view.PCA_BLUE, label='PCA9685 servo board')
    half = p['tube']['outside'] / 2
    cadkit.add(doc, 'SpineTube', box(-half, half, -half, half, -80, 160), STEEL, 40, label='Spine tube, 1 in square')
    top = z['motor_hat_bottom'] + t + 12
    pins = [pi_to_shelf(p, 8.37 + 2.54 * k, 52.0) for k in range(4)]
    for k, (name, (x, y)) in enumerate(zip(['3v3', 'sda', 'scl', 'gnd'], pins)):
        end = V(q['origin'][0], q['origin'][1] - 2.54 * (k + 1), t + q['boss_height'] + 4)
        points = [V(x, y, top - 4), V(x, y, top + 4 + k), V(end.x + 4, end.y, top + 4 + k), V(end.x + 4, end.y, end.z), end]
        cadkit.add(doc, f'i2c_{name}', Part.makePolygon(points), hardware_view.WIRE[name], label=f'I2C jumper {name}', line_width=4)
    bundle = Part.makePolygon([V(-14, 22, t + 2), V(-14, 22, 60), V(-14, 16, 150)])
    cadkit.add(doc, 'Bundle', bundle, (0.3, 0.3, 0.3), label='Bundle up the tube into the skull', line_width=8)
    if App.GuiUp:
        hardware_view.label(doc, 'note_bundle', ['Bundle up the tube into the skull neck hole', 'leave a loop for pan and tilt'],
                            -10, 30, 4)
        hardware_view.label(doc, 'note_collar', ['Collar on the 1 in tube', '2 x M3 set screws, captured nuts'], 26, -30, 4)
        hardware_view.label(doc, 'note_pca', ['PCA9685 on bosses', 'short I2C jumpers to the stack'], -84, 92, 4)
    return part, case_shape, checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--run', required=True, help='new run name under generated/ultraskelly/mount/')
    args = parser.parse_args(argv)
    source = HERE / 'mount.json'
    params = json.loads(source.read_text(encoding='utf-8'))
    folder = cadkit.run_folder('mount', args.run)
    cadkit.close_saved_runs(folder.parent)
    doc = App.newDocument('UltraSkellyMount')
    part, case_shape, checks = build(doc, params)
    doc.recompute()
    native = folder / 'mount.FCStd'
    native_sha = cadkit.save_verified(doc, native)
    plate_stl = cadkit.export_stl(part, folder / 'shelf-plate.stl')
    case_stl = cadkit.export_stl(case_shape, folder / 'omt-case-cut.stl')
    cadkit.write_report(folder / 'build-report.json', {
        'part': 'mount', 'run': args.run, 'units': 'mm', 'parameters_sha256': cadkit.sha256(source),
        'native': {'path': native.name, 'sha256': native_sha},
        'prints': {'shelf-plate.stl': plate_stl, 'omt-case-cut.stl': case_stl},
        'geometry_validation': checks,
        'not_established': ['printed fit on the tube', 'set-screw grip', 'case and board fit', 'clearance to the skull']})
    if App.GuiUp:
        cadkit.present(doc, 'isometric')
    else:
        App.closeDocument(doc.Name)
    print(json.dumps({'saved': str(native), **checks}))


if __name__ == '__main__':
    main()
