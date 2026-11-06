"""Render one image per printed part, each part alone on a grey bed square, as it is printed.

part_titles.py then adds a large name band above each image, so no text can overlap a part
or another label. Run in the live project FreeCAD window from the repository root, one call
per step so the window redraws between images:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py part_images build generated/ultraskelly/enclosure/r007
    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py part_images shot clamp-u
    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py part_images finish
    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/part_titles.py generated/ultraskelly/part-images/r007

`build` loads the STL files listed in the run's build report, after checking each against its
hash there. Images go to generated/ultraskelly/part-images/<run> for an enclosure run and to
part-images/<part>-<run> for other parts, such as part-images/splice-r001.
"""
import argparse
import json
from pathlib import Path

import FreeCAD as App
import Mesh
import Part

import cadkit

V = App.Vector
DOC = 'UltraSkellyPartImages'
BED = (0.84, 0.84, 0.86)
# STL stem: (name on the image, colour, direction from the part toward the camera, supports note)
PARTS = {
    'clamp-u': ('1  Clamp U', (0.95, 0.55, 0.15), (1.0, -0.9, 1.1), 'no supports'),
    'clamp-bar': ('2  Clamp bar', (0.95, 0.55, 0.15), (0.6, -1.0, 1.3), 'no supports'),
    'enclosure-back': ('3  Enclosure back', (0.3, 0.6, 0.85), (1.0, 0.9, 0.7), 'no supports, 5 mm brim'),
    'pi-carrier': ('4  Pi carrier', (0.72, 0.74, 0.78), (0.6, -1.0, 1.2), 'no supports'),
    'splice-u': ('1  Splice U', (0.95, 0.55, 0.15), (1.0, -0.9, 1.1), 'no supports'),
    'splice-bar': ('2  Splice bar, print 2', (0.95, 0.55, 0.15), (0.6, -1.0, 1.3), 'no supports'),
}


def state_file():
    return cadkit.GENERATED / 'part-images' / 'current.json'


def activate():
    import FreeCADGui as Gui
    view = Gui.getDocument(DOC).mdiViewsOfType('Gui::View3DInventor')[0]
    Gui.getMainWindow().setActiveWindow(view)
    App.setActiveDocument(DOC)
    Gui.ActiveDocument = Gui.getDocument(DOC)
    return view


def camera(view, look_from):
    back = V(*look_from).normalize()
    up = (V(0, 0, 1) - back * back.z).normalize()
    right = up.cross(back)
    axes = App.Matrix(right.x, up.x, back.x, 0, right.y, up.y, back.y, 0, right.z, up.z, back.z, 0, 0, 0, 0, 1)
    # An image saved during a camera animation shows a half-turned view, so animations stay off.
    App.ParamGet('User parameter:BaseApp/Preferences/View').SetBool('UseNavigationAnimations', False)
    view.setCameraType('Orthographic')
    view.setCameraOrientation(App.Placement(axes).Rotation)
    view.fitAll()  # hidden objects are ignored, so this fits the one part and its bed


def build(stl_folder):
    report = json.loads((stl_folder / 'build-report.json').read_text(encoding='utf-8'))
    stems = [name[:-len('.stl')] for name in report['prints']]
    unknown = [stem for stem in stems if stem not in PARTS]
    if unknown:
        raise ValueError(f'no image settings for {unknown}; add them to PARTS')
    run = stl_folder.name if report['part'] == 'enclosure' else f"{report['part']}-{stl_folder.name}"
    out = cadkit.GENERATED / 'part-images' / run
    out.mkdir(parents=True, exist_ok=False)
    if DOC in App.listDocuments():
        raise RuntimeError(f'{DOC} is already open; finish or close it first')
    doc = App.newDocument(DOC)
    titles = {}
    for stem in stems:
        title, color, _view, supports = PARTS[stem]
        path = stl_folder / f'{stem}.stl'
        sha = cadkit.sha256(path)
        if sha != report['prints'][path.name]['sha256']:
            raise ValueError(f'{path} differs from its build report')
        mesh = Mesh.Mesh(str(path))
        b = mesh.BoundBox
        obj = doc.addObject('Mesh::Feature', stem.replace('-', '_'))
        obj.Mesh = mesh
        obj.Label = title.replace('  ', ' ')
        bed = doc.addObject('Part::Feature', 'bed_' + obj.Name)
        bed.Shape = Part.makeBox(b.XLength + 30, b.YLength + 30, 1.0, V(b.XMin - 15, b.YMin - 15, -1.0))
        bed.Label = f'Print bed under {stem}'
        if App.GuiUp:
            obj.ViewObject.ShapeColor = color
            bed.ViewObject.ShapeColor = BED
        size = ' × '.join(f'{v:g}' for v in (round(b.XLength, 1), round(b.YLength, 1), round(b.ZLength, 1)))
        titles[f'{stem}.png'] = {'title': title, 'details': [f'{path.name}   ·   {size} mm',
                                                             f'Printed as shown, on the bed   ·   {supports}'],
                                 'stl_sha256': sha}
    doc.recompute()
    native_sha = cadkit.save_verified(doc, out / 'part-images.FCStd')
    (out / 'titles.json').write_text(json.dumps(titles, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    state_file().write_text(json.dumps({'folder': str(out), 'native_sha256': native_sha}), encoding='utf-8')
    print(out)


def shot(stem, width=1600):
    import FreeCADGui as Gui
    out = Path(json.loads(state_file().read_text(encoding='utf-8'))['folder'])
    doc = App.getDocument(DOC)
    view = activate()
    name = stem.replace('-', '_')
    for obj in doc.Objects:
        obj.Visibility = obj.Name in (name, 'bed_' + name)
    camera(view, PARTS[stem][2])
    Gui.updateGui()
    vw, vh = view.getSize()  # save at the window's aspect so the fitted view is not cropped
    k = width / vw
    path = out / f'{stem}-render.png'
    view.saveImage(str(path), round(vw * k), round(vh * k), 'White')
    print(path)


def finish():
    state = json.loads(state_file().read_text(encoding='utf-8'))
    doc = App.getDocument(DOC)
    for obj in doc.Objects:
        obj.Visibility = True
    sha = cadkit.save_verified(doc, Path(state['folder']) / 'part-images.FCStd')
    App.closeDocument(DOC)
    print(json.dumps({'saved': state['folder'], 'native_sha256': sha}))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='step', required=True)
    sub.add_parser('build').add_argument('stl_folder', type=Path)
    sub.add_parser('shot').add_argument('stem', choices=sorted(PARTS))
    sub.add_parser('finish')
    args = parser.parse_args(argv)
    if args.step == 'build':
        build(cadkit.ROOT / args.stl_folder)
    elif args.step == 'shot':
        shot(args.stem)
    else:
        finish()


if __name__ == '__main__':
    main()
