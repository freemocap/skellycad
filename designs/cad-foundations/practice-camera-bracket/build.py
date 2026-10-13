"""One GUI entry point; stages will be extended as the lessons progress."""
from pathlib import Path
import json
import runpy
import FreeCAD as App
import FreeCADGui as Gui


def main(stage='envelope', checkpoint=None, continue_existing=False):
    folder = Path(__file__).resolve().parent
    assert stage in ('envelope', 'cradle', 'slotted-tab', 'hardware', 'retention', 'interfaces', 'support', 'motion', 'access'), 'Stage not implemented yet.'
    if checkpoint is None:
        checkpoint = {'envelope': '01-camera-envelope.FCStd', 'cradle': '02-cradle.FCStd',
                      'slotted-tab': '03-slotted-tab.FCStd', 'hardware': '04-hardware-references.FCStd',
                      'retention': '05-retention.FCStd', 'interfaces': '06-lens-cable-access.FCStd', 'support': '07-support-assembly.FCStd',
                      'motion': '08-slide-and-pivot.FCStd', 'access': '11-nut-tool-access.FCStd'}[stage]
    assert Path(checkpoint).name == checkpoint and checkpoint.endswith('.FCStd')
    target = folder / 'checkpoints' / checkpoint
    assert not target.exists(), 'Choose a new checkpoint name; preserve existing files.'
    params = json.loads((folder / 'parameters.json').read_text())
    model = runpy.run_path(str(folder / 'model.py'))
    if continue_existing:
        doc = App.getDocument('PracticeCameraBracket')
    else:
        assert 'PracticeCameraBracket' not in App.listDocuments(), 'Inspect/save the open design before rebuilding.'
        doc = App.newDocument('PracticeCameraBracket')
    doc.openTransaction('Build ' + stage)
    try:
        model['build_stage'](doc, params, stage)
        doc.Label = 'Practice camera bracket - ' + stage
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise
    view = Gui.getDocument(doc.Name).activeView()
    view.viewAxonometric()
    view.fitAll()
    target.parent.mkdir(exist_ok=True)
    doc.saveAs(str(target))
    print('Saved stage:', stage, 'to', target)
    if stage == 'cradle':
        print('Cradle inside width:', doc.Dimensions.InsideWidth, 'side gaps:', doc.Dimensions.SideClearance)


if __name__ == '__main__':
    main()
