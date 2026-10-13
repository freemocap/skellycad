"""Canonical numbered overview and seated assembly of the current six whole parts."""
from pathlib import Path
import json,runpy,sys
import FreeCAD as App
import FreeCADGui as Gui

HERE=Path(__file__).resolve().parent
api=runpy.run_path(str(HERE/'build_mount.py'));api['load_modules']()
from current_view import LayoutControl
ROOT=api['ROOT'];OUT=ROOT/'generated/mouse-hats/current'
OUT.mkdir(parents=True,exist_ok=True)
manifest=json.loads((HERE/'current-parts.json').read_text())
doc=App.newDocument('MouseHatsCurrent')
doc.Label='CURRENT — Mouse hats — six working parts'
doc.saveAs(str(OUT/'CURRENT.FCStd'))
overview=doc.addObject('App::DocumentObjectGroup','PartsOverview')
overview.Label='01 — Numbered whole parts'
assembly=doc.addObject('App::DocumentObjectGroup','Assembled')
assembly.Label='02 — Same parts assembled (old arm omitted)'
colors=[(0.65,0.45,0.9),(0.2,0.8,0.9),(0.35,0.85,0.45),
        (0.95,0.7,0.2),(0.45,0.65,0.95),(0.95,0.35,0.65)]
rotation=App.Rotation(App.Vector(1,1,0),55)
for index,entry in enumerate(manifest['parts']):
    path=(ROOT/entry['file']).resolve()
    source_doc=next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName).resolve()==path),None)
    if source_doc is None:source_doc=App.openDocument(str(path))
    source=source_doc.getObject(entry['object'])
    assert source is not None and len(source.Shape.Solids)==1
    p=entry['local_to_assembly']
    frame=App.Placement(App.Vector(*p['translation_mm']),App.Rotation(*p['quaternion_xyzw']))
    label=f"{index+1:02d} — {entry['label']}"
    for group,prefix in [(assembly,'Seated'),(overview,'Part')]:
        link=doc.addObject('App::Link',prefix+entry['name'])
        link.setLink(source);link.LinkTransform=True;link.LinkPlacement=frame
        link.Label=label;group.addObject(link)
        view=link.ViewObject;view.OverrideMaterial=True
        material=view.ShapeMaterial;material.DiffuseColor=colors[index];material.Transparency=0
        view.ShapeMaterial=material
        if group==overview:
            rotated=App.Placement(App.Vector(),rotation).multiply(frame)
            shape=source.Shape.copy();shape.Placement=rotated.multiply(shape.Placement)
            center=shape.BoundBox.Center
            cell=App.Vector((index%3)*60, -(index//3)*65,0)
            rotated.Base+=cell-center
            link.LinkPlacement=rotated
            annotation=doc.addObject('App::Annotation','Label'+entry['name'])
            annotation.LabelText=[f"{index+1:02d}  {entry['label'].split(' — ')[0]}"]
            annotation.Position=cell+App.Vector(-23,-26,0)
            annotation.ViewObject.FontSize=13
            annotation.ViewObject.TextColor=(0.95,0.95,0.95)
            overview.addObject(annotation)
    source_doc.Label='SOURCE — '+entry['label']
control=doc.addObject('App::FeaturePython','ViewSelector')
control.Label='VIEW — choose numbered parts or assembled'
LayoutControl(control)
doc.recompute();App.setActiveDocument(doc.Name)
for index,entry in enumerate(manifest['parts']):
    for prefix in ('Seated','Part'):
        view=doc.getObject(prefix+entry['name']).ViewObject
        material=view.ShapeMaterial;material.DiffuseColor=colors[index];material.Transparency=0
        view.ShapeMaterial=material;view.OverrideMaterial=True
control.Proxy.onChanged(control,'Layout')
Gui.Selection.clearSelection();Gui.Selection.addSelection(control)
doc.save()
Gui.activeDocument().activeView().saveImage(str(OUT/'numbered-parts.png'),1400,900,'Current')
print('Current tray links to',doc.SeatedTray.LinkedObject.Name,'in',doc.SeatedTray.LinkedObject.Document.FileName)
