from pathlib import Path
import json,hashlib,zipfile,itertools,xml.etree.ElementTree as ET
import numpy as np,trimesh,manifold3d as mf
from functools import reduce
ROOT=Path.cwd();HERE=ROOT/'designs/eye-tracker/rat/print-r27';OUT=ROOT/'generated/eye-tracker/rat/print-r27';PR=OUT/'anatomy';PR.mkdir(exist_ok=True)
def solid(m):
 s=mf.Manifold(mf.Mesh64(np.array(m.vertices,dtype=np.float64),np.array(m.faces,dtype=np.uint64)));assert s.status()==mf.Error.NoError;return s
def mesh(s):
 r=s.to_mesh64();return trimesh.Trimesh(np.array(r.vert_properties)[:,:3],np.array(r.tri_verts),process=True)
def union(*ms):return mesh(reduce(lambda a,b:a+b,map(solid,ms)))
def cut(a,b):return mesh(solid(a)-solid(b))
def common(a,b):return mesh(solid(a)^solid(b))
src=OUT/'skull-print-world.stl'
skull=trimesh.load_mesh(src);assert skull.is_volume
base=trimesh.load_mesh(OUT/'baseplate-world.stl');sclera=union(*(trimesh.load_mesh(OUT/('Rat'+s+'Sclera.stl')) for s in ['Left','Right']));cornea=union(*(trimesh.load_mesh(OUT/('Rat'+s+'Cornea.stl')) for s in ['Left','Right']))
p=json.loads((ROOT/'designs/eye-tracker/rat/registered-eyes-r14/placement.json').read_text());centers=[x['center_mm'] for x in p['eyes']];rod=trimesh.creation.cylinder(radius=1.125,segment=centers,sections=96)
assert common(rod,skull).volume>.1 and common(rod,sclera).volume>.1
white=cut(sclera,cornea);eyes=union(white,cornea);bone=cut(cut(union(skull,rod),eyes),base);white=cut(white,base);cornea=cut(cornea,base)
def stabilize(m):
 x=mf.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32),tolerance=.001)
 s=mf.Manifold(x).simplify(.001);assert s.status()==mf.Error.NoError;r=s.to_mesh();out=trimesh.Trimesh(r.vert_properties[:,:3],r.tri_verts);assert out.is_volume;return out
bone=stabilize(bone)
parts={'Skull-and-bridge':bone,'Sclera':white,'Cornea':cornea,'Baseplate':base}
whole=union(skull,rod,eyes,base);no_base=union(skull,rod,eyes)
whole=stabilize(whole);no_base=stabilize(no_base)
print('whole positive shells',[(len(c.faces),c.volume) for c in whole.split() if c.volume>0],flush=True)
assert sum(x.volume>0 for x in whole.split())==1 and sum(x.volume>0 for x in no_base.split())==1
T=np.eye(4)
for m in list(parts.values())+[whole,no_base]:m.apply_transform(T)
shift=np.array([-whole.bounds[:,0].mean(),-whole.bounds[:,1].mean(),-whole.bounds[0,2]])
report={'mesh_stabilization_tolerance_mm':.001,'units':'mm','revision':'RAT R27','source_checkpoint':'ET-RAT-ALIGNED-TIP-R27','skull_source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'bridge_diameter_mm':2.25,'bridge_comparison':'Same 2.25 mm bridge diameter as the current mouse print; skull material','bridge_material':'Skull-and-bridge','bridge_endpoints_world_mm':centers,'world_to_anatomical_print_frame':T.tolist(),'common_print_translation_mm':shift.tolist(),'parts':{},'overlap_mm3':{}}
for a,b in itertools.combinations(parts,2):
 vol=abs(common(parts[a],parts[b]).volume);assert vol<.01;report['overlap_mm3'][a+'/'+b]=vol
for name,m in {**parts,'rat-eyes':no_base,'rat-eyes-embedded-baseplate':whole}.items():
 m.apply_translation(shift);file=PR/(name+'.stl');m.export(file);saved=trimesh.load_mesh(file);assert saved.is_volume
 report['parts'][name]={'watertight':bool(saved.is_watertight),'shells':len(saved.split()),'volume_mm3':float(saved.volume),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
assert abs(sum(m.volume for m in parts.values())-whole.volume)<.1
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS)
def el(p,n,a=None):return ET.SubElement(p,'{'+NS+'}'+n,a or {})
model=ET.Element('{'+NS+'}model',{'unit':'millimeter'});res=el(model,'resources')
colors=['#FF0000FF','#FFFFFFFF','#202020FF','#FFFF00FF'];mat=el(res,'basematerials',{'id':'10'})
for name,color in zip(parts,colors):el(mat,'base',{'name':name,'displaycolor':color})
for i,(name,m) in enumerate(parts.items(),1):
 o=el(res,'object',{'id':str(i),'type':'model','name':name,'pid':'10','pindex':str(i-1)});me=el(o,'mesh');vs=el(me,'vertices');ts=el(me,'triangles')
 for xyz in m.vertices:el(vs,'vertex',dict(zip(['x','y','z'],map(lambda x:format(x,'.10g'),xyz))))
 for f in m.faces:el(ts,'triangle',dict(zip(['v1','v2','v3'],map(str,f))))
o=el(res,'object',{'id':'5','type':'model','name':'RAT R27 four colors'});cs=el(o,'components')
for i in range(1,5):el(cs,'component',{'objectid':str(i)})
bu=el(model,'build');el(bu,'item',{'objectid':'5'})
template=ROOT/'designs/mouse-hats/skull-print/inputs/orca-source-project.3mf'
with zipfile.ZipFile(template) as z:data={n:z.read(n) for n in ['[Content_Types].xml','_rels/.rels','Metadata/project_settings.config']}
with zipfile.ZipFile(PR/'RAT-R27-four-colors.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml',data['[Content_Types].xml']);z.writestr('_rels/.rels',data['_rels/.rels']);z.writestr('3D/3dmodel.model',ET.tostring(model))
# Native Orca project metadata follows the already used mouse project format.
el(model,'metadata',{'name':'Application'}).text='Snapmaker_Orca-2.4.0'
el(model,'metadata',{'name':'BambuStudio:3mfVersion'}).text='1'
bu[0].set('transform','1 0 0 0 1 0 0 0 1 135 135 0')
config=ET.Element('config');obj=ET.SubElement(config,'object',{'id':'5'})
ET.SubElement(obj,'metadata',{'key':'name','value':'RAT R27 skull, eyes and baseplate'})
slots=[1,3,2,4]
for i,(name,slot) in enumerate(zip(parts,slots),1):
 part=ET.SubElement(obj,'part',{'id':str(i),'subtype':'normal_part'})
 for key,value in [('name',name),('extruder',str(slot)),('matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')]:ET.SubElement(part,'metadata',{'key':key,'value':value})
plate=ET.SubElement(config,'plate');ET.SubElement(plate,'metadata',{'key':'plater_id','value':'1'});inst=ET.SubElement(plate,'model_instance')
for k,val in [('object_id','5'),('instance_id','0'),('identify_id','1')]:ET.SubElement(inst,'metadata',{'key':k,'value':val})
settings=json.loads(data['Metadata/project_settings.config']);print('Printer',settings.get('printer_model'),settings.get('printer_settings_id'),flush=True)
assert 'U1' in str(settings.get('printer_settings_id'))
# Do not inherit single-tool maps or stale mouse thumbnails/sliced toolpaths.
settings['filament_colour']=['#FF0000','#202020','#FFFFFF','#FFFF00']
with zipfile.ZipFile(PR/'RAT-R27-Snapmaker-U1.3mf','w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('[Content_Types].xml',data['[Content_Types].xml']);z.writestr('_rels/.rels',data['_rels/.rels']);z.writestr('3D/3dmodel.model',ET.tostring(model));z.writestr('Metadata/model_settings.config',ET.tostring(config));z.writestr('Metadata/project_settings.config',json.dumps(settings))
for f in PR.glob('*.3mf'):
 with zipfile.ZipFile(f) as z:root=ET.fromstring(z.read('3D/3dmodel.model'))
 loaded=[]
 for node in root.findall('.//{'+NS+'}mesh'):
  vertices=[[float(v.get(k)) for k in ['x','y','z']] for v in node.find('{'+NS+'}vertices')]
  faces=[[int(t.get(k)) for k in ['v1','v2','v3']] for t in node.find('{'+NS+'}triangles')]
  loaded.append(trimesh.Trimesh(vertices,faces,process=True))
 assert len(loaded)==4 and all(m.is_volume for m in loaded)
 assert abs(sum(m.volume for m in loaded)-whole.volume)<.1
report['filament_slots']=dict(zip(parts,slots));report['printer_settings_id']=settings['printer_settings_id'];(OUT/'anatomy-validation.json').write_text(json.dumps(report,indent=2));print('Anatomy and four-color packs passed',flush=True)


