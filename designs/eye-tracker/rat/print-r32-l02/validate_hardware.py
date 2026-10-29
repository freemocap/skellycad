"""Validate and stabilize STL triangulation without altering matched CAD interfaces."""
from pathlib import Path
import json,hashlib,numpy as np,trimesh,manifold3d as mf
O=Path.cwd()/'generated/eye-tracker/rat/print-r32-l02';report={}
for p in (O/'hardware').glob('*.stl'):
 m=trimesh.load_mesh(p);assert m.is_volume,p.name;s=mf.Manifold(mf.Mesh64(np.asarray(m.vertices,dtype=np.float64),np.asarray(m.faces,dtype=np.uint64)));assert s.status()==mf.Error.NoError,p.name;r=s.simplify(1e-5).to_mesh64();clean=trimesh.Trimesh(r.vert_properties[:,:3],r.tri_verts,process=True);assert clean.is_volume and abs(clean.volume-m.volume)<.001;clean.export(p);saved=trimesh.load_mesh(p)
 expected=5 if 'all-hardware' in p.name else 3 if 'carrier-and-two-holders' in p.name else 1
 assert len(saved.split())==expected,(p.name,len(saved.split()),expected)
 report[p.name]={'watertight':bool(saved.is_watertight),'winding_consistent':bool(saved.is_winding_consistent),'shells':len(saved.split()),'volume_mm3':float(saved.volume),'volume_change_mm3':float(saved.volume-m.volume),'tolerance_mm':1e-5,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(O/'hardware-mesh-validation.json').write_text(json.dumps(report,indent=2));print('HARDWARE_STL_ROUNDTRIP_PASS',len(report))

