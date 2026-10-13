"""Apply the single Pocket lesson to the existing practice plate."""
from pathlib import Path
import runpy
import FreeCAD as App
import FreeCADGui as Gui


def main():
    folder = Path(__file__).resolve().parent
    target = folder / 'checkpoints' / '04-through-hole.FCStd'
    assert not target.exists(), 'Preserve existing checkpoint.'
    doc = App.getDocument('PracticeMount')
    gui_doc = Gui.getDocument(doc.Name)
    if gui_doc.getInEdit():
        gui_doc.resetEdit()
    create = runpy.run_path(str(folder / 'model.py'))['add_mounting_pocket']
    pocket = create(doc, doc.PlateBody, doc.MountingHole)
    doc.recompute()
    Gui.Selection.clearSelection()
    gui_doc.activeView().viewAxonometric()
    gui_doc.activeView().fitAll()
    doc.saveAs(str(target))
    print('ThroughAll Pocket saved. Valid single solid; volume mm^3:', pocket.Shape.Volume)


if __name__ == '__main__':
    main()
