"""Convex polygon-face clipping for stable camera-membership partitions (mm)."""
import numpy as np

def box_faces(lo,hi):
    x,y,z=lo;X,Y,Z=hi
    v=np.array([[x,y,z],[X,y,z],[X,Y,z],[x,Y,z],[x,y,Z],[X,y,Z],[X,Y,Z],[x,Y,Z]])
    return [v[list(i)] for i in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))]

def clip(faces,normal,offset):
    """Keep n dot p <= offset; faces retain outward winding."""
    if not faces:return []
    n=np.asarray(normal,float);n=n/np.linalg.norm(n)
    allp=np.concatenate(faces);dist=allp@n-offset
    if dist.max()<=1e-7:return faces
    if dist.min()>=-1e-7:return []
    result=[];cuts=[]
    for face in faces:
        output=[]
        for a,b in zip(face,np.roll(face,-1,axis=0)):
            da,db=a@n-offset,b@n-offset
            if da<=1e-7:output.append(a)
            if (da>1e-7)!=(db>1e-7):
                p=a+(b-a)*da/(da-db);output.append(p);cuts.append(p)
        unique=[]
        for p in output:
            if not unique or np.linalg.norm(p-unique[-1])>1e-7:unique.append(p)
        if len(unique)>2 and np.linalg.norm(unique[0]-unique[-1])<1e-7:unique.pop()
        if len(unique)>=3:result.append(np.array(unique))
    unique=[]
    for p in cuts:
        if not any(np.linalg.norm(p-q)<1e-6 for q in unique):unique.append(p)
    if len(unique)>=3:
        p=np.array(unique);center=p.mean(axis=0);u=p[0]-center;u/=np.linalg.norm(u);v=np.cross(n,u)
        angles=np.arctan2((p-center)@v,(p-center)@u)
        result.append(p[np.argsort(angles)])
    return result

def planes(camera,axes,shift):
    r,u,f=axes;p=np.array(camera['position_mm'])+shift
    ratios=np.array(camera['sensor_mm'])/(2*camera['focal_mm'])*(1-2*camera['edge_margin'])
    normals=[r-ratios[0]*f,-r-ratios[0]*f,u-ratios[1]*f,-u-ratios[1]*f,-f,f]
    offsets=[0,0,0,0,-camera['near_mm'],camera['far_mm']]
    return [(n/np.linalg.norm(n),(n@p+d)/np.linalg.norm(n)) for n,d in zip(normals,offsets)]
