"""Check the exported mesh, sampled outer surfaces, core, and visual sections."""
from pathlib import Path
import json
import sys
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from inspect_source import draw, ROOT, OUT, SOURCE
from build import sha, solid, stats

def display(mesh):
    mesh=mesh.copy()
    # Display only: +Z anterior becomes -Y; +Y dorsal becomes +Z.
    mesh.vertices=np.column_stack((mesh.vertices[:,0],-mesh.vertices[:,2],mesh.vertices[:,1]))
    return mesh

def main():
    source=trimesh.load(SOURCE)
    mainpart=max(source.split(only_watertight=False),key=lambda m:len(m.faces))
    path=OUT/'marmoset-skull-print-r01.stl'
    result=trimesh.load(path)
    if '--render-only' in sys.argv:
        render(source,result)
        return
    report=json.loads((OUT/'validation.json').read_text())
    assert sha(path)==report['output']['sha256']
    assert result.is_watertight and result.is_winding_consistent and result.volume>0
    assert len(result.split())==1
    solid(result)
    measured={}
    # Cast first-hit rays at a fixed 0.8 mm grid onto three exterior regions.
    for name,axis,sign in [('dorsal',1,1),('right_side',0,1),('left_side',0,-1),('face',2,1)]:
        axes=[i for i in range(3) if i!=axis]
        grids=[np.arange(mainpart.bounds[0,i],mainpart.bounds[1,i],.8) for i in axes]
        g=np.meshgrid(*grids,indexing='ij')
        origins=np.zeros((g[0].size,3))
        origins[:,axes[0]]=g[0].ravel();origins[:,axes[1]]=g[1].ravel()
        origins[:,axis]=mainpart.bounds[int(sign>0),axis]+sign*5
        directions=np.zeros_like(origins);directions[:,axis]=-sign
        points,_,_=mainpart.ray.intersects_location(origins,directions,multiple_hits=False)
        if name=='dorsal':points=points[(points[:,1]>24)&(points[:,2]>-4)]
        elif name=='face':points=points[points[:,2]>26]
        else:points=points[(np.abs(points[:,0])>9)&(points[:,1]>18)&(points[:,2]>0)]
        _,distances,_=trimesh.proximity.closest_point(result,points)
        measured[name]=dict(samples=len(points),median_mm=float(np.median(distances)),p95_mm=float(np.quantile(distances,.95)),max_mm=float(distances.max()))
        print(name,measured[name],flush=True)
    # Engineering probes, chosen from the source sections; not anatomical landmarks.
    core=np.array([[0,25,z] for z in [0,5,10,15,20]])
    orbits=np.array([[-8,22,29],[8,22,29]])
    assert result.contains(core).all(), 'Braincase fill incomplete at specified probes'
    assert not result.contains(orbits).any(), 'Eye socket probes must stay open'
    assert not result.contains([[0,10,-5],[0,10,-10]]).any(), 'Neck probes must be removed'
    report['surface_comparison']=measured
    report['probes']=dict(braincase_mm=core.tolist(),braincase_all_solid=True,orbit_mm=orbits.tolist(),orbits_open=True,neck_removed=True)
    report['surface_comparison_scope']='First-hit rays at 0.8 mm spacing in named exterior regions; not a Hausdorff bound or full-surface proof. Interior filling and neck cut deliberately excluded.'
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    render(source,result)

def render(source,result):
    fig=plt.figure(figsize=(15,12))
    for row,(e,a,label) in enumerate([(12,-90,'Face'),(10,0,'Side'),(75,-90,'Dorsal')]):
        for col,(m,title) in enumerate([(source,'Original scan'),(result,'Print R01')]):
            ax=fig.add_subplot(4,2,row*2+col+1,projection='3d')
            draw(ax,display(m),e,a)
            lo,hi=display(source).bounds;center=(lo+hi)/2;radius=max(hi-lo)/2
            ax.set(xlim=(center[0]-radius,center[0]+radius),ylim=(center[1]-radius,center[1]+radius),zlim=(center[2]-radius,center[2]+radius))
            ax.set_box_aspect((1,1,1),zoom=1.5)
            ax.set_axis_off();ax.set_title(f'{title} — {label}')
    for col,(m,title) in enumerate([(source,'Original'),(result,'Print R01')]):
        ax=fig.add_subplot(4,2,7+col)
        section=m.section(plane_origin=[0,0,0],plane_normal=[1,0,0])
        for line in section.discrete:ax.plot(-line[:,2],line[:,1],color='#285f8a',linewidth=.7)
        ax.set(xlim=(-40,15),ylim=(-1,37),xlabel='−Z (anterior left, posterior right)',ylabel='Dorsal +Y',title=f'{title} — central section (X = 0)')
        ax.set_aspect('equal');ax.grid(alpha=.2)
    fig.suptitle('Marmoset CT skull: preserved source and simplified print derivative\nDisplay rotated only; exported coordinates are unchanged.',fontsize=14)
    fig.tight_layout(rect=(0,0,1,.95));fig.savefig(OUT/'comparison.png',dpi=150)
if __name__=='__main__':main()
