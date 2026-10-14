"""Regression checks for the rejected R01's cutaway rear and porous topology."""
from pathlib import Path
import json, sys
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'generated/eye-tracker/marmoset/skull-print-r02'
SOURCE=ROOT/'designs/eye-tracker/marmoset/references/skull/female_100months_403g.stl'

def source():
    OUT.mkdir(parents=True,exist_ok=True)
    cached=OUT/'source-main.ply'
    if cached.exists():return trimesh.load(cached)
    mesh=trimesh.load(SOURCE)
    mesh=max(mesh.split(only_watertight=False),key=lambda m:len(m.faces))
    mesh.export(cached)
    return mesh

def check(path):
    src=source();mesh=trimesh.load(path)
    # Posterior lateral occipital surface, outside the central neck attachment.
    points=src.vertices[(src.vertices[:,2]<0)&(src.vertices[:,1]<19)&(src.vertices[:,1]>14)&(np.abs(src.vertices[:,0])>7)]
    points=points[::max(1,len(points)//500)]
    _,distance,_=trimesh.proximity.closest_point(mesh,points)
    report=dict(posterior_samples=len(points),posterior_max_loss_mm=float(distance.max()),posterior_p95_loss_mm=float(np.quantile(distance,.95)),euler=int(mesh.euler_number),watertight=bool(mesh.is_watertight))
    print(json.dumps(report,indent=2),flush=True)
    assert report['posterior_p95_loss_mm']<.20, 'Posterior skull surface cut away'
    assert report['euler']>-150, 'Excessive tunnels introduced: porous / Swiss-cheese topology'
    return report

if __name__=='__main__':check(Path(sys.argv[1]))
