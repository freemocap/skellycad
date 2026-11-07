"""Tube splice for UltraSkelly: one U channel and one top plate hold two pieces of the square tube end to end.

The U has the fit-tested neck clamp's cross-section (U1 pocket and arms, M2.5 screws into captured nuts)
with a thicker base, made long enough to grip both pieces. The tube ends meet at its middle. One plate
covers both pieces, with a screw at each corner. A tongue on the plate reaches between the arms, which
stand past the tube, and presses on both pieces. The cross-section comes from enclosure.json; the
thicknesses and lengths are in splice.json. Both parts print flat without supports: the U lies on its back,
so bending at the joint runs along its layers, and the plate prints tongue up. Run live in the project
FreeCAD window from the repository root:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py splice --run r003
"""
import argparse
import copy
import json
import math
from pathlib import Path

import FreeCAD as App
import Part

import cadkit
import enclosure

HERE = Path(__file__).resolve().parent
V = App.Vector
box = cadkit.box
DOC = 'UltraSkellySplice'
ORANGE, STEEL = (0.95, 0.55, 0.15), (0.55, 0.57, 0.6)


def layout(p, s):
    """The neck clamp's cross-section with the splice's base, plate, tongue and recess depth; positions along the tube.

    Returns the adjusted parameters, the geometry and the layout. The parts are built with the tube along z:
    the U's ends at z = 0 and z = length, the tube ends meeting at z = grip, and a screw at each corner,
    row_inset from the ends. The plate is placed on the nominal tube: its tongue face on the tube's front face.
    """
    q = copy.deepcopy(p)
    c = q['clamp']
    c['base'], c['bar'] = s['base'], s['plate']
    # Deeper head recesses keep each screw head where it sits on the neck clamp, so the same screw fits.
    c['bolt_head_depth'] = s['plate'] - s['under_head']
    g = enclosure.geometry(q)
    g['z_bed'] = 0.0  # no dovetail tongue or lock here
    # The plate's tongue reaches into the channel, so the arms rise by its height: they stand past the largest
    # tube's front face, and the plate still clears them by takeup_min on the smallest tube. The nut slots rise
    # with the arm fronts, so the screw window stays the neck clamp's.
    g['x_arm_front'] = g['x_tube_back'] + q['tube']['range'][0] + s['tongue'] - c['takeup_min']
    g['nut_slot_x'] = g['x_arm_front'] - c['nut_slot_setback'] - c['nut_slot']
    face = q['tube']['outside'] / 2
    g['x_tongue'] = (face, face + s['tongue'])
    g['x_bar'] = (face + s['tongue'], face + s['tongue'] + s['plate'])
    g['tongue_half'] = g['half'] - s['tongue_clearance']
    # The blind holes end under the pocket floor, not near the back, so the thicker base stays solid.
    g['hole_end_x'] = g['x_tube_back'] - s['hole_end_below_pocket']
    length = 2 * s['grip']
    return q, g, {'length': length, 'split': s['grip'], 'rows': [s['row_inset'], length - s['row_inset']]}


def splice_u(p, g, lay):
    c, half, length = p['clamp'], g['half'], lay['length']
    outer = box(g['x_back'], g['x_arm_front'], -g['y_out'], g['y_out'], 0, length)
    # The U prints on its back (x up), so only its corner edges along x stand vertical; they are rounded.
    # The other edges stay square: a fillet on an edge at the bed would print as an overhang.
    outer = outer.makeFillet(c['corner_radius'], enclosure.edges_along(outer, 0, lambda m: True))
    body = outer.cut(box(g['x_tube_back'], g['x_arm_front'] + 1, -half, half, -1, length + 1)).removeSplitter()
    cutters = []
    for side in (1, -1):
        for z in lay['rows']:
            # Blind holes from the arm front, as on the neck clamp, so the screw window is the same.
            cutters.append(Part.makeCylinder(c['bolt_clearance'] / 2, g['x_arm_front'] + 1 - g['hole_end_x'],
                                             V(g['x_arm_front'] + 1, side * g['bolt_y'], z), V(-1, 0, 0)))
            y_a, y_b = side * (g['bolt_y'] - c['nut_slot_inner']), side * (g['y_out'] + 1)
            cutters.append(box(g['nut_slot_x'], g['nut_slot_x'] + c['nut_slot'], min(y_a, y_b), max(y_a, y_b),
                               z - c['nut_flats'] / 2, z + c['nut_flats'] / 2))
    body = body.cut(Part.makeCompound(cutters)).removeSplitter()
    return Part.Solid(body.Solids[0])


def splice_plate(p, g, lay):
    c, (x0, x1), length = p['clamp'], g['x_bar'], lay['length']
    plate = box(x0, x1, -g['y_out'], g['y_out'], 0, length)
    # Rounded corners seen from the front; these edges stand vertical when the plate prints flat.
    plate = plate.makeFillet(c['corner_radius'], enclosure.edges_along(plate, 0, lambda m: True))
    # The tongue runs the plate's length between the arms and bears on both tube pieces. It overlaps the
    # plate by 1 mm so the two fuse into one solid.
    w = g['tongue_half']
    plate = plate.fuse(box(g['x_tongue'][0], x0 + 1, -w, w, 0, length)).removeSplitter()
    cutters = []
    for side in (1, -1):
        for z in lay['rows']:
            cutters.append(Part.makeCylinder(c['bolt_clearance'] / 2, x1 - x0 + 2, V(x0 - 1, side * g['bolt_y'], z), V(1, 0, 0)))
            cutters.append(Part.makeCylinder(c['bolt_head'] / 2, c['bolt_head_depth'] + 1,
                                             V(x1 - c['bolt_head_depth'], side * g['bolt_y'], z), V(1, 0, 0)))
    return Part.Solid(plate.cut(Part.makeCompound(cutters)).removeSplitter().Solids[0])


def inside(shape, x, y, z):
    return shape.isInside(V(x, y, z), 1e-6, True)


def section(shape, z):
    """Area and second moments of area of a part's cross-section across the tube at z.

    front_back is the integral of x squared about the centroid (the joint bending toward the plate or the
    base); sideways is the integral of y squared. Each modulus divides by the farthest fibre.
    """
    wires = shape.slice(V(0, 0, 1), z)
    assert len(wires) == 1, f'section at z = {z} has {len(wires)} outlines, expected one with no holes'
    face = Part.Face(wires[0])
    m, com, b = face.MatrixOfInertia, face.CenterOfMass, face.BoundBox
    i_fb, i_side = m.A22, m.A11
    return {'area_mm2': round(face.Area, 1), 'front_back_mm4': round(i_fb), 'sideways_mm4': round(i_side),
            'front_back_modulus_mm3': round(i_fb / max(b.XMax - com.x, com.x - b.XMin)),
            'sideways_modulus_mm3': round(i_side / max(b.YMax - com.y, com.y - b.YMin))}


def validate(p, g, s, lay, u, plate):
    """Geometry checks only: printed fit, grip and the joint's strength are untested."""
    c, half = p['clamp'], g['half']
    t_min, t_max = p['tube']['range']
    for name, shape in (('splice_u', u), ('splice_plate', plate)):
        assert shape.isValid() and len(shape.Solids) == 1, f'{name} is not one valid solid'
    for zm in (lay['split'] / 2, lay['split'], lay['split'] * 1.5):  # each piece's grip and the joint
        assert not inside(u, 0, 0, zm), 'tube passage blocked'
        for side in (1, -1):
            assert not inside(u, g['x_tube_back'] + 0.05, side * (half - 0.05), zm), 'pocket narrower than the largest tube'
            assert inside(u, g['x_tube_back'] + 1, side * (half + 0.05), zm), 'pocket wider than designed'
        assert inside(u, g['x_back'] + 0.05, 0, zm) and inside(u, g['x_tube_back'] - 0.05, 0, zm), 'base thinner than designed'
        xt, w = sum(g['x_tongue']) / 2, g['tongue_half']
        for side in (1, -1):
            assert inside(plate, xt, side * (w - 0.05), zm), 'tongue narrower than designed'
            assert not inside(plate, xt, side * (w + 0.05), zm), 'tongue wider than designed'
        assert inside(plate, g['x_tongue'][0] + 0.05, 0, zm), 'tongue shorter than designed'
        assert not inside(plate, g['x_tongue'][0] - 0.05, 0, zm), 'tongue taller than designed'
    # Tightened on any tube in range, the tongue bears on the tube with the plate still clear of the arms, and
    # the arms stand past the tube's front face, so the tongue sits inside the channel.
    face = lambda tube: g['x_tube_back'] + tube
    gap = lambda tube: face(tube) + s['tongue'] - g['x_arm_front']  # plate to arm fronts, tightened
    assert gap(t_min) >= c['takeup_min'] - 1e-9, 'plate meets the arms before the tongue bears on the smallest tube'
    assert g['x_arm_front'] > face(t_max), 'arms stop short of the largest tube: the tongue would not enter the channel'
    tongue_side = half - g['tongue_half']
    assert tongue_side >= 0.3 - 1e-9, 'tongue tighter in the channel than a 0.3 mm moving fit'
    for side in (1, -1):
        y = side * g['bolt_y']
        # The joint is solid: the screws and nut slots are only at the corners.
        assert inside(u, g['nut_slot_x'] + c['nut_slot'] / 2, y, lay['split']), 'hole or slot at the joint'
        assert inside(plate, g['x_bar'][1] - 0.5, y, lay['split']), 'hole at the joint in the plate'
        for z in lay['rows']:
            assert not inside(u, g['x_arm_front'] - 1, y, z), 'bolt hole missing'
            assert not inside(u, g['hole_end_x'] + 0.5, y, z), 'bolt hole too short'
            assert inside(u, g['hole_end_x'] - 1, y, z), 'bolt hole runs past its depth'
            assert not inside(u, g['nut_slot_x'] + c['nut_slot'] / 2, side * (g['bolt_y'] + 2), z), 'nut slot missing'
            assert not inside(plate, g['x_bar'][0] + 1, y, z), 'plate hole not in line with the U'
            ring = side * (g['bolt_y'] + c['bolt_head'] / 2 - 0.3)  # inside the head recess, outside the hole
            assert not inside(plate, g['x_bar'][1] - c['bolt_head_depth'] + 0.3, ring, z), 'head recess missing'
            assert inside(plate, g['x_bar'][1] - c['bolt_head_depth'] - 0.3, ring, z), 'head recess deeper than designed'
            assert inside(plate, g['x_bar'][0] + 1, y, z + c['bolt_head'] / 2 + 0.5), 'plate missing around its hole'
    rows = lay['rows']
    walls = {
        'nut_slot_to_pocket': g['bolt_y'] - c['nut_slot_inner'] - half,
        'nut_slot_to_u_ends': min(rows[0], lay['length'] - rows[-1]) - c['nut_flats'] / 2,
        'nut_slot_to_arm_front': g['x_arm_front'] - g['nut_slot_x'] - c['nut_slot'],
        'hole_end_to_u_back': g['hole_end_x'] - g['x_back'],
        'beside_plate_head_recess': g['y_out'] - g['bolt_y'] - c['bolt_head'] / 2,
        'head_recess_to_plate_ends': min(rows[0], lay['length'] - rows[-1]) - c['bolt_head'] / 2,
        'plate_under_screw_head': g['x_bar'][1] - g['x_bar'][0] - c['bolt_head_depth'],
    }
    assert min(walls.values()) >= 1.35, f'wall under three perimeters: {walls}'
    # Screw lengths across the tube range, clamped: the tip passes the nut by 1.5 mm on the largest tube and
    # stops 1.5 mm short of the hole end on the smallest (the neck clamp's rule).
    head = lambda tube: face(tube) + s['tongue'] + c['bar'] - c['bolt_head_depth']
    nut_back = g['nut_slot_x'] + c['nut_slot'] - c['nut_thickness']
    screws = (round(head(t_max) - nut_back + 1.5, 1), round(head(t_min) - g['hole_end_x'] - 1.5, 1))
    assert screws[0] <= s['screw'] <= screws[1], f"M2.5 x {s['screw']} does not fit the window {screws}"
    # The plate as built sits on the nominal tube; also check it tightened on the smallest tube.
    low = plate.copy()
    low.translate(V(t_min - p['tube']['outside'], 0, 0))
    clash = {'u-plate': u.common(plate).Volume, 'u-plate_on_smallest_tube': u.common(low).Volume}
    assert max(clash.values()) < 1e-3, f'U and plate overlap: {clash}'
    play = (round(2 * half - t_max, 2), round(2 * half - t_min, 2))
    tubes = (t_min, p['tube']['outside'], t_max)
    return {'valid': True, 'clash_mm3': {k: round(v, 4) for k, v in clash.items()},
            'volumes_mm3': {'splice_u': round(u.Volume, 1), 'splice_plate': round(plate.Volume, 1)},
            'length_mm': lay['length'], 'split_z_mm': lay['split'], 'screw_rows_z_mm': rows,
            'base_mm': s['base'], 'plate_mm': s['plate'], 'head_recess_depth_mm': round(c['bolt_head_depth'], 2),
            'tongue': {'height_mm': s['tongue'], 'width_mm': round(2 * g['tongue_half'], 2),
                       'clearance_each_side_mm': round(tongue_side, 2),
                       'into_channel_mm': {str(t): round(g['x_arm_front'] - face(t), 2) for t in tubes},
                       'plate_to_arm_gap_tightened_mm': {str(t): round(gap(t), 2) for t in tubes}},
            'arm_height_above_pocket_floor_mm': round(g['x_arm_front'] - g['x_tube_back'], 2),
            'walls_mm': {k: round(v, 2) for k, v in walls.items()},
            'joint_section': {'splice_u': section(u, lay['split']), 'splice_plate': section(plate, lay['split'])},
            'clamp_screw_length_mm': list(screws), 'sideways_play_mm': list(play),
            'sideways_rock_limit_deg': [round(math.degrees(math.atan(x / s['grip'])), 2) for x in play]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--run', required=True, help='new run name under generated/ultraskelly/splice/')
    args = parser.parse_args(argv)
    p = json.loads((HERE / 'enclosure.json').read_text(encoding='utf-8'))
    s = json.loads((HERE / 'splice.json').read_text(encoding='utf-8'))
    q, g, lay = layout(p, s)
    if DOC in App.listDocuments():
        raise RuntimeError(f'{DOC} is already open; close it first')
    folder = cadkit.run_folder('splice', args.run)
    u, plate = splice_u(q, g, lay), splice_plate(q, g, lay)
    checks = validate(q, g, s, lay, u, plate)
    doc = App.newDocument(DOC)
    cadkit.add(doc, 'SpliceU', u, ORANGE, label='Splice U (print 1)')
    cadkit.add(doc, 'SplicePlate', plate, ORANGE, label=f"Splice plate, 4 x M2.5 x {s['screw']} (print 1)")
    w = p['tube']['outside'] / 2
    for i, (z0, z1) in enumerate(((-40.0, lay['split']), (lay['split'], lay['length'] + 40.0)), start=1):
        cadkit.add(doc, f'TubePiece{i}', box(-w, w, -w, w, z0, z1), STEEL, 40,
                   label=f"Tube piece {i}, {p['tube']['outside']} mm (not printed)")
    doc.recompute()
    native_sha = cadkit.save_verified(doc, folder / 'splice.FCStd')
    prints = {}
    # The U prints x up: on its back with the pocket open upward. The plate prints x down: its outer face with
    # the head recesses on the bed and its tongue up, so the tongue needs no support.
    for name, shape, turn in (('splice-u.stl', u, -90), ('splice-plate.stl', plate, 90)):
        flat = shape.copy()
        flat.rotate(V(0, 0, 0), V(0, 1, 0), turn)
        flat.translate(V(0, 0, -flat.BoundBox.ZMin))
        prints[name] = cadkit.export_stl(flat, folder / name)
    cadkit.write_report(folder / 'build-report.json', {
        'part': 'splice', 'run': args.run, 'units': 'mm',
        'parameters_sha256': {'splice.json': cadkit.sha256(HERE / 'splice.json'),
                              'enclosure.json': cadkit.sha256(HERE / 'enclosure.json')},
        'native': {'path': 'splice.FCStd', 'sha256': native_sha}, 'prints': prints,
        'quantities': {'splice-u.stl': 1, 'splice-plate.stl': 1}, 'geometry_validation': checks,
        'status': 'Concept for review; geometry checks only.'})
    if App.GuiUp:
        cadkit.present(doc, 'isometric')
    print(json.dumps({'saved': str(folder), **checks}))


if __name__ == '__main__':
    main()
