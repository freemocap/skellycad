from pathlib import Path
import json,hashlib
import numpy as np,trimesh
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
R=Path.cwd();S=R/'designs/eye-tracker/rat/symmetric-design-r16';O=R/'generated/eye-tracker/rat/symmetric-design-r16';O.mkdir(parents=True,exist_ok=True)
for f in [S.parent/'active-model.json',S.parent/'symmetry-review-r15/review.json']:
 a=json.loads(f.read_text());assert hashlib.sha256((R/a['native_checkpoint']).read_bytes()).hexdigest()==a['native_sha256']
audit=json.loads((S.parent/'symmetry-review-r15/audit.json').read_text());src=R/'generated/eye-tracker/rat/skull-registration-r12/rat-skull-high-res-refined-atlas-frame-r12.stl';assert hashlib.sha256(src.read_bytes()).hexdigest()==audit['source_sha256']
m=trimesh.load_mesh(src);n=np.array(audit['fits']['whole']['normal']);d=audit['fits']['whole']['offset_mm'];target=np.array([0.,1.,0.]);axis=np.cross(n,target);angle=np.arctan2(np.linalg.norm(axis),n@target);rot=Rotation.from_rotvec(axis/np.linalg.norm(axis)*angle).as_matrix();T=np.eye(4);T[:3,:3]=rot;T[:3,3]=[0,-d,0]
assert np.allclose(rot@n,target);assert abs(np.linalg.det(rot)-1)<1e-12
rigid=m.copy();rigid.apply_transform(T);rigid.export(O/'rat-skull-rigid-r16.stl')
# Preserve original surface detail and topology on one half, rather than warp thin bones.
# Both alternatives are evaluated; choose the half with lower whole-surface discrepancy.
np.random.seed(16);q,_=trimesh.sample.sample_surface(rigid,12000)
candidates=[]
for sign in [1,-1]:
 hv,hf,_=trimesh.intersections.slice_faces_plane(rigid.vertices,rigid.faces,[0,sign,0],[0,0,0]);half=trimesh.Trimesh(hv,hf,process=False)
 half.vertices[np.abs(half.vertices[:,1])<1e-7,1]=0
 reflected=half.copy();reflected.vertices[:,1]*=-1;reflected.faces=reflected.faces[:,::-1]
 sym=trimesh.util.concatenate([half,reflected]);sym.merge_vertices();sym.update_faces(sym.nondegenerate_faces());sym.update_faces(sym.unique_faces());sym.remove_unreferenced_vertices()
 # True point-to-triangle distances on reproducible area samples, both directions.
 _,dist,_=trimesh.proximity.closest_point(sym,q)
 qs,_=trimesh.sample.sample_surface(sym,12000);_,back,_=trimesh.proximity.closest_point(rigid,qs)
 score=float(np.mean(dist**2)+np.mean(back**2));candidates.append((score,sign,sym,dist,back))
score,sign,sym,dist,back=min(candidates,key=lambda c:c[0]);sym.export(O/'rat-skull-symmetric-r16.stl')
reflection=sym.vertices*np.array([1,-1,1]);err=cKDTree(sym.vertices).query(reflection)[0];assert err.max()<1e-6
def stats(x):return {'median':float(np.median(x)),'p95':float(np.percentile(x,95)),'maximum_sampled':float(x.max())}
report={'units':'mm','source_sha256':audit['source_sha256'],'source_frame_to_design_frame':T.tolist(),'rotation_deg':float(np.rad2deg(angle)),'translation_mm':T[:3,3].tolist(),'frame':'Design frame: corrected symmetry plane Y=0; X anterior, Z superior approximately retained. Not the unchanged Ratlas bregma frame.','atlas_origin_in_design_frame':T[:3,3].tolist(),'method':'Rigid alignment followed by exact half-surface reflection; no smoothing, scaling or arbitrary vertex warp. Selected among left/right half reconstructions by bidirectional sampled point-to-triangle squared distance.','retained_half':'left' if sign==1 else 'right','candidate_scores':{('left' if s==1 else 'right'):v for v,s,*_ in candidates},'rigid_to_symmetric_mm':stats(dist),'symmetric_to_rigid_mm':stats(back),'exact_mirror_vertex_max_mm':float(err.max()),'source_watertight':bool(m.is_watertight),'derivative_watertight':bool(sym.is_watertight),'derivative_winding_consistent':bool(sym.is_winding_consistent),'faces':len(sym.faces),'landmarks':[]}
# Re-evaluate paired visible references on the derivative; retain old ones only as provenance.
for name,x,y,z in [('NasalRoof',22,2,None),('RearRoof',-8,5,None),('FrontArch',8,None,-10),('RearArch',-3,None,-10)]:
 for side,s in [('Left',1),('Right',-1)]:
  origin=[x,s*y,10] if y else [x,s*30,z];direction=[0,0,-1] if y else [0,-s,0];hits,_,_=sym.ray.intersects_location([origin],[direction]);p=hits[np.argmin(np.linalg.norm(hits-origin,axis=1))];report['landmarks'].append({'name':side+' '+name,'point':p.tolist(),'label':[x,s*20,3]})
for side,s in [('Left',1),('Right',-1)]:
 v=sym.vertices;v=v[(v[:,1]*s>=0)&(v[:,0]>25)&(v[:,2]>-9)];p=v[np.argmax(v[:,0])];report['landmarks'].append({'name':side+' nasal tip','point':p.tolist(),'label':[35,s*6,3]})
# The existing eye pair is held fixed in the design frame for a controlled comparison.
eyes=json.loads((S.parent/'registered-eyes-r14/placement.json').read_text());whole=trimesh.load_mesh(R/'generated/eye-tracker/adult-eyes-r01/rat-whole.stl');z=np.unique(whole.vertices[:,2]);rad=np.array([np.linalg.norm(whole.vertices[whole.vertices[:,2]==v,:2],axis=1).max() for v in z]);checks=[]
for eye in eyes['eyes']:
 c=np.array(eye['center_mm']);B=np.array(eye['pose'])[:3,:3];tri=sym.triangles[np.linalg.norm(sym.triangles_center-c,axis=1)<7];p=np.vstack([(tri[:,0]*i+tri[:,1]*j+tri[:,2]*(10-i-j))/10 for i in range(11) for j in range(11-i)]);local=(p-c)@B;depth=np.interp(local[:,2],z,rad,left=0,right=0)-np.linalg.norm(local[:,:2],axis=1);checks.append({'side':eye['side'],'sampled_radial_penetration_mm':float(max(0,depth.max())),'samples':len(p)})
report['eyes_held_at_R14_design_coordinates']=True;report['eye_clearance_sample_check']=checks
(S/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))


