"""Put checked STL triangulations into both four-material 3MF files."""
from pathlib import Path
import json,hashlib,zipfile,itertools,xml.etree.ElementTree as ET
import trimesh,numpy as np,manifold3d as mf
R=Path.cwd();O=R/'generated/eye-tracker/rat/print-eye-bridge-r02';P=O/'anatomy';S=R/'designs/eye-tracker/rat/print-eye-bridge-r02'
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS)
parts={n:trimesh.load_mesh(P/(n+'.stl')) for n in ['Skull-and-bridge','Sclera','Cornea','Baseplate']}
assert all(m.is_volume for m in parts.values());assert len(parts['Sclera'].split())==1
def solid(m):return mf.Manifold(mf.Mesh64(np.asarray(m.vertices,dtype=np.float64),np.asarray(m.faces,dtype=np.uint64)))
overlaps={}
for a,b in itertools.combinations(parts,2):
 v=abs((solid(parts[a])^solid(parts[b])).volume());assert v<.01,(a,b,v);overlaps[a+'/'+b]=v
for p in P.glob('*.3mf'):
 with zipfile.ZipFile(p) as z:data={n:z.read(n) for n in z.namelist()}
 root=ET.fromstring(data['3D/3dmodel.model'])
 for node in root.findall('./{'+NS+'}resources/{'+NS+'}object'):
  name=node.get('name')
  if name not in parts:continue
  node.remove(node.find('{'+NS+'}mesh'));me=ET.SubElement(node,'{'+NS+'}mesh');vs=ET.SubElement(me,'{'+NS+'}vertices');ts=ET.SubElement(me,'{'+NS+'}triangles')
  for xyz in parts[name].vertices:ET.SubElement(vs,'{'+NS+'}vertex',dict(zip(['x','y','z'],[format(x,'.10g') for x in xyz])))
  for face in parts[name].faces:ET.SubElement(ts,'{'+NS+'}triangle',dict(zip(['v1','v2','v3'],map(str,face))))
 data['3D/3dmodel.model']=ET.tostring(root)
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in data.items():z.writestr(n,b)
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
audit=json.loads((O/'anatomy-validation.json').read_text());audit['overlap_mm3']=overlaps
for p in P.glob('*.stl'):
 m=trimesh.load_mesh(p);audit['parts'][p.stem]={'watertight':bool(m.is_watertight),'shells':len(m.split()),'volume_mm3':float(m.volume),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
assert audit['parts']['Sclera']['shells']==1
(O/'anatomy-validation.json').write_text(json.dumps(audit,indent=2))
(S/'final-files.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in P.iterdir()},indent=2));print('FINAL_FOUR_COLOR_PROJECTS_UPDATED_AND_VERIFIED')
