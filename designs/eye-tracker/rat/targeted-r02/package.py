"""Freeze the GUI-reviewed rat candidate after the reproducibility checks."""
from pathlib import Path
import json,hashlib,shutil,zipfile
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;OUT=ROOT/'generated/eye-tracker/rat/targeted-r02';REPLAY=OUT/'replay-check'
recipe=json.loads((HERE/'recipe.json').read_text());validation=json.loads((REPLAY/'validation.json').read_text());containment=json.loads((REPLAY/'anatomy-containment.json').read_text());comparison=json.loads((OUT/'replay-comparison.json').read_text())
assert all(v['samples_inside_skull_bone']==0 for v in containment.values());assert all(v['max_corresponding_vertex_error_mm']<1e-7 for v in comparison.values());assert all(v['skull_surface_crossings']==0 for v in validation['anatomy_surface_checks'].values());assert not any(validation['eye_surface_checks'].values())
working=OUT/'monocular-rat-targeted-r02-review-01.FCStd';digest=hashlib.sha256(working.read_bytes()).hexdigest();folder=HERE/'checkpoints';folder.mkdir(exist_ok=True);frozen=folder/'ET-RAT-MONO-TARGET-R02.FCStd'
if frozen.exists():assert hashlib.sha256(frozen.read_bytes()).hexdigest()==digest,'Preserve checkpoint; use a new revision'
else:shutil.copy2(working,frozen)
manifest={'revision':'ET-RAT-MONO-TARGET-R02','status':'Geometric review candidate; physical seating, focus and nominal JST fit remain provisional','units':'mm','native_checkpoint':frozen.relative_to(ROOT).as_posix(),'native_sha256':digest,'recipe':'designs/eye-tracker/rat/targeted-r02/recipe.json','recipe_sha256':hashlib.sha256((HERE/'recipe.json').read_bytes()).hexdigest(),'source_hardware_manifest':recipe['hardware_manifest'],'source_anatomy':recipe['anatomy'],'validation':validation,'sampled_anatomy_checks':containment,'replay_comparison':comparison,'print_frames':{'carrier-and-holder':'Common mount frame, preserving relative mating pose','separate_cap_clip_baseplate':'Original mouse kit print poses; use native document for skull-frame assembly'},'limitations':['Same nominal JST/tray overlap as mouse R08: about 0.0590 mm^3','Mouse baseplate raised clear of skull, not anatomically contoured or physically seated','Eye geometry and placement schematic; no optical focus or material-fatigue claim']}
(HERE/'review.json').write_text(json.dumps(manifest,indent=2));(OUT/'validation.json').write_text(json.dumps(validation,indent=2));(OUT/'print').mkdir(exist_ok=True)
for file in (REPLAY/'print').glob('*.stl'):shutil.copy2(file,OUT/'print'/file.name)
(OUT/'print/manifest.json').write_text(json.dumps(manifest,indent=2));(OUT/'print/README.txt').write_text('Monocular rat targeted R02. Units mm. Review candidate. Carrier and holder are together in their common mount frame. Cap, clip and baseplate are separate unchanged matched parts in original kit print poses. Native assembly records actual placement. Physical skull seating and nominal JST clearance remain provisional.\n')
with zipfile.ZipFile(OUT/'monocular-rat-R02-print-review.zip','w',zipfile.ZIP_DEFLATED) as archive:
 for file in sorted((OUT/'print').iterdir()):archive.write(file,file.name)
print('Frozen',frozen,'SHA256',digest)
