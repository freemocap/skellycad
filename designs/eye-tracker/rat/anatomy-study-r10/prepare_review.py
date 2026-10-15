from pathlib import Path
import json,hashlib,numpy as np,trimesh
from scipy.spatial import cKDTree
R=Path.cwd();S=R/'designs/eye-tracker/rat/anatomy-study-r10';O=R/'generated/eye-tracker/rat/anatomy-study-r10'
for path in ['designs/eye-tracker/rat/active-model.json','designs/eye-tracker/rat/compact-guard-r09/review.json']:
 a=json.loads((R/path).read_text());assert hashlib.sha256((R/a['native_checkpoint']).read_bytes()).hexdigest()==a['native_sha256']
m=trimesh.load_mesh(O/'ratlas-skull-nominal.stl');small=m.simplify_quadric_decimation(face_count=180000);small.fix_normals(multibody=True);trimesh.smoothing.filter_taubin(small,iterations=5);small.export(O/'ratlas-review.stl')
rows=[{'id':'bregma','name':'Bregma — atlas origin','position_mm':[0.,0.,0.],'status':'Published atlas coordinate origin; not a new manually picked suture','color':[.95,.2,.2]}]
for id,name,q in [('lambda','Lambda — estimated',[-8.5,0,0]),('nasion','Nasion — estimated',[9,0,-2])]:
 pts=m.vertices[np.abs(m.vertices[:,1])<.3];idx=cKDTree(pts).query(q)[1];rows.append({'id':id,'name':name,'position_mm':pts[idx].tolist(),'status':'Local visual candidate; surface-snapped, not an author landmark; requires review','color':[1.,.65,.05]})
for side,sign in [('left',1),('right',-1)]:
 pts=m.vertices[(m.vertices[:,0]>0)&(m.vertices[:,0]<12)&(m.vertices[:,2]>-12)&(m.vertices[:,2]<-3)&(m.vertices[:,1]*sign>0)];p=pts[np.argmax(sign*pts[:,1])];rows.append({'id':side+'zygion','name':side.title()+' cheek-arch lateral extreme','position_mm':p.tolist(),'status':'Geometric extremum within declared orbital-region crop; candidate zygion, not author annotation','color':[.15,.65,1.]})
(S/'landmarks.json').write_text(json.dumps(rows,indent=2))
existing=trimesh.load_mesh(R/'designs/eye-tracker/rat/references/skull/aligned-r01/rat-skull-high-res-refined-aligned-r01.stl')
report={'selected_baseline':'ET-RAT-MONO-R01','latest_complete_review':'ET-RAT-GUARD-R09','source_hashes_verified':True,'new_reference':'Ratlas-LH; adult male Lister hooded average; not a species median','frame':'X anterior, Y animal left, Z superior; bregma origin','review_mesh_faces':len(small.faces),'reference_extent_mm':m.extents.tolist(),'current_skull_extent_mm':existing.extents.tolist(),'extents_not_homologous_landmark_distances':True,'landmark_review_pending':True,'eyes_registered':False,'assembly_changed':False,'source_notes':'Volume grid 0.075 mm; paper describes 0.15 mm effective atlas resolution. Sampling spacing is not anatomical accuracy.'};(S/'audit.json').write_text(json.dumps(report,indent=2));print(rows,report)
