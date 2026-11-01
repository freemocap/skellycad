from pathlib import Path
import trimesh,manifold3d as mf,numpy as np,json
out=Path('generated/eye-tracker/rat/print-r27/hardware');report={}
for p in out.glob('*.stl'):
 m=trimesh.load_mesh(p);s=mf.Manifold(mf.Mesh64(np.array(m.vertices,dtype=np.float64),np.array(m.faces,dtype=np.uint64)));print(p.name,m.is_volume,s.status(),flush=True);assert s.status()==mf.Error.NoError
 # Resolve redundant coplanar triangulation introduced by the CAD frame conversion.
 r=s.simplify(1e-5).to_mesh64();clean=trimesh.Trimesh(r.vert_properties[:,:3],r.tri_verts,process=True);assert clean.is_volume and abs(clean.volume-m.volume)<.001
 clean.export(p);report[p.name]={'watertight':True,'volume_mm3':float(clean.volume),'simplification_tolerance_mm':1e-5,'volume_change_mm3':float(clean.volume-m.volume)}
(out.parent/'hardware-mesh-validation.json').write_text(json.dumps(report,indent=2))
