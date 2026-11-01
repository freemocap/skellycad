"""Validate the specific rear, socket, and topology defects in R01."""
import json
from pathlib import Path
import numpy as np
import trimesh
from check_defects import source,check,OUT,ROOT
from build import sha,solid,stats,HASH,SOURCE

def summaries(d):return dict(samples=len(d),median_mm=float(np.median(d)),p95_mm=float(np.quantile(d,.95)),maximum_mm=float(d.max()))

def main():
    assert sha(SOURCE)==HASH
    src=source();report=json.loads((OUT/'build-report.json').read_text())
    name='marmoset-skull-print-r02.stl';path=OUT/name
    model=trimesh.load(path)
    assert sha(path)==report['outputs'][name]['sha256']
    assert model.is_watertight and model.is_winding_consistent and model.volume>0
    assert len(model.split())==1;solid(model)
    report['defect_regression']=check(path)
    xx,zz=np.meshgrid(np.arange(-15,15.1,.65),np.arange(-8,25,.65))
    origins=np.column_stack((xx.ravel(),np.full(xx.size,50.),zz.ravel()))
    protected,_,_=src.ray.intersects_location(origins,np.tile([0,-1,0],(len(origins),1)),multiple_hits=False)
    protected=protected[protected[:,1]>29]
    _,d,_=trimesh.proximity.closest_point(model,protected)
    report['outer_vault']=summaries(d)
    assert np.quantile(d,.95)<.06,report['outer_vault']
    neck_removed=trimesh.load(OUT/'source-neck-removed.stl')
    neck_removed=max(neck_removed.split(only_watertight=False),key=lambda m:abs(m.volume))
    detailed=trimesh.load(OUT/'marmoset-skull-detailed-r02.stl')
    removed=solid(neck_removed)-solid(detailed)
    report['unintentionally_removed_material_mm3']=float(removed.volume())
    assert abs(removed.volume())<.001, 'Additive repairs removed original bone'
    xy=np.array([[3.,19.],[3.25,19.],[3.,19.25]])
    origins=np.column_stack((xy,np.full(len(xy),50.)))
    socket_checks={}
    for label,obj in [('original',src),('r02',model)]:
        hits,rays,_=obj.ray.intersects_location(origins,np.tile([0,0,-1],(len(xy),1)),multiple_hits=False)
        depths=np.full(len(xy),np.nan);depths[rays]=hits[:,2]
        socket_checks[label]=depths.tolist()
    report['socket_hole_probes']=dict(xy_mm=xy.tolist(),first_hit_z_mm=socket_checks)
    assert np.isfinite(socket_checks['r02']).all() and min(socket_checks['r02'])>14, 'Small socket hole remains open'
    probes=np.array([[x,y,z] for x in [-4,0,4] for y in [23,25,27] for z in [4,8,12,16]])
    inside=model.contains(probes)
    assert inside.all(), 'Braincase has unfilled interior at sampled positions'
    assert not model.contains([[0,7,-8],[0,7,-11]]).any(), 'Neck remains'
    report['braincase_probes']=dict(count=len(probes),all_solid=True,points_mm=probes.tolist())
    report['status']='Geometric and defect regression checks passed; rendered close-up review required. No slicing or physical print validation.'
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['outer_vault','socket_hole_probes','unintentionally_removed_material_mm3']},indent=2))

if __name__=='__main__':main()
