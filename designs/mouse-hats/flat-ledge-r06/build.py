"""Remove only the PCB catch return; preserve all matched geometry. Units mm."""
from pathlib import Path
import json, hashlib
import FreeCAD as App, FreeCADGui as Gui, Part, MeshPart
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
source=ROOT/'designs/mouse-hats/current/checkpoints/MH-T3-EYE-R04.FCStd'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='51f7d8ae465cf4c99f839e7101016f1f14180fd813e399c35d2c14e5eae4735f'
src=App.openDocument(str(source))
seat=5.28706399647303; top=18.4423586623637
# The retained shelf is 0.4 thick, 1.6 projecting from the seat, 3 along the edge.
region=Part.makeBox(10,10,5,App.Vector(seat,top-.4-10,-13.7))
removed=src.UpperCatch.Shape.common(region)
ledge=src.UpperCatch.Shape.cut(removed).removeSplitter()
assert removed.Volume>0 and ledge.isValid()
OUT=ROOT/'generated/mouse-hats/active/print-r06';OUT.mkdir(parents=True,exist_ok=True)
report={'units':'mm and mm3','source':str(source.relative_to(ROOT)), 'removed_return_mm3':removed.Volume,'ledge_thickness_mm':.4,'ledge_projection_from_seat_mm':1.6,'ledge_length_mm':3.,'arm_choice':'pending; R04 reference arm retained', 'variants':{}}
def change(old):
    sh=old.cut(removed).removeSplitter();sh.check(True)
    assert sh.isValid() and len(sh.Solids)==1
    assert abs(old.Volume-sh.Volume-removed.Volume)<1e-4
    assert sh.cut(old).Volume<1e-6
    return sh
doc=App.newDocument('FlatLedgeR06');doc.Label='R06 — flat PCB ledge / arm selection pending'
for old in src.Objects:
    if old.TypeId=='Part::Feature':
        o=doc.addObject('Part::Feature',old.Name)
        o.Shape=change(old.Shape) if old.Name in ['Carrier','T3ProtectedTray'] else ledge if old.Name=='UpperCatch' else old.Shape.copy()
        o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
    elif old.TypeId=='Mesh::Feature':
        o=doc.addObject('Mesh::Feature',old.Name);o.Mesh=old.Mesh.copy();o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
info=doc.addObject('App::FeaturePython','Revision');info.addProperty('App::PropertyString','RevisionID');info.RevisionID='MH-T3-EYE-R06'
carrier=doc.Carrier.Shape
for name in ['Holder','Cap','Clip','Baseplate','ApproxPCB','UpperRail']:
    a=src.getObject(name).Shape;b=doc.getObject(name).Shape
    assert a.cut(b).Volume+b.cut(a).Volume<1e-6
    before=src.Carrier.Shape.common(a).Volume;after=carrier.common(b).Volume
    assert abs(before-after)<1e-6
    report[name+'_contact_mm3']=after
report['holder_gap_mm']=carrier.distToShape(doc.Holder.Shape)[0]
assert abs(report['holder_gap_mm']-src.Carrier.Shape.distToShape(src.Holder.Shape)[0])<1e-7
assert ledge.cut(carrier).Volume<1e-6
report['carrier_valid']=True
for letter in 'ABC':
    p=ROOT/('designs/mouse-hats/loop-options-r05/R05-'+letter+'.FCStd')
    variant=App.openDocument(str(p));v=App.newDocument('R06_'+letter);v.Label='R06 '+letter+' — flat PCB ledge'
    for old in variant.Objects:
        if old.TypeId!='Part::Feature':continue
        o=v.addObject('Part::Feature',old.Name);o.Shape=change(old.Shape) if old.Name=='Carrier' else old.Shape.copy()
        o.ViewObject.ShapeColor=old.ViewObject.ShapeColor;o.Visibility=old.Visibility
    v.recompute();v.saveAs(str(HERE/('R06-'+letter+'.FCStd')))
    pair=Part.makeCompound([v.Carrier.Shape,v.Holder.Shape])
    MeshPart.meshFromShape(Shape=pair,LinearDeflection=.03,AngularDeflection=.15,Relative=False).write(str(OUT/('R06-'+letter+'-flat-ledge-carrier-and-holder.stl')))
    report['variants'][letter]={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'removed_mm3':variant.Carrier.Shape.Volume-v.Carrier.Shape.Volume,'holder_gap_mm':v.Carrier.Shape.distToShape(v.Holder.Shape)[0]}
App.setActiveDocument(doc.Name);doc.recompute()
Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
checkpoint=ROOT/'designs/mouse-hats/current/checkpoints/MH-T3-EYE-R06.FCStd'
doc.saveAs(str(checkpoint))
(HERE/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

