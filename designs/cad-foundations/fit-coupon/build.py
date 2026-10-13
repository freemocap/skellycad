"""Build a separate fit coupon in the pinned FreeCAD GUI."""
from pathlib import Path
import json
import runpy
import FreeCAD as App
import FreeCADGui as Gui


def main():
    folder = Path(__file__).resolve().parent
    target = folder / 'checkpoints' / '01-clearance-coupon.FCStd'
    assert not target.exists() and 'FitCoupon' not in App.listDocuments()
    params = json.loads((folder / 'parameters.json').read_text())
    model = runpy.run_path(str(folder / 'model.py'))
    doc = App.newDocument('FitCoupon')
    doc.Label = 'Fit coupon - clearance study'
    model['build_coupon'](doc, params)
    view = Gui.getDocument(doc.Name).activeView()
    view.viewTop()
    view.fitAll()
    target.parent.mkdir(exist_ok=True)
    doc.saveAs(str(target))
    print('Saved 36 x 16 x 4 mm coupon. Left-to-right hole diameters:',
          [2 * doc.getObject(f'Hole{i}').Radius.Value for i in range(1, 4)])


if __name__ == '__main__':
    main()
