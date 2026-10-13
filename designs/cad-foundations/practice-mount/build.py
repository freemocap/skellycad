"""Run inside pinned FreeCAD GUI; preserves other open documents."""
from pathlib import Path
import json
import runpy
import FreeCAD as App
import FreeCADGui as Gui


def main():
    folder = Path(__file__).resolve().parent
    assert 'PracticeMount' not in App.listDocuments(), 'PracticeMount is already open; inspect before rebuilding.'
    parameters = json.loads((folder / 'parameters.json').read_text())
    create = runpy.run_path(str(folder / 'model.py'))['create_plate_sketch']
    doc = App.newDocument('PracticeMount')
    body, sketch = create(doc, parameters)
    Gui.activeDocument().activeView().viewTop()
    Gui.activeDocument().activeView().fitAll()
    checkpoints = folder / 'checkpoints'
    checkpoints.mkdir(exist_ok=True)
    target = checkpoints / '01-constrained-outline.FCStd'
    assert not target.exists(), 'Preserve existing checkpoint.'
    doc.saveAs(str(target))
    Gui.activeDocument().setEdit(sketch.Name)
    Gui.activeDocument().activeView().fitAll()
    print('40 x 24 mm closed rectangle; fully constrained; lower-left corner fixed to origin. Sketch edit mode open.')


if __name__ == '__main__':
    main()
