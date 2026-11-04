"""Neck clamp and quick-release enclosure for UltraSkelly's Pi 5 stack and PCA9685.

A U clamp and front bar stay on the square tube. The enclosure back is a light frame that
carries the Pi carrier (four standoffs on a frame), the Pi stack with its long axis along the
tube and the USB end up, and the PCA9685 on a side wing. It slides down onto the clamp's
dovetail and is locked by one M2.5 screw through the enclosure into the tongue, so the electronics lift
off without touching the clamp.
Every printed part prints without supports. Clamp frame and parameters are in enclosure.json.
Run live in the project FreeCAD window:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py enclosure --run r010
    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py enclosure --run r011 --lifted

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
CLAMP, BACK, CARRIER, STEEL, PIN = (0.95, 0.55, 0.15), (0.3, 0.6, 0.85), (0.72, 0.74, 0.78), (0.55, 0.57, 0.6), (0.8, 0.8, 0.82)


def prism(points, z0, z1):
    wire = Part.makePolygon([V(x, y, z0) for x, y in points] + [V(points[0][0], points[0][1], z0)])
    return Part.Face(wire).extrude(V(0, 0, z1 - z0))


def dovetail(x_a, width_a, x_b, width_b, z0, z1):
    """Prism between two widths at x_a and x_b, centered on Y = 0."""
    return prism([(x_a, -width_a / 2), (x_a, width_a / 2), (x_b, width_b / 2), (x_b, -width_b / 2)], z0, z1)


def gusset(x_wall, x_front, z_top, y0, y1):
    """45 degree chamfer under a ledge that sticks out from x_wall to x_front, so it prints without supports."""
    d = x_front - x_wall
    points = [V(x_wall, y0, z_top), V(x_front, y0, z_top), V(x_wall, y0, z_top - d), V(x_wall, y0, z_top)]
    return Part.Face(Part.makePolygon(points)).extrude(V(0, y1 - y0, 0))


def geometry(p):
    t, c, ch, pl, pi, w = p['tube'], p['clamp'], p['channel'], p['plate'], p['pi'], p['wing']
    t_min, t_max = t['range']
    half = t_max / 2 + t['clearance']  # pocket half-width: the largest tube in the range still slides in
    x_tube_back = -t['outside'] / 2  # the nominal tube is centred on the axis, its back face on the base (tight)
    g = {'half': half, 'H': c['height'], 'H_tongue': c['tongue_height'], 'x_tube_back': x_tube_back,
         'x_back': x_tube_back - c['base'],
         # The arms stop short of the smallest tube's front face, so the bar always bears on the tube.
         'x_arm_front': x_tube_back + t_min - c['takeup_min'],
         'y_out': half + c['arm'], 'x_bar': (t['outside'] / 2, t['outside'] / 2 + c['bar'])}
    g['x_block_front'] = g['x_back'] - ch['gap']
    g['x_plate_front'] = g['x_block_front'] - c['tongue_depth'] - ch['clearance'] - ch['floor']
    g['x_plate_back'] = g['x_plate_front'] - pl['thickness']
    g['block_w'] = c['tongue_tip'] + 2 * ch['clearance'] + 2 * ch['walls']
    g['z_block'] = (-ch['below'], c['tongue_height'] + ch['cap'])
    g['pin'] = (g['x_back'] - c['tongue_depth'] / 2, -ch['below'] / 2)
    # The clamp body and tongue start body_drop below the enclosure's seat datum, so the tongue reaches the
    # enclosure's pin hole and takes the lock screw, while the U still stands on one flat bottom.
    g['z_bed'] = -c['body_drop']
    g['bolt_z'] = [g['z_bed'] + z for z in c['bolt_heights']]
    g['bolt_y'] = half + c['bolt_y_inset']
    g['nut_slot_x'] = g['x_arm_front'] - c['nut_slot_setback'] - c['nut_slot']
    g['hole_end_x'] = g['x_back'] + c['bolt_hole_back_wall']  # blind: screws cannot reach the enclosure
    g['pca_x'] = g['x_plate_back'] + p['pca9685']['origin_x_from_plate']
    g['board'] = (pi['origin_y'], pi['origin_y'] + pi['board'][1], pi['origin_z'], pi['origin_z'] + pi['board'][0])
    g['wing_y'] = (w['y0'], w['y0'] + w['thickness'])
    y0, _y1, z0, z1 = g['board']
    g['plate'] = (y0 - pl['margin'], g['wing_y'][1], z0 - pl['margin'], z1 + pl['margin'])
    return g


def tongue_width(p, g, x):
    c = p['clamp']
    return c['tongue_root'] + (g['x_back'] - x) * (c['tongue_tip'] - c['tongue_root']) / c['tongue_depth']


def bed_fit_edges(shape, g):
    """Edges on the bed (z = 0) of the tube pocket and the dovetail tongue: the faces whose fit matters."""
    half, tol = g['half'], 1e-4
    picked = []
    for e in shape.Edges:
        if max(abs(v.Point.z - g['z_bed']) for v in e.Vertexes) > tol:
            continue
        m = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        pocket_side = abs(abs(m.y) - half) < tol and g['x_tube_back'] - tol <= m.x <= g['x_arm_front'] + tol
        pocket_back = abs(m.x - g['x_tube_back']) < tol and abs(m.y) <= half + tol
        tongue = m.x < g['x_back'] - tol
        if pocket_side or pocket_back or tongue:
            picked.append(e)
    return picked


def edges_along(shape, axis, keep):
    """Straight edges parallel to an axis (0 = X, 2 = Z) whose midpoint passes keep(midpoint)."""
    picked = []
    for e in shape.Edges:
        a, b = e.Vertexes[0].Point, e.Vertexes[-1].Point
        d = b - a
        if d.Length > 1e-6 and abs(abs([d.x, d.y, d.z][axis]) - d.Length) < 1e-6 and keep((a + b) * 0.5):
            picked.append(e)
    return picked


def clamp_u(p, g):
    c, half, H = p['clamp'], g['half'], g['H']
    zb = g['z_bed']
    outer = box(g['x_back'], g['x_arm_front'], -g['y_out'], g['y_out'], zb, zb + H)
    # Rounded outer corners: vertical edges print as walls, so the fillets need no support.
    outer = outer.makeFillet(c['corner_radius'], edges_along(outer, 2, lambda m: abs(abs(m.y) - g['y_out']) < 1e-6))
    body = outer.cut(box(g['x_tube_back'], g['x_arm_front'] + 1, -half, half, zb - 1, zb + H + 1))
    # The tongue reaches up to the enclosure's seat on its top and down to the bed, past the enclosure's pin
    # hole; above the clamp body it stands on its own.
    x_in, x_tip = g['x_back'] + 0.5, g['x_back'] - c['tongue_depth']
    body = body.fuse(dovetail(x_in, tongue_width(p, g, x_in), x_tip, c['tongue_tip'], zb, g['H_tongue'])).removeSplitter()
    # A 45 degree chamfer where the pocket and tongue meet the bed keeps the first layer's flare out of the fits.
    body = body.makeChamfer(c['bed_chamfer'], bed_fit_edges(body, g))
    cutters = []
    for s in (1, -1):
        for z in g['bolt_z']:
            # Blind holes from the arm front, deep enough for the screw lengths that validate() reports.
            cutters.append(Part.makeCylinder(c['bolt_clearance'] / 2, g['x_arm_front'] + 1 - g['hole_end_x'],
                                             V(g['x_arm_front'] + 1, s * g['bolt_y'], z), V(-1, 0, 0)))
            y_a, y_b = s * (g['bolt_y'] - c['nut_slot_inner']), s * (g['y_out'] + 1)
            cutters.append(box(g['nut_slot_x'], g['nut_slot_x'] + c['nut_slot'], min(y_a, y_b), max(y_a, y_b),
                               z - c['nut_flats'] / 2, z + c['nut_flats'] / 2))
    # Pilot across the tongue for the lock screw, in line with the enclosure's pin hole (behind the U, so it
    # only cuts the tongue).
    cutters.append(Part.makeCylinder(c['lock_pilot'] / 2, 2 * g['y_out'] + 2, V(g['pin'][0], -g['y_out'] - 1, g['pin'][1]), V(0, 1, 0)))
    body = body.cut(Part.makeCompound(cutters)).removeSplitter()
    return Part.Solid(body.Solids[0])


def clamp_bar(p, g):
    c, (x0, x1) = p['clamp'], g['x_bar']
    bar = box(x0, x1, -g['y_out'], g['y_out'], g['z_bed'], g['z_bed'] + g['H'])
    # Rounded corners seen from the front; these edges stand vertical when the bar prints flat.
    bar = bar.makeFillet(c['corner_radius'], edges_along(bar, 0, lambda m: True))
    cutters = []
    for s in (1, -1):
        for z in g['bolt_z']:
            cutters.append(Part.makeCylinder(c['bolt_clearance'] / 2, x1 - x0 + 2, V(x0 - 1, s * g['bolt_y'], z), V(1, 0, 0)))
            cutters.append(Part.makeCylinder(c['bolt_head'] / 2, c['bolt_head_depth'] + 1, V(x1 - c['bolt_head_depth'], s * g['bolt_y'], z), V(1, 0, 0)))
    return Part.Solid(bar.cut(Part.makeCompound(cutters)).removeSplitter().Solids[0])


def pi_matrix(p, g):
    """Pi-origin coordinates to the clamp frame: Pi x up, Pi y left, board normal toward the back."""
    pi = p['pi']
    return App.Matrix(0, 0, -1, g['x_plate_back'], 0, 1, 0, pi['origin_y'], 1, 0, 0, pi['origin_z'], 0, 0, 0, 1)


def pca_matrix(p, g, wing_outer):
    q = p['pca9685']
    return App.Matrix(0, 1, 0, g['pca_x'], 0, 0, 1, wing_outer + q['boss_length'], 1, 0, 0, q['origin_z'], 0, 0, 0, 1)


def pca_holes(p, g):
    q = p['pca9685']
    return [(g['pca_x'] + hy, q['origin_z'] + hx) for hx, hy in q['holes_local']]


def pi_holes(p):
    pi = p['pi']
    return [(pi['origin_y'] + y, pi['origin_z'] + x) for x, y in case_view.HOLES]


def carrier(p):
    """Pi carrier in Pi-origin coordinates: a rail frame on the plate with four standoffs up to the board."""
    cr, holes = p['carrier'], case_view.HOLES
    h, w, t = case_view.STANDOFF_TOP, cr['rail_width'], cr['rail_thickness']
    xs, ys = sorted({x for x, _ in holes}), sorted({y for _, y in holes})
    rails = [box(xs[0], xs[-1], y - w / 2, y + w / 2, 0, t) for y in ys]
    rails += [box(x - w / 2, x + w / 2, ys[0], ys[-1], 0, t) for x in xs]
    posts = [Part.makeCylinder(cr['standoff_diameter'] / 2, h, V(x, y, 0)) for x, y in holes]
    body = rails[0].fuse(rails[1:] + posts)
    bores = [Part.makeCylinder(cr['bore'] / 2, h + 2, V(x, y, -1)) for x, y in holes]
    body = body.cut(Part.makeCompound(bores)).removeSplitter()
    return Part.Solid(body.Solids[0])


def plate_windows(p, g):
    """Windows through the plate, leaving rails through the Pi screw rows, a border and the spine behind the block."""
    r, bw = p['plate']['rail'], g['block_w']
    y0, _y1, _z0, z1 = g['plate']
    rows = sorted({z for _, z in pi_holes(p)})
    bands = [(y0 + r, -bw / 2 - 1), (bw / 2 + 1, g['wing_y'][0] - r)]  # left and right of the spine
    spans = [(rows[0] + r, rows[1] - r), (rows[1] + r, z1 - r)]       # between the rows, and above the top row
    windows = [(ya, yb, za, zb) for ya, yb in bands for za, zb in spans]
    windows.append((-bw / 2 + r, bw / 2 - r, max(g['z_block'][1], rows[1]) + r, z1 - r))  # spine, above the block
    return [w for w in windows if w[1] - w[0] > 4 and w[3] - w[2] > 4]


def peaked(u0, u1, z0, z1):
    """Window outline (u, z) with a 45 degree peak instead of a flat top, so it prints without bridging."""
    rise = min((u1 - u0) / 2, z1 - z0)
    return [(u0, z0), (u1, z0), (u1, z1 - rise), ((u0 + u1) / 2, z1), (u0, z1 - rise)]


def plate_window(x0, x1, ya, yb, za, zb):
    points = [V(x0, y, z) for y, z in peaked(ya, yb, za, zb)]
    return Part.Face(Part.makePolygon(points + points[:1])).extrude(V(x1 - x0, 0, 0))


def wing_window_cutter(y0, y1, xa, xb, za, zb):
    points = [V(x, y0, z) for x, z in peaked(xa, xb, za, zb)]
    return Part.Face(Part.makePolygon(points + points[:1])).extrude(V(0, y1 - y0, 0))


def teardrop_boss(r, length, x, y0, z):
    """Horizontal boss along +Y with a 45 degree point underneath, so its underside needs no support."""
    k = r / 2 ** 0.5
    points = [V(x - k, y0, z - k), V(x + k, y0, z - k), V(x, y0, z - r * 2 ** 0.5)]
    point = Part.Face(Part.makePolygon(points + points[:1])).extrude(V(0, length, 0))
    return Part.makeCylinder(r, length, V(x, y0, z), V(0, 1, 0)).fuse(point)


def wing_window(p, g):
    """Window through the PCA9685 wing, inside its four bosses."""
    m = p['pca9685']['boss_diameter'] / 2 + p['wing']['margin']
    holes = pca_holes(p, g)
    xs, zs = sorted({x for x, _ in holes}), sorted({z for _, z in holes})
    return xs[0] + m, xs[-1] - m, zs[0] + m, zs[-1] - m


def enclosure_back(p, g):
    c, ch, pl, w, q = p['clamp'], p['channel'], p['plate'], p['wing'], p['pca9685']
    xf, xb = g['x_plate_front'], g['x_plate_back']
    y0, y1, z0, z1 = g['plate']
    yw0, yw1 = g['wing_y']
    bw, (zb0, zb1) = g['block_w'], g['z_block']
    x_wall = xf - 0.5
    drop = g['x_block_front'] - x_wall  # the 45 degree chamfer under the block is as tall as the block is deep
    holes = pca_holes(p, g)
    m = q['boss_diameter'] / 2 + w['margin']
    zw = (z0, max(z for _, z in holes) + m)  # the wing starts on the bed, so it needs no support
    tw = pl['tie_tab_width']
    solids = [box(xb, xf, y0, y1, z0, z1),
              box(xb, xf, -tw / 2, tw / 2, z1 - 1, z1 + pl['tie_tab']),
              box(x_wall, g['x_block_front'], -bw / 2, bw / 2, zb0, zb1),
              gusset(x_wall, g['x_block_front'], zb0, -bw / 2, bw / 2),
              box(xb - w['depth'], xb + 0.5, yw0, yw1, *zw)]
    solids += [teardrop_boss(q['boss_diameter'] / 2, q['boss_length'] + 0.5, x, yw1 - 0.5, z) for x, z in holes]
    body = solids[0].fuse(solids[1:])
    x_mouth, x_bottom = g['x_block_front'] + 1, g['x_back'] - c['tongue_depth'] - ch['clearance']
    cutters = [dovetail(x_mouth, tongue_width(p, g, x_mouth) + 2 * ch['clearance'], x_bottom,
                        tongue_width(p, g, x_bottom) + 2 * ch['clearance'], zb0 - drop - 1, g['H_tongue']),
               Part.makeCylinder(ch['pin_clearance'] / 2, bw + 2, V(g['pin'][0], -bw / 2 - 1, g['pin'][1]), V(0, 1, 0))]
    seat = pl['thickness'] - pl['head_seat']  # counterbore depth for the M2.5 heads on the front face
    for y, z in pi_holes(p):
        cutters += [Part.makeCylinder(1.5, pl['thickness'] + 2, V(xf + 1, y, z), V(-1, 0, 0)),
                    Part.makeCylinder(2.8, seat + 1, V(xf + 1, y, z), V(-1, 0, 0))]
    cb_d, cb_depth = q['pilot_counterbore']  # guides the screw and relieves the boss edge
    boss_end = yw1 + q['boss_length']
    for x, z in holes:
        cutters += [Part.makeCylinder(q['pilot'] / 2, w['thickness'] + q['boss_length'] + 2, V(x, yw0 - 1, z), V(0, 1, 0)),
                    Part.makeCylinder(cb_d / 2, cb_depth + 1, V(x, boss_end - cb_depth, z), V(0, 1, 0))]
    sw, sl = pl['tie_slot']
    for y in (-pl['tie_spacing'] / 2, pl['tie_spacing'] / 2):
        cutters.append(box(xb - 1, xf + 1, y - sw / 2, y + sw / 2, z1 + pl['tie_tab'] / 2 - sl / 2, z1 + pl['tie_tab'] / 2 + sl / 2))
    cutters += [plate_window(xb - 1, xf + 1, ya, yb, za, zb) for ya, yb, za, zb in plate_windows(p, g)]
    cutters.append(wing_window_cutter(yw0 - 1, yw1 + 1, *wing_window(p, g)))
    body = body.cut(Part.makeCompound(cutters)).removeSplitter()
    assert len(body.Solids) == 1, 'enclosure back is not one solid'
    return Part.Solid(body.Solids[0]), yw1


def inside(shape, x, y, z):
    return shape.isInside(V(x, y, z), 1e-6, True)


def validate(p, g, parts):
    """Geometry checks only: printed fit, clamp grip and latch feel are untested."""
    c, ch, half = p['clamp'], p['channel'], g['half']
    u, bar, back = parts['clamp_u'], parts['clamp_bar'], parts['enclosure_back']
    for name in ('clamp_u', 'clamp_bar', 'enclosure_back', 'carrier'):
        assert parts[name].isValid() and len(parts[name].Solids) == 1, f'{name} is not one valid solid'
    zm = g['z_bed'] + g['H'] / 2
    assert not inside(u, 0, 0, zm), 'tube passage blocked'
    for s in (1, -1):
        assert not inside(u, g['x_tube_back'] + 0.05, s * (half - 0.05), zm), 'pocket narrower than the largest tube'
    for z in (zm, g['H_tongue'] - 1):
        assert inside(u, g['x_back'] - c['tongue_depth'] / 2, 0, z), 'dovetail tongue missing'
    t_min, t_max = p['tube']['range']
    assert g['x_arm_front'] < g['x_tube_back'] + t_min, 'arms reach the front face of the smallest tube'
    for s in (1, -1):
        for z in g['bolt_z']:
            y = s * g['bolt_y']
            assert not inside(u, g['x_arm_front'] - 1, y, z) and not inside(bar, g['x_bar'][0] + 1, y, z), 'bolt hole missing'
            assert not inside(u, g['hole_end_x'] + 0.5, y, z), 'bolt hole too short'
            assert inside(u, g['hole_end_x'] - 1, y, z), 'bolt hole runs past its depth'
            assert not inside(u, g['nut_slot_x'] + c['nut_slot'] / 2, s * (g['bolt_y'] + 2), z), 'nut slot missing'
    # Screw lengths across the tube range, clamped: the tip passes the nut by 1.5 mm on the largest tube and
    # stops 1.5 mm short of the hole end on the smallest.
    head = lambda t: g['x_tube_back'] + t + c['bar'] - c['bolt_head_depth']
    nut_back = g['nut_slot_x'] + c['nut_slot'] - c['nut_thickness']
    screws = (round(head(t_max) - nut_back + 1.5, 1), round(head(t_min) - g['hole_end_x'] - 1.5, 1))
    assert screws[0] < screws[1], f'no clamp screw length fits: {screws}'
    zb0 = g['z_block'][0]
    assert not inside(back, g['x_back'] - c['tongue_depth'] / 2, 0, g['H_tongue'] / 2), 'channel blocked'
    assert not inside(back, g['x_back'] - c['tongue_depth'] / 2, 0, zb0 - 2), 'channel closed below the block'
    assert inside(back, g['x_plate_front'] + 0.5, g['block_w'] / 2 - 1, zb0 - 1.5), 'chamfer under the block missing'
    assert not inside(back, g['pin'][0], 0, g['pin'][1]), 'lock pin hole blocked'
    # The lock screw passes the enclosure's pin hole in one wall and threads into the tongue's pilot.
    assert not inside(u, g['pin'][0], 0, g['pin'][1]), 'lock pilot missing in the tongue'
    assert g['pin'][1] - c['lock_pilot'] / 2 - g['z_bed'] >= 1.35, 'under three perimeters below the lock pilot'
    tongue_here = tongue_width(p, g, g['pin'][0])
    wall = g['block_w'] / 2 - (tongue_here / 2 + ch['clearance'])  # enclosure side wall at the pin
    lock_engagement = c['lock_screw'] - wall - ch['clearance']
    assert 2 * 2.5 <= lock_engagement < tongue_here - 1, f'lock screw engagement {lock_engagement:.1f} mm'
    for y, z in pi_holes(p):
        assert not inside(back, g['x_plate_back'] + 0.5, y, z), 'Pi screw hole missing'
        assert inside(back, g['x_plate_back'] + 0.5, y + (4.0 if y > 0 else -4.0), z), 'plate missing around a Pi screw'
    for ya, yb, za, zb in plate_windows(p, g):
        assert not inside(back, g['x_plate_back'] + 1.5, (ya + yb) / 2, (za + zb) / 2), 'plate window missing'
    for x, z in pca_holes(p, g):
        assert not inside(back, x, g['wing_y'][1] + 1, z), 'PCA9685 pilot missing'
        r = p['pca9685']['boss_diameter'] / 2
        assert inside(back, x, g['wing_y'][1] + 1, z - r * 1.2), 'teardrop under a PCA9685 boss missing'
    k = c['bed_chamfer']
    zk = g['z_bed'] + k / 3
    assert not inside(u, g['x_tube_back'] - k / 3, 0, zk), 'pocket edge on the bed not chamfered'
    assert not inside(u, g['x_back'] - c['tongue_depth'] + k / 3, 0, zk), 'tongue edge on the bed not chamfered'
    assert inside(u, g['x_tube_back'] - 2 * k, 0, zk), 'U base missing behind the pocket chamfer'
    clashes = {'clamp_u-back': u.common(back).Volume, 'clamp_u-bar': u.common(bar).Volume,
               'carrier-back': parts['carrier'].common(back).Volume, 'pca-back': parts['pca9685'].common(back).Volume}
    for name, volume in clashes.items():
        assert volume < 1e-3, f'{name} overlap {volume:.3f} mm3'
    return {'valid': True, 'clash_mm3': {k: round(v, 4) for k, v in clashes.items()},
            'volumes_mm3': {k: round(parts[k].Volume, 1) for k in ('clamp_u', 'clamp_bar', 'enclosure_back', 'carrier')},
            'clamp_screw_length_mm': list(screws), 'lock_screw_engagement_mm': round(lock_engagement, 1)}


def build(doc, p, dz=0.0, lift=0.0, tube=True):
    g = geometry(p)
    m = pi_matrix(p, g)
    local = carrier(p)
    carrier_shape = cadkit.moved(local, m)
    back, wing_outer = enclosure_back(p, g)
    pca = cadkit.moved(vendor.shape('pca9685-step'), pca_matrix(p, g, wing_outer))
    parts = {'clamp_u': clamp_u(p, g), 'clamp_bar': clamp_bar(p, g), 'enclosure_back': back,
             'carrier': carrier_shape, 'carrier_local': local, 'pca9685': pca}
    checks = validate(p, g, parts)
    up = V(0, 0, dz)
    lifted = V(0, 0, dz + lift)

    def add(name, shape, color, label, transparency=0, offset=up):
        shape = shape.copy()
        shape.translate(offset)
        return cadkit.add(doc, name, shape, color, transparency, label=label)

    add('ClampU', parts['clamp_u'], CLAMP, 'U clamp with dovetail (print)')
    add('ClampBar', parts['clamp_bar'], CLAMP, 'Clamp bar, 4 x M2.5 (print)')
    add('EnclosureBack', back, BACK, 'Enclosure back with dovetail channel and PCA9685 wing (print)', offset=lifted)
    add('PiCarrier', carrier_shape, CARRIER, 'Pi carrier: frame and four standoffs (print)', offset=lifted)
    z = case_view.stack_heights()
    for name, shape, height, color in (('Pi5', vendor.shape('pi5-step'), z['pi_z'], hardware_view.PCB_GREEN),
                                       ('AIHat', hardware_view.ai_hat(), z['ai_hat_bottom'], hardware_view.PCB_GREEN),
                                       ('MotorHat', vendor.shape('motor-hat-step'), z['motor_hat_bottom'], hardware_view.HAT_BLUE)):
        add(name, cadkit.moved(hardware_view.placed(shape, 0, 0, height), m), color, name, offset=lifted)
    add('PCA9685', pca, hardware_view.PCA_BLUE, 'PCA9685 on the side wing', offset=lifted)
    y_wall = -g['block_w'] / 2
    lock = Part.makeCylinder(1.25, p['clamp']['lock_screw'], V(g['pin'][0], y_wall, g['pin'][1]), V(0, 1, 0)).fuse(
        Part.makeCylinder(2.25, 2.5, V(g['pin'][0], y_wall - 2.5, g['pin'][1]), V(0, 1, 0)))
    add('LockPin', lock, PIN, f"M2.5 x {p['clamp']['lock_screw']} lock screw into the tongue", offset=lifted)
    if tube:
        w = p['tube']['outside'] / 2
        add('SpineTube', box(-w, w, -w, w, -60, 140), STEEL, f"Square tube, {p['tube']['outside']} mm", 40)
    return parts, checks


def print_shapes(parts):
    """Print orientation: clamp U standing, bar flat with its head recesses up, enclosure back on its lower end,
    Pi carrier flat with its standoffs up."""
    u = parts['clamp_u'].copy()
    bar = parts['clamp_bar'].copy()
    bar.rotate(V(0, 0, 0), V(0, 1, 0), -90)  # front face, with the screw-head recesses, faces up
    back = parts['enclosure_back'].copy()
    out = {'clamp-u.stl': u, 'clamp-bar.stl': bar, 'enclosure-back.stl': back, 'pi-carrier.stl': parts['carrier_local'].copy()}
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
        ours = [doc.getObject(n).Shape for n in ('ClampU', 'ClampBar', 'EnclosureBack', 'PiCarrier', 'MotorHat', 'PCA9685')]
        for other in ('Shoulders', 'NeckDrive', 'Skull', 'Jaw', 'Ribcage'):
            body = doc.getObject(other).Shape
            gaps[other] = round(min(shape.distToShape(body)[0] for shape in ours), 1)
    doc.recompute()
    native = folder / 'enclosure.FCStd'
    native_sha = cadkit.save_verified(doc, native)
    prints = {name: cadkit.export_stl(shape, folder / name) for name, shape in print_shapes(parts).items()}
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
