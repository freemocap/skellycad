"""Add the opposite row, verify resizing, and save the four-hole milestone."""
from pathlib import Path
import json
import runpy
import FreeCAD as App
import FreeCADGui as Gui


def main():
    folder = Path(__file__).resolve().parent
    target = folder / 'checkpoints' / '06-four-holes.FCStd'
    assert not target.exists(), 'Preserve existing checkpoint.'
    functions = runpy.run_path(str(folder / 'model.py'))
    doc = App.getDocument('PracticeMount')
    gui_doc = Gui.getDocument(doc.Name)
    if gui_doc.getInEdit():
        gui_doc.resetEdit()
    functions['add_opposite_row'](doc)
    original = [doc.PlateOutline.getDatum(n).Value for n in ('PlateLength', 'PlateWidth')]
    thickness = doc.PlatePad.Length.Value
    results = []
    try:
        for length, width, height in [(40, 24, 3), (50, 24, 3), (40, 32, 3), (50, 32, 5)]:
            doc.PlateOutline.setDatum('PlateLength', App.Units.Quantity(f'{length} mm'))
            doc.PlateOutline.setDatum('PlateWidth', App.Units.Quantity(f'{width} mm'))
            doc.PlatePad.Length = height
            doc.recompute()
            functions['validate_four_holes'](doc)
            results.append({'dimensions_mm': [length, width, height], 'passed': True})
    finally:
        for name, value in zip(('PlateLength', 'PlateWidth'), original):
            doc.PlateOutline.setDatum(name, App.Units.Quantity(f'{value} mm'))
        doc.PlatePad.Length = thickness
        doc.recompute()
    functions['validate_four_holes'](doc)
    doc.MountingHole.Visibility = False
    doc.MountingPocket.Visibility = True
    Gui.Selection.clearSelection()
    gui_doc.activeView().viewTop()
    gui_doc.activeView().fitAll()
    doc.saveAs(str(target))
    root = next(p for p in folder.parents if (p / 'tools/cad/toolchain.json').is_file())
    out = root / 'generated' / 'practice-mount'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'four-hole-checks.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Four-hole checkpoint saved. Centers:', [tuple(g.Center) for g in doc.MountingHole.Geometry])
    print('Passed variants:', results)


if __name__ == '__main__':
    main()
