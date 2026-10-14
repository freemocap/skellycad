import bpy,json,hashlib
from pathlib import Path
here=Path(__file__).resolve().parent
out=here
s=bpy.context.scene
result={'units':s.unit_settings.system,'scale_length':s.unit_settings.scale_length,
        'cad_mm_per_coordinate_unit':1.0,
        'scale_status':'Provisional interpretation from photograph; Blender declares metres.',
        'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'objects':[]}
for o in s.objects:
 if o.type!='MESH':continue
 mesh=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
 mesh.calc_loop_triangles()
 vertices=[list(o.matrix_world@v.co) for v in mesh.vertices]
 result['objects'].append({'name':o.name,'dimensions':list(o.dimensions),'vertices':vertices,'triangles':[list(t.vertices) for t in mesh.loop_triangles],'materials':[m.name for m in o.data.materials if m]})
(out/'blender-scene.json').write_text(json.dumps(result,indent=2))
print(json.dumps({**{k:v for k,v in result.items() if k!='objects'},'objects':[{k:v for k,v in o.items() if k not in ('vertices','triangles')} for o in result['objects']]},indent=2))
