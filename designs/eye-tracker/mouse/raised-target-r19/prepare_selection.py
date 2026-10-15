from pathlib import Path
import json,sys,hashlib
import FreeCAD as A,Part,Mesh
R=Path.cwd();S=R/'designs/eye-tracker/mouse/raised-target-r19';O=R/'generated/eye-tracker/mouse/raised-target-r19';d=A.openDocument(str(O/'ET-MOUSE-RAISED-TARGET-R19.FCStd'));sol=json.loads((S/'solution.json').read_text());M=A.Placement(A.Matrix(*sum(sol['mount_to_skull'],[])));sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
record=json.loads((S.parent/'compact-guard-r16/review.json').read_text());source=A.openDocument(str(R/record['native_checkpoint']))
for n in ['eye_primary_UpperCatch','eye_primary_UpperRail','eye_primary_SideLedge']:
 o=d.getObject(n);shape=world(source.getObject(n));shape.Placement=M.multiply(shape.Placement);assign(o,shape)
d.Revision.RevisionID='ET-MOUSE-RAISED-TARGET-R19';d.recompute();d.save()
manifest=json.loads((S/'previous-active-model.json').read_text());manifest.update(revision=d.Revision.RevisionID,status='Selected complete raised mount and aimed camera; physical fit pending',native_checkpoint='',native_sha256='',print_directory='generated/eye-tracker/mouse/print-raised-target-r19',build_script='designs/eye-tracker/mouse/raised-target-r19/build.py',lineage='designs/eye-tracker/mouse/raised-target-r19/recipe.json',validation='designs/eye-tracker/mouse/raised-target-r19/validation.json');manifest['parts']['eye_primary_Carrier']='FinishedCarrier';station=manifest['camera_instances'][0];station['camera']='pupil-core-eye-r08';station['mount']='raised-target-r19';station['objects'].update(Carrier='FinishedCarrier',ApproxPCB='camera_pcb',OpticalAxis='DetailedOpticalAxis');station['objects'].pop('LensDatum',None);sys.path.insert(0,str(R/'designs/eye-tracker'));from shared.validation import validate_selected
validate_selected(d,manifest)
# Check the accepted R18 baseplate is reproduced, not merely offset visually.
base=Part.Shape();base.read(str(S.parent/'anatomical-mount-r17/baseline-baseplate-world.brep'));base.Placement=M.multiply(base.Placement);actual=world(d.skull_mount_Baseplate);diff=actual.cut(base).Volume+base.cut(actual).Volume;assert diff<1e-6
(S/'candidate-manifest.json').write_text(json.dumps(manifest,indent=2));(O/'selection-validation.json').write_text(json.dumps({'matched_parts_pass':True,'R18_baseplate_difference_mm3':diff,'rear_hole_clearance_inherited_mm':5.058031955568655},indent=2));print('MATCHED PARTS AND R18 PLACEMENT PASS')
