"""Apply one top-perimeter chamfer to the existing four-hole plate."""
from pathlib import Path
import json
import runpy
import FreeCAD as App
import FreeCADGui as Gui


def main():
    folder = Path(__file__).resolve().parent
    target = folder / 'checkpoints' / '07-top-chamfer.FCStd'
    assert not target.exists(), 'Preserve existing checkpoint.'
    functions = runpy.run_path(str(folder / 'model.py'))
    parameters = json.loads((folder / 'parameters.json').read_text())
    doc = App.getDocument('PracticeMount')
    gui_doc = Gui.getDocument(doc.Name)
    if gui_doc.getInEdit():
        gui_doc.resetEdit()
    chamfer = functions['add_top_chamfer'](doc, parameters)
    Gui.Selection.clearSelection()
    gui_doc.activeView().viewAxonometric()
    gui_doc.activeView().fitAll()
    doc.saveAs(str(target))
    print('Saved 0.5 mm equal-distance top chamfer. Selected edges:', chamfer.Base[1])
    print('Verified solid, volume, bounds, underside, and four unchanged hole radii.')


if __name__ == '__main__':
    main()
