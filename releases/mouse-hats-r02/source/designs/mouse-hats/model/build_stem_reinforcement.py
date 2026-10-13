"""Bounded reinforcement candidate preserving the finished arms and mount fit."""
from pathlib import Path
import json,sys,runpy
import FreeCAD as App
import Part

HERE=Path(__file__).resolve().parent
api=runpy.run_path(str(HERE/'build_mount.py'));api['load_modules']()
ROOT=api['ROOT']
import attachment_arm_features,arm_finish_features
from stem_reinforcement_features import StemReinforcement
OUT=ROOT/'generated/mouse-hats/arms/stem-reinforced'


def validate(doc):
    before=doc.JunctionFillets.Shape;after=doc.ReinforcedCarrier.Shape
    added=after.cut(before,.001);removed=before.cut(after,.001)
    report={'valid':after.isValid(),'solid_count':len(after.Solids),
            'added_mm3':added.Volume,'removed_mm3':removed.Volume,
            'extra_backing_mm':doc.ReinforcedCarrier.ExtraBacking.Value}
    assert report['valid'] and report['solid_count']==1 and removed.Volume<1e-6
    for name,file,objname in [
        ('baseplate','baseplate/01-baseplate-candidate.FCStd','Baseplate'),
        ('cap','pcb-cap/01-pcb-cap-candidate.FCStd','PCBCap')]:
        other=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction'/file))
        report[name+'_overlap_mm3']=after.common(other.getObject(objname).Shape,.001).Volume
        assert report[name+'_overlap_mm3']<1e-6,report
        App.closeDocument(other.Name)
    # No changes in seated stem / lip region below Y=6, or on PCB side of backing.
    for name,guard in [('seated_stem',Part.makeBox(100,56,100,App.Vector(-50,-50,-50))),
                       ('pcb_side',Part.makeBox(50,100,100,App.Vector(5.287063996473035,-50,-50)))]:
        report[name+'_added_mm3']=added.common(guard,.001).Volume
        assert report[name+'_added_mm3']<1e-6
    return report


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    doc=App.openDocument(str(ROOT/'generated/mouse-hats/arms/finished/finished-arm-carrier.FCStd'))
    doc.Label='STEM REINFORCEMENT — tapered rear backing'
    final=doc.addObject('Part::FeaturePython','ReinforcedCarrier')
    final.Label='Carrier — reinforced stem junction (+0.6 mm backing)'
    StemReinforcement(final,doc.JunctionFillets,json.loads((HERE/'stem-reinforcement.json').read_text()))
    doc.recompute();report=validate(doc)
    doc.saveAs(str(OUT/'stem-reinforced-carrier.FCStd'))
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
