"""Rigid camera targeting in explicitly named millimetre frames."""
import numpy as np
from scipy.spatial.transform import Rotation

def rigid(matrix):
    T=np.asarray(matrix,dtype=float)
    if T.shape!=(4,4) or not np.isfinite(T).all(): raise ValueError('Expected finite 4x4 transform')
    R=T[:3,:3]
    if not np.allclose(R.T@R,np.eye(3),atol=1e-8) or not np.isclose(np.linalg.det(R),1,atol=1e-8): raise ValueError('Expected proper rigid rotation; no scale or reflection')
    if not np.allclose(T[3],[0,0,0,1]): raise ValueError('Invalid homogeneous row')
    return T

def aim_sensor(target_mm,lens_position_mm,lens_local_mm,reference_rotation):
    """Keep lens center fixed; minimal rotation takes sensor +Z toward target."""
    target=np.asarray(target_mm);lens=np.asarray(lens_position_mm);R=np.asarray(reference_rotation)
    delta=target-lens;distance=np.linalg.norm(delta)
    if distance<1e-6: raise ValueError('Lens and target coincide')
    z=delta/distance;old=R[:,2];cross=np.cross(old,z);dot=np.clip(old@z,-1,1)
    if dot<-1+1e-9: raise ValueError('Antiparallel aim needs an explicit roll reference')
    K=np.array([[0,-cross[2],cross[1]],[cross[2],0,-cross[0]],[-cross[1],cross[0],0]])
    newR=(np.eye(3)+K+K@K/(1+dot))@R
    T=np.eye(4);T[:3,:3]=newR;T[:3,3]=lens-newR@np.asarray(lens_local_mm)
    rigid(T)
    return T

def axis_error(sensor,lens_local,target):
    T=rigid(sensor);lens=T[:3,:3]@np.asarray(lens_local)+T[:3,3];v=np.asarray(target)-lens;z=T[:3,2]
    return {'axis_miss_mm':float(np.linalg.norm(np.cross(v,z))),'forward_distance_mm':float(v@z),'angle_error_deg':float(np.degrees(np.arctan2(np.linalg.norm(np.cross(v,z)),v@z)))}
