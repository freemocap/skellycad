"""Build and verify saved camera and mouse optics reviews in a hidden GUI process."""
from pathlib import Path
import hashlib
import json
import math
import os
import shutil
import sys
import traceback
import zipfile
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets

ROOT = Path(__file__).resolve().parents[6]
OUT = ROOT / 'generated/eye-tracker/shared/optics-r01'
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / 'designs/eye-tracker'))
from shared.camera import add_camera, selected_model
from shared.model import load_manifest
from shared.optics_r01 import add_optics, field_angles, parameters

Gui.showMainWindow()
Gui.getMainWindow().hide()
qtapp = QtWidgets.QApplication.instance()
qtapp.setQuitOnLastWindowClosed(False)
exit_code = 1


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integrity(path):
    with zipfile.ZipFile(path) as archive:
        assert 'Document.xml' in archive.namelist()
        assert archive.testzip() is None


def snapshot(doc):
    result = {}
    for obj in doc.Objects:
        if not hasattr(obj, 'getGlobalPlacement'):
            continue
        if hasattr(obj, 'Shape'):
            result[obj.Name] = {'brep': hashlib.sha256(obj.Shape.exportBrepToString().encode()).hexdigest(),
                                'placement': str(obj.getGlobalPlacement())}
        elif hasattr(obj, 'Mesh'):
            result[obj.Name] = {'topology': hashlib.sha256(repr(obj.Mesh.Topology).encode()).hexdigest(),
                                'placement': str(obj.getGlobalPlacement())}
    return result


def check_optics(group):
    p = parameters()
    assert abs(group.SensorArea.Shape.Area - 1.15**2) < 1e-9
    assert abs(group.FocalLengthGuide.Shape.Length - 1.7) < 1e-9
    assert abs(group.Frustum192.FarWidth.Value - 20*1.15/1.7) < 1e-9
    assert len(group.Frustum192.Shape.Edges) == 8
    assert abs(group.SensorX.dot(group.Direction)) < 1e-9
    assert abs(group.SensorX.cross(group.SensorY).dot(group.Direction)-1) < 1e-9
    assert abs((group.ProjectionCenter-group.SensorCenter).Length-1.7) < 1e-9
    assert 37.3 < group.HorizontalFOV192.Value < 37.5
    assert 39 < group.Frustum400Comparison.HorizontalFOV.Value < 39.3
    for obj in [group] + list(group.Group):
        if obj.TypeId.startswith('App::Origin'):
            continue
        assert not obj.ExportForPrinting
        if hasattr(obj, 'Shape'):
            assert obj.Shape.isValid() and not obj.Shape.Solids
    assert group.Frustum400Comparison.ViewObject.Visibility
    assert group.Frustum192.ViewObject.Visibility


def save_review(doc, path, preview):
    doc.recompute()
    App.setActiveDocument(doc.Name)
    Gui.setActiveDocument(doc.Name)
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    Gui.updateGui()
    doc.saveAs(str(path))
    integrity(path)
    Gui.activeDocument().activeView().saveImage(str(preview), 1400, 1000, 'White')
    App.closeDocument(doc.Name)
    reopened = App.openDocument(str(path))
    for suffix in ('Frustum192', 'Frustum400'):
        obj = next(o for o in reopened.Objects if o.Name.endswith(suffix))
        assert obj.ViewObject.Visibility and not obj.ExportForPrinting
    App.closeDocument(reopened.Name)
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'zip_integrity': True,
            'reopened': True, 'preview': str(preview.relative_to(ROOT))}


def build():
    global exit_code
    report = {'passed': False, 'units': 'mm', 'revision': 'PUPIL-CORE-OPTICS-R01'}
    try:
        model = selected_model()
        assert model['revision'] == 'CAMERA-DUMMY-R08'
        report['camera_source'] = model['native_checkpoint']
        doc = App.newDocument('CameraOpticsR01')
        doc.Label = 'Pupil ribbon camera - optics R01 (nominal)'
        camera = add_camera(doc, optics='r01')
        doc.saveAs(str(OUT / 'PUPIL-CAMERA-OPTICS-R01.FCStd'))
        check_optics(camera.Optics)
        # Confirm the overlay follows a translated and rotated whole camera.
        pose = App.Placement(App.Vector(12, -4, 9), App.Rotation(App.Vector(1, 2, 3), 35))
        camera.Placement = pose
        doc.recompute()
        assert (camera.Optics.getGlobalPlacement().multVec(camera.Optics.SensorCenter)
                - pose.multVec(camera.OpticalAxis.SensorCenter)).Length < 1e-8
        camera.Placement = App.Placement()
        doc.recompute()
        report['camera'] = save_review(doc, OUT/'PUPIL-CAMERA-OPTICS-R01.FCStd', OUT/'camera-preview.png')

        manifest, checkpoint = load_manifest(ROOT/'designs/eye-tracker/mouse/active-model.json')
        assert manifest['revision'] == 'ET-MOUSE-RAISED-TARGET-R19'
        report['mouse_source'] = {'path': manifest['native_checkpoint'], 'sha256': manifest['native_sha256']}
        path = OUT/'ET-MOUSE-R19-OPTICS-R01.FCStd'
        shutil.copy2(checkpoint, path)
        doc = App.openDocument(str(path))
        doc.Label = 'Mouse R19 + optics R01 - primary 400 / comparison 192'
        before = snapshot(doc)
        axis = doc.DetailedOpticalAxis
        placement = axis.getGlobalPlacement()
        sensor = placement.multVec(axis.SensorCenter)
        direction = placement.Rotation.multVec(axis.Direction)
        origin = placement.multVec(axis.Origin)
        x_hint = doc.M4_lens.getGlobalPlacement().Rotation.multVec(App.Vector(1, 0, 0))
        group = add_optics(doc, sensor, direction, x_hint, name='MouseCameraOptics')
        check_optics(group)
        after = snapshot(doc)
        assert all(after[k] == v for k, v in before.items()), 'Existing geometry or placement changed'
        assert (group.ProjectionCenter-origin).cross(direction).Length < 1e-7
        eye = doc.Eye1OpticalFrame.getGlobalPlacement().Base
        ray = eye-origin
        report['mouse_axis'] = {'origin_mm': list(origin), 'direction': list(direction),
                                'eye_center_miss_mm': ray.cross(direction).Length/direction.Length,
                                'eye_forward_mm': ray.dot(direction)/direction.Length,
                                'schematic_apex_shift_from_inherited_origin_mm': (group.ProjectionCenter-origin).Length}
        report['unchanged_mouse_shape_and_mesh_count'] = len(before)
        report['mouse'] = save_review(doc, path, OUT/'mouse-preview.png')
        assert sha(checkpoint) == manifest['native_sha256']
        selected_model()  # Recheck all source asset hashes after the build.
        for values in [(0, 1, 1), (1, -1, 1), (1, 1, float('nan'))]:
            try:
                field_angles(*values)
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid optical dimensions accepted')
        p = parameters()
        report['fov_192_email_deg'] = field_angles(1.15, 1.15, 1.7)
        c = p['comparison_400']
        report['fov_400_conditional_cam2_deg'] = [math.degrees(2*math.atan(200/c[k])) for k in ('fx_px', 'fy_px')]
        report.update(passed=True, source_hashes_preserved=True, transformed_camera_reference_verified=True,
                      physical_geometry_unchanged=True, calibrated_optics=False, physical_fit_verified=False)
        exit_code = 0
    except Exception:
        report['error'] = traceback.format_exc()
        print(report['error'], flush=True)
    finally:
        (OUT/'validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        for name in list(App.listDocuments()):
            App.closeDocument(name)
        print('OPTICS_R01_OK' if report['passed'] else 'OPTICS_R01_FAILED', flush=True)
        qtapp.quit()
        # Exit this dedicated process after saving and closing all documents.
        # Windows can otherwise retain FreeCAD's nested GUI event loop.
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(exit_code)


QtCore.QTimer.singleShot(0, build)
qtapp.exec()
# All task documents and files are closed above. Avoid a Windows Qt teardown hang
# in this dedicated process; never import this entry point into desktop FreeCAD.
sys.stdout.flush()
sys.stderr.flush()
os._exit(exit_code)
