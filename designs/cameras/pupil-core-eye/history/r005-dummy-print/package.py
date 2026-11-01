"""Package material regions as one multipart 3MF; no unverified thermal profile."""
from pathlib import Path
import json,hashlib,zipfile,itertools,xml.etree.ElementTree as ET
import trimesh
ROOT=Path(__file__).resolve().parents[6];HERE=Path(__file__).resolve().parent
OUT=ROOT/'generated/eye-tracker/shared/camera-dummy-r05'
names=['Red_PLA_boards','Black_PLA_lens','White_PLA_connector_LEDs','Yellow_TPU_ribbon']
colors=['#FF201AFF','#202024FF','#F0F0E6FF','#FFCC05FF'];slots=[1,2,3,4]
meshes=[trimesh.load_mesh(OUT/(n+'.stl')) for n in names]
assert all(m.is_volume for m in meshes)
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS)
def el(p,n,a=None):return ET.SubElement(p,'{'+NS+'}'+n,a or {})
model=ET.Element('{'+NS+'}model',{'unit':'millimeter'});res=el(model,'resources');mat=el(res,'basematerials',{'id':'10'})
for n,c in zip(names,colors):el(mat,'base',{'name':n,'displaycolor':c})
for i,(name,m) in enumerate(zip(names,meshes),1):
 o=el(res,'object',{'id':str(i),'type':'model','name':name,'pid':'10','pindex':str(i-1)})
 me=el(o,'mesh');vs=el(me,'vertices');ts=el(me,'triangles')
 for xyz in m.vertices:el(vs,'vertex',dict(zip(['x','y','z'],[format(x,'.10g') for x in xyz])))
 for f in m.faces:el(ts,'triangle',dict(zip(['v1','v2','v3'],map(str,f))))
o=el(res,'object',{'id':'5','type':'model','name':'CAMERA DUMMY R05'});cs=el(o,'components')
for i in range(1,5):el(cs,'component',{'objectid':str(i)})
el(el(model,'build'),'item',{'objectid':'5'})
content='<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
rels='<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
path=OUT/'CAMERA-DUMMY-R05-four-materials.3mf'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml',content);z.writestr('_rels/.rels',rels);z.writestr('3D/3dmodel.model',ET.tostring(model))
with zipfile.ZipFile(path) as z:r=ET.fromstring(z.read('3D/3dmodel.model'))
assert r.get('unit')=='millimeter' and len(r.findall('.//{'+NS+'}component'))==4
for node,original in zip(r.findall('.//{'+NS+'}mesh'),meshes):
 verts=[[float(v.get(k)) for k in ['x','y','z']] for v in node.find('{'+NS+'}vertices')]
 faces=[[int(t.get(k)) for k in ['v1','v2','v3']] for t in node.find('{'+NS+'}triangles')]
 m=trimesh.Trimesh(verts,faces,process=True);assert m.is_volume and abs(m.volume-original.volume)<1e-5
report={'passed':True,'units':'mm','material_slots_suggested':dict(zip(names,slots)),'sliced':False,'physical_print_verified':False,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.suffix in ['.stl','.3mf','.step','.FCStd']}}
(OUT/'package-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('CAMERA_DUMMY_PACKAGE_OK')
