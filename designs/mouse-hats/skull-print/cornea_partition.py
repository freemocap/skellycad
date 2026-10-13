"""Partition the existing eye surface at its two-spheroid intersection ring."""
import numpy as np
import trimesh

def partition(eye,fit):
 body_vertices=set(eye.faces[fit['body_faces']].ravel())
 cornea_vertices=set(eye.faces[fit['cornea_faces']].ravel())
 assert not body_vertices.intersection(cornea_vertices)
 seam=set(range(len(eye.vertices)))-body_vertices-cornea_vertices
 assert len(seam)==32
 assert not any(any(v in body_vertices for v in f) and any(v in cornea_vertices for v in f) for f in eye.faces)
 cap_mask=np.array([not any(v in body_vertices for v in f) for f in eye.faces])
 surface=eye.faces[cap_mask]
 edges=np.vstack([surface[:,[0,1]],surface[:,[1,2]],surface[:,[2,0]]])
 _,inv,counts=np.unique(np.sort(edges,axis=1),axis=0,return_inverse=True,return_counts=True)
 boundary=edges[counts[inv]==1]
 assert len(boundary)==32 and set(boundary.ravel())==seam
 center=eye.vertices[list(seam)].mean(axis=0)
 verts=np.vstack([eye.vertices,center]);ci=len(verts)-1
 # Opposite winding on each side of exactly the same internal closing fan.
 closing=np.array([[b,a,ci] for a,b in boundary])
 cornea=trimesh.Trimesh(verts,np.vstack([surface,closing]),process=True)
 sclera=trimesh.Trimesh(verts,np.vstack([eye.faces[~cap_mask],closing[:,::-1]]),process=True)
 assert cornea.is_volume and sclera.is_volume
 assert abs(cornea.volume+sclera.volume-eye.volume)<1e-9
 return cornea,sclera,dict(boundary_vertices=32,cornea_surface_triangles=int(cap_mask.sum()),sclera_surface_triangles=int((~cap_mask).sum()),boundary_center_mm=center.tolist(),surface_geometry_preserved=True)
