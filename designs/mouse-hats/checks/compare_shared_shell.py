"""Test rigid correspondence of the 3358-triangle shell; no scale or source edit."""
from pathlib import Path
import itertools
import json
import numpy as np
import trimesh
from scipy.spatial import cKDTree

PROJECT=Path(__file__).resolve().parents[1]
WORKSPACE=next(p for p in PROJECT.parents if (p/'tools/cad/toolchain.json').is_file())


def shell(relative):
    raw=trimesh.load_mesh(PROJECT/relative,process=False)
    vertices,inverse=np.unique(raw.vertices,axis=0,return_inverse=True)
    mesh=trimesh.Trimesh(vertices,inverse[raw.faces],process=False)
    candidates=[m for m in mesh.split(only_watertight=False,repair=False) if len(m.faces)==3358]
    assert len(candidates)==1
    return candidates[0]


def main():
    src='old/df-hardware/camera-assembly/cad/57nassembly/57nassembly.stl'
    dst='old/df-hardware/camera-assembly/camera-assembly-2arm-v5.stl'
    a,b=shell(src),shell(dst)
    x,y=a.vertices,b.vertices
    cx,cy=x.mean(axis=0),y.mean(axis=0)
    _,ea=np.linalg.eigh(np.cov((x-cx).T))
    _,eb=np.linalg.eigh(np.cov((y-cy).T))
    tree=cKDTree(y)
    candidates=[]
    for signs in itertools.product((-1,1),repeat=3):
        rotation=ea@np.diag(signs)@eb.T
        if np.linalg.det(rotation)<0:
            continue
        translation=cy-cx@rotation
        moved=x@rotation+translation
        forward=tree.query(moved)[0]
        backward=cKDTree(moved).query(y)[0]
        candidates.append(dict(rotation_row_vector=rotation.tolist(),translation=translation.tolist(),
            rms_vertex_distance=float(np.sqrt(np.mean(forward**2))),
            max_bidirectional_vertex_distance=float(max(forward.max(),backward.max()))))
    candidates.sort(key=lambda c:c['max_bidirectional_vertex_distance'])
    report=dict(source=src,target=dst,source_shell_triangles=3358,target_shell_triangles=3358,
        source_volume_raw=float(a.volume),target_volume_raw=float(b.volume),
        method='PCA principal frames; four proper sign choices; bidirectional nearest-vertex distances; no scaling',
        candidates=candidates,
        limitation='Candidate registration from one shell only; not full assembly parity or physical units confirmation.')
    out=WORKSPACE/'generated/mouse-hats/inspection/shared-shell-registration.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print('Volumes:',a.volume,b.volume)
    print('Candidate max vertex distances:',[c['max_bidirectional_vertex_distance'] for c in candidates])


if __name__=='__main__':
    main()
