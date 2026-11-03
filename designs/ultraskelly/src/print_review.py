"""Lay out a print checkpoint's STL files in one document, as they sit on the print bed.

Each file is checked against the SHA-256 in the checkpoint's manifest.json before it is shown.
Run live in the project FreeCAD window:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py print_review --checkpoint r005-neck-mount --run r002
"""
import argparse
import json
from pathlib import Path

import FreeCAD as App
import Mesh
import Part

import cadkit

PROJECT = Path(__file__).resolve().parents[1]
COLORS = [(0.95, 0.55, 0.15), (0.3, 0.6, 0.85), (0.88, 0.88, 0.9), (0.1, 0.35, 0.75)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--checkpoint', required=True, help='folder name under designs/ultraskelly/checkpoints/')
    parser.add_argument('--run', required=True, help='new run name under generated/ultraskelly/print-review/<checkpoint>/')
    parser.add_argument('--gap', type=float, default=15.0, help='spacing between parts on the bed, mm')
    parser.add_argument('--bed', type=float, default=270.0, help='square bed outline drawn for scale, mm')
    args = parser.parse_args(argv)
    checkpoint = PROJECT / 'checkpoints' / args.checkpoint
    manifest = json.loads((checkpoint / 'manifest.json').read_text(encoding='utf-8'))
    folder = cadkit.run_folder(f'print-review/{args.checkpoint}', args.run)
    cadkit.close_saved_runs(folder.parent)
    doc = App.newDocument('UltraSkellyPrints')
    x = 0.0
    for index, (name, info) in enumerate(manifest['parts'].items()):
        path = checkpoint / name
        if cadkit.sha256(path) != info['sha256']:
            raise ValueError(f'{path} differs from its manifest')
        mesh = Mesh.Mesh(str(path))
        box = mesh.BoundBox
        mesh.translate(x - box.XMin, -box.YMin, -box.ZMin)
        obj = doc.addObject('Mesh::Feature', Path(name).stem.replace('-', '_'))
        obj.Mesh = mesh
        obj.Label = f"{manifest['id']} {name}: {info['orientation']}"
        if App.GuiUp:
            obj.ViewObject.ShapeColor = COLORS[index % len(COLORS)]
        x += box.XLength + args.gap
    b = args.bed
    outline = Part.makePolygon([App.Vector(-10, -10, 0), App.Vector(b - 10, -10, 0), App.Vector(b - 10, b - 10, 0),
                                App.Vector(-10, b - 10, 0), App.Vector(-10, -10, 0)])
    cadkit.add(doc, 'BedOutline', outline, (0.6, 0.6, 0.6), label=f'{b:.0f} x {b:.0f} mm outline for scale', line_width=2)
    doc.recompute()
    native = folder / 'print-review.FCStd'
    native_sha = cadkit.save_verified(doc, native)
    cadkit.write_report(folder / 'build-report.json', {
        'part': 'print-review', 'checkpoint': manifest['id'], 'run': args.run,
        'native': {'path': native.name, 'sha256': native_sha}, 'files': {k: v['sha256'] for k, v in manifest['parts'].items()}})
    if App.GuiUp:
        cadkit.present(doc, 'isometric')
    else:
        App.closeDocument(doc.Name)
    print(json.dumps({'saved': str(native), 'parts': list(manifest['parts'])}))


if __name__ == '__main__':
    main()
