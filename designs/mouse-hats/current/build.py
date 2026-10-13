"""Unify authoritative T3 PCB geometry with the accepted eye/ribbon study.

Run synchronously in the pinned FreeCAD GUI. Local input snapshots contain all
required geometry; historical documents are not selected by open-document name.
"""
from pathlib import Path
import hashlib,json
import FreeCAD as App,FreeCADGui as Gui,Part
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
HERE=Path(__file__).parent;OUT=ROOT/'generated/mouse-hats/active';OUT.mkdir(parents=True,exist_ok=True)
settings=json.loads((HERE/'inputs.json').read_text())
source=HERE/'sources/inputs.FCStd'
assert hashlib.sha256(source.read_bytes()).hexdigest()==settings['input_snapshot_sha256']
src=App.openDocument(str(source));doc=App.newDocument('MouseHatsActive');doc.Label='CURRENT — MH-T3-EYE-R03 — PCB catch + neutral eye + ribbon loop'
def add(name,shape,color,visible=True):
 o=doc.addObject('Part::Feature',name);o.Shape=shape.copy();o.ViewObject.ShapeColor=color;o.Visibility=visible;return o
roi=Part.makeBox(100,100,64.5,App.Vector(-50,-50,-50)).fuse(Part.makeBox(47,100,3.5,App.Vector(3,-50,14.5))).removeSplitter()
tray=src.T3Carrier.Shape.common(roi).removeSplitter()
arms=src.EyeCarrier.Shape.cut(roi).removeSplitter()
carrier=tray.fuse(arms,.0001).removeSplitter();carrier.check(True)
assert carrier.isValid() and len(carrier.Solids)==1
add('Carrier',carrier,(.2,.75,.8));add('Holder',src.Holder.Shape,(.62,.45,.8))
add('Cap',src.T3Cap.Shape,(.85,.65,.2),False);add('Clip',src.Clip.Shape,(.85,.65,.2));add('Baseplate',src.Baseplate.Shape,(.75,.65,.35))
for name in ['UpperCatch','UpperRail','ApproxPCB','LensDatum','EyeTarget','OpticalAxis']:
 o=add(name,src.getObject(name).Shape,(1.,.6,.1),name in ['LensDatum','EyeTarget','OpticalAxis']);o.ViewObject.LineColor=(1.,.1,.1)
add('T3ProtectedTray',tray,(.3,.8,.4),False);add('EyeRibbonArms',arms,(.2,.6,.9),False)
for name in ['Skull','Eye1','Eye2']:
 old=src.getObject(name);o=doc.addObject('Mesh::Feature',name);o.Mesh=old.Mesh.copy();o.Placement=old.Placement;o.ViewObject.ShapeColor=old.ViewObject.ShapeColor
info=doc.addObject('App::FeaturePython','Revision')
for name,value in [('RevisionID',settings['revision']),('PCBBaseline','T3 +1 mm tray, T2 catch/deeper cap, T3 +0.7 mm rail'),('PoseBaseline','R02 eye neutral placement with rigidly preserved R11B rear loop')]:
 info.addProperty('App::PropertyString',name);setattr(info,name,value)
def common(a,b):return a.copy().common(b.copy()).Volume
report={'revision':settings['revision'],'units':'mm, mm3','carrier_valid':carrier.isValid(),'carrier_solids':len(carrier.Solids),'carrier_volume_mm3':carrier.Volume,'holder_gap_mm':carrier.distToShape(doc.Holder.Shape)[0],'holder_overlap_mm3':common(carrier,doc.Holder.Shape),'clip_overlap_mm3':common(carrier,doc.Clip.Shape),'baseplate_overlap_mm3':common(carrier,doc.Baseplate.Shape),'board_overlap_mm3':common(carrier,doc.ApproxPCB.Shape),'cap_contact_mm3':common(carrier,doc.Cap.Shape),'T3_cap_contact_mm3':common(src.T3Carrier.Shape,src.T3Cap.Shape),'catch_missing_mm3':doc.UpperCatch.Shape.cut(carrier).Volume,'rail_missing_mm3':doc.UpperRail.Shape.cut(carrier).Volume,'optical_obstruction_mm':doc.OpticalAxis.Shape.common(carrier).Length}
assert max(report[k] for k in ['holder_overlap_mm3','clip_overlap_mm3','baseplate_overlap_mm3','board_overlap_mm3','catch_missing_mm3','rail_missing_mm3'])<1e-6,report
assert abs(report['cap_contact_mm3']-report['T3_cap_contact_mm3'])<1e-6,report
# Section signatures verify T3 tray geometry away from the two arm splice planes.
sections=[]
for z in [-15,-10,-5,0,5,10,13]:
 a=src.T3Carrier.Shape.slice(App.Vector(0,0,1),z);b=carrier.slice(App.Vector(0,0,1),z)
 av=sorted([w.Length for w in a]);bv=sorted([w.Length for w in b]);err=max([abs(x-y) for x,y in zip(av,bv)],default=0)
 assert len(av)==len(bv) and err<1e-5,(z,av,bv)
 sections.append({'z_mm':z,'wire_count':len(av),'max_wire_length_difference_mm':err})
report['T3_tray_section_checks']=sections
# Preserve exact current holder/clip/target poses and matching cap from input snapshot.
def unchanged(a,b):
 assert len(a.Vertexes)==len(b.Vertexes) and len(a.Edges)==len(b.Edges)
 assert abs(a.Volume-b.Volume)<1e-7 and abs(a.Area-b.Area)<1e-7
 assert max([(x.Point-y.Point).Length for x,y in zip(a.Vertexes,b.Vertexes)],default=0)<1e-7
for name in ['Holder','Clip','OpticalAxis']:unchanged(doc.getObject(name).Shape,src.getObject(name).Shape)
unchanged(doc.Cap.Shape,src.T3Cap.Shape)
doc.recompute();Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
path=OUT/(settings['revision']+'.FCStd');doc.saveAs(str(path))
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
