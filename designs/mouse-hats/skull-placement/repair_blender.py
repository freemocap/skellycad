"""Separate voxel repair candidate; preserve all supplied files and eye meshes."""
from pathlib import Path
import bpy,json
from mathutils.bvhtree import BVHTree
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-placement'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(OUT/'solid-0.stl'));o=bpy.context.object
mod=o.modifiers.new('Repair self intersections at 0.04 mm','REMESH');mod.mode='VOXEL';mod.voxel_size=.04;mod.use_smooth_shade=False
bpy.ops.object.modifier_apply(modifier=mod.name)
tri=o.modifiers.new('Triangulate','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=tri.name)
dec=o.modifiers.new('Compact reference mesh','DECIMATE');dec.ratio=.05;bpy.ops.object.modifier_apply(modifier=dec.name)
faces=[tuple(p.vertices) for p in o.data.polygons];verts=[v.co for v in o.data.vertices]
tree=BVHTree.FromPolygons(verts,faces,all_triangles=True,epsilon=0.0)
pairs=[(a,b) for a,b in tree.overlap(tree) if a<b and not set(faces[a]).intersection(faces[b])]
bpy.ops.wm.stl_export(filepath=str(OUT/'skull-repaired.stl'),export_selected_objects=True)
(OUT/'repair-settings.json').write_text(json.dumps(dict(method='Blender voxel remesh then 0.05-ratio decimation, no smoothing',voxel_size_mm=.04,decimate_ratio=.05,triangles=len(faces),nonadjacent_intersection_pairs=len(pairs)),indent=2))
print('REPAIR',len(faces),'triangles',len(pairs),'nonadjacent intersections')
