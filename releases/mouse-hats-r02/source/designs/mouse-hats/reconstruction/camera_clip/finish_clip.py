"""Finish the clip using wall lofts and small source-preserving crown additions."""
from pathlib import Path
import json
import runpy
import FreeCAD as App
import FreeCADGui as Gui

HERE = Path(__file__).resolve().parent
WORKSPACE = next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
profile = runpy.run_path(str(HERE/'build_base.py'))['profile']


def wall_sketch(body,name,data):
    sketch = profile(body,name,data['points_xy_mm'],0)
    sketch.Placement = App.Placement(App.Vector(*data['origin_mm']),App.Rotation(*data['rotation_xyzw']))
    sketch.setExpression('Placement.Base.z',f"{data['origin_mm'][2]:.17g} mm + Dimensions.BaseThickness - 1.5 mm")
    return sketch


def main():
    data = json.loads((HERE/'wall_parameters.json').read_text())
    doc = App.getDocument('CameraClipRebuild58')
    body = doc.CameraClip
    assert doc.getObject('LeftRetainingWall') is None
    out = WORKSPACE/'generated/mouse-hats/reconstruction/camera-clip'
    target = out/'03-complete-clip.FCStd'
    assert not target.exists()
    sketches=[]
    previous=doc.BaseLoft
    for name,wall in zip(['Left','Right'],data['walls']):
        rear = wall_sketch(body,name+'BackProfile',wall['back'])
        front = wall_sketch(body,name+'FrontProfile',wall['front'])
        sketches.extend([rear,front])
        doc.recompute()
        feature = body.newObject('PartDesign::AdditiveLoft',name+'RetainingWall')
        feature.Profile=rear
        feature.Sections=[front]
        feature.Ruled=True
        feature.Refine=True
        doc.recompute()
        assert feature.Shape.isValid() and len(feature.Shape.Solids)==1, name
        previous.Visibility=False
        rear.Visibility=False
        front.Visibility=False
        previous=feature
    # The source has tiny crown regions extending beyond the tapered front.
    # Overlapping lofts to its second front plane preserve those regions exactly.
    for name,wall in zip(['Left','Right'],data['walls']):
        rear=wall_sketch(body,name+'CrownBackProfile',wall['back'])
        front=wall_sketch(body,name+'CrownFrontProfile',wall['cap_front'])
        sketches.extend([rear,front])
        doc.recompute()
        finish=body.newObject('PartDesign::AdditiveLoft',name+'Crown')
        finish.Profile=rear
        finish.Sections=[front]
        finish.Ruled=True
        finish.Refine=True
        doc.recompute()
        assert finish.Shape.isValid() and len(finish.Shape.Solids)==1
        previous.Visibility=False
        rear.Visibility=False
        front.Visibility=False
        previous=finish
    assert all(s.FullyConstrained for s in sketches)
    source=App.getDocument('CameraClipStudy58').SourceClip.Shape
    excess=finish.Shape.cut(source).Volume
    missing=source.cut(finish.Shape).Volume
    result=dict(stage='complete clip',source_volume_mm3=source.Volume,
                rebuilt_volume_mm3=finish.Shape.Volume,excess_mm3=excess,
                missing_mm3=missing,source_faces=len(source.Faces),
                rebuilt_faces=len(finish.Shape.Faces),sketches_fully_constrained=True)
    print(json.dumps(result,indent=2))
    assert excess+missing<1e-6, 'Whole-clip difference exceeds tolerance'
    doc.Dimensions.BaseThickness=1.6
    doc.recompute()
    assert finish.Shape.isValid() and len(finish.Shape.Solids)==1
    assert abs(finish.Shape.BoundBox.ZLength-source.BoundBox.ZLength-0.1)<1e-6
    doc.Dimensions.BaseThickness=1.5
    doc.recompute()
    result['thickness_edit_mm']=[1.5,1.6,1.5]
    result['restored_difference_mm3']=finish.Shape.cut(source).Volume+source.cut(finish.Shape).Volume
    assert result['restored_difference_mm3']<1e-6
    finish.ViewObject.ShapeColor=(0.3,0.75,0.85)
    finish.Visibility=True
    doc.SourceReference.Visibility=True
    doc.Label='Camera clip - complete native reconstruction'
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    doc.saveAs(str(target))
    (out/'complete-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    return doc
