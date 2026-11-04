"""Join a clamp-set run's part STLs into one plate STL and a 3MF with one named object per part, then check both.

The parts are already laid out on the plate in print orientation by clamp_set.py. Run with the
tools Python from the repository root:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/plate_files.py generated/ultraskelly/clamp-set/r001

Writes clamp-fit-set-plate.stl and clamp-fit-set-plate.3mf beside the parts.
"""
import argparse
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import trimesh

CORE = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
CONTENT_TYPES = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                 '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                 '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
RELS = ('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_3mf(path, objects):
    """objects: list of (name, mesh) in plate coordinates (mm); one build item each, no transforms."""
    out = [f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="{CORE}"><resources>']
    for i, (name, mesh) in enumerate(objects, start=1):
        out.append(f'<object id="{i}" type="model" name="{name}"><mesh><vertices>')
        out.extend(f'<vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>' for x, y, z in mesh.vertices)
        out.append('</vertices><triangles>')
        out.extend(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in mesh.faces)
        out.append('</triangles></mesh></object>')
    out.append('</resources><build>')
    out.extend(f'<item objectid="{i}"/>' for i in range(1, len(objects) + 1))
    out.append('</build></model>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', CONTENT_TYPES)
        z.writestr('_rels/.rels', RELS)
        z.writestr('3D/3dmodel.model', ''.join(out))


def read_3mf(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read('3D/3dmodel.model'))
    ns = {'m': CORE}
    objects = []
    for obj in root.findall('m:resources/m:object', ns):
        v = np.array([[float(e.get(k)) for k in 'xyz'] for e in obj.findall('m:mesh/m:vertices/m:vertex', ns)])
        f = np.array([[int(e.get(k)) for k in ('v1', 'v2', 'v3')] for e in obj.findall('m:mesh/m:triangles/m:triangle', ns)])
        objects.append((obj.get('name'), v, f))
    items = [int(e.get('objectid')) for e in root.findall('m:build/m:item', ns)]
    return objects, items


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    report = json.loads((args.folder / 'build-report.json').read_text(encoding='utf-8'))
    names = list(report['prints'])
    pockets = report['pockets_mm']
    objects = []
    for name in names:
        path = args.folder / name
        assert sha(path) == report['prints'][name]['sha256'], f'{name} differs from its build report'
        mesh = trimesh.load_mesh(path)
        assert mesh.is_watertight and mesh.is_volume, f'{name} is not a closed solid'
        assert abs(mesh.bounds[0][2]) < 1e-4, f'{name} is not on the bed'
        stem = name[:-4]
        label = f'U {stem[-1]} ({pockets[int(stem[-1]) - 1]} mm pocket)' if stem.startswith('clamp-u') else 'Bar for U 1 to 5'
        objects.append((label, mesh))
    plate = trimesh.util.concatenate([m for _, m in objects])
    stl, three_mf = args.folder / 'clamp-fit-set-plate.stl', args.folder / 'clamp-fit-set-plate.3mf'
    plate.export(stl)
    write_3mf(three_mf, objects)
    # Read both back: the plate STL holds every triangle; the 3MF holds each part as its own named object.
    back = trimesh.load_mesh(stl, process=False)
    assert len(back.faces) == sum(len(m.faces) for _, m in objects), 'plate STL lost triangles'
    read, items = read_3mf(three_mf)
    assert items == list(range(1, len(objects) + 1)), '3MF build items do not match the objects'
    for (label, mesh), (name, v, f) in zip(objects, read):
        assert name == label and len(f) == len(mesh.faces) and np.abs(v - mesh.vertices).max() < 1e-5, f'3MF {label} differs'
    lo, hi = plate.bounds
    bodies = len(plate.split(only_watertight=False))
    print(json.dumps({'plate_stl': {'path': stl.name, 'sha256': sha(stl), 'bodies': bodies, 'triangles': len(back.faces)},
                      'plate_3mf': {'path': three_mf.name, 'sha256': sha(three_mf), 'objects': [n for n, *_ in read]},
                      'plate_size_mm': [round(float(v), 1) for v in hi - lo]}, indent=1))


if __name__ == '__main__':
    main()
