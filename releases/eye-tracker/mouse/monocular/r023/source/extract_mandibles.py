"""Extract atlas jaw labels without changing their registration or articulation."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import trimesh
import manifold3d as mf
from scipy import ndimage as ndi
from skimage.measure import marching_cubes

ROOT = Path.cwd()
OUT = ROOT / 'generated/eye-tracker/mouse/print-r23'
OUT.mkdir(parents=True, exist_ok=True)
STUDY = ROOT / 'designs/eye-tracker/mouse/skull-landmarks-study-r01'
sys.path.insert(0, str(ROOT / 'generated/eye-tracker/mouse/skull-landmarks-study-r01/python-deps'))
import nibabel as nib

active = json.loads((STUDY.parent / 'active-model.json').read_text())
assert hashlib.sha256((ROOT / active['native_checkpoint']).read_bytes()).hexdigest() == active['native_sha256']
source = STUDY / 'sources/35_mic_23strain_mus_template_UCHAR-label.nii.gz'
assert hashlib.sha256(source.read_bytes()).hexdigest() == '06f68b4612d9611d3645c58548106a375f57cef960947105c70bb5895a37c29f'
im = nib.load(source)
v = np.asarray(im.dataobj)
T = np.array(json.loads((STUDY / 'validation.json').read_text())['matrix_atlas_lps_to_assembly'])
report = {'units': 'mm', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'matrix_atlas_lps_to_assembly': T.tolist(), 'parts': {},
          'sources': ['magaMouseCTAtlasRepository'], 'additional_articulation_transform': 'identity'}
# Retained upstream main.R identifies label 2 as right and 21 as left mandible.
# [@magaMouseCTAtlasRepository]
for label, name in [(2, 'right-mandible'), (21, 'left-mandible')]:
    indices = np.argwhere(v == label)
    low = indices.min(axis=0) - 3; high = indices.max(axis=0) + 4
    mask = v[tuple(slice(a,b) for a,b in zip(low,high))] == label
    labels, count = ndi.label(mask)
    sizes = np.bincount(labels.ravel()); sizes[0] = 0
    largest = labels == sizes.argmax()
    filled = ndi.binary_fill_holes(largest | ndi.binary_closing(largest, iterations=1))
    verts, faces, _, _ = marching_cubes(ndi.gaussian_filter(np.pad(filled, 2).astype(np.float32), 1.0), .5, allow_degenerate=False)
    verts = nib.affines.apply_affine(im.affine, verts - 2 + low) * [-1, -1, 1]
    m = trimesh.Trimesh(verts, faces)
    m.fix_normals()
    s = mf.Manifold(mf.Mesh64(np.asarray(m.vertices, dtype=np.float64), np.asarray(m.faces, dtype=np.uint64)))
    assert s.status() == mf.Error.NoError
    z = s.simplify(.015).to_mesh64()
    m = trimesh.Trimesh(np.asarray(z.vert_properties)[:, :3], np.asarray(z.tri_verts), process=False)
    m.apply_transform(T)
    shells = sorted(m.split(only_watertight=False), key=lambda s: abs(s.volume), reverse=True)
    print(name, 'surface shells', [(len(s.faces), s.volume, s.is_volume) for s in shells], flush=True)
    removed_surface_volume = sum(abs(s.volume) for s in shells[1:])
    m = shells[0]
    assert m.is_volume
    dest = OUT / (name + '-world.stl'); m.export(dest)
    saved = trimesh.load_mesh(dest)
    assert saved.is_volume and len(saved.split(only_watertight=False)) == 1
    report['parts'][name] = {'label': label, 'source_voxels': int(mask.sum()),
                            'discarded_dust_voxels': int(mask.sum() - largest.sum()),
                            'filled_internal_voxels': int(filled.sum() - largest.sum()),
                            'smoothing_sigma_voxels': 1.0, 'closing_voxels': 1, 'simplification_source_mm': .015,
                            'removed_surface_volume_mm3': float(removed_surface_volume),
                            'volume_mm3': float(m.volume), 'faces': len(m.faces),
                            'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()}
    print(name, report['parts'][name], flush=True)
(OUT / 'mandible-extraction.json').write_text(json.dumps(report, indent=2))
