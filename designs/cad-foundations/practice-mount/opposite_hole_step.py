"""Add the opposite hole to the current model and save a separate milestone."""
from pathlib import Path
import runpy
import FreeCAD as App
import FreeCADGui as Gui


def main():
    folder = Path(__file__).resolve().parent
    target = folder / 'checkpoints' / '05-opposite-hole.FCStd'
    assert not target.exists(), 'Preserve existing checkpoint.'
    functions = runpy.run_path(str(folder / 'model.py'))
    doc = App.getDocument('PracticeMount')
    gui_doc = Gui.getDocument(doc.Name)
    if gui_doc.getInEdit():
        gui_doc.resetEdit()
    functions['add_opposite_hole'](doc)
    doc.MountingHole.Visibility = False
    doc.MountingPocket.Visibility = True
    Gui.Selection.clearSelection()
    gui_doc.activeView().viewTop()
    gui_doc.activeView().fitAll()
    doc.saveAs(str(target))
    print('Two holes, centers:', [tuple(g.Center) for g in doc.MountingHole.Geometry])


if __name__ == '__main__':
    main()
