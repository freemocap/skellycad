"""Separate support and simplified nut; centered assembly, no joint solver."""
import FreeCAD as App


def create_support(doc, params):
    assert doc.getObject('SupportPlate') is None
    dims = doc.Dimensions
    assert abs(dims.ScrewOffset.Value) < 1e-7, 'Center the screw before assembling.'
    for name, key in [('SupportWidth', 'support_width'), ('SupportDepth', 'support_depth'),
                      ('SupportThickness', 'support_thickness'), ('SupportHole', 'support_hole_diameter'),
                      ('NutDiameter', 'nut_reference_diameter'), ('NutThickness', 'nut_reference_thickness')]:
        assert params[key] > 0
        dims.addProperty('App::PropertyLength', name, 'Support assembly')
        setattr(dims, name, params[key])
    group = doc.addObject('App::DocumentObjectGroup', 'SupportAssembly')
    group.Label = 'Separate support and reference nut'

    def primitive(kind, name, expressions):
        obj = doc.addObject(kind, name)
        group.addObject(obj)
        for prop, expr in expressions.items():
            obj.setExpression(prop, expr)
        return obj

    blank = primitive('Part::Box', 'SupportBlank', {
        'Length': 'Dimensions.SupportWidth', 'Width': 'Dimensions.SupportDepth',
        'Height': 'Dimensions.SupportThickness',
        'Placement.Base.x': '-Dimensions.SupportWidth / 2',
        'Placement.Base.y': 'Dimensions.SlotCenterY - Dimensions.SupportDepth / 2',
        'Placement.Base.z': '-Dimensions.FloorThickness - Dimensions.SupportThickness',
    })
    bore = primitive('Part::Cylinder', 'SupportBore', {
        'Radius': 'Dimensions.SupportHole / 2',
        'Height': 'Dimensions.SupportThickness + Dimensions.NutThickness + 2 mm',
        'Placement.Base.y': 'Dimensions.SlotCenterY',
        'Placement.Base.z': '-Dimensions.FloorThickness - Dimensions.SupportThickness - Dimensions.NutThickness - 1 mm',
    })
    support = doc.addObject('Part::Cut', 'SupportPlate')
    group.addObject(support)
    support.Base = blank
    support.Tool = bore
    support.Label = 'Separate support plate - clearance hole'
    nut_blank = primitive('Part::Cylinder', 'NutBlank', {
        'Radius': 'Dimensions.NutDiameter / 2', 'Height': 'Dimensions.NutThickness',
        'Placement.Base.y': 'Dimensions.SlotCenterY',
        'Placement.Base.z': '-Dimensions.FloorThickness - Dimensions.SupportThickness - Dimensions.NutThickness',
    })
    nut = doc.addObject('Part::Cut', 'NutReference')
    group.addObject(nut)
    nut.Base = nut_blank
    nut.Tool = bore
    nut.Label = 'Fictional nut envelope - no threads or wrench flats'
    doc.recompute()
    validate_support(doc)
    for obj in (blank, bore, nut_blank):
        obj.Visibility = False
    support.ViewObject.ShapeColor = (0.55, 0.6, 0.68)
    nut.ViewObject.ShapeColor = (0.3, 0.35, 0.4)
    return support


def validate_support(doc):
    dims = doc.Dimensions
    support, nut, bracket = doc.SupportPlate.Shape, doc.NutReference.Shape, doc.AccessibleBracket.Shape
    assert dims.ScrewDiameter.Value < dims.SupportHole.Value < dims.NutDiameter.Value
    for shape in (support, nut):
        assert shape.isValid() and len(shape.Solids) == 1
        for obj in (doc.AccessibleBracket, doc.ScrewReference, doc.CameraEnvelope,
                    doc.StrapReference, doc.ConnectorReference, doc.CableKeepOut):
            assert shape.common(obj.Shape).Volume < 1e-7
    assert support.common(nut).Volume < 1e-7
    assert abs(support.BoundBox.ZMax - bracket.BoundBox.ZMin) < 1e-7
    assert abs(nut.BoundBox.ZMax - support.BoundBox.ZMin) < 1e-7
    def contact_area(a, b, z):
        fa = [f for f in a.Faces if abs(f.BoundBox.ZMin-z)<1e-7 and abs(f.BoundBox.ZMax-z)<1e-7]
        fb = [f for f in b.Faces if abs(f.BoundBox.ZMin-z)<1e-7 and abs(f.BoundBox.ZMax-z)<1e-7]
        return sum(x.common(y).Area for x in fa for y in fb)
    assert contact_area(support, bracket, support.BoundBox.ZMax) > 20
    assert contact_area(nut, support, nut.BoundBox.ZMax) > 5
    protrusion = nut.BoundBox.ZMin - doc.ScrewReference.Shape.BoundBox.ZMin
    assert protrusion > 0, 'Screw must reach through the simplified nut.'
    return protrusion


MOVING_SOURCES = ('AccessibleBracket', 'CameraEnvelope', 'StrapReference',
                  'LensReference', 'ViewKeepOut', 'ConnectorReference', 'CableKeepOut')


def create_motion(doc):
    """Explicitly refreshed snapshots preserve the original feature graph."""
    assert doc.getObject('MotionStudy') is None
    assert abs(doc.Dimensions.ScrewOffset.Value) < 1e-7
    study = doc.addObject('App::DocumentObjectGroup', 'MotionStudy')
    study.Label = 'Motion study - copies; apply_pose refreshes them'
    study.addProperty('App::PropertyDistance', 'Slide', 'Pose')
    study.addProperty('App::PropertyAngle', 'Pivot', 'Pose')
    for name in MOVING_SOURCES:
        source = doc.getObject(name)
        copy = doc.addObject('Part::Feature', 'Moving' + name)
        copy.addProperty('App::PropertyLink', 'Source', 'Motion study')
        copy.Source = source
        copy.Label = 'Moving: ' + source.Label
        study.addObject(copy)
        copy.ViewObject.ShapeColor = source.ViewObject.ShapeColor
        copy.ViewObject.Transparency = source.ViewObject.Transparency
        source.Visibility = False
    apply_pose(doc, 0, 0)
    return study


def apply_pose(doc, slide_mm, pivot_deg):
    """Slide in bracket-local Y, then pivot about the fixed screw's Z axis."""
    dims = doc.Dimensions
    limit = (dims.SlotOverallLength.Value - dims.SlotWidth.Value) / 2
    assert abs(slide_mm) <= limit + 1e-7, 'Outside conservative slot travel.'
    assert abs(dims.ScrewOffset.Value) < 1e-7, 'Keep the screw fixed.'
    center = App.Vector(0, dims.SlotCenterY.Value, 0)
    shift = App.Vector(0, slide_mm, 0)
    rotation = App.Rotation(App.Vector(0, 0, 1), pivot_deg)
    translation = center + rotation.multVec(shift - center)
    transform = App.Placement(translation, rotation)
    for copy in doc.MotionStudy.Group:
        source_shape = copy.Source.Shape.copy()
        source_shape.Placement = transform.multiply(source_shape.Placement)
        copy.Shape = source_shape
    doc.MotionStudy.Slide = slide_mm
    doc.MotionStudy.Pivot = pivot_deg
    doc.recompute()
    validate_motion(doc)


def validate_motion(doc):
    fixed = (doc.SupportPlate, doc.NutReference, doc.ScrewReference,
             doc.WasherReference, doc.DriverEnvelope)
    for moving in doc.MotionStudy.Group:
        assert moving.Shape.isValid() and len(moving.Shape.Solids) == 1
        assert abs(moving.Shape.Volume - moving.Source.Shape.Volume) < 1e-6
        for obstacle in fixed:
            assert moving.Shape.common(obstacle.Shape).Volume < 1e-7, f'{moving.Name} hits {obstacle.Name}'
    def contact(a, b, z):
        fa = [f for f in a.Faces if abs(f.BoundBox.ZMin-z)<1e-7 and abs(f.BoundBox.ZMax-z)<1e-7]
        fb = [f for f in b.Faces if abs(f.BoundBox.ZMin-z)<1e-7 and abs(f.BoundBox.ZMax-z)<1e-7]
        return sum(x.common(y).Area for x in fa for y in fb)
    bracket = doc.MovingAccessibleBracket.Shape
    assert contact(bracket, doc.SupportPlate.Shape, -doc.Dimensions.FloorThickness.Value) > 20
    assert contact(bracket, doc.WasherReference.Shape, 0) > 1


def create_exploded_view(doc, step_mm):
    """Presentation copies of the centered clamp stack; not assembly motion."""
    assert step_mm > 0 and doc.getObject('ExplodedView') is None
    group = doc.addObject('App::DocumentObjectGroup', 'ExplodedView')
    group.Label = 'Exploded centered clamp stack - presentation only'
    group.addProperty('App::PropertyLength', 'SeparationStep', 'Presentation')
    group.SeparationStep = step_mm
    group.addProperty('App::PropertyLinkList', 'PreviouslyVisible', 'Presentation')
    group.PreviouslyVisible = [o for o in doc.Objects if hasattr(o, 'Shape')
                               and not o.isDerivedFrom('App::DocumentObjectGroup') and o.Visibility]
    layers = [('SupportPlate', 0), ('NutReference', -1),
              ('AccessibleBracket', 1), ('WasherReference', 2), ('ScrewReference', 3)]
    for name, layer in layers:
        source = doc.getObject(name)
        copy = doc.addObject('Part::Feature', 'Exploded' + name)
        group.addObject(copy)
        copy.addProperty('App::PropertyLink', 'Source', 'Presentation')
        copy.Source = source
        copy.Label = 'Exploded: ' + source.Label
        shape = source.Shape.copy()
        shape.translate(App.Vector(0, 0, layer * step_mm))
        copy.Shape = shape
        copy.ViewObject.ShapeColor = source.ViewObject.ShapeColor
        assert shape.isValid() and abs(shape.Volume-source.Shape.Volume) < 1e-6
    for original in group.PreviouslyVisible:
        original.Visibility = False
    enable_exploded_control(doc)
    doc.recompute()
    return group


def show_assembled_view(doc):
    """Set explicit leaf visibility; toggling groups can expose construction tools."""
    visible = {'SupportPlate', 'NutReference', 'ScrewReference', 'WasherReference',
               'DriverEnvelope', 'NutToolEnvelope'}
    visible.update('Moving' + name for name in MOVING_SOURCES)
    # Enable containers first, then correct their propagated child visibility.
    for name in ('References', 'SupportAssembly', 'MotionStudy'):
        doc.getObject(name).Visibility = True
    for obj in doc.Objects:
        if hasattr(obj, 'Shape') and not obj.isDerivedFrom('App::DocumentObjectGroup'):
            obj.Visibility = obj.Name in visible
    actual = {o.Name for o in doc.Objects if hasattr(o, 'Shape')
              and not o.isDerivedFrom('App::DocumentObjectGroup') and o.Visibility}
    assert actual == {name for name in visible if doc.getObject(name) is not None}


def enable_exploded_control(doc):
    """Native expressions make SeparationStep editable without callbacks."""
    controls = doc.getObject('ExplosionControls')
    if controls is None:
        controls = doc.addObject('App::FeaturePython', 'ExplosionControls')
        controls.Label = 'Explosion controls - edit Separation Step'
        controls.addProperty('App::PropertyLength', 'SeparationStep', 'Presentation')
        controls.SeparationStep = doc.ExplodedView.SeparationStep
    layers = {'SupportPlate': 0, 'NutReference': -1, 'AccessibleBracket': 1,
              'WasherReference': 2, 'ScrewReference': 3}
    for copy in doc.ExplodedView.Group:
        if 'Layer' not in copy.PropertiesList:
            copy.addProperty('App::PropertyInteger', 'Layer', 'Presentation')
            copy.addProperty('App::PropertyDistance', 'BaseZ', 'Presentation')
        copy.Layer = layers[copy.Source.Name]
        copy.BaseZ = copy.Source.Shape.Placement.Base.z
        copy.setExpression('Placement.Base.z', 'BaseZ + Layer * ExplosionControls.SeparationStep')
        copy.setEditorMode('Layer', 1)
        copy.setEditorMode('BaseZ', 1)
    if 'SeparationStep' in doc.ExplodedView.PropertiesList:
        doc.ExplodedView.removeProperty('SeparationStep')
    doc.recompute()


def create_nut_access(doc, params):
    """Fictional straight tool envelope; no actual socket engagement geometry."""
    assert doc.getObject('NutToolEnvelope') is None
    dims = doc.Dimensions
    for name, key in [('NutToolDiameter', 'nut_tool_diameter'), ('NutToolLength', 'nut_tool_length')]:
        assert params[key] > 0
        dims.addProperty('App::PropertyLength', name, 'Tool access')
        setattr(dims, name, params[key])
    tool = doc.addObject('Part::Cylinder', 'NutToolEnvelope')
    doc.References.addObject(tool)
    tool.Label = 'Lower tool clearance - fictional straight approach'
    tool.setExpression('Radius', 'Dimensions.NutToolDiameter / 2')
    tool.setExpression('Height', 'Dimensions.NutToolLength')
    tool.setExpression('Placement.Base.y', 'Dimensions.SlotCenterY')
    tool.setExpression('Placement.Base.z', '-Dimensions.FloorThickness - Dimensions.SupportThickness - Dimensions.NutToolLength')
    doc.recompute()
    validate_nut_access(doc)
    tool.ViewObject.ShapeColor = (0.85, 0.3, 0.7)
    tool.ViewObject.Transparency = 80
    show_assembled_view(doc)
    tool.Visibility = True
    return tool


def validate_nut_access(doc):
    envelope = doc.NutToolEnvelope.Shape
    assert envelope.isValid() and len(envelope.Solids) == 1
    assert doc.Dimensions.NutToolDiameter.Value > doc.Dimensions.NutDiameter.Value
    assert doc.Dimensions.NutToolLength.Value > doc.Dimensions.NutThickness.Value
    assert doc.NutReference.Shape.cut(envelope).Volume < 1e-7
    assert abs(envelope.BoundBox.ZMax-doc.SupportPlate.Shape.BoundBox.ZMin) < 1e-7
    # Nut and screw intentionally lie inside this outer clearance volume.
    for obstacle in [doc.SupportPlate, *doc.MotionStudy.Group]:
        assert envelope.common(obstacle.Shape).Volume < 1e-7, f'Lower tool blocked by {obstacle.Name}'
