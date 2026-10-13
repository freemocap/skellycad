"""Add only the hole sketch to the existing practice plate, then inspect it."""
from pathlib import Path
import json
import runpy
import FreeCAD as App
import FreeCADGui as Gui


def main():
    folder = Path(__file__).resolve().parent
    target = folder / 'checkpoints' / '03-hole-outline.FCStd'
    assert not target.exists(), 'Preserve existing checkpoint.'
    params = json.loads((folder / 'parameters.json').read_text())
    doc = App.getDocument('PracticeMount')
    assert abs(doc.PlatePad.Length.Value - params['plate_thickness']) < 1e-7
    assert abs(doc.PlateOutline.getDatum('PlateLength').Value - params['plate_length']) < 1e-7
    assert abs(doc.PlateOutline.getDatum('PlateWidth').Value - params['plate_width']) < 1e-7
    gui_doc = Gui.getDocument(doc.Name)
    if gui_doc.getInEdit():
        gui_doc.resetEdit()
    make_hole = runpy.run_path(str(folder / 'model.py'))['add_mounting_hole_sketch']
    hole = make_hole(doc, doc.PlateBody, params)
    doc.PlateBody.Tip = doc.PlatePad
    doc.recompute()
    App.setActiveDocument(doc.Name)
    Gui.Selection.clearSelection()
    hole.ViewObject.LineColor = (1.0, 0.25, 0.1)
    hole.ViewObject.LineWidth = 4.0
    doc.PlatePad.Visibility = True
    hole.Visibility = True
    gui_doc.activeView().viewTop()
    gui_doc.activeView().fitAll()
    doc.saveAs(str(target))
    assert abs(doc.PlatePad.Shape.Volume - 2880) < 1e-6
    print('Saved hole outline: diameter 3.2 mm; center (6,6) mm; plane Z follows plate thickness. Plate not cut.')


if __name__ == '__main__':
    main()
