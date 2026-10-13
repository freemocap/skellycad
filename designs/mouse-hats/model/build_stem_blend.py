"""Replacement for the rejected raised stem pad: direct tangent root fillet."""
from pathlib import Path
import json,sys,runpy
import FreeCAD as App
import Part

HERE=Path(__file__).resolve().parent
api=runpy.run_path(str(HERE/'build_mount.py'));api['load_modules']()
ROOT=api['ROOT']
import attachment_arm_features,arm_finish_features
from stem_blend_features import StemBlend
OUT=ROOT/'generated/mouse-hats/arms/stem-blend'


def validate(doc):
    before=doc.JunctionFillets.Shape;after=doc.BlendedCarrier.Shape
    added=after.cut(before,.001);removed=before.cut(after,.001)
    report={'valid':after.isValid(),'solid_count':len(after.Solids),
            'added_mm3':added.Volume,'removed_mm3':removed.Volume,
            'root_blend_radius_mm':doc.BlendedCarrier.RootBlendRadius.Value}
    assert report['valid'] and report['solid_count']==1 and removed.Volume<1e-6
    for name,file,objname in [
        ('baseplate','baseplate/01-baseplate-candidate.FCStd','Baseplate'),
        ('cap','pcb-cap/01-pcb-cap-candidate.FCStd','PCBCap')]:
        other=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction'/file))
        report[name+'_overlap_mm3']=after.common(other.getObject(objname).Shape,.001).Volume
        assert report[name+'_overlap_mm3']<1e-6,report
        App.closeDocument(other.Name)
    guards=[('seated_stem',Part.makeBox(100,56,100,App.Vector(-50,-50,-50))),
            ('pcb_side',Part.makeBox(50,100,100,App.Vector(5.287063996473035,-50,-50)))]
    for name,guard in guards:
        report[name+'_added_mm3']=added.common(guard,.001).Volume
        assert report[name+'_added_mm3']<1e-6
    # Added material must stay local, so the accepted arm/socket finish is intact.
    local=Part.makeBox(4,5,8,App.Vector(1.5,7,-4))
    report['addition_outside_root_mm3']=added.cut(local,.001).Volume
    assert report['addition_outside_root_mm3']<1e-6
    return report


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    doc=App.openDocument(str(ROOT/'generated/mouse-hats/arms/finished/finished-arm-carrier.FCStd'))
    doc.Label='STEM BLEND — continuous stem-to-tray transition'
    final=doc.addObject('Part::FeaturePython','BlendedCarrier')
    final.Label='Complete carrier — tangent stem blend R3 mm'
    StemBlend(final,doc.JunctionFillets,json.loads((HERE/'stem-blend.json').read_text()))
    doc.recompute();report=validate(doc)
    doc.saveAs(str(OUT/'stem-blended-carrier.FCStd'))
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    App.closeDocument(doc.Name)
    doc=App.openDocument(str(OUT/'stem-blended-carrier.FCStd'))
    volume=doc.BlendedCarrier.Shape.Volume;checks=[]
    for r in [2,3]:
        doc.BlendedCarrier.RootBlendRadius=r;doc.recompute();checks.append(validate(doc))
    assert abs(doc.BlendedCarrier.Shape.Volume-volume)<1e-6
    (OUT/'edit-validation.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(report,indent=2));print('Fresh reopen, R2 edit and R3 restore passed.')


if __name__=='__main__':main()
