"""Render source components and sections without modifying the source."""
from pathlib import Path
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'generated/eye-tracker/marmoset/skull-print-r01'
SOURCE = ROOT / 'designs/eye-tracker/marmoset/references/skull/female_100months_403g.stl'

def draw(ax, mesh, elev, azim):
    small = mesh.simplify_quadric_decimation(face_count=100000) if len(mesh.faces)>100000 else mesh
    normals = small.face_normals
    light = np.array([.3, -.4, .85]); light /= np.linalg.norm(light)
    shade = .4 + .6*np.abs(normals @ light)
    colors = np.column_stack((shade*.86, shade*.90, shade*.96, np.ones(len(shade))))
    ax.add_collection3d(Poly3DCollection(small.triangles, facecolors=colors, linewidths=0, rasterized=True))
    lo, hi = mesh.bounds; center=(lo+hi)/2; radius=max(hi-lo)/2
    ax.set(xlim=(center[0]-radius,center[0]+radius),ylim=(center[1]-radius,center[1]+radius),zlim=(center[2]-radius,center[2]+radius),xlabel='X',ylabel='Y',zlabel='Z')
    ax.set_box_aspect((1,1,1)); ax.view_init(elev,azim)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    src=trimesh.load(SOURCE)
    fig=plt.figure(figsize=(15,10))
    for i,(e,a) in enumerate([(15,-60),(0,0),(90,-90),(0,-90)]):
        ax=fig.add_subplot(2,3,i+1,projection='3d');draw(ax,src,e,a);ax.set_title(f'Source: elevation {e}, azimuth {a}')
    for i,(normal,origin) in enumerate([([1,0,0],[0,0,0]),([0,0,1],[0,0,18])]):
        ax=fig.add_subplot(2,3,5+i)
        section=src.section(plane_normal=normal,plane_origin=origin)
        axes=[1,2] if i==0 else [0,1]
        for line in section.discrete: ax.plot(line[:,axes[0]],line[:,axes[1]],linewidth=.5)
        ax.set_aspect('equal');ax.set_title('Section X=0 (Y,Z)' if i==0 else 'Section Z=18 (X,Y)');ax.grid()
    fig.tight_layout();fig.savefig(OUT/'source-inspection.png',dpi=140)
if __name__=='__main__': main()
