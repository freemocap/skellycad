"""Regression checks for shared hardware composition and camera instancing."""
from pathlib import Path
import copy
import json
import sys
import traceback
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

ROOT = Path(__file__).resolve().parents[2]
EYE = ROOT / 'designs/eye-tracker'
sys.path.insert(0, str(EYE))
from shared.assembly import build_assembly, _hardware, _pose
from shared.validation import compare_mouse_baseline, validate_selected
from shared.model import export_selected

OUT = ROOT / 'generated/verification/shared'
OUT.mkdir(parents=True, exist_ok=True)
Gui.showMainWindow()
Gui.getMainWindow().hide()
app = QtWidgets.QApplication.instance()
app.setQuitOnLastWindowClosed(False)
exit_code = 1


def verify():
    global exit_code
    report = {'passed': False}
    try:
        mouse = build_assembly(EYE / 'mouse/assembly.json', ROOT / 'generated/eye-tracker/mouse/shared-r01')
        report['mouse'] = compare_mouse_baseline(mouse)
        validate_selected(mouse.document, mouse.manifest)
        export_selected(ROOT / 'generated/eye-tracker/mouse/shared-r01/manifest.json',
                        lambda doc: validate_selected(doc, mouse.manifest))
        # A spatial fixture, not a proposed rat design. Exercise two independent
        # instances and a world-camera role, including nonidentity rotation.
        config = copy.deepcopy(mouse.config)
        config['anatomy'] = str(EYE / 'mouse/anatomy.json')
        config.pop('baseline')
        config['label'] = 'TEST ONLY — two camera instance placement'
        config['revision'] = 'TEST-TWO-CAMERAS'
        second = copy.deepcopy(config['cameras'][0])
        second.update(id='world_secondary', role='world', label='World-camera role test', baseplate='second_mount',
                      placement={'translation_mm': [65, 20, -10], 'rotation_xyzw': [0, 0, 0.7071067811865476, 0.7071067811865476]})
        config['cameras'].append(second)
        config['baseplates'].append({'id': 'second_mount', 'label': 'Second placement test', 'placement': second['placement']})
        path = OUT / 'two-cameras.json'
        path.write_text(json.dumps(config))
        pair = build_assembly(path)
        assert len(pair.manifest['camera_instances']) == 2
        assert len(pair.manifest['parts']) == 10 and len(pair.manifest['print_groups']) == 8
        validate_selected(pair.document, pair.manifest)
        first, repeated = pair.manifest['camera_instances']
        inverse = _pose(second['placement']).inverse()
        for role in ('Carrier', 'Holder', 'Cap', 'Clip', 'ApproxPCB'):
            a = pair.document.getObject(first['objects'][role]).Shape
            b = pair.document.getObject(repeated['objects'][role]).Shape.copy()
            b.Placement = inverse.multiply(b.Placement)
            assert a.cut(b).Volume + b.cut(a).Volume < 1e-6, role
        report['independent_camera_instances'] = True
        # Bad configuration fails explicitly rather than silently choosing defaults.
        bad = copy.deepcopy(config)
        bad['cameras'][1]['id'] = bad['cameras'][0]['id']
        bad_path = OUT / 'invalid.json'
        bad_path.write_text(json.dumps(bad))
        try:
            build_assembly(bad_path)
        except ValueError as error:
            assert 'unique' in str(error)
        else:
            raise AssertionError('Duplicate camera identifiers were accepted')
        report['duplicate_id_rejected'] = True
        bad = copy.deepcopy(config)
        bad['cameras'][0]['placement']['rotation_xyzw'] = [0, 0, 0, 0]
        bad_path.write_text(json.dumps(bad))
        try:
            build_assembly(bad_path)
        except ValueError as error:
            assert 'unit length' in str(error)
        else:
            raise AssertionError('Invalid rotation was accepted')
        report['invalid_rotation_rejected'] = True
        report['passed'] = True
        exit_code = 0
    except Exception:
        report['error'] = traceback.format_exc()
        print(report['error'], flush=True)
    finally:
        (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
        for name in list(App.listDocuments()):
            App.closeDocument(name)
        print('SHARED_ASSEMBLY_OK' if report['passed'] else 'SHARED_ASSEMBLY_FAILED', flush=True)
        app.quit()


QtCore.QTimer.singleShot(0, verify)
app.exec()
sys.exit(exit_code)
