"""Create an exploded inspection document for a compatible camera/mount pair."""
from pathlib import Path
import json
from .assembly import HERE, ROOT, _hardware, _id


def build_catalog(camera_id='pupil-core-eye-inherited', mount_id='r10-monocular'):
    import FreeCAD as App
    import FreeCADGui as Gui
    camera = json.loads((HERE / 'cameras' / _id(camera_id) / 'camera.json').read_text())
    mount = json.loads((HERE / 'mounts' / _id(mount_id) / 'mount.json').read_text())
    if camera_id not in mount['compatible_cameras']:
        raise ValueError('Camera and mount preset are incompatible')
    shapes = _hardware(camera, mount)
    doc = App.newDocument('SharedHardware')
    doc.Label = 'Shared hardware — exploded inspection (not a print layout)'
    groups = [('Carrier', ['Carrier'], 0, (.2, .75, .8)),
              ('Sensor holder + clip', ['Holder', 'Clip'], 35, (.62, .45, .8)),
              ('Matching cap', ['Cap'], 60, (.85, .65, .2)),
              ('PCB fit reference', ['ApproxPCB'], 85, (.3, .8, .4))]
    for index, (label, names, offset, color) in enumerate(groups):
        group = doc.addObject('App::DocumentObjectGroup', 'Hardware' + str(index))
        group.Label = label
        for name in names:
            obj = doc.addObject('Part::Feature', name)
            shape = shapes[name].copy()
            shape.translate(App.Vector(offset, 0, 0))
            obj.Shape = shape
            obj.ViewObject.ShapeColor = (.85, .65, .2) if name == 'Clip' else color
            group.addObject(obj)
        note = doc.addObject('App::Annotation', 'Caption' + str(index))
        note.LabelText = [label]
        note.Position = App.Vector(offset, 0, -25)
        note.ViewObject.FontSize = 18
        note.ViewObject.TextColor = (.9, .9, .9)
        group.addObject(note)
    doc.recompute()
    App.setActiveDocument(doc.Name)
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    out = ROOT / 'generated/eye-tracker/shared'
    out.mkdir(parents=True, exist_ok=True)
    doc.saveAs(str(out / 'hardware-catalog.FCStd'))
    return doc
