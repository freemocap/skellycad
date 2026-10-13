"""Validate and export R08A print-in-place candidate."""
from pathlib import Path
import sys,json,zipfile,hashlib,shutil
import FreeCAD as App
import Part,MeshPart
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
for p in [HERE,HERE.parent/'model',HERE.parent/'print-test-r03',HERE.parent/'print-test']:sys.path.insert(0,str(p))
import wide_sweep,wide_carrier_features,socket_revision_features,attachment_arm_features,arm_finish_features,stem_blend_features,retention_features
OUT=ROOT/'generated/mouse-hats/rear-arm-r08';OLD=ROOT/'generated/mouse-hats/print-test/r03'
reference=App.openDocument(str(OLD/'print-in-place-review.FCStd'))
settings=json.loads((HERE/'settings.json').read_text());reports={}
def iso(s):
 t=Part.Shape();t.importBrepFromString(s.exportBrepToString());return t
def overlap(a,b):return iso(a).common(iso(b),0).Volume
for key,variant in settings['variants'].items():
 doc=App.openDocument(str(OUT/('r08'+key.lower()+'-carrier.FCStd')))
 new=doc.RibbonClearanceCarrier.Shape;old=doc.StrongerClearanceCarrier.Shape
 new.check(True)
 d=json.loads(doc.TopArm.DesignJSON);d.update(attachment_radius_mm=2.65,socket_lead_mm=1.,socket_width_mm=3.,socket_thickness_mm=2.2)
 top=attachment_arm_features.geometry(d,3,1.8)[0]
 report={'valid':new.isValid(),'solids':len(new.Solids),'holder_overlap_mm3':overlap(new,reference.Holder.Shape),
 'minimum_joint_gap_mm':new.distToShape(reference.Holder.Shape)[0],
 'rear_arm_to_holder_gap_mm':doc.RearSweepInspection.Shape.distToShape(reference.Holder.Shape)[0],
 'top_boundary_samples_outside_count':sum(not new.isInside(p,.001,True) for p in top.tessellate(.15)[0]),
 'tray_boundary_samples_outside_count':sum(not new.isInside(p,.001,True) for p in doc.TrayReference.Shape.tessellate(.15)[0]),
 'cap_overlap_before_mm3':overlap(old,reference.CapReference.Shape),
 'cap_overlap_after_mm3':overlap(new,reference.CapReference.Shape),
 'baseplate_overlap_mm3':overlap(new,reference.BaseplateReference.Shape),
 'attachment_angle_deg':doc.RibbonClearanceCarrier.AttachmentAngle.Value,'extra_drop_mm':variant['extra_drop_mm'],'volume_mm3':new.Volume}
 print('checking',key,json.dumps(report),flush=True)
 assert report['valid'] and report['solids']==1
 for k in ['holder_overlap_mm3','top_boundary_samples_outside_count','tray_boundary_samples_outside_count','baseplate_overlap_mm3']:assert report[k]<1e-6,(key,k,report[k])
 assert abs(report['cap_overlap_before_mm3']-report['cap_overlap_after_mm3'])<1e-6
 assert abs(report['minimum_joint_gap_mm']-.33172186266949016)<1e-6
 assembly=App.newDocument('R08'+key+'Print');assembly.Label='R08'+key+' - '+variant['label']
 for name in ['Carrier','Holder','ClipReference','CapReference','BaseplateReference']:
  ob=assembly.addObject('Part::Feature',name);ob.Shape=new.copy() if name=='Carrier' else reference.getObject(name).Shape.copy()
 assembly.recompute();assembly.saveAs(str(OUT/('r08'+key.lower()+'-assembly.FCStd')))
 mesh=MeshPart.meshFromShape(Shape=Part.makeCompound([new,reference.Holder.Shape]),LinearDeflection=.03,AngularDeflection=.15,Relative=False)
 assert mesh.isSolid();mesh.write(str(OUT/('R08'+key+'-carrier-and-holder.stl')))
 reports[key]=report;print(key,json.dumps(report),flush=True)
 App.closeDocument(assembly.Name);App.closeDocument(doc.Name)
(OUT/'validation.json').write_text(json.dumps(reports,indent=2)+'\n')
for n in ['clip.stl','cap.stl','baseplate.stl']:shutil.copy2(OLD/n,OUT/n)



