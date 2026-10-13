"""Blender BVH check of non-neighbor triangle overlap on conservatively cleaned meshes."""
from pathlib import Path
import bpy,json
from mathutils.bvhtree import BVHTree
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-placement'
report={}
for name in ['solid-0','hollow-0','solid_w_eyes-0','solid_w_eyes-1','solid_w_eyes-2']:
 bpy.ops.wm.stl_import(filepath=str(OUT/(name+'.stl')))
 o=bpy.context.object;m=o.data
 # STL import merges coincident vertices.
 faces=[tuple(p.vertices) for p in m.polygons];verts=[v.co for v in m.vertices]
 tree=BVHTree.FromPolygons(verts,faces,all_triangles=True,epsilon=0.0)
 pairs=[(a,b) for a,b in tree.overlap(tree) if a<b and not set(faces[a]).intersection(faces[b])]
 report[name]={'nonadjacent_intersection_pairs':len(pairs),'pairs':pairs}
 bpy.data.objects.remove(o,do_unlink=True)
(OUT/'self-intersections.json').write_text(json.dumps(report,indent=2));print({k:v['nonadjacent_intersection_pairs'] for k,v in report.items()})
