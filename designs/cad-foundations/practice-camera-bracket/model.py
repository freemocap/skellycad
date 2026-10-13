"""Original camera-bracket lessons. No client geometry or dimensions."""
import FreeCAD as App


def create_dimensions(doc, params):
    assert params['units'] == 'mm' and params['camera_is_fictional'] is True
    dimensions = doc.addObject('App::FeaturePython', 'Dimensions')
    dimensions.Label = 'Design dimensions (mm)'
    for name, key in [('CameraWidth', 'camera_width'), ('CameraDepth', 'camera_depth'),
                      ('CameraHeight', 'camera_height'), ('SideClearance', 'side_clearance')]:
        value = params[key]
        assert value > 0
        dimensions.addProperty('App::PropertyLength', name, 'Dimensions')
        setattr(dimensions, name, value)
    return dimensions


def create_camera_envelope(doc):
    references = doc.addObject('App::DocumentObjectGroup', 'References')
    references.Label = 'Reference geometry (not the printed part)'
    camera = doc.addObject('Part::Box', 'CameraEnvelope')
    references.addObject(camera)
    camera.Label = 'Fictional camera envelope'
    camera.setExpression('Length', 'Dimensions.CameraWidth')
    camera.setExpression('Width', 'Dimensions.CameraDepth')
    camera.setExpression('Height', 'Dimensions.CameraHeight')
    camera.setExpression('Placement.Base.x', '-Dimensions.CameraWidth / 2')
    camera.setExpression('Placement.Base.y', '-Dimensions.CameraDepth / 2')
    camera.Placement.Base.z = 0
    camera.addProperty('App::PropertyString', 'Purpose', 'Reference')
    camera.Purpose = 'Fictional camera bounding volume; exclude from bracket print exports.'
    camera.setEditorMode('Purpose', 1)
    doc.recompute()
    camera.ViewObject.ShapeColor = (0.25, 0.65, 0.85)
    camera.ViewObject.Transparency = 65
    camera.ViewObject.DisplayMode = 'Flat Lines'
    return camera


def validate_envelope(doc):
    dims, camera = doc.Dimensions, doc.CameraEnvelope
    shape = camera.Shape
    assert shape.isValid() and len(shape.Solids) == 1
    box = shape.BoundBox
    expected = (dims.CameraWidth.Value, dims.CameraDepth.Value, dims.CameraHeight.Value)
    assert all(abs(a - b) < 1e-7 for a, b in zip((box.XLength, box.YLength, box.ZLength), expected))
    assert abs(box.XMin + box.XMax) < 1e-7 and abs(box.YMin + box.YMax) < 1e-7
    assert abs(box.ZMin) < 1e-7
    assert abs(shape.Volume - expected[0] * expected[1] * expected[2]) < 1e-6


def build_stage(doc, params, stage):
    if stage == 'access':
        from pathlib import Path
        import runpy
        build_stage(doc, params, 'motion')
        assembly = runpy.run_path(str(Path(__file__).with_name('assembly.py')))
        return assembly['create_nut_access'](doc, params)
    if stage == 'motion':
        from pathlib import Path
        import runpy
        build_stage(doc, params, 'support')
        assembly = runpy.run_path(str(Path(__file__).with_name('assembly.py')))
        if doc.getObject('MotionStudy') is None:
            assembly['create_motion'](doc)
        assembly['apply_pose'](doc, params['motion_slide_mm'], params['motion_pivot_deg'])
        return doc.MotionStudy
    if stage not in ('envelope', 'cradle', 'slotted-tab', 'hardware', 'retention', 'interfaces', 'support'):
        raise ValueError('Unknown build stage.')
    if doc.getObject('Dimensions') is None:
        create_dimensions(doc, params)
        create_camera_envelope(doc)
    for name, key in [('CameraWidth', 'camera_width'), ('CameraDepth', 'camera_depth'),
                      ('CameraHeight', 'camera_height'), ('SideClearance', 'side_clearance')]:
        assert abs(getattr(doc.Dimensions, name).Value - params[key]) < 1e-7, 'Reconcile manual parameter changes first.'
    validate_envelope(doc)
    if stage in ('cradle', 'slotted-tab', 'hardware', 'retention', 'interfaces', 'support'):
        if doc.getObject('Cradle') is None:
            create_cradle(doc, params)
        for name, key in [('FloorThickness', 'floor_thickness'), ('WallThickness', 'wall_thickness'),
                          ('WallHeight', 'wall_height')]:
            assert abs(getattr(doc.Dimensions, name).Value - params[key]) < 1e-7, 'Reconcile cradle changes first.'
        validate_cradle(doc)
        if stage in ('slotted-tab', 'hardware', 'retention', 'interfaces', 'support'):
            if doc.getObject('SlottedBracket') is None:
                create_slotted_tab(doc, params)
            validate_slotted_tab(doc)
            if stage in ('hardware', 'retention', 'interfaces', 'support'):
                if doc.getObject('ScrewReference') is None:
                    create_hardware_references(doc, params)
                validate_hardware(doc)
                if stage in ('retention', 'interfaces', 'support'):
                    if doc.getObject('RetainedBracket') is None:
                        create_retention(doc, params)
                    validate_retention(doc)
                    if stage in ('interfaces', 'support'):
                        from pathlib import Path
                        import runpy
                        interface_model = runpy.run_path(str(Path(__file__).with_name('interfaces.py')))
                        if doc.getObject('AccessibleBracket') is None:
                            interface_model['create_interfaces'](doc, params)
                        interface_model['validate_interfaces'](doc)
                        if stage == 'support':
                            assembly = runpy.run_path(str(Path(__file__).with_name('assembly.py')))
                            if doc.getObject('SupportPlate') is None:
                                assembly['create_support'](doc, params)
                            assembly['validate_support'](doc)
                            return doc.SupportPlate
                        return doc.AccessibleBracket
                    return doc.RetainedBracket
                return doc.ScrewReference
            return doc.SlottedBracket
        return doc.Cradle
    return doc.CameraEnvelope


def create_cradle(doc, params):
    assert doc.getObject('Cradle') is None, 'Cradle stage already exists.'
    dims = doc.Dimensions
    for name, key in [('FloorThickness', 'floor_thickness'), ('WallThickness', 'wall_thickness'),
                      ('WallHeight', 'wall_height')]:
        assert params[key] > 0
        dims.addProperty('App::PropertyLength', name, 'Cradle')
        setattr(dims, name, params[key])
    assert dims.WallHeight.Value < dims.CameraHeight.Value
    dims.addProperty('App::PropertyLength', 'InsideWidth', 'Derived')
    dims.setExpression('InsideWidth', 'CameraWidth + 2 * SideClearance')
    dims.addProperty('App::PropertyLength', 'OutsideWidth', 'Derived')
    dims.setExpression('OutsideWidth', 'InsideWidth + 2 * WallThickness')
    dims.addProperty('App::PropertyLength', 'CradleDepth', 'Derived')
    dims.setExpression('CradleDepth', 'CameraDepth + 2 * SideClearance')
    group = doc.addObject('App::DocumentObjectGroup', 'PrintableParts')
    group.Label = 'Printable bracket geometry'
    floor = doc.addObject('Part::Box', 'CradleFloor')
    group.addObject(floor)
    for prop, expr in [('Length', 'Dimensions.OutsideWidth'), ('Width', 'Dimensions.CradleDepth'),
                       ('Height', 'Dimensions.FloorThickness'),
                       ('Placement.Base.x', '-Dimensions.OutsideWidth / 2'),
                       ('Placement.Base.y', '-Dimensions.CradleDepth / 2'),
                       ('Placement.Base.z', '-Dimensions.FloorThickness')]:
        floor.setExpression(prop, expr)
    walls = []
    for name, x in [('LeftWall', '-Dimensions.OutsideWidth / 2'),
                    ('RightWall', 'Dimensions.InsideWidth / 2')]:
        wall = doc.addObject('Part::Box', name)
        group.addObject(wall)
        for prop, expr in [('Length', 'Dimensions.WallThickness'), ('Width', 'Dimensions.CradleDepth'),
                           ('Height', 'Dimensions.WallHeight + Dimensions.FloorThickness'),
                           ('Placement.Base.x', x), ('Placement.Base.y', '-Dimensions.CradleDepth / 2'),
                           ('Placement.Base.z', '-Dimensions.FloorThickness')]:
            wall.setExpression(prop, expr)
        walls.append(wall)
    cradle = doc.addObject('Part::MultiFuse', 'Cradle')
    group.addObject(cradle)
    cradle.Label = 'Cradle - floor and side walls'
    cradle.Shapes = [floor] + walls
    cradle.Refine = True
    doc.recompute()
    validate_cradle(doc)
    for source in [floor] + walls:
        source.Visibility = False
    cradle.ViewObject.ShapeColor = (0.9, 0.65, 0.25)
    cradle.Visibility = True
    return cradle


def validate_cradle(doc):
    validate_envelope(doc)
    dims, shape = doc.Dimensions, doc.Cradle.Shape
    assert shape.isValid() and len(shape.Solids) == 1
    expected = (dims.OutsideWidth.Value * dims.CradleDepth.Value * dims.FloorThickness.Value
                + 2 * dims.WallThickness.Value * dims.CradleDepth.Value * dims.WallHeight.Value)
    assert abs(shape.Volume - expected) < 1e-6
    assert shape.common(doc.CameraEnvelope.Shape).Volume < 1e-7
    left_gap = doc.CameraEnvelope.Shape.BoundBox.XMin - doc.LeftWall.Shape.BoundBox.XMax
    right_gap = doc.RightWall.Shape.BoundBox.XMin - doc.CameraEnvelope.Shape.BoundBox.XMax
    assert abs(left_gap - dims.SideClearance.Value) < 1e-7
    assert abs(right_gap - dims.SideClearance.Value) < 1e-7
    assert abs(doc.CradleFloor.Shape.BoundBox.ZMax) < 1e-7


def expression_object(doc, type_name, name, expressions):
    obj = doc.addObject(type_name, name)
    doc.PrintableParts.addObject(obj)
    for prop, expression in expressions.items():
        obj.setExpression(prop, expression)
    return obj


def create_slotted_tab(doc, params):
    assert doc.getObject('SlottedBracket') is None, 'Slotted tab already exists.'
    dims = doc.Dimensions
    for name, key in [('TabWidth', 'tab_width'), ('TabExtension', 'tab_extension'),
                      ('TabOverlap', 'tab_overlap'), ('SlotOverallLength', 'slot_overall_length'),
                      ('SlotWidth', 'slot_width')]:
        assert params[key] > 0
        dims.addProperty('App::PropertyLength', name, 'Mounting tab')
        setattr(dims, name, params[key])
    assert dims.TabWidth.Value < dims.InsideWidth.Value
    assert dims.TabOverlap.Value < dims.CradleDepth.Value
    assert dims.SlotWidth.Value < dims.TabWidth.Value
    assert dims.SlotWidth.Value < dims.SlotOverallLength.Value < dims.TabExtension.Value
    dims.addProperty('App::PropertyLength', 'SlotCenterY', 'Derived')
    dims.setExpression('SlotCenterY', 'CradleDepth / 2 + TabExtension / 2')
    tab = expression_object(doc, 'Part::Box', 'MountingTab', {
        'Length': 'Dimensions.TabWidth',
        'Width': 'Dimensions.TabExtension + Dimensions.TabOverlap',
        'Height': 'Dimensions.FloorThickness',
        'Placement.Base.x': '-Dimensions.TabWidth / 2',
        'Placement.Base.y': 'Dimensions.CradleDepth / 2 - Dimensions.TabOverlap',
        'Placement.Base.z': '-Dimensions.FloorThickness',
    })
    base = doc.addObject('Part::Fuse', 'BracketWithTab')
    doc.PrintableParts.addObject(base)
    base.Base, base.Tool, base.Refine = doc.Cradle, tab, True
    bridge = expression_object(doc, 'Part::Box', 'SlotBridge', {
        'Length': 'Dimensions.SlotWidth',
        'Width': 'Dimensions.SlotOverallLength - Dimensions.SlotWidth',
        'Height': 'Dimensions.FloorThickness + 2 mm',
        'Placement.Base.x': '-Dimensions.SlotWidth / 2',
        'Placement.Base.y': 'Dimensions.SlotCenterY - (Dimensions.SlotOverallLength - Dimensions.SlotWidth) / 2',
        'Placement.Base.z': '-Dimensions.FloorThickness - 1 mm',
    })
    ends = []
    for name, sign in [('SlotNearEnd', '-'), ('SlotFarEnd', '+')]:
        ends.append(expression_object(doc, 'Part::Cylinder', name, {
            'Radius': 'Dimensions.SlotWidth / 2',
            'Height': 'Dimensions.FloorThickness + 2 mm',
            'Placement.Base.y': f'Dimensions.SlotCenterY {sign} (Dimensions.SlotOverallLength - Dimensions.SlotWidth) / 2',
            'Placement.Base.z': '-Dimensions.FloorThickness - 1 mm',
        }))
    slot = doc.addObject('Part::MultiFuse', 'SlotTool')
    doc.PrintableParts.addObject(slot)
    slot.Shapes, slot.Refine = [bridge] + ends, True
    result = doc.addObject('Part::Cut', 'SlottedBracket')
    doc.PrintableParts.addObject(result)
    result.Label = 'Cradle with rear adjustment slot'
    result.Base = base
    result.Tool = slot
    result.Refine = True
    doc.recompute()
    validate_slotted_tab(doc)
    for obj in [doc.Cradle, tab, base, bridge, *ends, slot]:
        obj.Visibility = False
    result.ViewObject.ShapeColor = (0.9, 0.65, 0.25)
    result.Visibility = True
    return result


def validate_slotted_tab(doc):
    import math
    validate_cradle(doc)
    dims, shape = doc.Dimensions, doc.SlottedBracket.Shape
    width, length = dims.SlotWidth.Value, dims.SlotOverallLength.Value
    assert shape.isValid() and len(shape.Solids) == 1
    assert doc.SlotTool.Shape.isValid() and len(doc.SlotTool.Shape.Solids) == 1
    assert abs(doc.SlotTool.Shape.BoundBox.XLength - width) < 1e-7
    assert abs(doc.SlotTool.Shape.BoundBox.YLength - length) < 1e-7
    area = width * (length - width) + math.pi * (width / 2)**2
    expected = doc.Cradle.Shape.Volume + (dims.TabWidth.Value * dims.TabExtension.Value - area) * dims.FloorThickness.Value
    assert abs(shape.Volume - expected) < 1e-6
    assert shape.common(doc.CameraEnvelope.Shape).Volume < 1e-7
    assert (dims.TabExtension.Value - length) / 2 > 0
    assert (dims.TabWidth.Value - width) / 2 > 0
    assert abs(shape.BoundBox.YMax - (dims.CradleDepth.Value / 2 + dims.TabExtension.Value)) < 1e-7


def reference_cylinder(doc, name, radius, height, z):
    obj = doc.addObject('Part::Cylinder', name)
    doc.References.addObject(obj)
    obj.setExpression('Radius', radius)
    obj.setExpression('Height', height)
    obj.setExpression('Placement.Base.y', 'Dimensions.SlotCenterY + Dimensions.ScrewOffset')
    obj.setExpression('Placement.Base.z', z)
    return obj


def create_hardware_references(doc, params):
    """Simplified unthreaded hardware and straight tool approach, not purchased parts."""
    assert doc.getObject('ScrewReference') is None
    dims = doc.Dimensions
    fields = [('ScrewDiameter', 'screw_shaft_diameter'), ('ScrewLength', 'screw_under_head_length'),
              ('HeadDiameter', 'screw_head_diameter'), ('HeadHeight', 'screw_head_height'),
              ('WasherOD', 'washer_outer_diameter'), ('WasherID', 'washer_inner_diameter'),
              ('WasherThickness', 'washer_thickness'), ('DriverDiameter', 'driver_diameter'),
              ('DriverLength', 'driver_approach_length')]
    for name, key in fields:
        assert params[key] > 0
        dims.addProperty('App::PropertyLength', name, 'Hardware references')
        setattr(dims, name, params[key])
    dims.addProperty('App::PropertyDistance', 'ScrewOffset', 'Hardware references')
    dims.ScrewOffset = 0
    shaft = reference_cylinder(doc, 'ScrewShaft', 'Dimensions.ScrewDiameter / 2',
                               'Dimensions.ScrewLength', 'Dimensions.WasherThickness - Dimensions.ScrewLength')
    head = reference_cylinder(doc, 'ScrewHead', 'Dimensions.HeadDiameter / 2',
                              'Dimensions.HeadHeight', 'Dimensions.WasherThickness')
    screw = doc.addObject('Part::Fuse', 'ScrewReference')
    doc.References.addObject(screw)
    screw.Label = 'Reference screw - simplified, unthreaded'
    screw.Base, screw.Tool, screw.Refine = shaft, head, True
    outer = reference_cylinder(doc, 'WasherOuter', 'Dimensions.WasherOD / 2', 'Dimensions.WasherThickness', '0 mm')
    inner = reference_cylinder(doc, 'WasherBore', 'Dimensions.WasherID / 2', 'Dimensions.WasherThickness + 2 mm', '-1 mm')
    washer = doc.addObject('Part::Cut', 'WasherReference')
    doc.References.addObject(washer)
    washer.Label = 'Reference washer'
    washer.Base, washer.Tool = outer, inner
    driver = reference_cylinder(doc, 'DriverEnvelope', 'Dimensions.DriverDiameter / 2',
                                'Dimensions.DriverLength', 'Dimensions.WasherThickness + Dimensions.HeadHeight')
    driver.Label = 'Driver approach space - reference only'
    doc.recompute()
    validate_hardware(doc)
    for obj in (shaft, head, outer, inner):
        obj.Visibility = False
    screw.ViewObject.ShapeColor = (0.65, 0.65, 0.7)
    washer.ViewObject.ShapeColor = (0.8, 0.8, 0.85)
    driver.ViewObject.ShapeColor = (0.8, 0.3, 0.75)
    driver.ViewObject.Transparency = 85
    return screw


def validate_hardware(doc):
    validate_slotted_tab(doc)
    dims = doc.Dimensions
    assert dims.ScrewDiameter.Value < dims.SlotWidth.Value
    assert dims.ScrewDiameter.Value < dims.WasherID.Value < dims.HeadDiameter.Value < dims.WasherOD.Value
    assert dims.SlotWidth.Value < dims.WasherOD.Value < dims.TabWidth.Value
    assert dims.ScrewLength.Value > dims.FloorThickness.Value + dims.WasherThickness.Value
    assert abs(dims.ScrewOffset.Value) <= (dims.SlotOverallLength.Value - dims.SlotWidth.Value) / 2 + 1e-7
    for obj in (doc.ScrewReference, doc.WasherReference, doc.DriverEnvelope):
        assert obj.Shape.isValid() and len(obj.Shape.Solids) == 1
        for obstruction in (doc.SlottedBracket, doc.CameraEnvelope):
            assert obj.Shape.common(obstruction.Shape).Volume < 1e-7
    assert doc.ScrewReference.Shape.common(doc.WasherReference.Shape).Volume < 1e-7
    washer_bottom = [f for f in doc.WasherReference.Shape.Faces
                     if abs(f.BoundBox.ZMin) < 1e-7 and abs(f.BoundBox.ZMax) < 1e-7]
    tab_top = [f for f in doc.SlottedBracket.Shape.Faces
               if abs(f.BoundBox.ZMin) < 1e-7 and abs(f.BoundBox.ZMax) < 1e-7]
    support_area = sum(a.common(b).Area for a in washer_bottom for b in tab_top)
    assert support_area > 1, 'Washer needs supporting contact area on the tab.'
    return support_area


def create_retention(doc, params):
    assert doc.getObject('RetainedBracket') is None
    dims = doc.Dimensions
    for name, key in [('StopThickness', 'stop_thickness'), ('StopHeight', 'stop_height'),
                      ('StrapWidth', 'strap_width'), ('StrapThickness', 'strap_thickness'),
                      ('StrapRecessWidth', 'strap_recess_width'), ('StrapRecessDepth', 'strap_recess_depth')]:
        assert params[key] > 0
        dims.addProperty('App::PropertyLength', name, 'Retention')
        setattr(dims, name, params[key])
    assert dims.StrapThickness.Value < dims.StrapRecessDepth.Value < dims.FloorThickness.Value
    assert dims.StrapWidth.Value < dims.StrapRecessWidth.Value < dims.CameraDepth.Value
    assert dims.StopHeight.Value < dims.CameraHeight.Value
    dims.setExpression('CradleDepth', 'CameraDepth + 2 * SideClearance + 2 * StopThickness')
    stops = []
    for name, y in [('FrontStop', '-Dimensions.CradleDepth / 2'),
                    ('RearStop', 'Dimensions.CradleDepth / 2 - Dimensions.StopThickness')]:
        stops.append(expression_object(doc, 'Part::Box', name, {
            'Length': 'Dimensions.InsideWidth', 'Width': 'Dimensions.StopThickness',
            'Height': 'Dimensions.FloorThickness + Dimensions.StopHeight',
            'Placement.Base.x': '-Dimensions.InsideWidth / 2', 'Placement.Base.y': y,
            'Placement.Base.z': '-Dimensions.FloorThickness',
        }))
    stopped = doc.addObject('Part::MultiFuse', 'BracketWithStops')
    doc.PrintableParts.addObject(stopped)
    stopped.Shapes, stopped.Refine = [doc.SlottedBracket] + stops, True
    recess = expression_object(doc, 'Part::Box', 'StrapRecessTool', {
        'Length': 'Dimensions.OutsideWidth + 2 mm', 'Width': 'Dimensions.StrapRecessWidth',
        'Height': 'Dimensions.StrapRecessDepth + 1 mm',
        'Placement.Base.x': '-Dimensions.OutsideWidth / 2 - 1 mm',
        'Placement.Base.y': '-Dimensions.StrapRecessWidth / 2',
        'Placement.Base.z': '-Dimensions.FloorThickness - 1 mm',
    })
    result = doc.addObject('Part::Cut', 'RetainedBracket')
    doc.PrintableParts.addObject(result)
    result.Label = 'Bracket with end stops and strap recess'
    result.Base, result.Tool, result.Refine = stopped, recess, True
    doc.recompute()
    update_strap_reference(doc)
    validate_retention(doc)
    for obj in [doc.SlottedBracket, stopped, recess, *stops]:
        obj.Visibility = False
    result.ViewObject.ShapeColor = (0.9, 0.65, 0.25)
    return result


def update_strap_reference(doc):
    """Regenerate a geometric strap route; no flexible-body/tension simulation."""
    import math
    import Part
    dims = doc.Dimensions
    a, c = dims.OutsideWidth.Value / 2, dims.CameraWidth.Value / 2
    bottom = -dims.FloorThickness.Value + dims.StrapRecessDepth.Value
    wall, top = dims.WallHeight.Value, dims.CameraHeight.Value
    points = [(-a, bottom), (a, bottom), (a, wall), (c, top), (-c, top), (-a, wall)]
    outward = []
    for i, (x, z) in enumerate(points):
        before, after = points[i - 1], points[(i + 1) % len(points)]
        normals = []
        for dx, dz in [(x - before[0], z - before[1]), (after[0] - x, after[1] - z)]:
            length = math.hypot(dx, dz)
            normals.append((dz / length, -dx / length))
        n1, n2 = normals
        scale = dims.StrapThickness.Value / (1 + n1[0] * n2[0] + n1[1] * n2[1])
        outward.append((x + scale * (n1[0] + n2[0]), z + scale * (n1[1] + n2[1])))
    def face(coords):
        vertices = [App.Vector(x, -dims.StrapWidth.Value / 2, z) for x, z in coords]
        return Part.Face(Part.makePolygon(vertices + [vertices[0]]))
    strap = doc.getObject('StrapReference')
    if strap is None:
        strap = doc.addObject('Part::Feature', 'StrapReference')
        doc.References.addObject(strap)
        strap.Label = 'Removable strap - route only, no buckle modeled'
    strap.Shape = face(outward).cut(face(points)).extrude(App.Vector(0, dims.StrapWidth.Value, 0))
    strap.ViewObject.ShapeColor = (0.2, 0.25, 0.3)
    doc.recompute()
    return strap


def validate_retention(doc):
    validate_hardware(doc)
    dims, shape = doc.Dimensions, doc.RetainedBracket.Shape
    assert shape.isValid() and len(shape.Solids) == 1
    added = 2 * dims.InsideWidth.Value * dims.StopThickness.Value * dims.StopHeight.Value
    removed = dims.OutsideWidth.Value * dims.StrapRecessWidth.Value * dims.StrapRecessDepth.Value
    assert abs(shape.Volume - (doc.SlottedBracket.Shape.Volume + added - removed)) < 1e-6
    assert shape.common(doc.CameraEnvelope.Shape).Volume < 1e-7
    assert abs(doc.CameraEnvelope.Shape.BoundBox.YMin - doc.FrontStop.Shape.BoundBox.YMax - dims.SideClearance.Value) < 1e-7
    assert abs(doc.RearStop.Shape.BoundBox.YMin - doc.CameraEnvelope.Shape.BoundBox.YMax - dims.SideClearance.Value) < 1e-7
    strap = doc.StrapReference.Shape
    assert strap.isValid() and len(strap.Solids) == 1
    assert strap.BoundBox.ZMin > shape.BoundBox.ZMin
    for reference in (doc.CameraEnvelope, doc.ScrewReference, doc.WasherReference, doc.DriverEnvelope):
        assert strap.common(reference.Shape).Volume < 1e-7
    assert strap.common(shape).Volume < 1e-7
    for reference in (doc.ScrewReference, doc.WasherReference, doc.DriverEnvelope):
        assert shape.common(reference.Shape).Volume < 1e-7
