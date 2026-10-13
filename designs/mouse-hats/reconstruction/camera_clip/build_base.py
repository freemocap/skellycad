"""Stage 1: two measured sketches and an editable native additive loft (mm)."""
from pathlib import Path
import json
import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher

HERE = Path(__file__).resolve().parent
WORKSPACE = next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())


def profile(body, name, points, z):
    sketch = body.newObject('Sketcher::SketchObject', name)
    sketch.Placement.Base.z = z
    for i, (x, y) in enumerate(points):
        nx, ny = points[(i+1) % len(points)]
        sketch.addGeometry(Part.LineSegment(App.Vector(x,y,0), App.Vector(nx,ny,0)), False)
    for i, (x, y) in enumerate(points):
        sketch.addConstraint(Sketcher.Constraint('Coincident', i, 2, (i+1)%len(points), 1))
        # Source corner coordinates preserve the inherited skew explicitly.
        if abs(x) < 1e-10:
            sketch.addConstraint(Sketcher.Constraint('PointOnObject', i, 1, -2))
        else:
            c = sketch.addConstraint(Sketcher.Constraint('DistanceX', i, 1, x))
            sketch.renameConstraint(c, f'Corner{i+1}X')
        if abs(y) < 1e-10:
            sketch.addConstraint(Sketcher.Constraint('PointOnObject', i, 1, -1))
        else:
            c = sketch.addConstraint(Sketcher.Constraint('DistanceY', i, 1, y))
            sketch.renameConstraint(c, f'Corner{i+1}Y')
    return sketch


def main():
    p = json.loads((HERE/'parameters.json').read_text())
    out = WORKSPACE/'generated/mouse-hats/reconstruction/camera-clip'
    target = out/'02-base-loft.FCStd'
    assert not target.exists()
    assert 'CameraClipRebuild58' not in App.listDocuments()
    source = App.getDocument('CameraClipStudy58').SourceClip.Shape.copy()
    doc = App.newDocument('CameraClipRebuild58')
    doc.Label = 'Camera clip - 02 base loft'
    body = doc.addObject('PartDesign::Body', 'CameraClip')
    dimensions = doc.addObject('App::FeaturePython', 'Dimensions')
    dimensions.addProperty('App::PropertyLength', 'BaseThickness', 'Dimensions')
    dimensions.BaseThickness = p['base_thickness_mm']
    bottom = profile(body, 'UndersideProfile', p['underside_xy_mm'], 0)
    top = profile(body, 'FloorProfile', p['floor_xy_mm'], p['base_thickness_mm'])
    top.setExpression('Placement.Base.z', 'Dimensions.BaseThickness')
    doc.recompute()
    loft = body.newObject('PartDesign::AdditiveLoft', 'BaseLoft')
    loft.Profile = bottom
    loft.Sections = [top]
    loft.Ruled = True
    doc.recompute()
    assert bottom.FullyConstrained and top.FullyConstrained
    assert loft.Shape.isValid() and len(loft.Shape.Solids) == 1
    expected = source.common(Part.makeBox(30,30,p['base_thickness_mm'],App.Vector(-10,-15,0)))
    excess = loft.Shape.cut(expected).Volume
    missing = expected.cut(loft.Shape).Volume
    assert excess + missing < 1e-6, (excess,missing)
    # Verify the intended control actually recomputes, then restore source value.
    dimensions.BaseThickness = p['base_thickness_mm'] + 0.1
    doc.recompute()
    assert loft.Shape.isValid() and abs(loft.Shape.BoundBox.ZLength-1.6)<1e-7
    dimensions.BaseThickness = p['base_thickness_mm']
    doc.recompute()
    bottom.Visibility = False
    top.Visibility = False
    loft.ViewObject.ShapeColor = (0.3,0.75,0.85)
    reference = doc.addObject('Part::Feature', 'SourceReference')
    reference.Label = '58 clip reference - display offset 12 mm'
    reference.Shape = source
    reference.Placement.Base.x += 12
    reference.ViewObject.ShapeColor = (0.8,0.4,0.7)
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    doc.recompute()
    doc.saveAs(str(target))
    result = dict(stage='base only', excess_mm3=excess, missing_mm3=missing,
                  base_volume_mm3=loft.Shape.Volume, sketches_fully_constrained=True,
                  thickness_edit_mm=[1.5,1.6,1.5], full_clip_parity=False)
    (out/'base-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return doc
