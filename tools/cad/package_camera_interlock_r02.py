from pathlib import Path
import zipfile,json,xml.etree.ElementTree as ET
import trimesh
R=Path.cwd();O=R/'generated/eye-tracker/shared/camera-interlock-075-r02'
src=R/'generated/eye-tracker/shared/camera-thickness-study/CAMERA-U1-0.750mm-PLA-TPU95AHF.3mf'
N='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',N)
names=['Red_PLA_boards','Black_PLA_lens','White_PLA_connector_LEDs','Yellow_TPU_ribbon']
outputs=[]
for t in [.75]:
 with zipfile.ZipFile(src) as z:data={n:z.read(n) for n in z.namelist()}
 root=ET.fromstring(data['3D/3dmodel.model'])
 for i,name in enumerate(names,1):
  if i not in [1,4]:continue
  obj=root.find('{'+N+'}resources/{'+N+"}object[@id='"+str(i)+"']")
  obj.remove(obj.find('{'+N+'}mesh'));mesh=ET.SubElement(obj,'{'+N+'}mesh');vs=ET.SubElement(mesh,'{'+N+'}vertices');ts=ET.SubElement(mesh,'{'+N+'}triangles')
  m=trimesh.load_mesh(O/(name+'.stl'));assert m.is_volume
  for xyz in m.vertices:ET.SubElement(vs,'{'+N+'}vertex',dict(zip(['x','y','z'],[format(v,'.10g') for v in xyz])))
  for tri in m.faces:ET.SubElement(ts,'{'+N+'}triangle',dict(zip(['v1','v2','v3'],map(str,tri))))
 data['3D/3dmodel.model']=ET.tostring(root)
 cfg=ET.fromstring(data['Metadata/model_settings.config']);cfg.find("object/metadata[@key='name']").set('value','Camera 0.75 mm - three captive TPU teeth per joint')
 assert [p.find("metadata[@key='extruder']").get('value') for p in cfg.findall('object/part')]==['1','2','3','4']
 data['Metadata/model_settings.config']=ET.tostring(cfg)
 out=O/'CAMERA-U1-0.750mm-INTERLOCK-3TEETH-PLA-TPU95AHF.3mf'
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in data.items():z.writestr(n,b)
 with zipfile.ZipFile(out) as z:assert z.testzip() is None
 outputs.append(out)
print([str(p) for p in outputs])
