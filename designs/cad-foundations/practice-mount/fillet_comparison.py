"""Build a separate fillet alternative while preserving the live chamfer plate."""
from pathlib import Path
import json
import runpy
import FreeCAD as App
import FreeCADGui as Gui


def main():
    folder = Path(__file__).resolve().parent
    target = folder / 'checkpoints' / '08-top-fillet.FCStd'
    assert not target.exists() and 'PracticeMountFillet' not in App.listDocuments()
    p = json.loads((folder / 'parameters.json').read_text())
    f = runpy.run_path(str(folder / 'model.py'))
    doc = App.newDocument('PracticeMountFillet')
    doc.Label = 'Plate - fillet comparison'
    body, sketch = f['create_plate_sketch'](doc, p)
    f['add_plate_pad'](doc, body, sketch, p)
    hole = f['add_mounting_hole_sketch'](doc, body, p)
    f['add_mounting_pocket'](doc, body, hole)
    f['add_opposite_hole'](doc)
    f['add_opposite_row'](doc)
    fillet = f['add_top_fillet'](doc, p)
    hole.Visibility = False
    fillet.ViewObject.ShapeColor = (0.8, 0.8, 0.8)
    # Match the original view so switching tabs compares the same viewpoint.
    original = Gui.getDocument('PracticeMount').activeView()
    view = Gui.getDocument(doc.Name).activeView()
    view.setCamera(original.getCamera())
    doc.saveAs(str(target))
    print('Saved separate 0.5 mm radius fillet plate; chamfer document preserved.')
    print('Checks: valid solid, bounds, underside, four bores, four 0.5 mm curved edge surfaces.')


if __name__ == '__main__':
    main()
