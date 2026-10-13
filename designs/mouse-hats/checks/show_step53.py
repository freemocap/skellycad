"""Numbered inspection of 53 STEP solids prepared by inspect_steps.py --generations 53."""
from pathlib import Path
import hashlib
import json
import FreeCAD as App
import FreeCADGui as Gui
import Part

PROJECT=Path(__file__).resolve().parents[1]
WORKSPACE=next(p for p in PROJECT.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=WORKSPACE/'generated/mouse-hats/inspection'


def set_layout(doc, separated=True):
    """Inspection translation only; source solid coordinates remain in the BREP files."""
    for i in range(1,4):
        obj=doc.getObject(f'Reference{i:02d}')
        obj.Placement.Base.x=obj.OriginalPlacementX.Value+(i-1)*55 if separated else obj.OriginalPlacementX.Value
        annotation=doc.getObject(f'Number{i:02d}')
        if annotation is not None:
            b=obj.Shape.BoundBox
            annotation.Position=App.Vector(b.Center.x,b.YMin,b.ZMax+3)
    doc.recompute()
    Gui.getDocument(doc.Name).activeView().fitAll()


def main(report_path=None):
    report=json.loads(Path(report_path or OUT/'assembly-53.json').read_text())
    source=PROJECT/report['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==report['sha256']
    assert len(report['components'])==3
    assert 'MouseHatsStep53' not in App.listDocuments(), 'Inspection document already exists.'
    target=OUT/'53-numbered-reference.FCStd'
    assert not target.exists(), 'Preserve prior inspection document.'
    doc=App.newDocument('MouseHatsStep53')
    colors=[(0.9,0.65,0.2),(0.25,0.65,0.95),(0.55,0.8,0.35)]
    labels=['Main carrier - arm and socket', 'Baseplate - skull-cut', 'Skull reference']
    for i,entry in enumerate(report['components'],1):
        obj=doc.addObject('Part::Feature',f'Reference{i:02d}')
        obj.Label=f'{i} - {labels[i-1]}'
        obj.Shape=Part.read(str(WORKSPACE/entry['inspection_brep']))
        obj.addProperty('App::PropertyString','SourceFile','Reference')
        obj.SourceFile=report['source']
        obj.addProperty('App::PropertyString','SourceSHA256','Reference')
        obj.SourceSHA256=report['sha256']
        obj.addProperty('App::PropertyInteger','SourceSolidIndex','Reference')
        obj.SourceSolidIndex=i
        obj.addProperty('App::PropertyDistance','OriginalPlacementX','Reference')
        obj.OriginalPlacementX=obj.Placement.Base.x
        obj.ViewObject.ShapeColor=colors[i-1]
        # Avoid drawing every imported face edge in a heavily faceted solid.
        obj.ViewObject.DisplayMode='Flat Lines' if entry['faces']<1000 else 'Shaded'
        number=doc.addObject('App::Annotation',f'Number{i:02d}')
        number.LabelText=[str(i)]
        number.ViewObject.FontSize=22
    doc.recompute()
    Gui.getDocument(doc.Name).activeView().viewAxonometric()
    set_layout(doc,True)
    doc.saveAs(str(target))
    doc.Label='53 STEP - numbered solids (inspection offsets only)'
    return doc
