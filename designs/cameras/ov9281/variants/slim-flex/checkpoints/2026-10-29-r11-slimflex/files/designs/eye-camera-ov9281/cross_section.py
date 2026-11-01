"""Quasi-static differential cross-section calculation, lengths in millimetres.

Solve div(epsilon grad(V))=0 on the positive half of an odd-mode pair.
The symmetry plane and ground are 0 V; the positive conductor is 1 V.
Capacitance is its integrated charge per metre. Zdiff=2/(c*sqrt(C*Cair)).
This models an infinitely straight uniform pair, not launches or a full PCB.
Run with the pinned FreeCAD Python, which includes NumPy and SciPy.
"""
import math
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

EPS0=8.8541878128e-12
C0=299792458.0

def capacitance(width, gap, height, copper, er, coat=0., coat_er=1.,
                step=.005, domain=1., guard_gap=None, guard_width=None, conformal=False, air=False, homogeneous=None):
    # Node-centred finite-volume grid. Harmonic means handle dielectric jumps.
    nx=round(domain/step)+1; ny=round((height+domain)/step)+1
    x=np.arange(nx)*step; y=np.arange(ny)*step-height
    X,Y=np.meshgrid(x,y); eps=np.ones_like(X)
    eps[Y<0]=er
    eps[(Y>=0)&(Y<copper+coat)]=coat_er
    if conformal:
        eps[Y>=0]=1
        coating=(Y>=0)&((Y<=coat)|((Y<=copper+coat)&(X>=gap/2-coat)&(X<=gap/2+width+coat)))
        if guard_gap is not None:
            guard_coating=(Y>=0)&(Y<=copper+coat)&(X>=gap/2+width+guard_gap-coat)
            if guard_width is not None:guard_coating&=X<=gap/2+width+guard_gap+guard_width+coat
            coating|=guard_coating
        eps[coating]=coat_er
    if air:eps[:]=1
    if homogeneous is not None:eps[:]=homogeneous
    metal=(X>=gap/2-1e-9)&(X<=gap/2+width+1e-9)&(Y>=-1e-9)&(Y<=copper+1e-9)
    fixed=np.zeros_like(metal);fixed[:,0]=True;fixed[:,-1]=True;fixed[0,:]=True;fixed[-1,:]=True;fixed|=metal
    guard=np.zeros_like(metal)
    if guard_gap is not None:
        guard=(X>=gap/2+width+guard_gap-1e-9)&(Y>=-1e-9)&(Y<=copper+1e-9)
        if guard_width is not None:guard&=X<=gap/2+width+guard_gap+guard_width+1e-9
        fixed|=guard
    voltage=np.zeros_like(X);voltage[metal]=1
    index=np.full(X.shape,-1,dtype=int);index[~fixed]=np.arange(np.count_nonzero(~fixed))
    rows=[];cols=[];data=[];rhs=np.zeros(np.count_nonzero(~fixed));diag=np.zeros_like(rhs)
    for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
        iy,ix=np.where(~fixed); jy,jx=iy+dy,ix+dx
        weight=2*eps[iy,ix]*eps[jy,jx]/(eps[iy,ix]+eps[jy,jx])
        weight=np.where(metal[jy,jx]|guard[jy,jx],eps[iy,ix],weight)
        ids=index[iy,ix];other=index[jy,jx];diag[ids]+=weight
        live=other>=0;rows.extend(ids[live]);cols.extend(other[live]);data.extend(-weight[live])
        rhs[ids[~live]]+=weight[~live]*voltage[jy[~live],jx[~live]]
    rows.extend(np.arange(len(rhs)));cols.extend(np.arange(len(rhs)));data.extend(diag)
    A=coo_matrix((data,(rows,cols)),shape=(len(rhs),len(rhs))).tocsr()
    solution=spsolve(A,rhs);voltage[~fixed]=solution
    residual=float(np.max(np.abs(A@solution-rhs)))
    charge=0.
    for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
        iy,ix=np.where(metal);jy,jx=iy+dy,ix+dx;outside=~metal[jy,jx]
        iy,ix,jy,jx=iy[outside],ix[outside],jy[outside],jx[outside]
        # The material on the nonmetal side sets the displacement flux.
        charge+=np.sum(eps[jy,jx]*(1-voltage[jy,jx]))
    return float(charge*EPS0),residual

def solve(**kwargs):
    c,res=capacitance(**kwargs);ca,resa=capacitance(**kwargs,air=True)
    return {'zdiff_ohm':2/(C0*math.sqrt(c*ca)), 'odd_capacitance_pf_m':c*1e12,
            'effective_er':c/ca,'delay_ps_mm':math.sqrt(c/ca)/C0*1e9,
            'residual':max(res,resa),**kwargs}

if __name__=='__main__':
    import json,sys
    print(json.dumps(solve(**json.loads(sys.argv[1])),indent=2))
