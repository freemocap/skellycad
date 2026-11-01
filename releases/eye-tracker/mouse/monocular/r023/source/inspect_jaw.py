from pathlib import Path
import json
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree

O = Path('generated/eye-tracker/mouse/print-r23')
p = json.loads(Path('designs/eye-tracker/mouse/landmark-eyes-r04/placement.json').read_text())
B = np.asarray(p['skull_basis_columns']); origin = np.asarray(p['skull_origin_world_mm'])
meshes = {}
for name, path in [('skull', O.with_name('print-r22')/'skull-print-world.stl'),
                   ('right', O/'right-mandible-world.stl'), ('left', O/'left-mandible-world.stl')]:
    m = trimesh.load_mesh(path); m.vertices = (m.vertices-origin) @ B; meshes[name] = m
    print(name, m.bounds.tolist())
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for ax, (i,j), title in zip(axes, [(0,2),(1,2),(0,1)], ['Side: anterior right', 'Front', 'Top']):
    for (name,m), color in zip(meshes.items(), ['#9b9b9b','#cf4b31','#3987d7']):
        ax.triplot(m.vertices[:,i],m.vertices[:,j],m.faces, color=color, lw=.1, alpha=.3)
    ax.set_aspect('equal'); ax.set_title(title); ax.set_xlabel('mm'); ax.grid(alpha=.2)
fig.tight_layout();fig.savefig(O/'jaw-registration-review.png',dpi=130)
for name in ['right','left']:
    m=meshes[name]; tree=cKDTree(meshes['skull'].vertices); d,ix=tree.query(m.vertices)
    for lower,upper in [(-8,-4),(-4,0),(0,4),(4,8),(8,14)]:
        candidates=np.where((m.vertices[:,0]>lower)&(m.vertices[:,0]<upper))[0]
        if len(candidates):
            v=candidates[np.argmin(d[candidates])];print(name,'x',lower,upper,'gap',d[v],'jaw',m.vertices[v].tolist(),'skull',meshes['skull'].vertices[ix[v]].tolist())
