"""Build a connected, actual-size skull/baseplate print and four-region core 3MF.
Run with tools/cad/.venv/Scripts/python.exe. Extra dependency: manifold3d==3.5.4.
"""
from pathlib import Path
import json,hashlib,zipfile,itertools
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
import manifold3d
from functools import reduce
from scipy.spatial import cKDTree
from cornea_partition import partition

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-print';OUT.mkdir(parents=True,exist_ok=True)
lineage=json.loads((HERE/'lineage.json').read_text())
for f,h in lineage['inputs'].items():assert hashlib.sha256((HERE/'inputs'/f).read_bytes()).hexdigest()==h
assert hashlib.sha256((ROOT/lineage['checkpoint']).read_bytes()).hexdigest()==lineage['checkpoint_sha256']
M={n:trimesh.load_mesh(HERE/'inputs'/(n+'.stl')) for n in ['Skull','Eye1','Eye2','Baseplate']}
assert all(m.is_volume for m in M.values())
def solid(m):
 s=manifold3d.Manifold(manifold3d.Mesh64(np.array(m.vertices,dtype=np.float64),np.array(m.faces,dtype=np.uint64)))
 assert str(s.status())=='Error.NoError',str(s.status())
 return s
def mesh(s):
 r=s.to_mesh64()
 return trimesh.Trimesh(np.array(r.vert_properties)[:,:3],np.array(r.tri_verts),process=False)
def union(*ms):return mesh(reduce(lambda a,b:a+b,map(solid,ms)))
def cut(a,b):return mesh(solid(a)-solid(b))
def common(a,b):return mesh(solid(a)^solid(b))

settings=dict(units='mm',scale=1.0,eye_connection_diameter_mm=1.3,eye_connection_embed_mm=.45,
              color_revision='cornea-r02',baseplate='Unchanged current Baseplate; skull removed only inside its overlap',
              pupil_note='Black covers the smaller corneal spheroid through the existing 32-vertex cornea/sclera junction; exact original exterior triangles retained',
              bed_orientation='Anatomical skull upright; minimum Z on bed; supports required; no printer profile embedded')
skull=M['Skull'];tree=cKDTree(skull.vertices);connectors=[];pupils=[];whites=[];eye_details=[]
placement=json.loads((ROOT/'designs/mouse-hats/skull-placement/placement.json').read_text())['stl_to_assembly']
R=np.array(placement['rotation_row_vector']);t=np.array(placement['translation_mm'])
cornea_fits=json.loads((HERE/'cornea-fit.json').read_text())
for n in ['Eye1','Eye2']:
 e=M[n];dist,ind=tree.query(e.vertices);j=dist.argmin();q=skull.vertices[ind[j]];c=e.center_mass
 direction=q-c;direction/=np.linalg.norm(direction)
 end=q+direction*settings['eye_connection_embed_mm']
 rod=trimesh.creation.cylinder(radius=settings['eye_connection_diameter_mm']/2,segment=np.array([c,end]),sections=48)
 assert common(rod,skull).volume>.01 and common(rod,e).volume>.1
 connectors.append(rod)
 pupil,sclera,partition_report=partition(e,cornea_fits[n]);pupils.append(pupil);whites.append(sclera)
 eye_details.append(dict(eye=n,nearest_vertex_gap_mm=float(dist[j]),connector_start_mm=c.tolist(),connector_end_mm=end.tolist(),cornea_partition=partition_report))
print('Eye bridges and eye-front regions built',flush=True)
eyes=union(M['Eye1'],M['Eye2']);pupil=union(*pupils)
# Exact non-overlapping color partitions with shared boundaries.
bone=cut(cut(union(skull,*connectors),eyes),M['Baseplate'])
white=union(*whites);mount=M['Baseplate'].copy()
parts={'Skull':bone,'Eyes':white,'PupilCornea':pupil,'Mount':mount}
# Union the overlapping source volumes directly, avoiding a second Boolean on
# the already coincident color interfaces (float32 roundoff creates slivers).
whole=union(skull,*connectors,eyes,mount);assert whole.is_volume and len(whole.split())==1,'Print must be one connected shell'
print('Connected union built',flush=True)
report=dict(lineage=lineage,settings=settings,eye_connections=eye_details,parts={},pairwise_overlap_mm3={})
for a,b in itertools.combinations(parts,2):
 v=abs(common(parts[a],parts[b]).volume);report['pairwise_overlap_mm3'][a+' / '+b]=float(v);assert v<1e-5
# Undo source skull registration: source Z is anatomical up. Rotation only;
# translate the complete set together, never individually drop eyes to bed.
T=np.eye(4);T[:3,:3]=R;T[:3,3]=-R@t
whole.apply_transform(T)
shift=np.array([-whole.bounds[:,0].mean(),-whole.bounds[:,1].mean(),-whole.bounds[0,2]])
T[:3,3]+=shift;whole.apply_translation(shift)
for name,m in parts.items():
 m.apply_transform(T);assert m.is_volume
 m.export(OUT/(name+'.stl'))
 report['parts'][name]=dict(volume_mm3=float(m.volume),watertight=bool(m.is_watertight),winding_consistent=bool(m.is_winding_consistent),shells=len(m.split()),triangles=len(m.faces))
stl=OUT/'MH-T3-EYE-R03-skull-eyes-embedded-baseplate.stl';whole.export(stl)
report['combined']=dict(volume_mm3=float(whole.volume),watertight=bool(whole.is_watertight),winding_consistent=bool(whole.is_winding_consistent),shells=len(whole.split()),size_mm=whole.extents.tolist(),triangles=len(whole.faces))
report['assembly_to_print_transform']=T.tolist()
assert abs(sum(m.volume for m in parts.values())-whole.volume)<.001

# 3MF Core 1.3: material resources plus a single component assembly.
# Names/colors are portable; physical filament slots are assigned in the slicer.
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
def el(parent,name,attrs=None,text=None):
 e=ET.SubElement(parent,'{'+NS+'}'+name,attrs or {})
 if text is not None:e.text=text
 return e
model=ET.Element('{'+NS+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
el(model,'metadata',{'name':'Title'},'Mouse skull + eyes + embedded current baseplate — 1:1')
res=el(model,'resources');mat=el(res,'basematerials',{'id':'1'})
colors=['#DCCBA0FF','#FFFFFFFF','#202020FF','#20A8BDFF']
for name,color in zip(parts,colors):el(mat,'base',{'name':name,'displaycolor':color})
for i,(name,m) in enumerate(parts.items()):
 obj=el(res,'object',{'id':str(i+2),'type':'model','name':name,'pid':'1','pindex':str(i)})
 mesh=el(obj,'mesh');verts=el(mesh,'vertices');tris=el(mesh,'triangles')
 for v in m.vertices:el(verts,'vertex',dict(zip(['x','y','z'],[format(float(x),'.9g') for x in v])))
 for f in m.faces:el(tris,'triangle',dict(zip(['v1','v2','v3'],[str(int(x)) for x in f])))
assembly=el(res,'object',{'id':'6','type':'model','name':'Skull with embedded baseplate'});components=el(assembly,'components')
for i in range(4):el(components,'component',{'objectid':str(i+2)})
build=el(model,'build');el(build,'item',{'objectid':'6'})
mf=OUT/'MH-T3-EYE-R03-skull-eyes-four-colors-cornea-r02.3mf'
with zipfile.ZipFile(mf,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
 z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
 z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
# Reopen both formats; compare geometry independently of XML construction.
reopened=trimesh.load_mesh(stl);assert reopened.is_volume and len(reopened.split())==1
scene=trimesh.load(mf,force='scene');assert len(scene.geometry)==4
loaded=scene.to_mesh();assert np.allclose(loaded.bounds,whole.bounds,atol=1e-5)
assert abs(loaded.volume-whole.volume)<.001
report['reopen_checks']=dict(stl_one_watertight_shell=True,three_mf_meshes=len(scene.geometry),three_mf_volume_matches=True)
(HERE/'settings.json').write_text(json.dumps(settings,indent=2))
(HERE/'validation.json').write_text(json.dumps(report,indent=2))
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report['combined'],indent=2));print(mf)
