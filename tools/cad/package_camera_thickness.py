from pathlib import Path
import zipfile,json,xml.etree.ElementTree as ET
import trimesh
R=Path.cwd();O=R/'generated/eye-tracker/shared/camera-thickness-study'
src=R/'generated/eye-tracker/shared/camera-u1-tpu95ahf-r01/CAMERA-R08-U1-Red-Black-White-TPU95AHF.3mf'
N='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',N)
names=['Red_PLA_boards','Black_PLA_lens','White_PLA_connector_LEDs','Yellow_TPU_ribbon']
outputs=[]
for t in [.375,.5,.75]:
 with zipfile.ZipFile(src) as z:data={n:z.read(n) for n in z.namelist()}
 root=ET.fromstring(data['3D/3dmodel.model'])
 for i,name in enumerate(names,1):
  obj=root.find('{'+N+'}resources/{'+N+"}object[@id='"+str(i)+"']")
  obj.remove(obj.find('{'+N+'}mesh'));mesh=ET.SubElement(obj,'{'+N+'}mesh');vs=ET.SubElement(mesh,'{'+N+'}vertices');ts=ET.SubElement(mesh,'{'+N+'}triangles')
  m=trimesh.load_mesh(O/(str(t)+'-'+name+'.stl'));assert m.is_volume
  for xyz in m.vertices:ET.SubElement(vs,'{'+N+'}vertex',dict(zip(['x','y','z'],[format(v,'.10g') for v in xyz])))
  for tri in m.faces:ET.SubElement(ts,'{'+N+'}triangle',dict(zip(['v1','v2','v3'],map(str,tri))))
 data['3D/3dmodel.model']=ET.tostring(root)
 cfg=ET.fromstring(data['Metadata/model_settings.config']);cfg.find("object/metadata[@key='name']").set('value',f'Camera thickness trial {t:.3f} mm')
 assert [p.find("metadata[@key='extruder']").get('value') for p in cfg.findall('object/part')]==['1','2','3','4']
 data['Metadata/model_settings.config']=ET.tostring(cfg)
 out=O/f'CAMERA-U1-{t:.3f}mm-PLA-TPU95AHF.3mf'
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in data.items():z.writestr(n,b)
 with zipfile.ZipFile(out) as z:assert z.testzip() is None
 outputs.append(out)
with zipfile.ZipFile(O/'CAMERA-U1-thickness-trials.zip','w',zipfile.ZIP_DEFLATED) as z:
 for out in outputs:z.write(out,out.name)
print([str(p) for p in outputs])
