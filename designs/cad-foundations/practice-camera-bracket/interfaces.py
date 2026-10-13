"""Fictional optical/cable interfaces; native expressions and a rear-stop notch."""
import FreeCAD as App


def reference(doc, kind, name, expressions):
    obj = doc.addObject(kind, name)
    doc.References.addObject(obj)
    for prop, expression in expressions.items():
        obj.setExpression(prop, expression)
    return obj


def create_interfaces(doc, params):
    assert doc.getObject('AccessibleBracket') is None
    dims = doc.Dimensions
    fields = [('LensRadius', 'lens_radius'), ('LensProjection', 'lens_projection'),
              ('LensCenterHeight', 'lens_center_height'), ('ViewSpaceLength', 'view_space_length'),
              ('ViewSpaceFarRadius', 'view_space_far_radius'), ('ConnectorX', 'connector_center_x'),
              ('ConnectorZ', 'connector_center_height'), ('ConnectorWidth', 'connector_width'),
              ('ConnectorHeight', 'connector_height'), ('ConnectorLength', 'connector_length'),
              ('PortClearance', 'port_clearance'), ('CableDiameter', 'cable_diameter'),
              ('CableSpaceLength', 'cable_space_length')]
    for name, key in fields:
        assert params[key] > 0
        dims.addProperty('App::PropertyLength', name, 'Fictional interfaces')
        setattr(dims, name, params[key])
    lens = reference(doc, 'Part::Cylinder', 'LensReference', {
        'Radius': 'Dimensions.LensRadius', 'Height': 'Dimensions.LensProjection',
        'Placement.Base.y': '-Dimensions.CameraDepth / 2',
        'Placement.Base.z': 'Dimensions.LensCenterHeight',
    })
    lens.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), 90)
    lens.Label = 'Fictional lens housing - front (-Y)'
    view = reference(doc, 'Part::Cone', 'ViewKeepOut', {
        'Radius1': 'Dimensions.LensRadius', 'Radius2': 'Dimensions.ViewSpaceFarRadius',
        'Height': 'Dimensions.ViewSpaceLength',
        'Placement.Base.y': '-Dimensions.CameraDepth / 2 - Dimensions.LensProjection',
        'Placement.Base.z': 'Dimensions.LensCenterHeight',
    })
    view.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), 90)
    view.Label = 'Viewing keep-out - illustrative, not calibrated optics'
    plug = reference(doc, 'Part::Box', 'ConnectorReference', {
        'Length': 'Dimensions.ConnectorWidth', 'Width': 'Dimensions.ConnectorLength',
        'Height': 'Dimensions.ConnectorHeight',
        'Placement.Base.x': 'Dimensions.ConnectorX - Dimensions.ConnectorWidth / 2',
        'Placement.Base.y': 'Dimensions.CameraDepth / 2',
        'Placement.Base.z': 'Dimensions.ConnectorZ - Dimensions.ConnectorHeight / 2',
    })
    plug.Label = 'Fictional rear connector'
    cable = reference(doc, 'Part::Cylinder', 'CableKeepOut', {
        'Radius': 'Dimensions.CableDiameter / 2 + Dimensions.PortClearance',
        'Height': 'Dimensions.CableSpaceLength',
        'Placement.Base.x': 'Dimensions.ConnectorX',
        'Placement.Base.y': 'Dimensions.CameraDepth / 2 + Dimensions.ConnectorLength',
        'Placement.Base.z': 'Dimensions.ConnectorZ',
    })
    cable.Placement.Rotation = App.Rotation(App.Vector(1, 0, 0), -90)
    cable.Label = 'Straight cable clearance - no bend model'
    notch = doc.addObject('Part::Box', 'ConnectorNotchTool')
    doc.PrintableParts.addObject(notch)
    for prop, expression in {
        'Length': 'Dimensions.ConnectorWidth + 2 * Dimensions.PortClearance',
        'Width': 'Dimensions.StopThickness + 2 * Dimensions.SideClearance',
        'Height': 'Dimensions.ConnectorHeight + 2 * Dimensions.PortClearance',
        'Placement.Base.x': 'Dimensions.ConnectorX - (Dimensions.ConnectorWidth / 2 + Dimensions.PortClearance)',
        'Placement.Base.y': 'Dimensions.CameraDepth / 2',
        'Placement.Base.z': 'Dimensions.ConnectorZ - (Dimensions.ConnectorHeight / 2 + Dimensions.PortClearance)',
    }.items():
        notch.setExpression(prop, expression)
    result = doc.addObject('Part::Cut', 'AccessibleBracket')
    doc.PrintableParts.addObject(result)
    result.Label = 'Bracket with rear connector notch'
    result.Base = doc.RetainedBracket
    result.Tool = notch
    result.Refine = True
    doc.recompute()
    validate_interfaces(doc)
    doc.RetainedBracket.Visibility = False
    notch.Visibility = False
    result.ViewObject.ShapeColor = (0.9, 0.65, 0.25)
    lens.ViewObject.ShapeColor = (0.2, 0.25, 0.3)
    view.ViewObject.ShapeColor = (0.3, 0.7, 0.95)
    view.ViewObject.Transparency = 88
    plug.ViewObject.ShapeColor = (0.25, 0.65, 0.3)
    cable.ViewObject.ShapeColor = (0.25, 0.65, 0.3)
    cable.ViewObject.Transparency = 80
    return result


def validate_interfaces(doc):
    shape = doc.AccessibleBracket.Shape
    assert shape.isValid() and len(shape.Solids) == 1
    assert doc.ConnectorReference.Shape.common(doc.RetainedBracket.Shape).Volume > 1, 'Notch should resolve the initial collision.'
    removed = doc.RetainedBracket.Shape.common(doc.ConnectorNotchTool.Shape).Volume
    assert removed > 0
    assert abs(shape.Volume - (doc.RetainedBracket.Shape.Volume - removed)) < 1e-6
    for item in (doc.LensReference, doc.ViewKeepOut, doc.ConnectorReference, doc.CableKeepOut):
        assert item.Shape.isValid() and len(item.Shape.Solids) == 1
        for obstruction in (doc.AccessibleBracket, doc.CameraEnvelope, doc.StrapReference,
                            doc.ScrewReference, doc.WasherReference, doc.DriverEnvelope):
            assert item.Shape.common(obstruction.Shape).Volume < 1e-7, f'{item.Name} intersects {obstruction.Name}'
    assert doc.ConnectorNotchTool.Shape.BoundBox.ZMin >= -1e-7, 'Keep the floor intact.'
    assert doc.ConnectorNotchTool.Shape.BoundBox.XMax < doc.Dimensions.InsideWidth.Value / 2
