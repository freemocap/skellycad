"""Build the independent R01 enclosure concept with the pinned FreeCAD Python."""
from pathlib import Path
import json
import hashlib
import zipfile
import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtWidgets, QtCore
import sys
import traceback
import os

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'generated/enclosure/starter-cube-r01'
OUT.mkdir(parents=True, exist_ok=True)
V = App.Vector
Gui.showMainWindow()
Gui.getMainWindow().hide()
app = QtWidgets.QApplication.instance()
app.setQuitOnLastWindowClosed(False)
exit_code = 1

def build():
    doc = App.newDocument('StarterCubeR01')
    doc.Label = 'Enclosure R01 - 500 mm clear cube - CONCEPT'
    groups = {}
    for name in ('Frame', 'Connectors', 'CameraMounts', 'CameraEnvelopes'):
        groups[name] = doc.addObject('App::DocumentObjectGroup', name)
    frame = []

    def add(name, shape, group, color, note):
        obj = doc.addObject('PartDesign::Feature', name)
        obj.Shape = shape
        obj.addProperty('App::PropertyString', 'DesignNote').DesignNote = note
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = (0.18, 0.20, 0.23)
        groups[group].addObject(obj)
        return obj

    def extrusion(name, start, direction, length):
        # Nominal 20 mm envelope with illustrative T-slots, not a supplier die drawing.
        s = Part.makeBox(20, 20, length, V(-10, -10, 0))
        slot = Part.makeBox(5, 3, length, V(-2.5, 7, 0)).fuse(
            Part.makeBox(7, 3, length, V(-3.5, 4, 0)))
        for angle in (0, 90, 180, 270):
            cut = slot.copy()
            cut.rotate(V(), V(0, 0, 1), angle)
            s = s.cut(cut)
        s = s.cut(Part.makeCylinder(2.1, length))
        s.Placement = App.Placement(V(*start), App.Rotation(V(0, 0, 1), V(*direction)))
        obj = add(name, s, 'Frame', (0.73, 0.76, 0.79), 'Nominal 2020; slot internals illustrative. Units: mm.')
        obj.addProperty('App::PropertyLength', 'CutLength').CutLength = length
        frame.append(obj)
        return obj

    def bracket(name, origin, u, w):
        # Local x points along rail, local z toward free space, y spans its width.
        u, w = V(*u), V(*w)
        v = w.cross(u)
        rot = App.Rotation(u, v, w, 'ZXY')
        s = Part.makeBox(20, 18, 3, V(0, -9, 0)).fuse(Part.makeBox(3, 18, 20, V(0, -9, 0)))
        s = s.cut(Part.makeCylinder(2.7, 3, V(12, 0, 0)))
        s = s.cut(Part.makeCylinder(2.7, 3, V(0, 0, 12), V(1, 0, 0)))
        s.Placement = App.Placement(V(*origin), rot)
        return add(name, s, 'Connectors', (0.32, 0.37, 0.42), 'Concept L-bracket with nominal M5 clearance holes; select matching 20-series kit.')

    for x in (10, 530):
        for y in (10, 530):
            extrusion(f'Post_{x}_{y}', (x, y, 0), (0, 0, 1), 540)
    for z in (10, 530):
        inward = 1 if z == 10 else -1
        face = z + 10 * inward
        for y in (10, 530):
            extrusion(f'RailX_{y}_{z}', (20, y, z), (1, 0, 0), 500)
            for x, ux in ((20, 1), (520, -1)):
                bracket(f'JointX_{x}_{y}_{z}', (x, y, face), (ux, 0, 0), (0, 0, inward))
        for x in (10, 530):
            extrusion(f'RailY_{x}_{z}', (x, 20, z), (0, 1, 0), 500)
            for y, uy in ((20, 1), (520, -1)):
                bracket(f'JointY_{x}_{y}_{z}', (x, y, face), (0, uy, 0), (0, 0, inward))
    extrusion('TopCenterCrossbar', (270, 20, 530), (0, 1, 0), 500)
    for y, uy in ((20, 1), (520, -1)):
        bracket(f'CrossbarJoint_{y}', (270, y, 520), (0, uy, 0), (0, 0, -1))

    def camera(name, center, target):
        # Generic environment camera proxy, not a head-mounted eye camera.
        s = Part.makeBox(34, 28, 24, V(-17, -14, -24))
        s = s.fuse(Part.makeCylinder(9, 12))
        s.Placement = App.Placement(V(*center), App.Rotation(V(0, 0, 1), V(*target) - V(*center)))
        return add(name, s, 'CameraEnvelopes', (0.10, 0.32, 0.45), 'Generic camera envelope only; lens direction points to arena center. No specified sensor or FOV.')

    for x in (10, 530):
        for y in (10, 530):
            sign = 1 if x == 10 else -1
            # Upright plate bolts into two points on one inward-facing vertical slot.
            plate_x = 20 if sign == 1 else 516
            s = Part.makeBox(4, 20, 40, V(plate_x, y-10, 300))
            for z in (308, 332):
                s = s.cut(Part.makeCylinder(2.7, 4, V(plate_x, y, z), V(1, 0, 0)))
            add(f'CameraPlate_{x}_{y}', s, 'CameraMounts', (0.85, 0.48, 0.13), '40 mm tall sliding plate; two slot fasteners. Hole centers 24 mm apart.')
            start = 24 if sign == 1 else 516
            arm = Part.makeCylinder(5, 38, V(start, y, 320), V(sign, 0, 0))
            arm = arm.fuse(Part.makeSphere(9, V(start + sign*38, y, 320)))
            add(f'CameraArm_{x}_{y}', arm, 'CameraMounts', (0.85, 0.48, 0.13), 'Short lockable ball-head concept; actual camera adapter TBD.')
            camera(f'CornerCamera_{x}_{y}', (start + sign*52, y, 320), (270, 270, 120))

    plate = Part.makeBox(20, 40, 4, V(260, 250, 516))
    for y in (258, 282):
        plate = plate.cut(Part.makeCylinder(2.7, 4, V(270, y, 516)))
    add('TopSlidingPlate', plate, 'CameraMounts', (0.85, 0.48, 0.13), 'Two slot fasteners; slide along crossbar. Center at x=y=270 mm.')
    add('TopCameraStem', Part.makeCylinder(5, 26, V(270, 270, 490)), 'CameraMounts', (0.85, 0.48, 0.13), 'Concept adapter; replace with compatible camera or hang-point hardware.')
    camera('TopCamera', (270, 270, 466), (270, 270, 20))
    doc.recompute()
    native = OUT / 'starter-cube-r01.FCStd'
    doc.saveAs(str(native))
    objects = [o for o in doc.Objects if o.TypeId == 'PartDesign::Feature']
    invalid = [(o.Name, o.Shape.isValid(), len(o.Shape.Solids)) for o in objects if not o.Shape.isValid() or len(o.Shape.Solids) != 1]
    assert not invalid, invalid
    overlaps = []
    for i, a in enumerate(frame):
        for b in frame[i+1:]:
            if a.Shape.common(b.Shape).Volume > 1e-6:
                overlaps.append([a.Name, b.Name])
    assert not overlaps, overlaps
    assert len(frame) == 13
    bb = Part.makeCompound([o.Shape for o in frame]).BoundBox
    assert all(abs(s - 540) < 1e-6 for s in (bb.XLength, bb.YLength, bb.ZLength))
    # Each illustrative bracket must meet both of its intended frame members.
    contacts = {}
    for joint in groups['Connectors'].Group:
        contacts[joint.Name] = [f.Name for f in frame if joint.Shape.distToShape(f.Shape)[0] < 1e-6]
        assert len(contacts[joint.Name]) == 2, (joint.Name, contacts[joint.Name])
    App.closeDocument(doc.Name)
    doc = App.openDocument(str(native))
    objects = [o for o in doc.Objects if o.TypeId == 'PartDesign::Feature']
    Gui.activateWorkbench('PartWorkbench')
    Gui.updateGui()
    view = Gui.activeDocument().activeView()
    rot = App.Rotation(V(), V(0, 0, 1), V(1, -1, 0.75), 'ZYX')
    pos = V(270, 270, 270) + rot.multVec(V(0, 0, 2000))
    axis = rot.Axis
    view.setCamera('#Inventor V2.1 ascii\nOrthographicCamera { position %s %s %s orientation %s %s %s %s nearDistance 1 farDistance 4000 focalDistance 2000 aspectRatio 1.272727 height 1000 }' % (pos.x, pos.y, pos.z, axis.x, axis.y, axis.z, rot.Angle))
    app.processEvents()
    Gui.activeDocument().activeView().saveImage(str(OUT / 'preview.png'), 1400, 1100, 'White')
    doc.save()
    Part.export(objects, str(OUT / 'starter-cube-r01.step'))
    App.closeDocument(doc.Name)
    with zipfile.ZipFile(native) as archive:
        assert archive.testzip() is None
        assert 'Document.xml' in archive.namelist()
    reopened = App.openDocument(str(native))
    assert all(o.Shape.isValid() for o in reopened.Objects if hasattr(o, 'Shape'))
    App.closeDocument(reopened.Name)
    report = {'revision': 'R01', 'lineage': 'New enclosure concept; no species checkpoint geometry used',
              'units': 'mm', 'clear_frame_opening': [500, 500, 500], 'outside_frame': [540, 540, 540],
              'extrusions': {'540_mm': 4, '500_mm': 9, 'total_mm': 6660},
              'solid_count': len(objects), 'valid_solids': True, 'frame_overlaps': overlaps,
              'bracket_frame_contacts': contacts, 'native_zip_integrity': True, 'reopen_valid': True,
              'sha256': hashlib.sha256(native.read_bytes()).hexdigest(),
              'limitations': ['Illustrative profile and connector details', 'Camera adapters and fasteners not selected',
                             'No load rating, optical coverage, physical fit or animal containment validation']}
    (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2), flush=True)


def run():
    global exit_code
    try:
        build()
        exit_code = 0
    except Exception:
        traceback.print_exc()
    finally:
        for name in list(App.listDocuments()):
            App.closeDocument(name)
        # Embedded Qt can hang during interpreter finalization after completion.
        os._exit(exit_code)

QtCore.QTimer.singleShot(0, run)
app.exec()
sys.exit(exit_code)
