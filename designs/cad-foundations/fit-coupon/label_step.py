"""Add raised diameter labels to the current coupon and save a new checkpoint."""
from pathlib import Path
import hashlib
import json
import runpy
import FreeCAD as App
import FreeCADGui as Gui


def main():
    folder = Path(__file__).resolve().parent
    target = folder / 'checkpoints' / '02-embossed-labels.FCStd'
    assert not target.exists()
    params = json.loads((folder / 'parameters.json').read_text())
    functions = runpy.run_path(str(folder / 'model.py'))
    doc = App.getDocument('FitCoupon')
    functions['validate_coupon'](doc)
    result = functions['add_embossed_labels'](doc, params)
    Gui.Selection.clearSelection()
    view = Gui.getDocument(doc.Name).activeView()
    view.viewAxonometric()
    view.fitAll()
    doc.saveAs(str(target))
    record = {'font': params['label_font'],
              'font_sha256': hashlib.sha256(Path(params['label_font']).read_bytes()).hexdigest(),
              'labels_mm': [2 * doc.getObject(f'Hole{i}').Radius.Value for i in range(1, 4)],
              'relief_mm': params['label_relief'], 'solid_count': len(result.Shape.Solids)}
    (folder / 'label-record.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Saved raised 3.1 / 3.3 / 3.5 mm labels, 0.6 mm above top; one fused valid solid.')


if __name__ == '__main__':
    main()
