"""Freeze the saved R03 review with geometry and visibility evidence."""
from pathlib import Path
import hashlib,json,shutil
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'generated/eye-tracker/rat/targeted-r03'
cfg=json.loads((HERE/'recipe.json').read_text())
validation=json.loads((OUT/'validation.json').read_text())
containment=json.loads((OUT/'anatomy-containment.json').read_text())
visibility=json.loads((OUT/'visibility.json').read_text())
for name in ['HighResSkull','HighResRefined','UserAlignedLowPoly','RetainedPCBTray','RetainedSocket','UpperSupport','RearRibbonGuard','M4_nominal_reference']:
 assert not visibility[name],name
assert visibility['StandardSkull'] and visibility['FinishedCarrier']
for name,row in validation['anatomy_surface_checks'].items():
 if name=='skull_mount_Baseplate':assert row['skull_surface_crossings']>0 and row['contact_policy']=='boolean_cut_stock'
 else:assert row['skull_surface_crossings']==0 and containment[name]['samples_inside_skull_bone']==0
assert not any(validation['eye_surface_checks'].values())
source=OUT/'monocular-rat-targeted-r03-review-01.FCStd'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
folder=HERE/'checkpoints';folder.mkdir(exist_ok=True)
frozen=folder/(cfg['revision']+'.FCStd')
if frozen.exists():assert hashlib.sha256(frozen.read_bytes()).hexdigest()==digest
else:shutil.copy2(source,frozen)
report={'revision':cfg['revision'],'units':'mm','status':'Review candidate; tapered baseplate is uncut Boolean stock, physical fit unverified','native_checkpoint':frozen.relative_to(ROOT).as_posix(),'native_sha256':digest,'recipe_sha256':hashlib.sha256((HERE/'recipe.json').read_bytes()).hexdigest(),'source_hardware_manifest':cfg['hardware_manifest'],'source_anatomy':cfg['anatomy'],'validation':validation,'sampled_anatomy_checks':containment,'visibility':visibility,'limitations':['Baseplate intentionally intersects skull; anatomical Boolean cut is not yet applied.','Eye position and optical reference are schematic.','Inherited nominal JST/tray overlap remains approximately 0.059 mm^3.']}
(HERE/'review.json').write_text(json.dumps(report,indent=2)+'\n')
print(frozen,digest)
