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
OUT = ROOT / 'generated/eye-tracker/shared/optics-r02'
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / 'designs/eye-tracker'))
from shared.camera import add_camera, selected_model
from shared.model import load_manifest
from shared.optics import add_optics, field_angles, mean_field_angles, parameters

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


def eye_surface_distances(doc, origin, direction):
    """Intersect the axis with existing anatomical triangles in world mm."""
    z = App.Vector(direction).normalize()
    result = {}
    for name in ('Eye1Cornea', 'Eye1Sclera'):
        obj = doc.getObject(name)
        if hasattr(obj, 'Mesh'):
            vertices, triangles = obj.Mesh.Topology
        else:
            vertices, triangles = obj.Shape.tessellate(.01)
        # Both topology APIs include the feature's own placement, not its parents.
        parent = obj.getGlobalPlacement().multiply(obj.Placement.inverse())
        vertices = [parent.multVec(App.Vector(v)) for v in vertices]
        hits = []
        for tri in triangles:
            a, b, c = (vertices[i] for i in tri)
            e1, e2 = b-a, c-a
            cross = z.cross(e2)
            det = e1.dot(cross)
            if abs(det) < 1e-12:
                continue
            tvec = origin-a
            u = tvec.dot(cross)/det
            q = tvec.cross(e1)
            v = z.dot(q)/det
            t = e2.dot(q)/det
            if u >= -1e-9 and v >= -1e-9 and u+v <= 1+1e-9 and t > 0:
                hits.append(t)
        result[name] = {'axis_intersections_mm': sorted(set(round(t, 6) for t in hits)),
                        'axial_vertex_range_mm': [min((v-origin).dot(z) for v in vertices),
                                                 max((v-origin).dot(z) for v in vertices)],
                        'triangle_count': len(triangles)}
    assert any(row['axis_intersections_mm'] for row in result.values()), 'Ray misses modeled eye surfaces'
    return result


def check_optics(group):
    p = parameters()
    assert abs(group.SensorArea.Shape.Area - group.EffectiveWidth.Value*group.EffectiveHeight.Value) < 1e-9
    assert abs(group.FocalLengthGuide.Shape.Length - 1.7) < 1e-9
    assert abs(group.Frustum.FarWidth.Value - 40*math.tan(math.radians(mean_field_angles(p)[0]/2))) < 1e-9
    assert len(group.Frustum.Shape.Edges) == 8
    assert abs(group.SensorX.dot(group.Direction)) < 1e-9
    assert abs(group.SensorX.cross(group.SensorY).dot(group.Direction)-1) < 1e-9
    assert abs((group.ProjectionCenter-group.SensorCenter).Length-1.7) < 1e-9
    assert 38.2 < group.HorizontalFOV.Value < 38.4
    for obj in [group] + list(group.Group):
        if obj.TypeId.startswith('App::Origin'):
            continue
        assert not obj.ExportForPrinting
        if hasattr(obj, 'Shape'):
            assert obj.Shape.isValid() and not obj.Shape.Solids
    assert group.Frustum.ViewObject.Visibility


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
    for suffix in ('FrustumMean',):
        obj = next(o for o in reopened.Objects if o.Name.endswith(suffix))
        assert obj.ViewObject.Visibility and not obj.ExportForPrinting
    App.closeDocument(reopened.Name)
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'zip_integrity': True,
            'reopened': True, 'preview': str(preview.relative_to(ROOT))}


def build():
    global exit_code
    report = {'passed': False, 'units': 'mm', 'revision': 'PUPIL-CORE-OPTICS-R02'}
    try:
        model = selected_model()
        assert model['revision'] == 'CAMERA-DUMMY-R08'
        report['camera_source'] = model['native_checkpoint']
        doc = App.newDocument('CameraOpticsR02')
        doc.Label = 'Pupil ribbon camera - optics R02 (nominal)'
        camera = add_camera(doc, optics=True)
        doc.saveAs(str(OUT / 'PUPIL-CAMERA-OPTICS-R02.FCStd'))
        check_optics(camera.Optics)
        # Confirm the overlay follows a translated and rotated whole camera.
        pose = App.Placement(App.Vector(12, -4, 9), App.Rotation(App.Vector(1, 2, 3), 35))
        camera.Placement = pose
        doc.recompute()
        assert (camera.Optics.getGlobalPlacement().multVec(camera.Optics.SensorCenter)
                - pose.multVec(camera.OpticalAxis.SensorCenter)).Length < 1e-8
        camera.Placement = App.Placement()
        doc.recompute()
        report['camera'] = save_review(doc, OUT/'PUPIL-CAMERA-OPTICS-R02.FCStd', OUT/'camera-preview.png')

        manifest, checkpoint = load_manifest(ROOT/'designs/eye-tracker/mouse/active-model.json')
        assert manifest['revision'] == 'ET-MOUSE-RAISED-TARGET-R19'
        report['mouse_source'] = {'path': manifest['native_checkpoint'], 'sha256': manifest['native_sha256']}
        path = OUT/'ET-MOUSE-R19-OPTICS-R02.FCStd'
        shutil.copy2(checkpoint, path)
        doc = App.openDocument(str(path))
        doc.Label = 'Mouse R19 + optics R02 - mean coverage estimate'
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
        report['eye_surfaces_from_schematic_projection_center'] = eye_surface_distances(doc, group.ProjectionCenter, direction)
        report['focus_status'] = 'Unknown: no measured focus distance, f-number, blur criterion or optical principal planes; mesh distances are not a focus validation'
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
        report['mean_fov_deg'] = mean_field_angles(p)
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
        print('OPTICS_R02_OK' if report['passed'] else 'OPTICS_R02_FAILED', flush=True)
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
