"""Exact-coordinate welded mesh audit; imported source files remain untouched."""
from pathlib import Path
import hashlib
import json
import numpy as np
import trimesh

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = next(p for p in PROJECT.parents if (p/'tools/cad/toolchain.json').is_file())


def describe(mesh):
    return dict(triangles=len(mesh.faces), bounds_raw=mesh.bounds.tolist(),
                extents_raw=mesh.extents.tolist(), watertight=bool(mesh.is_watertight),
                winding_consistent=bool(mesh.is_winding_consistent),
                volume_raw=float(mesh.volume) if mesh.is_watertight else None)


def main():
    results=[]
    for path in sorted((PROJECT/'old/df-hardware').rglob('*.stl')):
        mesh=trimesh.load_mesh(path, process=False)
        vertices,inverse=np.unique(mesh.vertices,axis=0,return_inverse=True)
        welded=trimesh.Trimesh(vertices=vertices,faces=inverse[mesh.faces],process=False)
        components=welded.split(only_watertight=False, repair=False)
        result=dict(source=path.relative_to(PROJECT).as_posix(),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    units='raw STL coordinates; physical units unconfirmed',
                    summary=describe(welded),
                    components=[dict(id=i+1,**describe(m)) for i,m in enumerate(components)])
        results.append(result)
    out=WORKSPACE/'generated/mouse-hats/inspection'
    out.mkdir(parents=True,exist_ok=True)
    (out/'mesh-inventory.json').write_text(json.dumps(results,indent=2)+'\n')
    for r in results:
        if '/57nassembly/' in r['source'] or '2arm-v5.stl' in r['source']:
            print(r['source'],r['summary'],'components:',len(r['components']))
    print('Audited',len(results),'STL files; no source edits or repair.')


if __name__=='__main__':
    main()
