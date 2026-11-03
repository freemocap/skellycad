"""Render each printed part of an earlier and a new set with one shared camera, for a before/after sheet.

Each pair is fitted together, then each part is saved alone, so both images of a pair are at
the same scale. compare_sheet.py then lays the pairs out with their names and grams. Run in
the live project FreeCAD window from the repository root, one call per step:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py compare_images build designs/ultraskelly/checkpoints/<earlier set> generated/ultraskelly/enclosure/<new run>
    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py compare_images shot clamp-u
    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py compare_images finish

`build` checks the earlier files against their checkpoint manifest and the new files against
their build report.
"""
import argparse
import json
from pathlib import Path

import FreeCAD as App
import Mesh
import Part

import cadkit
import part_images

V = App.Vector
DOC = 'UltraSkellyCompareImages'
OLD, NEW = (0.62, 0.64, 0.68), (0.95, 0.55, 0.15)
# new STL stem: earlier STL stem
PAIRS = {'clamp-u': 'clamp-u', 'clamp-bar': 'clamp-bar', 'enclosure-back': 'enclosure-back', 'pi-carrier': 'pi-case-30mm'}


def state_file():
    return cadkit.GENERATED / 'compare-images' / 'current.json'


def add_part(doc, name, path, color):
    mesh = Mesh.Mesh(str(path))
    b = mesh.BoundBox
    obj = doc.addObject('Mesh::Feature', name)
    obj.Mesh = mesh
    bed = doc.addObject('Part::Feature', 'bed_' + name)
    bed.Shape = Part.makeBox(b.XLength + 30, b.YLength + 30, 1.0, V(b.XMin - 15, b.YMin - 15, -1.0))
    if App.GuiUp:
        obj.ViewObject.ShapeColor = color
        bed.ViewObject.ShapeColor = part_images.BED


def build(old_folder, new_folder):
    manifest = json.loads((old_folder / 'manifest.json').read_text(encoding='utf-8'))
    report = json.loads((new_folder / 'build-report.json').read_text(encoding='utf-8'))
    out = cadkit.GENERATED / 'compare-images' / new_folder.name
    out.mkdir(parents=True, exist_ok=False)
    if DOC in App.listDocuments():
        raise RuntimeError(f'{DOC} is already open; finish or close it first')
    doc = App.newDocument(DOC)
    files = {}
    for new, old in PAIRS.items():
        old_path, new_path = old_folder / f'{old}.stl', new_folder / f'{new}.stl'
        if cadkit.sha256(old_path) != manifest['parts'][old_path.name]['sha256']:
            raise ValueError(f'{old_path} differs from its manifest')
        if cadkit.sha256(new_path) != report['prints'][new_path.name]['sha256']:
            raise ValueError(f'{new_path} differs from its build report')
        add_part(doc, 'old_' + new.replace('-', '_'), old_path, OLD)
        add_part(doc, 'new_' + new.replace('-', '_'), new_path, NEW)
        files[new] = {'old': {'path': str(old_path), 'sha256': cadkit.sha256(old_path)},
                      'new': {'path': str(new_path), 'sha256': cadkit.sha256(new_path)}}
    doc.recompute()
    cadkit.save_verified(doc, out / 'compare.FCStd')
    (out / 'files.json').write_text(json.dumps(files, indent=1) + '\n', encoding='utf-8')
    state_file().write_text(json.dumps({'folder': str(out)}), encoding='utf-8')
    print(out)


def shot(stem, width=1200):
    import FreeCADGui as Gui
    out = Path(json.loads(state_file().read_text(encoding='utf-8'))['folder'])
    doc = App.getDocument(DOC)
    view = Gui.getDocument(DOC).mdiViewsOfType('Gui::View3DInventor')[0]
    Gui.getMainWindow().setActiveWindow(view)
    name = stem.replace('-', '_')
    pair = {'old_' + name, 'new_' + name}
    for obj in doc.Objects:
        obj.Visibility = obj.Name in pair or obj.Name in {'bed_' + n for n in pair}
    part_images.camera(view, part_images.PARTS[stem][2])  # fits both parts of the pair: one scale for both
    for side in ('old', 'new'):
        for obj in doc.Objects:
            obj.Visibility = obj.Name in (f'{side}_{name}', f'bed_{side}_{name}')
        Gui.updateGui()
        vw, vh = view.getSize()
        k = width / vw
        path = out / f'{stem}-{side}.png'
        view.saveImage(str(path), round(vw * k), round(vh * k), 'White')
        print(path)


def finish():
    out = Path(json.loads(state_file().read_text(encoding='utf-8'))['folder'])
    doc = App.getDocument(DOC)
    for obj in doc.Objects:
        obj.Visibility = True
    sha = cadkit.save_verified(doc, out / 'compare.FCStd')
    App.closeDocument(DOC)
    print(json.dumps({'saved': str(out), 'native_sha256': sha}))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='step', required=True)
    b = sub.add_parser('build')
    b.add_argument('old_folder', type=Path)
    b.add_argument('new_folder', type=Path)
    sub.add_parser('shot').add_argument('stem', choices=sorted(PAIRS))
    sub.add_parser('finish')
    args = parser.parse_args(argv)
    if args.step == 'build':
        build(cadkit.ROOT / args.old_folder, cadkit.ROOT / args.new_folder)
    elif args.step == 'shot':
        shot(args.stem)
    else:
        finish()


if __name__ == '__main__':
    main()
