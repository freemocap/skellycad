"""Load the selected complete camera without changing historical mount recipes."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def checked_asset(record):
    path = (ROOT / record['path']).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Camera asset must be inside the repository')
    if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
        raise ValueError(f'Camera asset hash mismatch: {path}')
    return path


def selected_model():
    defaults = json.loads((HERE / 'cameras/defaults.json').read_text())
    path = (HERE / 'cameras' / defaults['selection']).resolve()
    if not path.is_relative_to(HERE / 'cameras'):
        raise ValueError('Camera selection must be inside the camera library')
    model = json.loads(path.read_text())
    if model['units'] != 'mm' or model['schema_version'] != 1:
        raise ValueError('Expected camera schema 1 with millimetre units')
    checked_asset(model['native_checkpoint'])
    for record in model['parts'].values():
        checked_asset(record)
    return model


def add_camera(document, name='PupilCoreEye', placement=None):
    """Return an App::Part with four material regions and its optical datum.

    Placement maps the saved R08 print frame into the caller's assembly frame.
    All geometry and datum properties are local to the returned group.
    """
    import FreeCAD as App
    import Part

    model = selected_model()
    shapes = {}
    for key, record in model['parts'].items():
        shape = Part.Shape()
        shape.read(str(checked_asset(record)))
        if not shape.isValid() or not shape.Solids:
            raise ValueError(f'Invalid selected camera part: {key}')
        shapes[key] = shape
    group = document.addObject('App::Part', name)
    group.Label = 'Pupil Labs eye camera — ' + model['revision']
    group.addProperty('App::PropertyString', 'Checkpoint').Checkpoint = model['revision']
    group.addProperty('App::PropertyString', 'Units').Units = 'mm'
    physical = []
    for key, record in model['parts'].items():
        obj = document.addObject('Part::Feature', name + '_' + key)
        obj.Label = key
        obj.Shape = shapes[key]
        obj.addProperty('App::PropertyString', 'Material').Material = record['material']
        obj.addProperty('App::PropertyInteger', 'Tool').Tool = record['tool']
        obj.addProperty('App::PropertyBool', 'ExportForPrinting').ExportForPrinting = True
        group.addObject(obj)
        physical.append(obj)
        if App.GuiUp:
            obj.ViewObject.ShapeColor = tuple(record['color_rgb'])
            obj.ViewObject.Visibility = True
    datum = model['optical_datum']
    origin = App.Vector(*datum['origin_mm'])
    direction = App.Vector(*datum['direction'])
    sensor = App.Vector(*datum['sensor_center_mm'])
    axis = document.addObject('Part::Feature', name + '_OpticalAxis')
    axis.Label = 'Optical axis / sensor normal — reference only'
    tip = origin + direction * 14
    axis.Shape = Part.makeCompound([
        Part.makeLine(origin, tip),
        Part.makeLine(tip, tip - direction * 1.2 + App.Vector(.55, 0, 0)),
        Part.makeLine(tip, tip - direction * 1.2 - App.Vector(.55, 0, 0)),
    ])
    for key, value in [('Origin', origin), ('Direction', direction), ('SensorCenter', sensor)]:
        axis.addProperty('App::PropertyVector', key, 'Optical datum')
        setattr(axis, key, value)
    axis.addProperty('App::PropertyBool', 'ExportForPrinting').ExportForPrinting = False
    axis.addProperty('App::PropertyLink', 'LensComponent').LensComponent = physical[1]
    group.addObject(axis)
    frame = document.addObject('Part::Feature', name + '_SensorFrame')
    frame.Placement = App.Placement(sensor, App.Rotation())
    frame.addProperty('App::PropertyBool', 'ExportForPrinting').ExportForPrinting = False
    group.addObject(frame)
    group.addProperty('App::PropertyLinkList', 'PhysicalParts').PhysicalParts = physical
    group.addProperty('App::PropertyLink', 'OpticalAxis').OpticalAxis = axis
    group.addProperty('App::PropertyLink', 'SensorFrame').SensorFrame = frame
    if placement is not None:
        group.Placement = placement
    if App.GuiUp:
        group.ViewObject.Visibility = True
        axis.ViewObject.LineColor = (0.0, .65, .95)
        axis.ViewObject.LineWidth = 3
    document.recompute()
    return group
