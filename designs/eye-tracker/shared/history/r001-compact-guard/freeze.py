from pathlib import Path
import json,hashlib,shutil,sys
root=Path(__file__).resolve().parents[4];p=Path(sys.argv[1]).resolve();cfg=json.loads((p/'recipe.json').read_text());sp=cfg['species'];out=root/'generated/eye-tracker'/sp/p.name
validation=json.loads((out/'validation.json').read_text());assert validation['carrier']['valid'] and validation['carrier']['solids']==1
(p/'checkpoints').mkdir(exist_ok=True);native=out/(cfg['revision']+'-final.FCStd');dest=p/'checkpoints'/(cfg['revision']+'.FCStd');shutil.copy2(native,dest)
for name in ['validation.json','guard-anatomy.json','assembly.png']:shutil.copy2(out/name,p/name)
source=json.loads((root/cfg['source_manifest']).read_text());manifest={**source,'revision':cfg['revision'],'native_checkpoint':dest.relative_to(root).as_posix(),'native_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source':cfg['source'],'source_manifest':cfg['source_manifest'],'recipe_sha256':hashlib.sha256((p/'recipe.json').read_bytes()).hexdigest(),'status':'Compact front-edge lower guard; static clearance validated; motion and physical fit unverified','guard_validation':'validation.json','guard_anatomy':'guard-anatomy.json','physical_fit_verified':False,'print_release':False}
(p/'review.json').write_text(json.dumps(manifest,indent=2)+'\n')
mesh_note=('Its mesh is closed with no detected self-intersections.' if not validation['carrier_mesh'].get('self_intersections') else 'Its tessellation has detected surface crossings; the print mesh is withheld. Native CAD review only.')
gap=validation['guard_clearance']['RibbonCandidate']['gap_mm'];holder=validation['guard_clearance']['eye_primary_Holder']['gap_mm']
(p/'README.md').write_text(f'''# {cfg['revision']}: compact lower ribbon guard

The lower guard now starts at the front plate edge below the ribbon, with a
broad 2.6 × 1.8 mm body and the existing full-thickness socket terminal.
The [shared construction note](../../shared/compact-guard-r01/README.md) describes
the route, validation, limitations and rebuild procedure.

Static guard clearance: **{gap:.2f} mm to ribbon**, **{holder:.2f} mm to holder**.
The finished carrier is one valid solid. {mesh_note}
Camera/ribbon/eye poses, upper arm and matched fixtures are
preserved. Existing source interferences remain. Motion clearance and physical
fit have not been demonstrated; this is a complete review assembly, not a print
release. The selected species checkpoint remains unchanged.

Open `open.FCMacro` through the existing desktop pipe to view the generated
review copy. `review.json` identifies the frozen native file under `checkpoints/`.
`validation.json` and `guard-anatomy.json` record the separate checks.
''',encoding='utf-8')
readme=p.parent/'README.md';text=readme.read_text();line=f'\nCompact lower guard: [{cfg["revision"]}]({p.name}/README.md) moves the lower root to the front edge and tightens the loop around the ribbon.\n'
if line.strip() not in text:readme.write_text(text+line)
print('FROZEN',cfg['revision'],manifest['native_sha256'])
