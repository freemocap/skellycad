from pathlib import Path
import sys,json,runpy
import FreeCAD as App
import Part,MeshPart
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
for path in [HERE,HERE.parent/'model',HERE.parent/'print-test']:
    sys.path.insert(0,str(path))
runpy.run_path(str(HERE.parent/'model/build_mount.py'))['load_modules']()
import attachment_arm_features,arm_finish_features,stem_blend_features,retention_features
from socket_revision_features import StrongerSocket
OUT=ROOT/'generated/mouse-hats/print-test/r03';OUT.mkdir(parents=True,exist_ok=True)
settings=json.loads((HERE/'settings.json').read_text())
doc=App.openDocument(str(ROOT/'generated/mouse-hats/print-test/r01/carrier.FCStd'))
pose=json.loads((ROOT/'generated/mouse-hats/print-test/r01/holder-pose.json').read_text())
final=doc.addObject('Part::FeaturePython','StrongerClearanceCarrier')
StrongerSocket(final,doc.LongerPCBRetainers,doc.TrayReference,doc.SocketReference,doc.RearArm,doc.TopArm,settings,pose['ball_center_mm'])
doc.recompute();final.Proxy.execute(final)
doc.Label='R03 - stronger socket connections and freer ball'
doc.saveAs(str(OUT/'carrier.FCStd'))
old=doc.LongerPCBRetainers.Shape;new=final.Shape
assembly=App.openDocument(str(ROOT/'generated/mouse-hats/print-test/r02/print-in-place-review.FCStd'))
report={'valid':new.isValid(),'solids':len(new.Solids),'old_volume_mm3':old.Volume,'new_volume_mm3':new.Volume,
 'min_holder_gap_mm':new.distToShape(assembly.Holder.Shape)[0],
 'holder_overlap_mm3':new.common(assembly.Holder.Shape,.0001).Volume,
 'cap_overlap_mm3':new.common(assembly.CapReference.Shape,.0001).Volume,
 'baseplate_overlap_mm3':new.common(assembly.BaseplateReference.Shape,.0001).Volume}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
