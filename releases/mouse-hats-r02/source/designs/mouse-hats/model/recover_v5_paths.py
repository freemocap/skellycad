"""Recover intact four-vertex sweep rings, socket spheres and tray landmarks."""
from pathlib import Path
import json
import numpy as np
import trimesh
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/arms'
report={'units':'mm','frame':'provisional registered V5, not adopted in CURRENT','arms':{}}
for name,shell,cap in [('rear',4,[28,29]),('top',5,[176,177])]:
    m=trimesh.load_mesh(OUT/f'v5-shell-{shell}.stl',process=True)
    # Pin these seed triangles to this exported mesh; they form a planar end cap.
    assert np.dot(m.face_normals[cap[0]],m.face_normals[cap[1]])>0.99999
    ring=set(m.faces[cap].ravel());seen=set();sections=[]
    while ring:
        assert len(ring)==4, 'Topology no longer describes four-corner sweep rings'
        pts=m.vertices[sorted(ring)];center=pts.mean(axis=0)
        _,_,vt=np.linalg.svd(pts-center)
        angles=np.arctan2((pts-center)@vt[1],(pts-center)@vt[0])
        pts=pts[np.argsort(angles)]
        sections.append(dict(center_mm=center.tolist(),corners_mm=pts.tolist(),
            planarity_error_mm=float(np.max(np.abs((pts-center)@vt[2])))))
        seen.update(ring);ring={j for i in ring for j in m.vertex_neighbors[i]}-seen
    assert len(seen)==len(m.vertices)
    report['arms'][name]=dict(sections=sections,vertex_count=len(m.vertices),
        path_length_mm=float(np.linalg.norm(np.diff([s['center_mm'] for s in sections],axis=0),axis=1).sum()))

tray=trimesh.load_mesh(OUT/'v5-shell-3.stl',process=True)
v=tray.vertices;landmarks=[]
for z in (-12.9033786820894,12.0966213179106):
    radius=np.linalg.norm(v[:,1:]-[11.9423591269588,z],axis=1)
    pts=v[(np.abs(radius-2)<.08)&(v[:,0]>3.5)&(v[:,0]<5.5),1:]
    assert len(pts)>12
    a=np.column_stack((2*pts,np.ones(len(pts))))
    c=np.linalg.lstsq(a,np.sum(pts**2,axis=1),rcond=None)[0]
    rad=np.sqrt(c[2]+c[:2]@c[:2])
    landmarks.append(dict(fitted_yz_mm=c[:2].tolist(),radius_mm=float(rad),
        center_error_mm=float(np.linalg.norm(c[:2]-[11.9423591269588,z])),vertices=len(pts)))
report['vent_landmarks']=landmarks
report['vent_spacing_mm']=float(np.linalg.norm(np.array(landmarks[1]['fitted_yz_mm'])-landmarks[0]['fitted_yz_mm']))
back=v[np.abs(v[:,0]-3.70677424482636)<.06,0]
report['backing_plane_x_median_mm']=float(np.median(back))
report['backing_plane_x_spread_mm']=float(np.ptp(back))

socket=trimesh.load_mesh(OUT/'v5-shell-2.stl',process=True).vertices
rng=np.random.default_rng(47);spheres=[]
for expected in (2.1,2.31730769889371):
    best=None
    for _ in range(4000):
        p=socket[rng.choice(len(socket),4,replace=False)]
        try:c=np.linalg.solve(2*(p[1:]-p[0]),np.sum(p[1:]**2,axis=1)-np.sum(p[0]**2))
        except np.linalg.LinAlgError:continue
        r=np.linalg.norm(p[0]-c)
        if abs(r-expected)>.005:continue
        dist=np.abs(np.linalg.norm(socket-c,axis=1)-r);mask=dist<.002
        if best is None or mask.sum()>best[0]:best=(mask.sum(),mask)
    assert best and best[0]>40
    pts=socket[best[1]];a=np.column_stack((2*pts,np.ones(len(pts))))
    fit=np.linalg.lstsq(a,np.sum(pts**2,axis=1),rcond=None)[0]
    c=fit[:3];r=np.sqrt(fit[3]+c@c)
    spheres.append(dict(center_mm=c.tolist(),radius_mm=float(r),inlier_vertices=int(best[0]),
        max_inlier_radial_error_mm=float(np.max(np.abs(np.linalg.norm(pts-c,axis=1)-r)))))
report['socket_spheres']=spheres
axis=np.array(spheres[1]['center_mm'])-spheres[0]['center_mm']
report['socket_axis_from_inner_to_outer_center']=(axis/np.linalg.norm(axis)).tolist()
report['socket_pose_limit']='Axis and sphere centers recovered; axial roll and holder pose not yet fitted.'
(OUT/'recovered-paths.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='arms'},indent=2))
print([(k,len(v['sections']),v['path_length_mm'],max(s['planarity_error_mm'] for s in v['sections'])) for k,v in report['arms'].items()])
