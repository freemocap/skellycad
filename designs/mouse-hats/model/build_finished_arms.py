"""Finish the checkpointed arm concept in a separate, reproducible candidate."""
from pathlib import Path
import json, sys
import FreeCAD as App
import Part

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
sys.path.insert(0, str(HERE))
import attachment_arm_features
from arm_finish_features import JunctionFillets
OUT = ROOT/'generated/mouse-hats/arms/finished'


def validate(doc):
    original = doc.CompleteCarrier.Shape; final = doc.JunctionFillets.Shape
    final.check(True)
    added = final.cut(original, .001); removed = original.cut(final, .001)
    data = json.loads(doc.RearArm.DesignJSON)
    center = App.Vector(*data['socket_center_mm'])
    axis = attachment_arm_features.unit(data['socket_axis'])
    guards = {'screw_bore': Part.makeCylinder(1.45, 10, center, axis),
              'ball_seat': Part.makeSphere(2.1, center)}
    capdoc = App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction/pcb-cap/01-pcb-cap-candidate.FCStd'))
    guards['pcb_cap'] = capdoc.PCBCap.Shape
    report = {'valid': final.isValid(), 'solids': len(final.Solids),
              'added_mm3': added.Volume, 'removed_mm3': removed.Volume,
              'original_mm3': original.Volume, 'finished_mm3': final.Volume,
              'tray_radius_mm': doc.JunctionFillets.TrayRootRadius.Value,
              'socket_radius_mm': doc.JunctionFillets.SocketRootRadius.Value}
    assert report['valid'] and report['solids'] == 1
    assert removed.Volume < 1e-6
    for name, guard in guards.items():
        overlap = added.common(guard, .001).Volume
        report[name+'_added_overlap_mm3'] = overlap
        assert overlap < 1e-6, (name, overlap)
    # Only local junction neighborhoods may change. This also protects the stem,
    # vents, PCB grooves and socket opening from distant fillet propagation.
    zones = [Part.makeSphere(3, App.Vector(*data['arm']['root_mm'])),
             Part.makeSphere(3, App.Vector(*json.loads(doc.TopArm.DesignJSON)['arm']['root_mm'])),
             Part.makeCylinder(4, 2.6, center+axis*2.6, axis)]
    outside = (added.cut(zones[0].fuse(zones[1]).fuse(zones[2]), .001).Volume
               if added.Solids else 0.0)
    report['addition_outside_junction_regions_mm3'] = outside
    assert outside < 1e-6
    App.closeDocument(capdoc.Name)
    return report


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    doc = App.openDocument(str(ROOT/'generated/mouse-hats/arms/attachments/attachment-arm-concept.FCStd'))
    doc.Label = 'ARM FINISH — strengthened junctions'
    feature = doc.addObject('Part::FeaturePython', 'JunctionFillets')
    feature.Label = 'Finished carrier — tray R0.5 / socket R0.3 mm'
    JunctionFillets(feature, doc.CompleteCarrier, doc.RearArm, doc.TopArm,
                    json.loads((HERE/'arm-finishing.json').read_text()))
    doc.recompute()
    report = validate(doc)
    doc.saveAs(str(OUT/'finished-arm-carrier.FCStd'))
    (OUT/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2), flush=True)
    return doc


if __name__ == '__main__': main()
