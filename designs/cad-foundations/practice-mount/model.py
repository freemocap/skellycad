"""Native constrained sketch for an original practice mounting plate."""
import FreeCAD as App
import Part
import Sketcher


def create_plate_sketch(doc, parameters):
    assert parameters['units'] == 'mm'
    length = parameters['plate_length']
    width = parameters['plate_width']
    assert length > 0 and width > 0
    body = doc.addObject('PartDesign::Body', 'PlateBody')
    body.Label = 'Practice mounting plate'
    sketch = doc.addObject('Sketcher::SketchObject', 'PlateOutline')
    body.addObject(sketch)
    sketch.Label = 'Plate outline (XY plane)'
    points = [(0, 0), (length, 0), (length, width), (0, width)]
    for i in range(4):
        a, b = points[i], points[(i + 1) % 4]
        sketch.addGeometry(Part.LineSegment(App.Vector(*a, 0), App.Vector(*b, 0)), False)
    for i in range(4):
        sketch.addConstraint(Sketcher.Constraint('Coincident', i, 2, (i + 1) % 4, 1))
    for i in (0, 2):
        sketch.addConstraint(Sketcher.Constraint('Horizontal', i))
    for i in (1, 3):
        sketch.addConstraint(Sketcher.Constraint('Vertical', i))
    sketch.addConstraint(Sketcher.Constraint('Coincident', 0, 1, -1, 1))
    for name, edge, value in [('PlateLength', 0, length), ('PlateWidth', 1, width)]:
        index = sketch.addConstraint(Sketcher.Constraint('Distance', edge, value))
        sketch.renameConstraint(index, name)
    doc.recompute()
    assert sketch.FullyConstrained, 'Sketch should have no remaining degrees of freedom.'
    assert len(sketch.Shape.Wires) == 1 and sketch.Shape.Wires[0].isClosed()
    return body, sketch


def add_plate_pad(doc, body, sketch, parameters):
    """Extrude the outline into one solid using thickness in millimetres."""
    assert parameters['units'] == 'mm'
    thickness = parameters['plate_thickness']
    assert thickness > 0
    assert doc.getObject('PlatePad') is None, 'Pad already exists.'
    pad = body.newObject('PartDesign::Pad', 'PlatePad')
    pad.Label = 'Plate thickness'
    pad.Profile = sketch
    pad.Length = thickness
    doc.recompute()
    assert pad.Shape.isValid() and len(pad.Shape.Solids) == 1
    expected = sketch.getDatum('PlateLength').Value * sketch.getDatum('PlateWidth').Value * thickness
    assert abs(pad.Shape.Volume - expected) < 1e-6
    assert abs(pad.Shape.BoundBox.ZLength - thickness) < 1e-7
    sketch.Visibility = False
    return pad


def add_mounting_hole_sketch(doc, body, parameters):
    """Draw a constrained circle on a plane following the plate's thickness."""
    assert parameters['units'] == 'mm'
    assert doc.getObject('MountingHole') is None
    radius = parameters['hole_diameter'] / 2
    offset = parameters['hole_edge_offset']
    assert 0 < radius < offset
    assert offset + radius < min(parameters['plate_length'], parameters['plate_width'])
    hole = body.newObject('Sketcher::SketchObject', 'MountingHole')
    hole.Label = 'Mounting hole outline'
    hole.setExpression('Placement.Base.z', 'PlatePad.Length')
    circle = hole.addGeometry(Part.Circle(App.Vector(offset, offset, 0), App.Vector(0, 0, 1), radius), False)
    for name, constraint in [
        ('HoleRadius', Sketcher.Constraint('Radius', circle, radius)),
        ('CenterX', Sketcher.Constraint('DistanceX', circle, 3, offset)),
        ('CenterY', Sketcher.Constraint('DistanceY', circle, 3, offset)),
    ]:
        index = hole.addConstraint(constraint)
        hole.renameConstraint(index, name)
    doc.recompute()
    assert hole.FullyConstrained
    assert abs(hole.Placement.Base.z - doc.PlatePad.Length.Value) < 1e-7
    return hole


def add_mounting_pocket(doc, body, hole):
    """Remove material through the plate using the existing circular sketch."""
    import math
    assert doc.getObject('MountingPocket') is None
    pocket = body.newObject('PartDesign::Pocket', 'MountingPocket')
    pocket.Label = 'Through mounting hole'
    pocket.Profile = hole
    pocket.Type = 'ThroughAll'
    doc.recompute()
    assert pocket.Shape.isValid() and len(pocket.Shape.Solids) == 1
    radius = hole.getDatum('HoleRadius').Value
    thickness = doc.PlatePad.Length.Value
    expected = doc.PlatePad.Shape.Volume - math.pi * radius**2 * thickness
    assert abs(pocket.Shape.Volume - expected) < 1e-6
    body.Tip = pocket
    doc.PlatePad.Visibility = False
    hole.Visibility = False
    pocket.Visibility = True
    return pocket


def add_opposite_row(doc):
    """Add two circles aligned with the first row, with matching edge margins."""
    hole = doc.MountingHole
    assert hole.GeometryCount == 2, 'Expected the two-hole checkpoint.'
    width = doc.PlateOutline.getDatum('PlateWidth').Value
    margin = hole.getDatum('CenterY').Value
    radius = hole.getDatum('HoleRadius').Value
    assert width > 2 * margin + 2 * radius
    for lower in (0, 1):
        x = hole.Geometry[lower].Center.x
        upper = hole.addGeometry(Part.Circle(App.Vector(x, width - margin, 0), App.Vector(0, 0, 1), radius), False)
        hole.addConstraint(Sketcher.Constraint('Equal', lower, upper))
        hole.addConstraint(Sketcher.Constraint('Vertical', lower, 3, upper, 3))
        index = hole.addConstraint(Sketcher.Constraint('DistanceY', upper, 3, width - margin))
        name = 'UpperLeftY' if lower == 0 else 'UpperRightY'
        hole.renameConstraint(index, name)
        hole.setExpression('Constraints.' + name, 'PlateOutline.Constraints.PlateWidth - Constraints.CenterY')
    doc.recompute()
    validate_four_holes(doc)
    return hole


def validate_four_holes(doc):
    import math
    hole, pocket = doc.MountingHole, doc.MountingPocket
    assert hole.GeometryCount == 4 and hole.FullyConstrained
    assert pocket.Shape.isValid() and len(pocket.Shape.Solids) == 1
    length = doc.PlateOutline.getDatum('PlateLength').Value
    width = doc.PlateOutline.getDatum('PlateWidth').Value
    mx, my = hole.getDatum('CenterX').Value, hole.getDatum('CenterY').Value
    radius = hole.getDatum('HoleRadius').Value
    assert radius < min(mx, my)
    assert length > 2 * mx + 2 * radius and width > 2 * my + 2 * radius
    expected_centers = [(mx, my), (length - mx, my), (mx, width - my), (length - mx, width - my)]
    for circle, (x, y) in zip(hole.Geometry, expected_centers):
        assert (circle.Center - App.Vector(x, y, 0)).Length < 1e-7
        assert abs(circle.Radius - radius) < 1e-7
    thickness = doc.PlatePad.Length.Value
    assert abs(hole.Placement.Base.z - thickness) < 1e-7
    expected = length * width * thickness - 4 * math.pi * radius**2 * thickness
    assert abs(pocket.Shape.Volume - expected) < 1e-6


def add_opposite_hole(doc):
    """Extend the existing Pocket profile with a dependent second circle."""
    hole = doc.MountingHole
    assert hole.GeometryCount == 1, 'Expected the single-hole checkpoint.'
    length = doc.PlateOutline.getDatum('PlateLength').Value
    margin = hole.getDatum('CenterX').Value
    y = hole.getDatum('CenterY').Value
    radius = hole.getDatum('HoleRadius').Value
    assert length > 2 * margin + 2 * radius
    second = hole.addGeometry(Part.Circle(App.Vector(length - margin, y, 0), App.Vector(0, 0, 1), radius), False)
    hole.addConstraint(Sketcher.Constraint('Equal', 0, second))
    hole.addConstraint(Sketcher.Constraint('Horizontal', 0, 3, second, 3))
    index = hole.addConstraint(Sketcher.Constraint('DistanceX', second, 3, length - margin))
    hole.renameConstraint(index, 'OppositeX')
    hole.setExpression('Constraints.OppositeX', 'PlateOutline.Constraints.PlateLength - Constraints.CenterX')
    hole.Label = 'Mounting hole outlines'
    doc.MountingPocket.Label = 'Through mounting holes'
    doc.recompute()
    validate_two_holes(doc)
    return hole


def validate_two_holes(doc):
    import math
    hole, pocket = doc.MountingHole, doc.MountingPocket
    assert hole.GeometryCount == 2 and hole.FullyConstrained
    assert pocket.Shape.isValid() and len(pocket.Shape.Solids) == 1
    length = doc.PlateOutline.getDatum('PlateLength').Value
    first, second = hole.Geometry
    assert abs((length - second.Center.x) - first.Center.x) < 1e-7
    assert abs(first.Center.y - second.Center.y) < 1e-7
    assert abs(first.Radius - second.Radius) < 1e-7
    expected = doc.PlatePad.Shape.Volume - 2 * math.pi * first.Radius**2 * doc.PlatePad.Length.Value
    assert abs(pocket.Shape.Volume - expected) < 1e-6


def top_perimeter_edges(shape):
    """Identify the four straight edges on this rectangular plate's top plane."""
    top_z = shape.BoundBox.ZMax
    edges = []
    for index, edge in enumerate(shape.Edges, 1):
        on_top = abs(edge.BoundBox.ZMin - top_z) < 1e-7 and abs(edge.BoundBox.ZMax - top_z) < 1e-7
        if isinstance(edge.Curve, Part.Line) and on_top:
            edges.append(f'Edge{index}')
    assert len(edges) == 4, 'Expected four straight outer edges; inspect changed geometry.'
    return edges


def add_top_chamfer(doc, parameters):
    """Break the top perimeter edge, preserving the underside and hole bores."""
    assert parameters['units'] == 'mm'
    assert doc.getObject('TopChamfer') is None
    size = parameters['top_chamfer']
    base = doc.MountingPocket
    assert 0 < size < doc.PlatePad.Length.Value
    radius = doc.MountingHole.getDatum('HoleRadius').Value
    assert size < min(doc.MountingHole.getDatum(n).Value - radius for n in ('CenterX', 'CenterY'))
    edges = top_perimeter_edges(base.Shape)
    chamfer = doc.PlateBody.newObject('PartDesign::Chamfer', 'TopChamfer')
    chamfer.Label = 'Top perimeter bevel'
    chamfer.Base = (base, edges)
    chamfer.ChamferType = 'Equal distance'
    chamfer.Size = size
    doc.recompute()
    validate_top_chamfer(doc)
    doc.PlateBody.Tip = chamfer
    base.Visibility = False
    chamfer.Visibility = True
    return chamfer


def validate_top_chamfer(doc):
    validate_four_holes(doc)
    base, result = doc.MountingPocket.Shape, doc.TopChamfer.Shape
    assert result.isValid() and len(result.Solids) == 1
    size = doc.TopChamfer.Size.Value
    length, width = base.BoundBox.XLength, base.BoundBox.YLength
    removed = (length + width) * size**2 - 4 * size**3 / 3
    assert abs(result.Volume - (base.Volume - removed)) < 1e-6
    assert all(abs(getattr(result.BoundBox, key) - getattr(base.BoundBox, key)) < 1e-7
               for key in ('XMin', 'XMax', 'YMin', 'YMax', 'ZMin', 'ZMax'))
    def underside(shape):
        return sum(face.Area for face in shape.Faces if abs(face.BoundBox.ZMin) < 1e-7 and abs(face.BoundBox.ZMax) < 1e-7)
    assert abs(underside(result) - underside(base)) < 1e-7
    bores = [face for face in result.Faces if isinstance(face.Surface, Part.Cylinder)]
    assert len(bores) == 4
    radius = doc.MountingHole.getDatum('HoleRadius').Value
    assert all(abs(face.Surface.Radius - radius) < 1e-7 for face in bores)


def add_top_fillet(doc, parameters):
    """Alternative to the chamfer: round the original Pocket's top perimeter."""
    assert parameters['units'] == 'mm'
    assert doc.getObject('TopFillet') is None and doc.getObject('TopChamfer') is None
    radius = parameters['top_fillet_radius']
    assert 0 < radius < doc.PlatePad.Length.Value
    hole_radius = doc.MountingHole.getDatum('HoleRadius').Value
    assert radius < min(doc.MountingHole.getDatum(n).Value - hole_radius for n in ('CenterX', 'CenterY'))
    base = doc.MountingPocket
    edges = top_perimeter_edges(base.Shape)
    fillet = doc.PlateBody.newObject('PartDesign::Fillet', 'TopFillet')
    fillet.Label = 'Top perimeter round'
    fillet.Base = (base, edges)
    fillet.Radius = radius
    doc.recompute()
    validate_top_fillet(doc)
    doc.PlateBody.Tip = fillet
    base.Visibility = False
    fillet.Visibility = True
    return fillet


def validate_top_fillet(doc):
    validate_four_holes(doc)
    base, result = doc.MountingPocket.Shape, doc.TopFillet.Shape
    assert result.isValid() and len(result.Solids) == 1
    assert 0 < result.Volume < base.Volume
    assert all(abs(getattr(result.BoundBox, key) - getattr(base.BoundBox, key)) < 1e-7
               for key in ('XMin', 'XMax', 'YMin', 'YMax', 'ZMin', 'ZMax'))
    def underside(shape):
        return sum(face.Area for face in shape.Faces if abs(face.BoundBox.ZMin) < 1e-7 and abs(face.BoundBox.ZMax) < 1e-7)
    assert abs(underside(result) - underside(base)) < 1e-7
    bores = [face for face in result.Faces if isinstance(face.Surface, Part.Cylinder)
             and abs(abs(face.Surface.Axis.z) - 1) < 1e-7]
    radius = doc.MountingHole.getDatum('HoleRadius').Value
    assert len(bores) == 4 and all(abs(face.Surface.Radius - radius) < 1e-7 for face in bores)
    rounds = [face for face in result.Faces if isinstance(face.Surface, Part.Cylinder)
              and abs(face.Surface.Axis.z) < 1e-7]
    assert len(rounds) == 4
    assert all(abs(face.Surface.Radius - doc.TopFillet.Radius.Value) < 1e-7 for face in rounds)
