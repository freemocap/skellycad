from support import *
import hashlib
ll=np.array(json.loads((S.parent/'oval-camera-r21/solution.json').read_text())['lens_local_offset']);result={}
for side in ['Right','Left']:
 result[side]={}
 for rev,path,H in [('R40',R/'generated/eye-tracker/rat/open-supports-r40',np.array(cfg['sides'][side]['previous_head'])),('R41',O,np.array(cfg['sides'][side]['head']))]:
  s=Part.Shape();s.read(str(path/(side+'-ribbon.brep')));l=H[:3,3]+H[:3,:3]@ll;a=H[:3,2];eye=np.array(cfg['sides'][side]['eye_target_mount_mm']);front=3.7-ll[2]+.05;cone=Part.makeCone(1.5,5.,float(np.linalg.norm(eye-l)-front),A.Vector(*(l+front*a)),A.Vector(*a));result[side][rev]={'ribbon_view_volume_overlap_mm3':s.common(cone).Volume}
(O/'view-comparison.json').write_text(json.dumps(result,indent=2));print(result)
