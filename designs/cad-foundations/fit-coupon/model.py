"""Three-hole clearance study; values are hypotheses, not validated printer fits."""
import math
import FreeCAD as App


def build_coupon(doc, params):
    assert params['units'] == 'mm'
    assert len(params['diametral_clearances']) == len(params['hole_centers_x']) == 3
    settings = doc.addObject('App::FeaturePython', 'Dimensions')
    settings.Label = 'Coupon dimensions (mm)'
    for name, value in [('Length', params['length']), ('Width', params['width']),
                        ('Thickness', params['thickness']), ('PinDiameter', params['nominal_pin_diameter'])]:
        assert value > 0
        settings.addProperty('App::PropertyLength', name, 'Dimensions')
        setattr(settings, name, value)
    block = doc.addObject('Part::Box', 'CouponBlank')
    for name, expression in [('Length', 'Dimensions.Length'), ('Width', 'Dimensions.Width'),
                             ('Height', 'Dimensions.Thickness')]:
        block.setExpression(name, expression)
    result = block
    for number, (clearance, x) in enumerate(zip(params['diametral_clearances'], params['hole_centers_x']), 1):
        assert clearance >= 0
        hole = doc.addObject('Part::Cylinder', f'Hole{number}')
        hole.Label = f'Hole {number}: diameter {params["nominal_pin_diameter"] + clearance:.1f} mm'
        hole.addProperty('App::PropertyLength', 'DiametralClearance', 'Fit')
        hole.DiametralClearance = clearance
        hole.setExpression('Radius', '(Dimensions.PinDiameter + DiametralClearance) / 2')
        hole.Placement.Base.x = x
        hole.setExpression('Placement.Base.y', 'Dimensions.Width / 2')
        hole.Placement.Base.z = -1
        hole.setExpression('Height', 'Dimensions.Thickness + 2 mm')
        cut = doc.addObject('Part::Cut', f'Cut{number}')
        cut.Base, cut.Tool = result, hole
        doc.recompute()
        result.Visibility = False
        hole.Visibility = False
        result = cut
    result.Label = 'Clearance coupon - 3 holes'
    result.ViewObject.ShapeColor = (0.25, 0.65, 0.85)
    validate_coupon(doc)
    return result


def validate_coupon(doc):
    dims, shape = doc.Dimensions, doc.Cut3.Shape
    assert shape.isValid() and len(shape.Solids) == 1
    expected = dims.Length.Value * dims.Width.Value * dims.Thickness.Value
    previous = None
    for number in range(1, 4):
        hole = doc.getObject(f'Hole{number}')
        r, x, y = hole.Radius.Value, hole.Placement.Base.x, hole.Placement.Base.y
        assert abs(2 * r - dims.PinDiameter.Value - hole.DiametralClearance.Value) < 1e-7
        assert r < x < dims.Length.Value - r and r < y < dims.Width.Value - r
        if previous:
            assert x - previous[0] > r + previous[1]
        previous = (x, r)
        expected -= math.pi * r**2 * dims.Thickness.Value
    assert abs(shape.Volume - expected) < 1e-6


def add_embossed_labels(doc, params):
    """Create editable text, extrude it, and fuse it into the coupon."""
    from pathlib import Path
    import Draft
    assert doc.getObject('LabeledCoupon') is None
    assert Path(params['label_font']).is_file()
    assert params['units'] == 'mm'
    relief, embed = params['label_relief'], params['label_embed']
    assert relief > 0 and 0 < embed < doc.Dimensions.Thickness.Value
    extrusions = []
    for number in range(1, 4):
        hole = doc.getObject(f'Hole{number}')
        label = f'{2 * hole.Radius.Value:.1f}'
        text = Draft.make_shapestring(label, params['label_font'], Size=params['label_size'])
        text.Label = f'Diameter label {number}: {label} mm'
        doc.recompute()
        bounds = text.Shape.BoundBox
        text.Placement.Base = App.Vector(hole.Placement.Base.x - (bounds.XMin + bounds.XMax) / 2,
                                         params['label_center_y'] - (bounds.YMin + bounds.YMax) / 2,
                                         doc.Dimensions.Thickness.Value - embed)
        doc.recompute()
        bounds = text.Shape.BoundBox
        assert bounds.XMin > 0 and bounds.XMax < doc.Dimensions.Length.Value
        assert bounds.YMin > 0 and bounds.YMax < hole.Placement.Base.y - hole.Radius.Value
        raised = doc.addObject('Part::Extrusion', f'RaisedLabel{number}')
        raised.Base = text
        raised.DirMode = 'Normal'
        raised.LengthFwd = relief + embed
        raised.Solid = True
        doc.recompute()
        assert raised.Shape.isValid() and len(raised.Shape.Solids) > 0
        text.Visibility = False
        extrusions.append(raised)
    result = doc.addObject('Part::MultiFuse', 'LabeledCoupon')
    result.Label = 'Clearance coupon - embossed diameters'
    result.Shapes = [doc.Cut3] + extrusions
    result.Refine = True
    doc.recompute()
    assert result.Shape.isValid() and len(result.Shape.Solids) == 1
    assert abs(result.Shape.BoundBox.ZMax - doc.Dimensions.Thickness.Value - relief) < 1e-7
    expected = doc.Cut3.Shape.Volume + sum(e.Shape.Volume for e in extrusions) * relief / (relief + embed)
    assert abs(result.Shape.Volume - expected) < 1e-5
    doc.Cut3.Visibility = False
    for raised in extrusions:
        raised.Visibility = False
    result.ViewObject.ShapeColor = (0.25, 0.65, 0.85)
    return result
