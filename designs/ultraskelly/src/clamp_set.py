"""Numbered clamp fit set for the R008 mount: five clamp U sizes and one bar that fits them all.

The tube measures 18.6 mm or so, so the set brackets it. Each U has a tube pocket 0.3 mm wider
than the last and fits tubes 0.3 to 0.9 mm narrower than its pocket (0.15 to 0.45 mm per side).
Every U keeps R008's screw positions, outer width and dovetail tongue, so one bar fits all five
and the printed enclosure back fits each U. Numbers are sunk into faces that print facing up.
Run in the live project FreeCAD window from the repository root:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py clamp_set build --run r001
    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py clamp_set shot --run r001

`build` lays the parts out on one plate in print orientation and exports one STL per part;
plate_files.py joins them into the plate STL and 3MF. `shot` renders the set with the numbers
shown dark for the image.
"""
import argparse
import copy
import json
from pathlib import Path

import FreeCAD as App
import Part

import cadkit
import enclosure

HERE = Path(__file__).resolve().parent
V = App.Vector
FONT = 'C:/Windows/Fonts/arialbd.ttf'
POCKETS = [18.9, 19.2, 19.5, 19.8, 20.1]  # tube pocket widths, numbered 1 to 5 from snug to loose
FIT = (0.3, 0.9)  # each U fits tubes this much narrower than its pocket: 0.15 to 0.45 mm per side
TEXT_SIZE, TEXT_DEPTH = 9.0, 0.6  # font size (digits about 6.5 mm tall, 1.3 mm strokes); 3 layers deep
GAP = 8.0  # between parts on the plate
DOC = 'UltraSkellyClampSet'
U_COLOR, BAR_COLOR, MARK = (0.95, 0.55, 0.15), (0.95, 0.55, 0.15), (0.1, 0.1, 0.1)


def variant_params(base, pocket):
    """R008 parameters with this pocket; arms and bolt inset absorb the change so bolts and outer width stay put."""
    p = copy.deepcopy(base)
    p['tube'].update({'outside': round(pocket - sum(FIT) / 2, 3), 'clearance': FIT[0] / 2,
                      'range': [round(pocket - FIT[1], 3), round(pocket - FIT[0], 3)]})
    g0 = enclosure.geometry(base)
    p['clamp']['arm'] = round(g0['y_out'] - pocket / 2, 4)
    p['clamp']['bolt_y_inset'] = round(g0['bolt_y'] - pocket / 2, 4)
    return p


def text_solid(text):
    """Text as a solid in its own frame: reads along +X, up +Y, centred, from z = -depth to z = +1."""
    faces = [Part.makeFace(wires, 'Part::FaceMakerBullseye') for wires in Part.makeWireString(text, FONT, TEXT_SIZE, 0) if wires]
    flat = Part.makeCompound(faces)
    c = flat.BoundBox.Center
    flat.translate(V(-c.x, -c.y, -TEXT_DEPTH))
    return flat.extrude(V(0, 0, TEXT_DEPTH + 1))


def numbered_u(p, g, label):
    u = enclosure.clamp_u(p, g)
    # On the +Y arm's top face, between the base and the nut slot, upright in a top view.
    x_c = (g['x_back'] + g['nut_slot_x']) / 2
    y_c = (g['half'] + g['y_out']) / 2
    cut = text_solid(label)
    cut.translate(V(x_c, y_c, g['H']))
    return u.cut(cut), u.common(cut)


def numbered_bar(p, g, label):
    bar = enclosure.clamp_bar(p, g)
    # On the front face between the screw rows; text x -> -Z, y -> +Y, out of the face -> +X, so it reads
    # normally from above once the bar lies flat with that face up.
    m = App.Matrix(0, 0, 1, g['x_bar'][1], 0, 1, 0, 0, -1, 0, 0, g['H'] / 2, 0, 0, 0, 1)
    cut = cadkit.moved(text_solid(label), m)
    return bar.cut(cut), bar.common(cut)


def print_pose(shape, part):
    """Print orientation: the U standing on its lower end, the bar flat with its front face up."""
    shape = shape.copy()
    if part == 'bar':
        shape.rotate(V(0, 0, 0), V(0, 1, 0), -90)
    return shape


def inside(shape, x, y, z):
    return shape.isInside(V(x, y, z), 1e-6, True)


def check_u(p, g, u, groove, base_g, pocket):
    c = p['clamp']
    t_min, t_max = p['tube']['range']
    for s in (1, -1):
        assert not inside(u, g['x_tube_back'] + 0.05, s * (pocket / 2 - 0.05), g['H'] / 2), 'pocket narrower than designed'
        assert inside(u, g['x_tube_back'] + 1, s * (pocket / 2 + 0.05), g['H'] / 2), 'pocket wider than designed'
        for z in c['bolt_heights']:
            assert not inside(u, g['x_arm_front'] - 1, s * g['bolt_y'], z), 'bolt hole missing'
            assert not inside(u, g['nut_slot_x'] + 1.5, s * (g['bolt_y'] + 2), z), 'nut slot missing'
    assert abs(g['bolt_y'] - base_g['bolt_y']) < 1e-6 and abs(g['y_out'] - base_g['y_out']) < 1e-6, 'bar would not fit'
    walls = {'nut_slot_to_pocket': g['bolt_y'] - 3.4 - g['half'], 'bolt_hole_to_pocket': g['bolt_y'] - c['bolt_clearance'] / 2 - g['half']}
    assert min(walls.values()) >= 1.35, f'wall under three perimeters: {walls}'
    assert g['x_arm_front'] < g['x_tube_back'] + t_min, 'arms reach the smallest tube front face'
    assert groove.Volume > 3.0, 'number missing'
    head = lambda t: g['x_tube_back'] + t + c['bar'] - c['bolt_head_depth']
    nut_back = g['nut_slot_x'] + c['nut_slot'] - c['nut_thickness']
    screws = (round(head(t_max) - nut_back + 1.5, 1), round(head(t_min) - g['hole_end_x'] - 1.5, 1))
    assert screws[0] < 16 < screws[1], f'M3 x 16 does not fit: {screws}'
    # The tongue must match R008's: same dovetail behind the U's back face.
    tongue = u.common(cadkit.box(g['x_back'] - c['tongue_depth'] - 1, g['x_back'] - 0.01, -20, 20, -1, g['H_tongue'] + 1))
    return {'walls_mm': {k: round(v, 2) for k, v in walls.items()}, 'm3_screw_length_mm': list(screws),
            'tongue_volume_mm3': round(tongue.Volume, 3), 'number_volume_mm3': round(groove.Volume, 2)}


def build(run):
    base = json.loads((HERE / 'enclosure.json').read_text(encoding='utf-8'))
    base_g = enclosure.geometry(base)
    folder = cadkit.run_folder('clamp-set', run)
    if DOC in App.listDocuments():
        raise RuntimeError(f'{DOC} is already open; close it first')
    doc = App.newDocument(DOC)
    parts, report, x = [], {'variants': {}}, 0.0
    for n, pocket in enumerate(POCKETS, start=1):
        p = variant_params(base, pocket)
        g = enclosure.geometry(p)
        u, groove = numbered_u(p, g, str(n))
        report['variants'][str(n)] = {'pocket_mm': pocket, 'fits_tube_mm': p['tube']['range'],
                                     'arm_mm': p['clamp']['arm'], **check_u(p, g, u, groove, base_g, pocket)}
        parts.append((f'clamp-u-{n}', print_pose(u, 'u'), print_pose(groove, 'u'), U_COLOR, f'Clamp U {n}, {pocket} mm pocket'))
    tongues = {v['tongue_volume_mm3'] for v in report['variants'].values()}
    assert len(tongues) == 1, f'tongues differ: {tongues}'
    bar, groove = numbered_bar(base, base_g, '1-5')
    assert groove.Volume > 3.0, 'bar number missing'
    parts.append(('clamp-bar-1-5', print_pose(bar, 'bar'), print_pose(groove, 'bar'), BAR_COLOR, 'Clamp bar for U 1 to 5'))
    # Lay the U's out in a row and the bar in front of them, every part on the bed (z = 0).
    prints, placed = {}, []
    for name, shape, groove, color, label in parts:
        b = shape.BoundBox
        if name.startswith('clamp-u'):
            at = V(x - b.XMin, -b.YMin, -b.ZMin)
        else:
            at = V(-b.XMin, -b.YMin - b.YLength - GAP, -b.ZMin)
        shape, groove = shape.copy(), groove.copy()
        shape.translate(at)
        groove.translate(at)
        if name.startswith('clamp-u'):
            x += b.XLength + GAP
        cadkit.add(doc, name.replace('-', '_'), shape, color, label=label)
        mark = cadkit.add(doc, 'mark_' + name.replace('-', '_'), groove, MARK, label=f'Number on {name} (engraved; shown dark)')
        if App.GuiUp:
            mark.ViewObject.Visibility = False
        prints[f'{name}.stl'] = cadkit.export_stl(shape, folder / f'{name}.stl')
        placed.append(name)
    doc.recompute()
    native_sha = cadkit.save_verified(doc, folder / 'clamp-set.FCStd')
    cadkit.write_report(folder / 'build-report.json', {
        'part': 'clamp-set', 'run': run, 'units': 'mm', 'parameters_sha256': cadkit.sha256(HERE / 'enclosure.json'),
        'pockets_mm': POCKETS, 'fit_window_mm': list(FIT), 'text': {'font': Path(FONT).name, 'size_mm': TEXT_SIZE, 'depth_mm': TEXT_DEPTH},
        'native': {'path': 'clamp-set.FCStd', 'sha256': native_sha}, 'prints': prints, 'checks': report,
        'bar_fits_all': True, 'status': 'Fit set for choosing a clamp U; geometry checks only.'})
    if App.GuiUp:
        cadkit.present(doc, 'isometric')
    print(json.dumps({'saved': str(folder), 'parts': placed, 'checks': report}))


def shot(run, width=1800):
    import FreeCADGui as Gui
    import part_images
    folder = cadkit.GENERATED / 'clamp-set' / run
    doc = App.getDocument(DOC)
    view = Gui.getDocument(DOC).mdiViewsOfType('Gui::View3DInventor')[0]
    Gui.getMainWindow().setActiveWindow(view)
    for obj in doc.Objects:
        obj.Visibility = True
    part_images.camera(view, (0.0, -0.45, 1.0))
    Gui.updateGui()
    vw, vh = view.getSize()
    k = width / vw
    view.saveImage(str(folder / 'clamp-fit-set-render.png'), round(vw * k), round(vh * k), 'White')
    for obj in doc.Objects:
        if obj.Name.startswith('mark_'):
            obj.Visibility = False
    cadkit.save_verified(doc, folder / 'clamp-set.FCStd')
    titles = {'clamp-fit-set.png': {'title': 'Clamp fit set: U 1 to 5 and one bar',
                                    'details': ['Tube pockets 18.9 to 20.1 mm in 0.3 mm steps  \u00b7  the bar fits every U',
                                                'Numbers are sunk 0.6 mm into the top faces (shown dark here)']}}
    (folder / 'titles.json').write_text(json.dumps(titles, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(folder / 'clamp-fit-set-render.png')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('step', choices=['build', 'shot'])
    parser.add_argument('--run', required=True)
    args = parser.parse_args(argv)
    build(args.run) if args.step == 'build' else shot(args.run)


if __name__ == '__main__':
    main()
