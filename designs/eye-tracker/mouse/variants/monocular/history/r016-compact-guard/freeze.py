from pathlib import Path
import json,hashlib,shutil
R=Path.cwd();S=R/'designs/eye-tracker/mouse/compact-guard-r16';O=R/'generated/eye-tracker/mouse/compact-guard-r16';v=json.loads((O/'validation.json').read_text());a=json.loads((O/'guard-anatomy.json').read_text());assert v['carrier']['valid'] and v['carrier']['solids']==1;assert v['carrier_mesh']['closed'] and not v['carrier_mesh']['self_intersections'];assert all(x['guard_surface_crossings']==0 for x in a.values());cp=S/'checkpoints';cp.mkdir(exist_ok=True);dst=cp/'ET-MOUSE-GUARD-R16.FCStd';shutil.copy2(O/dst.name,dst)
for n in ['validation.json','guard-anatomy.json','assembly.png']:shutil.copy2(O/n,S/n)
(S/'review.json').write_text(json.dumps({'revision':'ET-MOUSE-GUARD-R16','native_checkpoint':dst.relative_to(R).as_posix(),'native_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'source':v['source'],'units':'mm','status':'complete review assembly','physical_fit_verified':False},indent=2))
amount=v['carrier']['new_guard_xmin_mm']-v['carrier']['old_guard_xmin_mm'];gap=v['guard_clearance']['RibbonCandidate']['gap_mm'];holder=v['guard_clearance']['eye_primary_Holder']['gap_mm']
(S/'README.md').write_text(f'''# Compact back loop — R16

R16 brings the R15 back loop inward. Its outer control point moves from X=-12 to X=-8 mm; the actual outer envelope moves inward {amount:.2f} mm. The root, socket terminal, 2.6 x 1.8 mm body section, camera alignment, neutral joint, ribbon route, upper arm and anatomy are preserved.

The loop clears the ribbon by {gap:.2f} mm and holder by {holder:.2f} mm. Solid checks show no new interference, preserved protected attachment material and one valid finished carrier solid. The carrier mesh is closed with no detected self-intersections. Guard/anatomy surface checks pass. Static geometry validation does not establish full joint motion clearance or physical fit.

`recipe.json` pins the R15 source hash and parameters. Rebuild with the pinned FreeCAD Python runtime and `designs/eye-tracker/shared/compact-guard-r02/build.py`, passing this recipe. Follow `docs/development.md` for runtime setup and existing-window review. Run this directory's `check_anatomy.py mouse` after building, then open `open.FCMacro` through the verified desktop pipe. Freeze only after the final GUI save and passing checks. `review.json` identifies the frozen native checkpoint; the selected active model remains unchanged.
''',encoding='utf-8')
p=S.parent/'README.md';p.write_text(p.read_text(encoding='utf-8')+'\nCompact back loop: [R16](compact-guard-r16/README.md) tightens the loop around the unchanged R15 ribbon and camera pose.\n',encoding='utf-8');print('FROZEN',amount,gap,holder)
