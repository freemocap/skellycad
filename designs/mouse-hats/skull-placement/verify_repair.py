from pathlib import Path
import json
import numpy as np
import trimesh
from scipy.spatial import cKDTree
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-placement'
a=trimesh.load_mesh(OUT/'solid-0.stl');b=trimesh.load_mesh(OUT/'skull-repaired.stl')
components=sorted(b.split(only_watertight=False,repair=False),key=lambda m:len(m.faces),reverse=True)
# Preserve the main skull; record any disconnected voxel debris explicitly.
b=components[0];b.export(OUT/'skull-repaired-main.stl')
samples,_=trimesh.sample.sample_surface(b,3000,seed=42)
# Exact candidate bound: nearest vertex is an upper bound on surface distance.
# A closer triangle must have its centroid within that bound plus its radius.
dist=[]
centroids=a.triangles.mean(axis=1);radii=np.linalg.norm(a.triangles-centroids[:,None,:],axis=2).max(axis=1)
tree=cKDTree(centroids);upper=cKDTree(a.vertices).query(samples)[0]
for point,bound in zip(samples,upper):
 ids=np.array(tree.query_ball_point(point,bound+radii.max()))
 ids=ids[np.linalg.norm(centroids[ids]-point,axis=1)<=bound+radii[ids]+1e-9]
 closest=trimesh.triangles.closest_point(a.triangles[ids],np.tile(point,(len(ids),1)))
 dist.append(np.linalg.norm(closest-point,axis=1).min())
dist=np.array(dist)
report=dict(watertight=bool(b.is_watertight),winding_consistent=bool(b.is_winding_consistent),volume_mm3=float(b.volume),volume_change_percent=float(100*(b.volume/a.volume-1)),components=len(components),discarded_component_faces=[len(c.faces) for c in components[1:]],sampled_repaired_to_original_surface_mm=dict(samples=len(samples),median=float(np.median(dist)),p95=float(np.quantile(dist,.95)),max=float(dist.max())),note='One-way sampled surface deviation, not a Hausdorff bound or anatomical validation.')
p=json.loads((OUT/'placement.json').read_text())['stl_to_assembly'];b.vertices=b.vertices@np.array(p['rotation_row_vector'])+p['translation_mm'];b.export(OUT/'placed-skull-repaired.stl')
(OUT/'repair-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
