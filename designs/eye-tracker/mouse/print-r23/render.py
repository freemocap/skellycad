"""Render the exported print meshes in an isolated Blender process."""
from pathlib import Path
import bpy
from mathutils import Vector
O=Path.cwd()/'generated/eye-tracker/mouse/print-r23'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1300;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.color=(.65,.65,.65)
for name,color in [('Skull-and-bridge',(.65,.035,.025,1)),('Sclera',(.9,.9,.85,1)),('Cornea',(.012,.012,.016,1)),('Baseplate',(.95,.62,.025,1))]:
    bpy.ops.wm.stl_import(filepath=str(O/'anatomy'/(name+'.stl')))
    obj=bpy.context.object;obj.name=name
    mat=bpy.data.materials.new(name);mat.diffuse_color=color;mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=color;bsdf.inputs['Roughness'].default_value=.45
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:poly.use_smooth=True
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.05))
mat=bpy.data.materials.new('Backdrop');mat.diffuse_color=(.8,.82,.85,1);bpy.context.object.data.materials.append(mat)
for location,power,size in [((10,-25,40),18000,30),((-20,15,25),12000,25),((25,25,20),8000,20)]:
    bpy.ops.object.light_add(type='AREA',location=location);bpy.context.object.data.energy=power;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=size
    bpy.context.object.rotation_euler=(Vector((0,0,8))-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=43
scene.view_settings.view_transform='AgX'
for name,loc in [('anatomy-preview',(35,-55,27)),('jaw-side-view',(0,-60,12)),('jaw-front-view',(65,0,15))]:
    camera.location=loc;camera.rotation_euler=(Vector((0,0,13))-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'MOUSE-R23-print-review.blend'))
