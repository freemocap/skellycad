"""Read supplied Blender scenes; export evaluated world meshes without saving sources."""
from pathlib import Path
import json
import bpy
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-placement';OUT.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'designs/mouse-hats/old/df-hardware'
report=[]
for tag,path in [('mount',BASE/'baseplate/tall_mount_w_skull.blend'),('assembly52',BASE/'camera-assembly/cad/52nassembly/52nassembly_w_mouse_skull_and_camera.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path))
 scene={'tag':tag,'source':str(path.relative_to(ROOT)),'units':str(bpy.context.scene.unit_settings.system),'scale_length':bpy.context.scene.unit_settings.scale_length,'objects':[]}
 for i,o in enumerate(bpy.context.scene.objects):
  entry={'name':o.name,'type':o.type,'matrix_world':[list(r) for r in o.matrix_world],'modifiers':[{'name':m.name,'type':m.type,'operand':getattr(getattr(m,'object',None),'name',None),'operation':getattr(m,'operation',None)} for m in o.modifiers]}
  if o.type=='MESH':
   ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
   v=[list(o.matrix_world@p.co) for p in mesh.vertices];f=[list(t.vertices) for t in mesh.loop_triangles]
   name=f'{tag}-{i}.json';(OUT/name).write_text(json.dumps({'vertices':v,'faces':f}))
   entry.update(mesh_file=name,vertices=len(v),triangles=len(f),dimensions=list(o.dimensions))
   ev.to_mesh_clear()
  scene['objects'].append(entry)
 report.append(scene)
(OUT/'blender-scenes.json').write_text(json.dumps(report,indent=2))
print(json.dumps([{**s,'objects':[{k:v for k,v in o.items() if k!='matrix_world'} for o in s['objects']]} for s in report],indent=2))
