from pathlib import Path
import sys,json,hashlib,shutil
root=Path(__file__).resolve().parents[4];folder=Path(sys.argv[1]).resolve();cfg=json.loads((folder/'recipe.json').read_text());out=root/'generated/eye-tracker'/cfg['species']/folder.name
checkpoint=folder/'checkpoints';checkpoint.mkdir(exist_ok=True)
native=out/(cfg['revision']+'.FCStd');dest=checkpoint/native.name;shutil.copy2(native,dest)
for name in ['validation.json','anatomy-surfaces.json','anatomy-containment.json','assembly.png']:
 shutil.copy2(out/name,folder/name)
report=json.loads((out/'validation.json').read_text())
m={'revision':cfg['revision'],'units':'mm','status':'Detailed camera integrated; holder and ribbon interference retained for next fitting revision','native_checkpoint':dest.relative_to(root).as_posix(),'native_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source':cfg['source'],'camera_manifest':cfg['camera_manifest'],'camera_manifest_sha256':cfg['camera_manifest_sha256'],'recipe_sha256':hashlib.sha256((folder/'recipe.json').read_bytes()).hexdigest(),'parts':{'carrier':'FinishedCarrier','holder':'eye_primary_Holder','cap':'eye_primary_Cap','clip':'eye_primary_Clip','baseplate':'skull_mount_Baseplate'},'new_interferences':report['new_interferences'],'ribbon_interference':report['ribbon_interference'],'physical_fit_verified':False,'print_release':False}
(folder/'review.json').write_text(json.dumps(m,indent=2)+'\n');print('REVIEW_FROZEN',dest)
