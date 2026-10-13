"""Exercise relocated CAD workflows in a hidden GUI process without RPC."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import sys
import traceback
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'generated/verification'
OUT.mkdir(parents=True, exist_ok=True)
os.environ['CAD_PLAYGROUND_ROOT'] = str(ROOT)
Gui.showMainWindow()
Gui.getMainWindow().hide()
app = QtWidgets.QApplication.instance()
app.setQuitOnLastWindowClosed(False)
exit_code = 1


def verify():
    global exit_code
    report = {'passed': False, 'freecad': App.Version(), 'course': [], 'parts': {}}
    try:
        course = runpy.run_path(str(ROOT / 'designs/cad-foundations/replay.py'))
        for lesson in course['STAGES']:
            doc = course['main'](lesson)
            report['course'].append({'lesson': lesson, 'file': Path(doc.FileName).relative_to(ROOT).as_posix()})
            App.closeDocument(doc.Name)
        mouse = ROOT / 'designs/eye-tracker/mouse'
        manifest = json.loads((mouse / 'active-model.json').read_text())
        checkpoint = ROOT / manifest['native_checkpoint']
        assert hashlib.sha256(checkpoint.read_bytes()).hexdigest() == manifest['native_sha256']
        rebuilt = runpy.run_path(str(mouse / 'build.py'))['doc']
        baseline = App.openDocument(str(checkpoint))
        for name in manifest['parts'].values():
            a, b = rebuilt.getObject(name).Shape, baseline.getObject(name).Shape
            delta = a.cut(b).Volume + b.cut(a).Volume
            assert a.isValid() and len(a.Solids) == 1
            assert delta < 1e-6, (name, delta)
            report['parts'][name] = {'symmetric_difference_mm3': delta, 'volume_mm3': a.Volume}
        for name in ('Skull', 'Eye1', 'Eye2'):
            a, b = rebuilt.getObject(name), baseline.getObject(name)
            assert a.Mesh.Topology == b.Mesh.Topology, name
            assert a.Placement == b.Placement, name
        report['anatomy_unchanged'] = True
        runpy.run_path(str(mouse / 'export_print.py'))
        assert hashlib.sha256(checkpoint.read_bytes()).hexdigest() == manifest['native_sha256']
        report['checkpoint_unchanged'] = True
        report['revision'] = manifest['revision']
        report['passed'] = True
        exit_code = 0
    except Exception:
        report['error'] = traceback.format_exc()
        print(report['error'], flush=True)
    finally:
        (OUT / 'cad.json').write_text(json.dumps(report, indent=2) + '\n')
        for name in list(App.listDocuments()):
            App.closeDocument(name)
        print('CAD_WORKSPACE_OK' if report['passed'] else 'CAD_WORKSPACE_FAILED', flush=True)
        app.quit()


QtCore.QTimer.singleShot(0, verify)
app.exec()
sys.exit(exit_code)
