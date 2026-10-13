"""Read-only mesh audit; run from the isolated tools/cad environment."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "generated"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(mesh):
    return {
        "vertices": len(mesh.vertices), "triangles": len(mesh.faces),
        "bounds": mesh.bounds.tolist(), "extents": mesh.extents.tolist(),
        "surface_area": float(mesh.area), "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "volume": float(mesh.volume) if mesh.is_volume else None,
        "euler_number": int(mesh.euler_number),
    }


def inspect(source, output):
    before = digest(source)
    # Exact duplicate STL vertices are welded in memory to recover adjacency.
    # No hole filling, smoothing, normal repair, scaling or transforms.
    mesh = trimesh.load_mesh(source, process=False)
    if not isinstance(mesh, trimesh.Trimesh) or len(mesh.faces) == 0:
        raise ValueError("Expected a nonempty triangle mesh")
    if not np.isfinite(mesh.vertices).all():
        raise ValueError("Mesh has non-finite coordinates")
    _, first, inverse = np.unique(mesh.vertices, axis=0, return_index=True, return_inverse=True)
    mesh = trimesh.Trimesh(mesh.vertices[first], inverse[mesh.faces], process=False)
    components = sorted(mesh.split(only_watertight=False), key=lambda m: (-len(m.faces), tuple(m.bounds[0])))
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "source": source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else str(source),
        "sha256": before, "units": "STL units unknown; dimensions are raw file units",
        "analysis": "Exact coincident vertices welded in memory; no source modifications or repairs",
        "limitations": "Connected shells are not necessarily physical parts. Watertightness does not prove absence of self-intersections or manufacturability.",
        "versions": {name: importlib.metadata.version(name) for name in ["trimesh", "numpy", "scipy", "matplotlib"]},
        **audit(mesh), "connected_components": [dict(id=i + 1, **audit(c)) for i, c in enumerate(components)],
    }
    fig = plt.figure(figsize=(14, 10), facecolor="#f5f7fa")
    center = mesh.bounds.mean(axis=0)
    radius = max(mesh.extents) * .55
    for index, (title, elev, azim) in enumerate([("Perspective", 25, -55), ("XY / top", 90, -90), ("XZ / front", 0, -90), ("YZ / side", 0, 0)], 1):
        ax = fig.add_subplot(2, 2, index, projection="3d" if index == 1 else None)
        axes = {2: (0, 1, 2), 3: (0, 2, 1), 4: (1, 2, 0)}.get(index)
        for i, comp in enumerate(components):
            color = plt.get_cmap("tab10")(i % 10)
            if index == 1:
                ax.add_collection3d(Poly3DCollection(comp.triangles, facecolor=color, edgecolor="none", alpha=1))
            else:
                u, v, depth = axes
                ax.add_collection(PolyCollection(comp.triangles[:, :, [u, v]], facecolor=color, edgecolor="none", alpha=.8))
                p = comp.bounds.mean(axis=0)
                ax.annotate(f"C{i+1}", (p[u], p[v]), xytext=(10+i*2, 12+i*2), textcoords="offset points", fontsize=9, arrowprops={"arrowstyle": "-", "color": "#444444"})
            if len(components) > 1 and index == 1:
                ax.text(*comp.bounds.mean(axis=0), f"C{i+1}", fontsize=10, color="black")
        if index == 1:
            ax.set(xlim=(center[0]-radius, center[0]+radius), ylim=(center[1]-radius, center[1]+radius), zlim=(center[2]-radius, center[2]+radius), xlabel="X", ylabel="Y", zlabel="Z", title=title)
            ax.set_box_aspect((1, 1, 1))
            ax.view_init(elev=elev, azim=azim)
        else:
            u, v, _ = axes
            ax.set(xlim=(mesh.bounds[0,u]-5, mesh.bounds[1,u]+7), ylim=(mesh.bounds[0,v]-5, mesh.bounds[1,v]+7), xlabel="XYZ"[u], ylabel="XYZ"[v], title=title + " · projected shells")
            ax.set_aspect("equal")
            ax.grid(alpha=.2)
    dims = " × ".join(f"{v:.3f}" for v in mesh.extents)
    fig.suptitle(f"{source.name}\nBounds: {dims} raw units · {len(mesh.faces):,} triangles · {len(components)} connected shells\nCoordinates preserved; scale and functional part identities not yet confirmed", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, .92), h_pad=4)
    fig.savefig(output / f"{source.stem}-views.png", dpi=150)
    plt.close(fig)
    if digest(source) != before:
        raise RuntimeError("Source changed during inspection")
    target = output / f"{source.stem}-audit.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(target), "extents": report["extents"], "triangles": report["triangles"], "shells": len(components), "watertight": report["watertight"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Explicit STL path; no client reference is implicit")
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    inspect(args.source.resolve(), args.output.resolve())
