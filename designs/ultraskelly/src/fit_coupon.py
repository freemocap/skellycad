"""Pi 5 hole-pattern fit coupon: four M2.5 bosses with different pilot holes and a zip-tie tab.

Coupon frame: origin at the Pi 5 board's lower-left corner, +X along its 85 mm edge,
+Z up from the print bed, millimetres. Boss n carries n index marks and the n-th pilot
diameter in fit-coupon.json. Run from the repository root with the pinned FreeCAD Python:

    .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe -B designs/ultraskelly/src/fit_coupon.py --run r001
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
PROBE = 0.02  # mm offset for inside/outside probes around designed edges


def boss_centers(pi5):
    """Mounting-hole centers, counter-clockwise from the lower-left hole [@raspberrypi2025Pi5Drawing]."""
    e = pi5['hole_edge_offset']
    px, py = pi5['hole_pattern']
    return [(e, e), (e + px, e), (e + px, e + py), (e, e + py)]


def rail_box(start, end, width, thickness):
    (x0, y0), (x1, y1) = start, end
    if y0 == y1:
        return Part.makeBox(abs(x1 - x0), width, thickness, V(min(x0, x1), y0 - width / 2, 0))
    return Part.makeBox(width, abs(y1 - y0), thickness, V(x0 - width / 2, min(y0, y1), 0))


def tab_layout(params):
    """Tie tab below the first rail, with two slots spaced across a cable laid along X."""
    centers, rail, tab = boss_centers(params['pi5']), params['rail'], params['tie_tab']
    x_mid = (centers[0][0] + centers[1][0]) / 2
    y_top = centers[0][1] - rail['width'] / 2
    y_mid = y_top - tab['length'] / 2
    slots = [(x_mid, y_mid + sign * tab['slot_spacing'] / 2) for sign in (1, -1)]
    return x_mid, y_top, slots


def mark_layout(params):
    """Index-mark centers: n dimples on the X rail beside boss n, pointing toward the middle."""
    centers, boss, mark = boss_centers(params['pi5']), params['boss'], params['index_mark']
    middle = sum(x for x, _ in centers) / len(centers)
    marks = []
    for number, (x, y) in enumerate(centers, 1):
        sign = 1 if x < middle else -1
        start = boss['outer_diameter'] / 2 + 1.5
        marks += [(number, x + sign * (start + i * mark['pitch']), y) for i in range(number)]
    return marks


def build(params):
    assert params['units'] == 'mm'
    pi5, rail, boss, tab, mark = (params[k] for k in ('pi5', 'rail', 'boss', 'tie_tab', 'index_mark'))
    assert boss['outer_diameter'] <= pi5['pad_diameter'], 'boss would overhang the mounting pad'
    assert len(params['pilot_diameters']) == 4 and max(params['pilot_diameters']) < boss['outer_diameter'] - 2
    centers = boss_centers(pi5)
    w, t = rail['width'], rail['thickness']
    height = t + boss['height_above_rail']
    solids = [rail_box(a, b, w, t) for a, b in zip(centers, centers[1:] + centers[:1])]
    solids += [Part.makeCylinder(boss['outer_diameter'] / 2, height, V(x, y, 0)) for x, y in centers]
    x_mid, y_top, slots = tab_layout(params)
    solids.append(Part.makeBox(tab['width'], tab['length'] + 0.5, t,
                               V(x_mid - tab['width'] / 2, y_top - tab['length'], 0)))
    cutters = [Part.makeCylinder(d / 2, height + 2, V(x, y, -1))
               for d, (x, y) in zip(params['pilot_diameters'], centers)]
    cutters += [Part.makeBox(tab['slot_length'], tab['slot_width'], t + 2,
                             V(x - tab['slot_length'] / 2, y - tab['slot_width'] / 2, -1)) for x, y in slots]
    cutters += [Part.makeCylinder(mark['diameter'] / 2, mark['depth'] + 1, V(x, y, t - mark['depth']))
                for _, x, y in mark_layout(params)]
    body = solids[0].fuse(solids[1:]).cut(Part.makeCompound(cutters)).removeSplitter()
    return Part.Solid(body.Solids[0]) if len(body.Solids) == 1 else body


def inside(shape, x, y, z):
    return shape.isInside(V(x, y, z), 1e-6, True)


def validate(shape, params):
    """Geometry checks only: they do not establish printed size or physical fit."""
    pi5, rail, boss, tab, mark = (params[k] for k in ('pi5', 'rail', 'boss', 'tie_tab', 'index_mark'))
    assert shape.isValid() and len(shape.Solids) == 1, 'expected one valid solid'
    centers = boss_centers(pi5)
    assert math.isclose(centers[1][0] - centers[0][0], pi5['hole_pattern'][0])
    assert math.isclose(centers[3][1] - centers[0][1], pi5['hole_pattern'][1])
    z_boss = rail['thickness'] + boss['height_above_rail'] / 2
    holes = []
    for d, (x, y) in zip(params['pilot_diameters'], centers):
        assert not inside(shape, x, y, z_boss), 'pilot hole is blocked'
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            assert not inside(shape, x + dx * (d / 2 - PROBE), y + dy * (d / 2 - PROBE), z_boss)
            assert inside(shape, x + dx * (d / 2 + PROBE), y + dy * (d / 2 + PROBE), z_boss)
            assert inside(shape, x + dx * (boss['outer_diameter'] / 2 - PROBE),
                          y + dy * (boss['outer_diameter'] / 2 - PROBE), z_boss)
        holes.append({'center': [x, y], 'pilot_diameter': d})
    _, _, slots = tab_layout(params)
    z_rail = rail['thickness'] / 2
    for x, y in slots:
        assert not inside(shape, x, y, z_rail), 'tie slot is blocked'
        assert inside(shape, x + tab['slot_length'] / 2 + PROBE, y, z_rail)
        assert inside(shape, x, y + tab['slot_width'] / 2 + PROBE, z_rail)
    marks = mark_layout(params)
    for _, x, y in marks:
        assert not inside(shape, x, y, rail['thickness'] - mark['depth'] / 2), 'index mark missing'
        assert inside(shape, x, y, rail['thickness'] - mark['depth'] - PROBE)
    box = shape.BoundBox
    height = rail['thickness'] + boss['height_above_rail']
    assert math.isclose(box.ZMin, 0, abs_tol=1e-6) and math.isclose(box.ZMax, height, abs_tol=1e-6)
    return {'holes': holes, 'tie_slots': [list(s) for s in slots],
            'index_marks': [[n, x, y] for n, x, y in marks],
            'bounds_mm': [[box.XMin, box.YMin, box.ZMin], [box.XMax, box.YMax, box.ZMax]],
            'volume_mm3': shape.Volume, 'solids': len(shape.Solids), 'valid': shape.isValid()}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--run', required=True, help='new run name under generated/ultraskelly/fit-coupon/')
    args = parser.parse_args()
    source = HERE / 'fit-coupon.json'
    params = json.loads(source.read_text(encoding='utf-8'))
    folder = cadkit.run_folder('fit-coupon', args.run)
    shape = build(params)
    checks = validate(shape, params)
    doc = App.newDocument('UltraSkellyFitCoupon')
    try:
        part = doc.addObject('Part::Feature', 'FitCoupon')
        part.Label = 'Pi 5 fit coupon'
        part.Shape = shape
        part.addProperty('App::PropertyString', 'Parameters', 'UltraSkelly', 'Source parameters (mm)')
        part.Parameters = json.dumps(params)
        doc.recompute()
        native = folder / 'fit-coupon.FCStd'
        native_sha = cadkit.save_verified(doc, native)
        mesh = cadkit.export_stl(shape, folder / 'fit-coupon.stl')
    finally:
        App.closeDocument(doc.Name)
    cadkit.write_report(folder / 'build-report.json', {
        'part': 'fit-coupon', 'run': args.run, 'units': 'mm',
        'parameters_sha256': cadkit.sha256(source),
        'native': {'path': native.name, 'sha256': native_sha}, 'stl': {'path': 'fit-coupon.stl', **mesh},
        'geometry_validation': checks,
        'not_established': ['printed dimensions', 'screw retention', 'physical fit on a Pi 5'],
    })
    print(json.dumps({'folder': str(folder), 'volume_mm3': round(checks['volume_mm3'], 1),
                      'bounds_mm': checks['bounds_mm'], 'stl_facets': mesh['facets']}))


if __name__ == '__main__':
    main()
