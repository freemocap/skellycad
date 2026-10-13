"""Validate the exported active mouse meshes using the locked tooling Python."""
from pathlib import Path
import argparse
import json
import trimesh

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--manifest', type=Path, default=ROOT / 'designs/eye-tracker/mouse/active-model.json')
args = parser.parse_args()
manifest = json.loads(args.manifest.read_text())
folder = ROOT / manifest['print_directory']
export = json.loads((folder / 'export.json').read_text())
assert export['native_sha256'] == manifest['native_sha256']
results = {}
for name, expected in export['files'].items():
    mesh = trimesh.load_mesh(folder / name)
    shells = mesh.split(only_watertight=False)
    assert mesh.is_watertight and mesh.is_winding_consistent, name
    assert len(shells) == expected['expected_shells'], name
    assert all(s.volume > 0 for s in shells), name
    results[name] = {'watertight': True, 'consistent_winding': True, 'shells': len(shells)}
out = ROOT / 'generated/verification/meshes.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({'passed': True, 'revision': manifest['revision'], 'files': results}, indent=2) + '\n')
print(f'CAD_MESHES_OK: {len(results)} exports')
