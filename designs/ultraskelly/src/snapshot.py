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
    parser.add_argument('--look-from', type=float, nargs=3, metavar=('X', 'Y', 'Z'),
                        help='camera direction from the model, for example -1 1 0.7 for rear left above')
    parser.add_argument('--fit', nargs='+', metavar='OBJECT', help='zoom to these object names after orienting')
    parser.add_argument('--size', type=int, nargs=2, default=[1600, 1000])
    args = parser.parse_args(argv)
    import FreeCADGui as Gui
    view = Gui.ActiveDocument.ActiveView
    if args.view:
        getattr(view, 'view' + args.view.capitalize())()
        view.fitAll()
    if args.look_from:
        # Camera axes: backward along the look-from direction, up as close to +Z as possible.
        back = App.Vector(*args.look_from).normalize()
        up = (App.Vector(0, 0, 1) - back * back.z).normalize()
        right = up.cross(back)
        axes = App.Matrix(right.x, up.x, back.x, 0, right.y, up.y, back.y, 0, right.z, up.z, back.z, 0, 0, 0, 0, 1)
        view.setCameraOrientation(App.Placement(axes).Rotation)
        view.fitAll()
    if args.fit:
        Gui.Selection.clearSelection()
        for name in args.fit:
            Gui.Selection.addSelection(App.ActiveDocument.getObject(name))
        Gui.SendMsgToActiveView('ViewSelection')
        Gui.Selection.clearSelection()
    target = (ROOT / args.path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    view.saveImage(str(target), *args.size, 'Current')
    print(target, App.ActiveDocument.Name)


if __name__ == '__main__':
    main()
