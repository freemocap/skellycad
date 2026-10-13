"""Inspect older STEP for missing components; all distances are millimetres."""
from pathlib import Path
import hashlib
import FreeCAD as App
import FreeCADGui as Gui
import Part

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = next(p for p in PROJECT.parents if (p/'tools/cad/toolchain.json').is_file())
PART_LABELS = ['Baseplate - short, drop-in nut', 'Socket - insert pocket unverified',
               'Mount stem', 'Carrier and arm - older version', 'Ball and camera holder']


def main():
    source = PROJECT/'old/df-hardware/camera-assembly/cad/52nassembly/52nassembly.step'
    shape = Part.read(str(source))
    assert len(shape.Solids) == 5
    target = WORKSPACE/'generated/mouse-hats/inspection/52-numbered-reference.FCStd'
    assert not target.exists()
    assert 'MouseHatsStep52' not in App.listDocuments()
    doc = App.newDocument('MouseHatsStep52')
    doc.Label = '52 STEP - missing component search'
    colors = [(0.3,0.65,0.95),(0.9,0.45,0.4),(0.75,0.45,0.9),
              (0.4,0.8,0.55),(0.9,0.65,0.2)]
    for i, solid in enumerate(shape.Solids, 1):
        obj = doc.addObject('Part::Feature', f'Reference{i:02d}')
        obj.Label = f'52-{i} - {PART_LABELS[i-1]}'
        obj.Shape = solid
        obj.addProperty('App::PropertyString','SourceFile','Reference')
        obj.SourceFile = source.relative_to(PROJECT).as_posix()
        obj.addProperty('App::PropertyString','SourceSHA256','Reference')
        obj.SourceSHA256 = hashlib.sha256(source.read_bytes()).hexdigest()
        obj.addProperty('App::PropertyVector','InspectionOffset','Reference')
        # Lay out each intact solid along X, retaining its source orientation.
        b = solid.BoundBox
        offset = App.Vector((i-1)*30-b.Center.x, -b.Center.y, -b.Center.z)
        obj.InspectionOffset = offset
        obj.Placement.Base = obj.Placement.Base + offset
        obj.ViewObject.ShapeColor = colors[i-1]
        obj.ViewObject.DisplayMode = 'Flat Lines'
        annotation = doc.addObject('App::Annotation', f'Number{i:02d}')
        annotation.LabelText = [f'52-{i}']
        annotation.Position = App.Vector((i-1)*30, 0, b.ZLength/2+3)
        annotation.ViewObject.FontSize = 18
    doc.recompute()
    Gui.activeDocument().activeView().viewFront()
    Gui.activeDocument().activeView().fitAll()
    doc.saveAs(str(target))
    return doc
