"""Create a separate GUI inspection document; translations are display-only."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Mesh

PROJECT=Path(__file__).resolve().parents[1]
WORKSPACE=next(p for p in PROJECT.parents if (p/'tools/cad/toolchain.json').is_file())


def main():
    assert 'MouseHatsReferences' not in App.listDocuments(), 'Reference study already open.'
    doc=App.newDocument('MouseHatsReferences')
    doc.Label='Mouse hats - 57 (left), two-arm V5 (right); NOT aligned'
    cases=[('Assembly57','old/df-hardware/camera-assembly/cad/57nassembly/57nassembly.stl',0),
           ('TwoArmV5','old/df-hardware/camera-assembly/camera-assembly-2arm-v5.stl',65)]
    colors=[(0.85,0.65,0.25),(0.25,0.65,0.9),(0.55,0.8,0.4),(0.75,0.4,0.75),(0.8,0.5,0.3),(1,0.1,0.1)]
    for name,relative,offset in cases:
        group=doc.addObject('App::DocumentObjectGroup',name)
        group.Label=name+' - original frame, display X offset '+str(offset)
        mesh=Mesh.Mesh(str(PROJECT/relative))
        obj=doc.addObject('Mesh::Feature',name+'Mesh')
        obj.Mesh=mesh
        group.addObject(obj)
        obj.addProperty('App::PropertyString','SourcePath','Provenance')
        obj.SourcePath=relative
        obj.addProperty('App::PropertyDistance','DisplayOffsetX','Provenance')
        obj.DisplayOffsetX=offset
        obj.addProperty('App::PropertyString','UnitsStatus','Provenance')
        obj.UnitsStatus='Raw STL coordinates displayed as mm; physical scale not confirmed.'
        obj.Placement.Base.x=offset
        obj.ViewObject.ShapeColor=colors[0 if offset==0 else 1]
        obj.ViewObject.DisplayMode='Shaded'
    doc.recompute()
    view=Gui.getDocument(doc.Name).activeView()
    view.viewAxonometric()
    view.fitAll()
    out=WORKSPACE/'generated/mouse-hats/inspection'
    out.mkdir(parents=True,exist_ok=True)
    target=out/'57-and-v5-reference.FCStd'
    assert not target.exists(), 'Preserve existing inspection file.'
    doc.saveAs(str(target))
    return doc
