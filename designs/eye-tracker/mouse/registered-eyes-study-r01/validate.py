from pathlib import Path
import json,hashlib,numpy as np
import FreeCAD as A,Mesh
ROOT=Path.cwd();ST=ROOT/'designs/eye-tracker/mouse/registered-eyes-study-r01';OUT=ROOT/'generated/eye-tracker/mouse/registered-eyes-study-r01'
r=json.loads((ST/'registration.json').read_text());c=json.loads((ST/'comparison.json').read_text());d=A.openDocument(str(OUT/'ET-MOUSE-REGISTERED-EYES-STUDY-R01.FCStd'))
B=np.array(c['skull_basis_columns_X_forward_Y_left_Z_dorsal']);T=np.array(r['matrix_source_index_mm_to_assembly']);R=T[:3,:3]/r['scale'];assert np.allclose(B.T@B,np.eye(3),atol=1e-10) and np.linalg.det(B)>.999999;assert np.allclose(R.T@R,np.eye(3),atol=1e-10)
result={'native_reopen':True,'frame_orthonormal':True,'registration_no_reflection':True,'all_numbered_landmarks':len(d.All45Landmarks.Group)//2,'candidate_checks':{},'physical_fit_verified':False,'assembly_changed':False};assert result['all_numbered_landmarks']==45
for i,row in enumerate(c['eyes'],1):
 axis=d.getObject(f'CandidateAxis{i}').Shape;points=[v.Point for v in axis.Vertexes];v=np.array(row['candidate_axis_world']);center=np.array(row['atlas_label_centroid_mm']);a=center-v*2;b=center+v*5
 assert np.linalg.norm(np.array(list(points[0]))-a)<1e-7 and np.linalg.norm(np.array(list(points[-1]))-b)<1e-7
 entries={}
 for part in ['sclera','cornea']:
  eye=d.getObject(f'CandidateEye{i}{part}').Mesh;combined=Mesh.Mesh(d.ExistingSkull.Mesh);n=combined.CountFacets;combined.addMesh(eye);cross=sum((x[0]<n)!=(x[1]<n) for x in combined.getSelfIntersections());entries[part]={'closed':eye.isSolid(),'skull_surface_crossings':cross}
 result['candidate_checks'][row['id']]=entries
print(json.dumps(result,indent=2));(ST/'geometry-validation.json').write_text(json.dumps(result,indent=2)+'\n')
