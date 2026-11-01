"""Reference-only sensor and pinhole frusta; no physical camera changes.

Projection equations: [@opencvCalibR02]. Mode defaults: [@pupilCoreEyeIntrinsics2026].
The email dimensions and all positioning assumptions live in optics-r01/parameters.json.
"""
from pathlib import Path
import json
import math

PARAMETERS = Path(__file__).parent / 'cameras/pupil-core-eye/optics-r01/parameters.json'


def parameters():
    return json.loads(PARAMETERS.read_text(encoding='utf-8'))


def field_angles(width, height, focal):
    if not all(math.isfinite(v) and v > 0 for v in (width, height, focal)):
        raise ValueError('Sensor dimensions and focal length must be finite and positive')
    return [math.degrees(2 * math.atan(v / (2 * focal))) for v in (width, height)]


def add_optics(document, sensor, direction, x_hint, name='CameraOptics', parent=None):
    """Place reference geometry in parent's coordinates (world if parent is None).

    The schematic projection center is f ahead of the inherited sensor datum.
    The original optical datum is never moved. All children are non-printing.
    """
    import FreeCAD as App
    import Part
    p = parameters()
    f = p['focal_length_mm']
    width, height = p['sensor_active_width_mm'], p['sensor_active_height_mm']
    angles = field_angles(width, height, f)
    depth = p['far_display_distance_mm']
    if not math.isfinite(depth) or depth <= 0:
        raise ValueError('Display depth must be finite and positive')
    if direction.Length < 1e-9:
        raise ValueError('Optical direction must be nonzero')
    z = App.Vector(direction).normalize()
    x = x_hint - z * x_hint.dot(z)
    if x.Length < 1e-9:
        raise ValueError('Sensor X hint must not be parallel to optical direction')
    x.normalize()
    y = z.cross(x).normalize()
    apex = sensor + z * f
    group = document.addObject('App::Part', name)
    group.Label = 'Optics R01 - primary 400 / comparison 192'
    if parent is not None:
        parent.addObject(group)

    def prop(obj, kind, key, value):
        obj.addProperty('App::Property' + kind, key, 'Optics reference')
        setattr(obj, key, value)

    for key, value in [('SensorCenter', sensor), ('ProjectionCenter', apex),
                       ('Direction', z), ('SensorX', x), ('SensorY', y)]:
        prop(group, 'Vector', key, value)
    for key, value in [('FocalLength', f), ('ActiveWidth192', width),
                       ('ActiveHeight192', height), ('DisplayDepth', depth)]:
        prop(group, 'Length', key, value)
    for key, value in [('HorizontalFOV192', angles[0]), ('VerticalFOV192', angles[1])]:
        prop(group, 'Angle', key, value)
    prop(group, 'String', 'Evidence', 'User-transcribed Pupil Labs email, received 2026-10-30; optics-r01/parameters.json')
    prop(group, 'String', 'Assumptions', json.dumps(p['assumptions']))
    prop(group, 'String', 'Revision', p['revision'])
    prop(group, 'String', 'PreferredMode', '400 x 400 @ 120 Hz (conditional Cam2 optics)')
    prop(group, 'Bool', 'ExportForPrinting', False)

    def rectangle(center, w, h):
        return [center + x * (sx*w/2) + y * (sy*h/2)
                for sx, sy in [(-1,-1), (1,-1), (1,1), (-1,1)]]

    def feature(suffix, label, shape, color, visible=True):
        obj = document.addObject('Part::Feature', name + suffix)
        obj.Label, obj.Shape = label, shape
        prop(obj, 'Bool', 'ExportForPrinting', False)
        group.addObject(obj)
        if App.GuiUp:
            obj.ViewObject.ShapeColor = color
            obj.ViewObject.LineColor = color
            obj.ViewObject.LineWidth = 2.0
            obj.ViewObject.Visibility = visible
        return obj

    corners = rectangle(sensor, width, height)
    sensor_obj = feature('_Sensor192', '192 sensor active area - 1.15 x 1.15 mm (nominal position)',
                         Part.Face(Part.makePolygon(corners + corners[:1])), (0.1, .85, .95))
    focal_obj = feature('_FocalLength', '1.7 mm focal-length schematic - not measured lens spacing',
                        Part.makeLine(sensor, apex), (1., .15, .75))

    def frustum(suffix, w, h, label, color, visible):
        far = rectangle(apex + z * depth, depth*w/f, depth*h/f)
        edges = [Part.makeLine(apex, point) for point in far]
        edges += [Part.makeLine(far[i], far[(i+1)%4]) for i in range(4)]
        obj = feature(suffix, label, Part.makeCompound(edges), color, visible)
        prop(obj, 'Angle', 'HorizontalFOV', field_angles(w, h, f)[0])
        prop(obj, 'Angle', 'VerticalFOV', field_angles(w, h, f)[1])
        prop(obj, 'Length', 'FarWidth', depth*w/f)
        prop(obj, 'Length', 'FarHeight', depth*h/f)
        return obj

    nominal = frustum('_Frustum192', width, height,
                      '192 x 192 @ 200 Hz - nominal 37.4 deg frustum', (0., .75, 1.), True)
    c = p['comparison_400']
    w400 = f*c['resolution_px'][0]/c['fx_px']
    h400 = f*c['resolution_px'][1]/c['fy_px']
    comparison = frustum('_Frustum400', w400, h400,
                         'PRIMARY 400 x 400 @ 120 Hz - CONDITIONAL Cam2 estimate', (1., .5, .05), True)
    if App.GuiUp:
        comparison.ViewObject.LineWidth = 3.0
    prop(comparison, 'String', 'Evidence', c['status'] + '; [@pupilCoreEyeIntrinsics2026]')
    for key, obj in [('SensorArea', sensor_obj), ('FocalLengthGuide', focal_obj),
                     ('Frustum192', nominal), ('Frustum400Comparison', comparison)]:
        prop(group, 'Link', key, obj)
    document.recompute()
    return group
