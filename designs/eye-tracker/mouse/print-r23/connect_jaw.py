"""Join atlas jaw halves and R22 skull with three localized print bridges."""
from pathlib import Path
import json
import hashlib
import numpy as np
import trimesh
import manifold3d as mf
from scipy.spatial import cKDTree
from functools import reduce

R=Path.cwd(); O=R/'generated/eye-tracker/mouse/print-r23'; P=O.with_name('print-r22')
def solid(m):
    s=mf.Manifold(mf.Mesh64(np.asarray(m.vertices,dtype=np.float64),np.asarray(m.faces,dtype=np.uint64)))
    assert s.status()==mf.Error.NoError
    return s
def mesh(s):
    z=s.to_mesh64();return trimesh.Trimesh(np.asarray(z.vert_properties)[:,:3],np.asarray(z.tri_verts),process=False)
skull=trimesh.load_mesh(P/'skull-print-world.stl')
jaws=[trimesh.load_mesh(O/(side+'-mandible-world.stl')) for side in ['right','left']]
pose=json.loads((R/'designs/eye-tracker/mouse/landmark-eyes-r04/placement.json').read_text())
B=np.asarray(pose['skull_basis_columns']);origin=np.asarray(pose['skull_origin_world_mm'])
def anatomical(m):return (m.vertices-origin)@B
records=[];bridges=[]
def bridge(name,a,b,first,second):
    radius=.6
    pieces=[trimesh.creation.cylinder(radius=radius,segment=[a,b],sections=48)]
    for p in [a,b]:
        sphere=trimesh.creation.icosphere(subdivisions=3,radius=radius);sphere.apply_translation(p);pieces.append(sphere)
    s=reduce(lambda a,b:a+b,map(solid,pieces))
    contacts=[(s^solid(m)).volume() for m in [first,second]]
    assert min(contacts)>.02
    records.append({'name':name,'diameter_mm':2*radius,'endpoints_world_mm':[a.tolist(),b.tolist()],
                    'surface_gap_mm':float(np.linalg.norm(a-b)),'contact_volumes_mm3':contacts})
    bridges.append(s)
# Local posterior superior jaw region in the accepted skull frame. These are
# engineering attachment sites, not newly identified author landmarks.
for side,jaw in zip(['right','left'],jaws):
    v=anatomical(jaw); indices=np.where((v[:,0]<0)&(v[:,2]>-6))[0]
    distance,nearest=cKDTree(skull.vertices).query(jaw.vertices[indices]); k=distance.argmin()
    bridge(side+'-posterior-attachment',jaw.vertices[indices[k]],skull.vertices[nearest[k]],jaw,skull)
# A small anterior midline connection joins the two hemi-mandibles directly.
v=anatomical(jaws[0]);w=anatomical(jaws[1])
left=np.where((v[:,0]>5)&(v[:,0]<10)&(v[:,2]<-10))[0]
right=np.where((w[:,0]>5)&(w[:,0]<10)&(w[:,2]<-10))[0]
distance,nearest=cKDTree(jaws[1].vertices[right]).query(jaws[0].vertices[left]);k=distance.argmin()
bridge('anterior-midline-attachment',jaws[0].vertices[left[k]],jaws[1].vertices[right[nearest[k]]],*jaws)
original=reduce(lambda a,b:a+b,map(solid,[skull,*jaws]))
combined=reduce(lambda a,b:a+b,bridges,original)
m=mesh(combined)
assert m.is_volume and len(m.split(only_watertight=False))==1
assert abs((solid(skull)-combined).volume())<1e-5
assert all(abs((solid(jaw)-combined).volume())<1e-5 for jaw in jaws)
m.export(O/'skull-print-world.stl')
saved=trimesh.load_mesh(O/'skull-print-world.stl');assert saved.is_volume and len(saved.split(only_watertight=False))==1
mesh(reduce(lambda a,b:a+b,bridges)).export(O/'print-connections-world.stl')
report={'units':'mm','parent_skull_sha256':hashlib.sha256((P/'skull-print-world.stl').read_bytes()).hexdigest(),
        'connections':records,'added_connection_volume_mm3':(combined-original).volume(),
        'combined_volume_mm3':float(saved.volume),'connected_shells':1,'watertight':True,
        'parent_skull_removed_volume_mm3':(solid(skull)-combined).volume(),
        'mandible_removed_volume_mm3':[(solid(j)-combined).volume() for j in jaws],
        'status':'Fixed atlas pose; engineering bridges; unsliced and unprinted'}
(O/'jaw-connections.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
