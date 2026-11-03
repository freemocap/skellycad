"""Neck clamp and quick-release enclosure for UltraSkelly's Pi 5 stack and PCA9685.

A U clamp and front bar stay on the square tube. The enclosure back carries the
community OMT case (30 mm deep, open side facing back), the Pi stack with its long axis along
the tube and the USB end up, and the PCA9685 on a side wing. It slides down onto the clamp's
dovetail and is locked by one M3 pin, so the electronics lift off without touching the clamp.
Clamp frame and parameters are in enclosure.json. Run live in the project FreeCAD window:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py enclosure --run r007
    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py enclosure --run r008 --lifted

--skeleton-z also draws the mock-up; it stops if the mock-up's spine tube differs from the clamp's tube.
"""
import argparse
import json
from pathlib import Path

import FreeCAD as App
import Part

import cadkit
import case_view
import hardware_view
import mockup
import vendor

HERE = Path(__file__).resolve().parent
V = App.Vector
box = cadkit.box
CLAMP, BACK, CASE, STEEL, PIN = (0.95, 0.55, 0.15), (0.3, 0.6, 0.85), (0.88, 0.88, 0.9), (0.55, 0.57, 0.6), (0.8, 0.8, 0.82)


def prism(points, z0, z1):
    wire = Part.makePolygon([V(x, y, z0) for x, y in points] + [V(points[0][0], points[0][1], z0)])
    return Part.Face(wire).extrude(V(0, 0, z1 - z0))


def dovetail(x_a, width_a, x_b, width_b, z0, z1):
    """Prism between two widths at x_a and x_b, centered on Y = 0."""
    return prism([(x_a, -width_a / 2), (x_a, width_a / 2), (x_b, width_b / 2), (x_b, -width_b / 2)], z0, z1)


def geometry(p):
    t, c, ch = p['tube'], p['clamp'], p['channel']
    half = t['outside'] / 2 + t['clearance']
    g = {'half': half, 'H': c['height'], 'x_back': -half - c['base'], 'x_arm_front': t['outside'] / 2 - c['bar_gap'],
         'y_out': half + c['arm'], 'x_bar': (t['outside'] / 2, t['outside'] / 2 + c['bar'])}
    g['x_block_front'] = g['x_back'] - ch['gap']
    g['x_plate_front'] = g['x_block_front'] - c['tongue_depth'] - ch['clearance'] - ch['floor']
    g['x_plate_back'] = g['x_plate_front'] - p['plate']['thickness']
    g['block_w'] = c['tongue_tip'] + 2 * ch['clearance'] + 2 * ch['walls']
    g['z_block'] = (-ch['below'], c['height'] + ch['cap'])
    g['pin'] = (g['x_back'] - c['tongue_depth'] / 2, -ch['below'] / 2)
    g['bolt_y'] = half + c['bolt_y_inset']
    g['nut_slot_x'] = g['x_arm_front'] - c['nut_slot_setback'] - c['nut_slot']
    g['hole_end_x'] = g['x_back'] + c['bolt_hole_back_wall']  # blind: screws cannot reach the enclosure
    # Arms are thinned from the outside between the base and the screw holes, to save material.
    g['x_thin'] = (g['x_back'] + c['base'] + 4, g['hole_end_x'] - 3)
    g['pca_x'] = g['x_plate_back'] + p['pca9685']['origin_x_from_plate']
    return g


def tongue_width(p, g, x):
    c = p['clamp']
    return c['tongue_root'] + (g['x_back'] - x) * (c['tongue_tip'] - c['tongue_root']) / c['tongue_depth']


def thinned(g):
    """Arms are thinned only where there is room between the base and the screw holes."""
    return g['x_thin'][1] - g['x_thin'][0] > 5


def clamp_u(p, g):
    c, half, H = p['clamp'], g['half'], g['H']
    body = box(g['x_back'], g['x_arm_front'], -g['y_out'], g['y_out'], 0, H).cut(
        box(-half, g['x_arm_front'] + 1, -half, half, -1, H + 1))
    x_in, x_tip = g['x_back'] + 0.5, g['x_back'] - c['tongue_depth']
    body = body.fuse(dovetail(x_in, tongue_width(p, g, x_in), x_tip, c['tongue_tip'], 0, H))
    cutters = []
    for s in (1, -1):
        if thinned(g):
            y_a, y_b = s * (half + c['arm_thin']), s * (g['y_out'] + 1)
            cutters.append(box(*g['x_thin'], min(y_a, y_b), max(y_a, y_b), -1, H + 1))
        for z in c['bolt_heights']:
            # Blind holes from the arm front, deep enough for the screw lengths that validate() reports.
            cutters.append(Part.makeCylinder(c['bolt_clearance'] / 2, g['x_arm_front'] + 1 - g['hole_end_x'],
                                             V(g['x_arm_front'] + 1, s * g['bolt_y'], z), V(-1, 0, 0)))
            y_a, y_b = s * (g['bolt_y'] - 3.4), s * (g['y_out'] + 1)
            cutters.append(box(g['nut_slot_x'], g['nut_slot_x'] + c['nut_slot'], min(y_a, y_b), max(y_a, y_b),
                               z - c['nut_flats'] / 2, z + c['nut_flats'] / 2))
    body = body.cut(Part.makeCompound(cutters)).removeSplitter()
    return Part.Solid(body.Solids[0])


def clamp_bar(p, g):
    c, (x0, x1) = p['clamp'], g['x_bar']
    bar = box(x0, x1, -g['y_out'], g['y_out'], 0, g['H'])
    cutters = []
    for s in (1, -1):
        for z in c['bolt_heights']:
            cutters.append(Part.makeCylinder(c['bolt_clearance'] / 2, x1 - x0 + 2, V(x0 - 1, s * g['bolt_y'], z), V(1, 0, 0)))
            cutters.append(Part.makeCylinder(c['bolt_head'] / 2, c['bolt_head_depth'] + 1, V(x1 - c['bolt_head_depth'], s * g['bolt_y'], z), V(1, 0, 0)))
    return Part.Solid(bar.cut(Part.makeCompound(cutters)).removeSplitter().Solids[0])


def case_matrix(p, g):
    """Pi-origin case coordinates to the clamp frame: Pi x up, Pi y left, board normal toward the back."""
    cs = p['case']
    return App.Matrix(0, 0, -1, g['x_plate_back'], 0, 1, 0, cs['pi_origin_y'], 1, 0, 0, cs['pi_origin_z'], 0, 0, 0, 1)


def pca_matrix(p, g, wing_outer):
    q = p['pca9685']
    return App.Matrix(0, 1, 0, g['pca_x'], 0, 0, 1, wing_outer + q['boss_length'], 1, 0, 0, q['origin_z'], 0, 0, 0, 1)


def pca_holes(p, g):
    q = p['pca9685']
    return [(g['pca_x'] + hy, q['origin_z'] + hx) for hx, hy in q['holes_local']]


def pi_holes(p):
    cs = p['case']
    return [(cs['pi_origin_y'] + y, cs['pi_origin_z'] + x) for x, y in case_view.HOLES]


def enclosure_back(p, g, case_box):
    c, ch, pl, lip, wing, q = p['clamp'], p['channel'], p['plate'], p['lip'], p['wing'], p['pca9685']
    xf, xb, m = g['x_plate_front'], g['x_plate_back'], pl['margin']
    y_wing0 = case_box.YMax + wing['gap']
    y_wing1 = y_wing0 + wing['thickness']
    z0, z1 = case_box.ZMin - m, case_box.ZMax + m
    bw, (zb0, zb1) = g['block_w'], g['z_block']
    solids = [box(xb, xf, case_box.YMin - m, y_wing1, z0, z1),
              box(xb, xf, -20, 20, z1 - 1, z1 + pl['tie_tab']),
              box(xf - 0.5, g['x_block_front'], -bw / 2, bw / 2, zb0, zb1),
              box(case_box.XMin, xb + 0.5, y_wing0, y_wing1, z0, z1)]
    off, w, gap, xl = lip['offset'], lip['wall'], lip['corner_gap'], xb - lip['height']
    cy0, cy1, cz0, cz1 = case_box.YMin - off, case_box.YMax + off, case_box.ZMin - off, case_box.ZMax + off
    solids += [box(xl, xb + 0.5, cy0 - w, cy0, cz0 + gap, cz1 - gap), box(xl, xb + 0.5, cy0 + gap, cy1 - gap, cz0 - w, cz0),
               box(xl, xb + 0.5, cy0 + gap, cy1 - gap, cz1, cz1 + w)]
    solids += [Part.makeCylinder(q['boss_diameter'] / 2, q['boss_length'] + 0.5, V(x, y_wing1 - 0.5, z), V(0, 1, 0))
               for x, z in pca_holes(p, g)]
    body = solids[0].fuse(solids[1:])
    x_mouth, x_bottom = g['x_block_front'] + 1, g['x_back'] - c['tongue_depth'] - ch['clearance']
    cutters = [dovetail(x_mouth, tongue_width(p, g, x_mouth) + 2 * ch['clearance'], x_bottom,
                        tongue_width(p, g, x_bottom) + 2 * ch['clearance'], zb0 - 1, g['H']),
               Part.makeCylinder(ch['pin_clearance'] / 2, bw + 2, V(g['pin'][0], -bw / 2 - 1, g['pin'][1]), V(0, 1, 0))]
    for y, z in pi_holes(p):
        cutters += [Part.makeCylinder(1.5, pl['thickness'] + 2, V(xf + 1, y, z), V(-1, 0, 0)),
                    Part.makeCylinder(2.8, 2.6 + 1, V(xf + 1, y, z), V(-1, 0, 0))]
    cutters += [Part.makeCylinder(q['pilot'] / 2, wing['thickness'] + q['boss_length'] + 2, V(x, y_wing0 - 1, z), V(0, 1, 0))
                for x, z in pca_holes(p, g)]
    sw, sl = pl['tie_slot']
    for y in (-pl['tie_spacing'] / 2, pl['tie_spacing'] / 2):
        cutters.append(box(xb - 1, xf + 1, y - sw / 2, y + sw / 2, z1 + pl['tie_tab'] / 2 - sl / 2, z1 + pl['tie_tab'] / 2 + sl / 2))
    body = body.cut(Part.makeCompound(cutters)).removeSplitter()
    assert len(body.Solids) == 1, 'enclosure back is not one solid'
    return Part.Solid(body.Solids[0]), y_wing1


def inside(shape, x, y, z):
    return shape.isInside(V(x, y, z), 1e-6, True)


def validate(p, g, parts):
    """Geometry checks only: printed fit, clamp grip and latch feel are untested."""
    c, half = p['clamp'], g['half']
    u, bar, back = parts['clamp_u'], parts['clamp_bar'], parts['enclosure_back']
    for name in ('clamp_u', 'clamp_bar', 'enclosure_back'):
        assert parts[name].isValid() and len(parts[name].Solids) == 1, f'{name} is not one valid solid'
    assert not inside(u, 0, 0, g['H'] / 2) and not inside(u, half - 0.05, half - 0.05, 5), 'tube passage blocked'
    assert inside(u, g['x_back'] - c['tongue_depth'] / 2, 0, g['H'] / 2), 'dovetail tongue missing'
    for s in (1, -1):
        for z in c['bolt_heights']:
            y = s * g['bolt_y']
            assert not inside(u, g['x_arm_front'] - 1, y, z) and not inside(bar, g['x_bar'][0] + 1, y, z), 'bolt hole missing'
            assert not inside(u, g['hole_end_x'] + 0.5, y, z), 'bolt hole too short'
            assert inside(u, g['hole_end_x'] - 1, y, z), 'bolt hole runs past its depth'
            assert not inside(u, g['nut_slot_x'] + 1.5, s * (g['bolt_y'] + 2), z), 'nut slot missing'
            assert not thinned(g) or inside(u, g['x_thin'][1] - 1, s * (half + c['arm_thin'] - 0.5), z), 'thinned arm missing'
    # Screw lengths: the tip passes the nut by 1.5 mm with the clamp loose, and stops 1.5 mm short of the
    # hole end with the clamp tight (the U then sits tube-clearance further forward).
    head = g['x_bar'][1] - c['bolt_head_depth']
    nut_back = g['nut_slot_x'] + c['nut_slot'] - c['nut_thickness']
    screws = (round(head - nut_back + 1.5, 1), round(head - g['hole_end_x'] - p['tube']['clearance'] - 1.5, 1))
    assert screws[0] < screws[1], f'no clamp screw length fits: {screws}'
    assert not inside(back, g['x_back'] - c['tongue_depth'] / 2, 0, g['H'] / 2), 'channel blocked'
    assert not inside(back, g['pin'][0], 0, g['pin'][1]), 'lock pin hole blocked'
    assert g['pin'][1] + p['channel']['pin_clearance'] / 2 < 0, 'lock pin would hit the seated tongue'
    clashes = {'clamp_u-back': u.common(back).Volume, 'clamp_u-bar': u.common(bar).Volume,
               'case-back': parts['case'].common(back).Volume, 'pca-back': parts['pca9685'].common(back).Volume}
    for name, volume in clashes.items():
        assert volume < 1e-3, f'{name} overlap {volume:.3f} mm3'
    return {'valid': True, 'clash_mm3': {k: round(v, 4) for k, v in clashes.items()},
            'volumes_mm3': {k: round(parts[k].Volume, 1) for k in ('clamp_u', 'clamp_bar', 'enclosure_back')},
            'clamp_screw_length_mm': list(screws)}


def build(doc, p, dz=0.0, lift=0.0, tube=True):
    g = geometry(p)
    m = case_matrix(p, g)
    case_shape = cadkit.moved(case_view.cut_case(p['case']['cut_height']), m)
    back, wing_outer = enclosure_back(p, g, case_shape.BoundBox)
    pca = cadkit.moved(vendor.shape('pca9685-step'), pca_matrix(p, g, wing_outer))
    parts = {'clamp_u': clamp_u(p, g), 'clamp_bar': clamp_bar(p, g), 'enclosure_back': back, 'case': case_shape, 'pca9685': pca}
    checks = validate(p, g, parts)
    up = V(0, 0, dz)
    lifted = V(0, 0, dz + lift)

    def add(name, shape, color, label, transparency=0, offset=up):
        shape = shape.copy()
        shape.translate(offset)
        return cadkit.add(doc, name, shape, color, transparency, label=label)

    add('ClampU', parts['clamp_u'], CLAMP, 'U clamp with dovetail (print)')
    add('ClampBar', parts['clamp_bar'], CLAMP, 'Clamp bar, 4 x M3 (print)')
    add('EnclosureBack', back, BACK, 'Enclosure back with dovetail channel and PCA9685 wing (print)', offset=lifted)
    add('CaseCut', case_shape, CASE, f"Pi case, {p['case']['cut_height']} mm deep (print)", 30, offset=lifted)
    z = case_view.stack_heights()
    for name, shape, height, color in (('Pi5', vendor.shape('pi5-step'), z['pi_z'], hardware_view.PCB_GREEN),
                                       ('AIHat', hardware_view.ai_hat(), z['ai_hat_bottom'], hardware_view.PCB_GREEN),
                                       ('MotorHat', vendor.shape('motor-hat-step'), z['motor_hat_bottom'], hardware_view.HAT_BLUE)):
        add(name, cadkit.moved(hardware_view.placed(shape, 0, 0, height), m), color, name, offset=lifted)
    add('PCA9685', pca, hardware_view.PCA_BLUE, 'PCA9685 on the side wing', offset=lifted)
    pin = Part.makeCylinder(1.5, g['block_w'] + 6, V(g['pin'][0], -g['block_w'] / 2 - 3, g['pin'][1]), V(0, 1, 0))
    add('LockPin', pin, PIN, 'M3 lock pin', offset=lifted)
    if tube:
        w = p['tube']['outside'] / 2
        add('SpineTube', box(-w, w, -w, w, -60, 140), STEEL, f"Square tube, {p['tube']['outside']} mm", 40)
    return parts, checks


def print_shapes(parts):
    """Print orientation: clamp U standing, bar flat with its head recesses up, enclosure back on its lower end."""
    u = parts['clamp_u'].copy()
    bar = parts['clamp_bar'].copy()
    bar.rotate(V(0, 0, 0), V(0, 1, 0), -90)  # front face, with the screw-head recesses, faces up
    back = parts['enclosure_back'].copy()
    out = {'clamp-u.stl': u, 'clamp-bar.stl': bar, 'enclosure-back.stl': back}
    for shape in out.values():
        shape.translate(V(0, 0, -shape.BoundBox.ZMin))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--run', required=True, help='new run name under generated/ultraskelly/enclosure/')
    parser.add_argument('--lifted', action='store_true', help='show the enclosure lifted off the dovetail')
    parser.add_argument('--skeleton-z', type=float, help='also draw the mock-up, with the clamp bottom at this height (mm)')
    args = parser.parse_args(argv)
    source = HERE / 'enclosure.json'
    params = json.loads(source.read_text(encoding='utf-8'))
    folder = cadkit.run_folder('enclosure', args.run)
    doc = App.newDocument('UltraSkellyEnclosure')
    dz = 0.0
    if args.skeleton_z is not None:
        body = json.loads((HERE / 'mockup.json').read_text(encoding='utf-8'))
        if body['spine_tube']['outside'] != params['tube']['outside']:
            App.closeDocument(doc.Name)
            raise SystemExit(f"mockup.json spine tube is {body['spine_tube']['outside']} mm but the clamp fits a "
                             f"{params['tube']['outside']} mm tube; robot gaps against it would be meaningless")
        mockup.build(doc, body)
        dz = args.skeleton_z
    parts, checks = build(doc, params, dz, params['lift_for_view'] if args.lifted else 0.0, tube=args.skeleton_z is None)
    gaps = {}
    if args.skeleton_z is not None:
        ours = [doc.getObject(n).Shape for n in ('ClampU', 'ClampBar', 'EnclosureBack', 'MotorHat', 'PCA9685')]
        cb = doc.getObject('CaseCut').Shape.BoundBox  # the case mesh is too heavy for exact distances; use its box
        ours.append(box(cb.XMin, cb.XMax, cb.YMin, cb.YMax, cb.ZMin, cb.ZMax))
        for other in ('Shoulders', 'NeckDrive', 'Skull', 'Jaw', 'Ribcage'):
            body = doc.getObject(other).Shape
            gaps[other] = round(min(shape.distToShape(body)[0] for shape in ours), 1)
    doc.recompute()
    native = folder / 'enclosure.FCStd'
    native_sha = cadkit.save_verified(doc, native)
    prints = {name: cadkit.export_stl(shape, folder / name) for name, shape in print_shapes(parts).items()}
    case_name = f"pi-case-{params['case']['cut_height']}mm.stl"
    prints[case_name] = cadkit.export_stl(case_view.cut_case(params['case']['cut_height']), folder / case_name)
    cadkit.write_report(folder / 'build-report.json', {
        'part': 'enclosure', 'run': args.run, 'units': 'mm', 'parameters_sha256': cadkit.sha256(source),
        'native': {'path': native.name, 'sha256': native_sha}, 'prints': prints, 'geometry_validation': checks,
        'skeleton_gaps_mm': gaps, 'status': 'Concept for review; not released for printing.'})
    if App.GuiUp:
        cadkit.present(doc, 'isometric')
    else:
        App.closeDocument(doc.Name)
    print(json.dumps({'saved': str(native), **checks, 'skeleton_gaps_mm': gaps}))


if __name__ == '__main__':
    main()
