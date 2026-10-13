"""Create a local-frame reference for the 58 clip; no geometry simplification."""
from pathlib import Path
import json
import hashlib
import FreeCAD as App
import FreeCADGui as Gui

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = next(p for p in PROJECT.parents if (p/'tools/cad/toolchain.json').is_file())


def main():
    source = App.getDocument('MouseHatsStep58').getObject('Part__Feature003')
    assert source.Label == 'RightCamClip (1)'
    shape = source.Shape.copy()
    assert len(shape.Faces) == 18 and shape.isValid()
    # Broadest planar face supplies the base plane; its longest edge supplies X.
    base = max(shape.Faces, key=lambda f: f.Area)
    edge = max(base.Edges, key=lambda e: e.Length)
    origin = edge.Vertexes[0].Point
    x_axis = edge.Vertexes[-1].Point - origin
    x_axis.normalize()
    z_axis = -base.normalAt(0, 0)
    y_axis = z_axis.cross(x_axis)
    y_axis.normalize()
    rotation = App.Rotation(x_axis, y_axis, z_axis, 'ZXY')
    local_to_assembly = App.Placement(origin, rotation)
    shape.Placement = local_to_assembly.inverse().multiply(shape.Placement)
    out = WORKSPACE/'generated/mouse-hats/reconstruction/camera-clip'
    out.mkdir(parents=True, exist_ok=True)
    assert not (out/'01-local-reference.FCStd').exists()
    assert 'CameraClipStudy58' not in App.listDocuments()
    doc = App.newDocument('CameraClipStudy58')
    doc.Label = 'Camera clip - 01 local reference'
    obj = doc.addObject('Part::Feature', 'SourceClip')
    obj.Label = '58 camera clip - unchanged reference'
    obj.Shape = shape
    obj.addProperty('App::PropertyPlacement', 'LocalToAssembly', 'Provenance')
    obj.LocalToAssembly = local_to_assembly
    obj.ViewObject.ShapeColor = (0.8, 0.4, 0.7)
    obj.ViewObject.DisplayMode = 'Flat Lines'
    doc.recompute()
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    doc.saveAs(str(out/'01-local-reference.FCStd'))
    b = shape.BoundBox
    report = dict(source='old/58nassembly.step',
        source_sha256=hashlib.sha256((PROJECT/'old/58nassembly.step').read_bytes()).hexdigest(),
        source_label=source.Label, units='mm', phase='reference preparation, not rebuilt',
        local_to_assembly=dict(translation_mm=list(origin), quaternion_xyzw=list(rotation.Q)),
        local_extents_mm=[b.XLength,b.YLength,b.ZLength],
        volume_mm3=shape.Volume,
        faces=[dict(index=i,area_mm2=f.Area,normal=list(f.normalAt(0,0)))
               for i,f in enumerate(shape.Faces,1)])
    (out/'reference-measurements.json').write_text(json.dumps(report,indent=2)+'\n')
    restored = shape.copy()
    restored.Placement = local_to_assembly.multiply(restored.Placement)
    delta = restored.cut(source.Shape).Volume + source.Shape.cut(restored).Volume
    assert delta < 1e-7, f'Frame transform changed solid: {delta}'
    print(json.dumps(dict(local_extents_mm=report['local_extents_mm'],
                         round_trip_difference_mm3=delta),indent=2))
    return doc
