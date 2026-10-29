"""Verify the GUI save and align the comparison using global placements once."""
from pathlib import Path
import FreeCAD as App,Part,json,hashlib,shutil
from verify_r11_native import measurements
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'generated/ov9281-r11-mechanics';PATH=OUT/'OV9281-R11-MATCHED.FCStd'
def global_shape(o):
    s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s
def main():
    baseline=OUT/'before-first-render.FCStd';assert not baseline.exists();shutil.copy2(OUT/'OV9281-R11-MATCHED.20261029-004128.FCBak',baseline)
    old=App.openDocument(str(baseline));expected=measurements(old);App.closeDocument(old.Name)
    doc=App.openDocument(str(PATH));assert measurements(doc)==expected,'First GUI save changed geometry';print('First GUI save geometry verified',flush=True)
    pupil=doc.getObject('PupilReference');shapes=[global_shape(o) for o in pupil.PhysicalParts];bb=Part.makeCompound(shapes).BoundBox;pupil.Placement.Base+=App.Vector(-bb.XMin,25-bb.YMin,0)
    q=doc.addObject('App::Annotation','PupilReferenceLabel');q.LabelText=['Pupil R08 reference — approximate photo electronics'];q.Position=App.Vector(0,39,0);q.addProperty('App::PropertyBool','ReviewVisible','Review').ReviewVisible=False
    hb=Part.makeCompound([global_shape(o) for o in doc.getObject('Bent_head').OutListRecursive if o.TypeId=='Part::Feature' and o.Shape.Solids]).BoundBox
    cb=Part.makeCompound([global_shape(o) for o in doc.getObject('Bent_controller').OutListRecursive if o.TypeId=='Part::Feature' and o.Shape.Solids]).BoundBox
    assert hb.ZMin>cb.ZMax;doc.recompute();(OUT/'geometry-measurements.json').write_text(json.dumps(measurements(doc),indent=2)+'\n');doc.save();App.closeDocument(doc.Name)
    p=OUT/'validation.json';r=json.loads(p.read_text());r['native_sha256']=hashlib.sha256(PATH.read_bytes()).hexdigest();r['independent_reload']['bent_head_controller_z_separation_mm']=hb.ZMin-cb.ZMax;r['reference_alignment']='Pupil and R11 minimum X aligned, Pupil minimum Y=25 mm; global placement applied once';p.write_text(json.dumps(r,indent=2)+'\n');print('Aligned reference; bend separation',hb.ZMin-cb.ZMax,flush=True)
if __name__=='__main__':main()
