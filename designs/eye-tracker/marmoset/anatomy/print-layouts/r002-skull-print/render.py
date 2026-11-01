"""Run with Blender in background mode; render close-up geometry review views."""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'generated/eye-tracker/marmoset/skull-print-r02'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16
scene.cycles.use_denoising=True
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.world.color=(.35,.35,.35)
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG'
material=bpy.data.materials.new('Bone clay');material.diffuse_color=(.72,.67,.56,1);material.use_nodes=True
bsdf=material.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.72,.67,.56,1);bsdf.inputs['Roughness'].default_value=.65
for name,pos,power,size in [('Key',(-45,-65,90),90000,55),('Fill',(55,-20,45),35000,50),('Rear',(0,60,70),65000,45)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=pos
    obj.rotation_euler=(Vector((0,-15,20))-obj.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('Review');camdata.type='ORTHO';camera=bpy.data.objects.new('Review',camdata);scene.collection.objects.link(camera);scene.camera=camera
views=[('front',(0,-100,24),(0,-24,23),36),('rear',(0,85,5),(0,0,20),40),('socket_oblique',(43,-95,42),(5,-27,23),29),('underside',(0,-8,-90),(0,-14,16),48)]
for label,path in [('source',ROOT/'designs/eye-tracker/marmoset/references/skull/female_100months_403g.stl'),('r02',OUT/'marmoset-skull-print-r02.stl')]:
    bpy.ops.wm.stl_import(filepath=str(path));obj=bpy.context.object
    for v in obj.data.vertices:v.co=(v.co.x,-v.co.z,v.co.y)
    obj.data.materials.append(material)
    for p in obj.data.polygons:p.use_smooth=True
    for view,position,target,scale in views:
        camera.location=position;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale
        scene.render.filepath=str(OUT/f'{label}-{view}.png');bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(obj,do_unlink=True)
