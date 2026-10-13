"""Apply only the Pad lesson to the existing PracticeMount document."""
from pathlib import Path
import json
import runpy
import FreeCAD as App
import FreeCADGui as Gui


def main():
    folder = Path(__file__).resolve().parent
    target = folder / 'checkpoints' / '02-padded-plate.FCStd'
    assert not target.exists(), 'Preserve existing checkpoint.'
    params = json.loads((folder / 'parameters.json').read_text())
    doc = App.getDocument('PracticeMount')
    sketch = doc.PlateOutline
    assert abs(sketch.getDatum('PlateLength').Value - params['plate_length']) < 1e-7
    assert abs(sketch.getDatum('PlateWidth').Value - params['plate_width']) < 1e-7
    gui_doc = Gui.getDocument(doc.Name)
    if gui_doc.getInEdit():
        gui_doc.resetEdit()
    add_pad = runpy.run_path(str(folder / 'model.py'))['add_plate_pad']
    pad = add_pad(doc, doc.PlateBody, sketch, params)
    gui_doc.activeView().viewAxonometric()
    gui_doc.activeView().fitAll()
    doc.saveAs(str(target))
    print('Saved plate: 40 x 24 x 3 mm; one valid solid; volume:', pad.Shape.Volume)


if __name__ == '__main__':
    main()
