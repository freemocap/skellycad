"""Tube splice for UltraSkelly: one U channel and two front bars hold two pieces of the square tube end to end.

The U has the fit-tested neck clamp's cross-section (U1 pocket, M2.5 screws into captured nuts), made long
enough to grip both pieces. The tube ends meet at its middle, and each piece has its own bar with four
screws, so each side tightens on its own tube. The cross-section comes from enclosure.json; the lengths
along the tube are in splice.json. Both parts print without supports. Run live in the project FreeCAD
window from the repository root:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py splice --run r001
"""
import argparse
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
    """Cross-section from the neck clamp; positions along the tube (z) from splice.json.

    The U stands on its lower end (z = 0) and the tube ends meet at z = grip. Each bar is grip minus half
    the split gap long, with its screw rows row_inset from both ends, so the two bars are one part.
    """
    g = enclosure.geometry(p)
    g['z_bed'] = 0.0  # no tongue or lock here: the whole U starts on the bed
    bar_length = s['grip'] - s['split_gap'] / 2
    bar_rows = [s['row_inset'], bar_length - s['row_inset']]
    bar_z = [0.0, s['grip'] + s['split_gap'] / 2]
    return g, {'length': 2 * s['grip'], 'split': s['grip'], 'bar_length': bar_length, 'bar_rows': bar_rows,
               'bar_z': bar_z, 'rows': [z0 + r for z0 in bar_z for r in bar_rows]}


def splice_u(p, g, lay):
    c, half, length = p['clamp'], g['half'], lay['length']
    outer = box(g['x_back'], g['x_arm_front'], -g['y_out'], g['y_out'], 0, length)
    # Rounded outer corners: vertical edges print as walls, so the fillets need no support.
    outer = outer.makeFillet(c['corner_radius'], enclosure.edges_along(outer, 2, lambda m: abs(abs(m.y) - g['y_out']) < 1e-6))
    body = outer.cut(box(g['x_tube_back'], g['x_arm_front'] + 1, -half, half, -1, length + 1)).removeSplitter()
    # A 45 degree chamfer where the pocket meets the bed keeps the first layer's flare out of the tube fit.
    body = body.makeChamfer(c['bed_chamfer'], enclosure.bed_fit_edges(body, g))
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


def splice_bar(p, g, lay):
    c, (x0, x1) = p['clamp'], g['x_bar']
    bar = box(x0, x1, -g['y_out'], g['y_out'], 0, lay['bar_length'])
    # Rounded corners seen from the front; these edges stand vertical when the bar prints flat.
    bar = bar.makeFillet(c['corner_radius'], enclosure.edges_along(bar, 0, lambda m: True))
    cutters = []
    for side in (1, -1):
        for z in lay['bar_rows']:
            cutters.append(Part.makeCylinder(c['bolt_clearance'] / 2, x1 - x0 + 2, V(x0 - 1, side * g['bolt_y'], z), V(1, 0, 0)))
            cutters.append(Part.makeCylinder(c['bolt_head'] / 2, c['bolt_head_depth'] + 1,
                                             V(x1 - c['bolt_head_depth'], side * g['bolt_y'], z), V(1, 0, 0)))
    return Part.Solid(bar.cut(Part.makeCompound(cutters)).removeSplitter().Solids[0])


def inside(shape, x, y, z):
    return shape.isInside(V(x, y, z), 1e-6, True)


def validate(p, g, s, lay, u, bars):
    """Geometry checks only: printed fit, grip and joint stiffness are untested."""
    c, half = p['clamp'], g['half']
    t_min, t_max = p['tube']['range']
    for name, shape in (('splice_u', u), ('bar_1', bars[0]), ('bar_2', bars[1])):
        assert shape.isValid() and len(shape.Solids) == 1, f'{name} is not one valid solid'
    for zm in (lay['split'] / 2, lay['split'] * 1.5):  # the middle of each tube piece's grip
        assert not inside(u, 0, 0, zm), 'tube passage blocked'
        for side in (1, -1):
            assert not inside(u, g['x_tube_back'] + 0.05, side * (half - 0.05), zm), 'pocket narrower than the largest tube'
            assert inside(u, g['x_tube_back'] + 1, side * (half + 0.05), zm), 'pocket wider than designed'
    assert g['x_arm_front'] < g['x_tube_back'] + t_min, 'arms reach the front face of the smallest tube'
    for side in (1, -1):
        for z in lay['rows']:
            y = side * g['bolt_y']
            assert not inside(u, g['x_arm_front'] - 1, y, z), 'bolt hole missing'
            assert not inside(u, g['hole_end_x'] + 0.5, y, z), 'bolt hole too short'
            assert inside(u, g['hole_end_x'] - 1, y, z), 'bolt hole runs past its depth'
            assert not inside(u, g['nut_slot_x'] + c['nut_slot'] / 2, side * (g['bolt_y'] + 2), z), 'nut slot missing'
            bar = bars[0] if z < lay['split'] else bars[1]
            assert not inside(bar, g['x_bar'][0] + 1, y, z), 'bar hole not in line with the U'
            assert inside(bar, g['x_bar'][0] + 1, y, z + c['bolt_head'] / 2 + 0.5), 'bar missing around its hole'
    rows = sorted(lay['rows'])
    walls = {
        'nut_slot_to_pocket': g['bolt_y'] - c['nut_slot_inner'] - half,
        'beside_bar_head_recess': g['y_out'] - g['bolt_y'] - c['bolt_head'] / 2,
        'nut_slot_to_u_ends': min(rows[0], lay['length'] - rows[-1]) - c['nut_flats'] / 2,
        'between_nut_slots': min(b - a for a, b in zip(rows, rows[1:])) - c['nut_flats'],
        'head_recess_to_bar_ends': min(lay['bar_rows'][0], lay['bar_length'] - lay['bar_rows'][-1]) - c['bolt_head'] / 2,
    }
    assert min(walls.values()) >= 1.35, f'wall under three perimeters: {walls}'
    # Screw lengths across the tube range, clamped: the tip passes the nut by 1.5 mm on the largest tube and
    # stops 1.5 mm short of the hole end on the smallest (the neck clamp's rule).
    head = lambda tube: g['x_tube_back'] + tube + c['bar'] - c['bolt_head_depth']
    nut_back = g['nut_slot_x'] + c['nut_slot'] - c['nut_thickness']
    screws = (round(head(t_max) - nut_back + 1.5, 1), round(head(t_min) - g['hole_end_x'] - 1.5, 1))
    assert screws[0] <= s['screw'] <= screws[1], f"M2.5 x {s['screw']} does not fit the window {screws}"
    k = c['bed_chamfer']
    assert not inside(u, g['x_tube_back'] - k / 3, 0, k / 3), 'pocket edge on the bed not chamfered'
    assert inside(u, g['x_tube_back'] - 2 * k, 0, k / 3), 'U base missing behind the pocket chamfer'
    assert abs(bars[1].BoundBox.ZMin - bars[0].BoundBox.ZMax - s['split_gap']) < 1e-6, 'bar gap at the split'
    clashes = {'u-bar_1': u.common(bars[0]).Volume, 'u-bar_2': u.common(bars[1]).Volume,
               'bar_1-bar_2': bars[0].common(bars[1]).Volume}
    for name, volume in clashes.items():
        assert volume < 1e-3, f'{name} overlap {volume:.3f} mm3'
    play = (round(2 * half - t_max, 2), round(2 * half - t_min, 2))
    return {'valid': True, 'clash_mm3': {k: round(v, 4) for k, v in clashes.items()},
            'volumes_mm3': {'splice_u': round(u.Volume, 1), 'splice_bar': round(bars[0].Volume, 1)},
            'length_mm': lay['length'], 'split_z_mm': lay['split'], 'bar_length_mm': lay['bar_length'],
            'screw_rows_z_mm': rows, 'walls_mm': {k: round(v, 2) for k, v in walls.items()},
            'clamp_screw_length_mm': list(screws), 'sideways_play_mm': list(play),
            'sideways_rock_limit_deg': [round(math.degrees(math.atan(x / s['grip'])), 2) for x in play]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--run', required=True, help='new run name under generated/ultraskelly/splice/')
    args = parser.parse_args(argv)
    p = json.loads((HERE / 'enclosure.json').read_text(encoding='utf-8'))
    s = json.loads((HERE / 'splice.json').read_text(encoding='utf-8'))
    g, lay = layout(p, s)
    if DOC in App.listDocuments():
        raise RuntimeError(f'{DOC} is already open; close it first')
    folder = cadkit.run_folder('splice', args.run)
    u, bar = splice_u(p, g, lay), splice_bar(p, g, lay)
    bars = []
    for z0 in lay['bar_z']:
        placed = bar.copy()
        placed.translate(V(0, 0, z0))
        bars.append(placed)
    checks = validate(p, g, s, lay, u, bars)
    doc = App.newDocument(DOC)
    cadkit.add(doc, 'SpliceU', u, ORANGE, label='Splice U (print 1)')
    for i, placed in enumerate(bars, start=1):
        cadkit.add(doc, f'SpliceBar{i}', placed, ORANGE, label=f"Splice bar {i} of 2, 4 x M2.5 x {s['screw']} (print 2)")
    w = p['tube']['outside'] / 2
    for i, (z0, z1) in enumerate(((-40.0, lay['split']), (lay['split'], lay['length'] + 40.0)), start=1):
        cadkit.add(doc, f'TubePiece{i}', box(-w, w, -w, w, z0, z1), STEEL, 40,
                   label=f"Tube piece {i}, {p['tube']['outside']} mm (not printed)")
    doc.recompute()
    native_sha = cadkit.save_verified(doc, folder / 'splice.FCStd')
    flat_bar = bar.copy()
    flat_bar.rotate(V(0, 0, 0), V(0, 1, 0), -90)  # front face, with the head recesses, up
    prints = {}
    for name, shape in (('splice-u.stl', u.copy()), ('splice-bar.stl', flat_bar)):
        shape.translate(V(0, 0, -shape.BoundBox.ZMin))
        prints[name] = cadkit.export_stl(shape, folder / name)
    cadkit.write_report(folder / 'build-report.json', {
        'part': 'splice', 'run': args.run, 'units': 'mm',
        'parameters_sha256': {'splice.json': cadkit.sha256(HERE / 'splice.json'),
                              'enclosure.json': cadkit.sha256(HERE / 'enclosure.json')},
        'native': {'path': 'splice.FCStd', 'sha256': native_sha}, 'prints': prints,
        'quantities': {'splice-u.stl': 1, 'splice-bar.stl': 2}, 'geometry_validation': checks,
        'status': 'Concept for review; geometry checks only.'})
    if App.GuiUp:
        cadkit.present(doc, 'isometric')
    print(json.dumps({'saved': str(folder), **checks}))


if __name__ == '__main__':
    main()
