"""Import the newly supplied 58 STEP with source names and original placement."""
from pathlib import Path
import hashlib
import json
import re
import FreeCAD as App
import FreeCADGui as Gui
import Import

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = next(p for p in PROJECT.parents if (p/'tools/cad/toolchain.json').is_file())
OUT = WORKSPACE/'generated/mouse-hats/inspection'


def restore_source_names(doc, source):
    """Match unique shell face counts in this STEP to imported solids; reject ambiguity."""
    entities = dict(re.findall(r'#(\d+)\s*=\s*(.*?);', source.read_text(), re.S))
    candidates = {}
    for value in entities.values():
        match = re.match(r"(?:MANIFOLD_SOLID_BREP|BREP_WITH_VOIDS)\('([^']*)',#(\d+)(.*)\)", value, re.S)
        if not match:
            continue
        name, outer, tail = match.groups()
        count = len(re.findall(r'#\d+', entities[outer]))
        for ref in re.findall(r'#(\d+)', tail):
            inner = re.findall(r'#(\d+)', entities[ref])
            assert len(inner) == 1
            count += len(re.findall(r'#\d+', entities[inner[0]]))
        assert count not in candidates, 'Ambiguous STEP face counts'
        candidates[count] = name
    objects = [o for o in doc.Objects if o.isDerivedFrom('Part::Feature') and not o.Shape.isNull()]
    assert len(objects) == len(candidates)
    assert len({len(o.Shape.Faces) for o in objects}) == len(objects)
    for obj in objects:
        obj.Label = candidates[len(obj.Shape.Faces)]


def main(doc=None):
    source = PROJECT/'old/58nassembly.step'
    target = OUT/'58-reference.FCStd'
    assert not target.exists(), 'Preserve existing inspection.'
    if doc is None:
        assert 'MouseHatsStep58' not in App.listDocuments()
        doc = App.newDocument('MouseHatsStep58')
        Import.insert(str(source), doc.Name)
    doc.recompute()
    restore_source_names(doc, source)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    report = dict(source=source.relative_to(PROJECT).as_posix(), sha256=digest,
                  units='mm', objects=[])
    colors = [(0.3,0.7,0.9), (0.6,0.8,0.4), (0.9,0.65,0.2),
              (0.8,0.4,0.7), (0.7,0.75,0.8), (0.9,0.45,0.25)]
    for obj in doc.Objects:
        if not obj.isDerivedFrom('Part::Feature') or obj.Shape.isNull():
            continue
        if 'SourceSHA256' not in obj.PropertiesList:
            obj.addProperty('App::PropertyString', 'SourceSHA256', 'Reference')
        obj.SourceSHA256 = digest
        if 'SourceFile' not in obj.PropertiesList:
            obj.addProperty('App::PropertyString', 'SourceFile', 'Reference')
        obj.SourceFile = report['source']
        obj.ViewObject.ShapeColor = colors[len(report['objects']) % len(colors)]
        obj.ViewObject.DisplayMode = 'Shaded' if len(obj.Shape.Faces)>1000 else 'Flat Lines'
        b = obj.Shape.BoundBox
        report['objects'].append(dict(name=obj.Name, label=obj.Label,
            solids=len(obj.Shape.Solids), faces=len(obj.Shape.Faces),
            valid=obj.Shape.isValid(), volume_mm3=obj.Shape.Volume,
            extents_mm=[b.XLength,b.YLength,b.ZLength]))
    doc.Label = '58 STEP - original assembly positions'
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    doc.saveAs(str(target))
    (OUT/'assembly-58.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    return doc
