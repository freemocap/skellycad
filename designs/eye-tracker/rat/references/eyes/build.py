"""Build schematic exterior meshes from parameters.json; see README.md.

Run with tools/cad/.venv/Scripts/python.exe. Outputs default to ignored generated/.
The original mouse mesh and rat assembly are not inputs or mutation targets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def arc(a, b, center, start, end, intervals):
    angles = np.linspace(start, end, intervals + 1)
    if end < np.pi / 2 < start:
        angles = np.unique(np.append(angles, np.pi / 2))[::-1]
    return np.column_stack((a * np.sin(angles), center + b * np.cos(angles)))


def profile(p, construction):
    v, sampling = p['literature_inputs'], p['mesh']
    length, a = v['external_axial_length_mm'], v['nasotemporal_diameter_mm'] / 2
    tip, back = length / 2, -length / 2
    if construction == 'single_spheroid':
        outline = arc(a, length / 2, 0, np.pi, 0,
                      sampling['body_intervals'] + sampling['cap_intervals'])
        meta = dict(body_radial_semiaxis_mm=a, body_axial_semiaxis_mm=length / 2,
                    body_center_z_mm=0., limbus_z_mm=None,
                    anterior_pole_radius_mm=a*a/(length/2))
        pieces = [(a, length / 2, 0., back, tip)]
    else:
        radius, limbus = v['anterior_cornea_radius_mm'], v['cornea_base_radius_mm']
        if construction == 'spherical_cap':
            cap_a = cap_b = radius
            height = radius - np.sqrt(radius**2 - limbus**2)
        elif construction == 'oblate_cap':
            height = v['cornea_height_mm']
            cap_b = radius * height**2 / (2 * radius * height - limbus**2)
            cap_a = np.sqrt(radius * cap_b)
        else:
            raise ValueError(construction)
        q = np.sqrt(1 - (limbus/a)**2)
        b = (length-height)/(1+q)
        center, seam, cap_center = back+b, tip-height, tip-cap_b
        body = arc(a, b, center, np.pi, np.arccos(q), sampling['body_intervals'])
        cap = arc(cap_a, cap_b, cap_center, np.arccos(1-height/cap_b), 0,
                  sampling['cap_intervals'])
        if not np.allclose(body[-1], cap[0], atol=1e-10):
            raise ValueError('Cap and body do not meet')
        outline = np.vstack((body, cap[1:]))
        meta = dict(body_radial_semiaxis_mm=a, body_axial_semiaxis_mm=float(b),
                    body_center_z_mm=float(center), limbus_z_mm=float(seam),
                    cornea_sag_mm=float(height), cap_radial_semiaxis_mm=float(cap_a),
                    cap_axial_semiaxis_mm=float(cap_b), cap_center_z_mm=float(cap_center),
                    anterior_pole_radius_mm=float(cap_a**2/cap_b))
        pieces = [(a, b, center, back, seam), (cap_a, cap_b, cap_center, seam, tip)]
    outline[[0, -1], 0] = 0
    # Each surface is single-valued in z, so revolving this positive monotone
    # profile creates an exterior without intersecting or internal shells.
    assert np.all(np.diff(outline[:, 1]) > 0)
    assert np.all(outline[1:-1, 0] > 0)
    volume = 0.
    for ra, rb, center, low, high in pieces:
        def integral(z):
            return np.pi * ra**2 * ((z-center) - (z-center)**3/(3*rb**2))
        volume += integral(high) - integral(low)
    meta['posterior_pole_radius_mm'] = a*a/meta['body_axial_semiaxis_mm']
    meta['analytic_volume_mm3'] = float(volume)
    return outline, meta


def revolve(outline, count):
    theta = np.arange(count) * 2*np.pi/count
    vertices = [[0., 0., outline[0, 1]]]
    for rho, z in outline[1:-1]:
        vertices.extend(np.column_stack((rho*np.cos(theta), rho*np.sin(theta),
                                         np.full(count, z))).tolist())
    top = len(vertices)
    vertices.append([0., 0., outline[-1, 1]])
    faces = []
    rings = len(outline)-2
    for j in range(count):
        k = (j+1) % count
        faces.append([0, 1+k, 1+j])
        for ring in range(rings-1):
            low, high = 1+ring*count, 1+(ring+1)*count
            faces.extend(([low+j, low+k, high+k], [low+j, high+k, high+j]))
        last = 1+(rings-1)*count
        faces.append([last+j, last+k, top])
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT/'generated/eye-tracker/rat/eyes-r01')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    source = HERE/'parameters.json'
    p = json.loads(source.read_text(encoding='utf-8'))
    reports, outlines = {}, {}
    for variant in p['variants']:
        key = variant['id']
        line, meta = profile(p, variant['construction'])
        mesh = revolve(line, p['mesh']['azimuth_segments'])
        path = args.output/f"rat-eye-r01-{key}.stl"
        mesh.export(path)
        # Validate the serialized float32 STL, not just the in-memory geometry.
        loaded = trimesh.load_mesh(path, process=True)
        L = p['literature_inputs']['external_axial_length_mm']
        D = p['literature_inputs']['nasotemporal_diameter_mm']
        expected = np.array([[-D/2, -D/2, -L/2], [D/2, D/2, L/2]])
        assert loaded.is_watertight and loaded.is_winding_consistent and loaded.is_volume
        assert loaded.body_count == 1 and loaded.euler_number == 2
        assert loaded.area_faces.min() > 1e-10
        assert np.max(np.abs(loaded.bounds-expected)) < 2e-6
        error = abs(loaded.volume/meta['analytic_volume_mm3']-1)
        assert error < .001
        reports[key] = dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            bytes=path.stat().st_size, triangles=len(loaded.faces),
                            watertight=bool(loaded.is_watertight),
                            winding_consistent=bool(loaded.is_winding_consistent),
                            connected_bodies=int(loaded.body_count), euler_number=int(loaded.euler_number),
                            bounds_mm=loaded.bounds.tolist(), volume_mm3=float(loaded.volume),
                            relative_volume_error=float(error), **meta)
        outlines[key] = line
    report = dict(revision=p['revision'], units='mm',
                  parameters_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  numpy_version=np.__version__, trimesh_version=trimesh.__version__,
                  validation_scope='Exterior mesh topology, orientation, bounds and analytic volume; no anatomical fit claim.',
                  variants=reports)
    (args.output/'validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    fig, axes = plt.subplots(1, 2, figsize=(11, 6), layout='constrained')
    colors = ['#777777', '#e69f00', '#0072b2']
    for (key, line), color in zip(outlines.items(), colors):
        for sign in [-1, 1]:
            axes[0].plot(sign*line[:, 0], line[:, 1], color=color,
                         label=key if sign == 1 else None, linewidth=1.6)
        if key.startswith('A'):
            continue
        axes[1].plot(line[:, 0], line[:, 1], color=color, label=key, linewidth=2)
        seam = reports[key]['limbus_z_mm']
        axes[1].plot(p['literature_inputs']['cornea_base_radius_mm'], seam, 'o', color=color)
    for ax in axes:
        ax.set_aspect('equal')
        ax.set_xlabel('Transverse coordinate (mm)')
        ax.set_ylabel('Axial Z (mm); +Z toward corneal apex')
        ax.grid(alpha=.2)
        ax.legend(fontsize=8, loc='lower left')
    axes[0].set_title('Same outer dimensions; different surface models')
    axes[0].axhline(0, color='black', linewidth=.5, alpha=.3)
    axes[0].axvline(0, color='black', linewidth=.5, alpha=.3)
    axes[1].set_xlim(1.9, 3.3)
    axes[1].set_ylim(.5, 2.6)
    axes[1].set_title('Cornea / sclera join detail\nDots: imposed limbus boundaries')
    fig.suptitle('Rat eye r01 — schematic exterior for manual placement\n6.410 × 6.410 × 6.291 mm; rotational symmetry assumed')
    fig.savefig(args.output/'comparison.png', dpi=180)
    print(json.dumps({key: {field: result[field] for field in
                           ['file', 'triangles', 'volume_mm3', 'relative_volume_error']}
                      for key, result in reports.items()}, indent=2))


if __name__ == '__main__':
    main()
