"""Save the live window's active 3D view as a PNG, optionally after changing the view.

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py snapshot generated/ultraskelly/view.png --view front
"""
import argparse
from pathlib import Path

import FreeCAD as App

ROOT = Path(__file__).resolve().parents[3]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('path', type=Path, help='PNG path, relative to the repository root')
    parser.add_argument('--view', help='isometric, front, top, right, ... (default: keep the current view)')
    parser.add_argument('--size', type=int, nargs=2, default=[1600, 1000])
    args = parser.parse_args(argv)
    import FreeCADGui as Gui
    view = Gui.ActiveDocument.ActiveView
    if args.view:
        getattr(view, 'view' + args.view.capitalize())()
        view.fitAll()
    target = (ROOT / args.path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    view.saveImage(str(target), *args.size, 'Current')
    print(target, App.ActiveDocument.Name)


if __name__ == '__main__':
    main()
