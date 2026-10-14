"""Expose eye-local +Z through the corneal apex without changing anatomy."""
from pathlib import Path
import sys,json,hashlib,math
import FreeCAD as A,Part
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent

def build(recipe):
    recipe=Path(recipe).resolve();cfg=json.loads(recipe.read_text())
    src=ROOT/cfg['source']['path']
    assert hashlib.sha256(src.read_bytes()).hexdigest()==cfg['source']['sha256']
    selected=json.loads((recipe.parent.parent/'active-model.json').read_text())
    assert hashlib.sha256((ROOT/selected['native_checkpoint']).read_bytes()).hexdigest()==selected['native_sha256']
    d=A.openDocument(str(src));sp=cfg['species']
    out=ROOT/'generated/eye-tracker'/sp/recipe.parent.name;out.mkdir(parents=True,exist_ok=True)
    reports={}
    if sp=='mouse':
        records=json.loads((HERE/'mouse-shape-audit.json').read_text())
    else:
        definition=json.loads((ROOT/'designs/eye-tracker/rat/references/eyes/r02/eye-definition.json').read_text())
        records={n:{} for n in ['RightEye','LeftEye']}
    for name,record in records.items():
        eye=d.getObject(name)
        if sp=='mouse':
            before=[eye.getGlobalPlacement().multVec(v.Vector) for v in eye.Mesh.Points]
            center=A.Vector(*record['center_mm']);z=A.Vector(*record['direction'])
            # Z is recovered from concentric spheroid symmetry, not the mesh object's identity placement.
            rot=A.Rotation(A.Vector(0,0,1),z)
            frame=d.addObject('App::Part',name+'OpticalFrame')
            frame.Label=name+' — fitted geometric eye frame (+Z anterior)'
            parent=d.getObject('Anatomy')
            if parent:
                parent.removeObject(eye);parent.addObject(frame)
            old=eye.getGlobalPlacement()
            frame.Placement=A.Placement(center,rot);frame.addObject(eye)
            eye.Placement=frame.Placement.inverse().multiply(old)
            apex=frame.Placement.inverse().multVec(A.Vector(*record['apex_mm']))
            back=frame.Placement.inverse().multVec(A.Vector(*record['posterior_pole_mm']))
            # Mesh.Points already includes the mesh object's own Placement.
            # Only its parent's placement remains to obtain world coordinates.
            parent_pose=eye.getGlobalPlacement().multiply(eye.Placement.inverse())
            after=[parent_pose.multVec(v.Vector) for v in eye.Mesh.Points]
            err=max((a-b).Length for a,b in zip(before,after));assert err<1e-5, err
        else:
            frame=eye;apex=A.Vector(*definition['apex_mm']);back=A.Vector(*definition['posterior_pole_mm']);err=0.0
        assert math.hypot(apex.x,apex.y)<1e-5 and math.hypot(back.x,back.y)<1e-5
        axis=d.addObject('Part::Feature',name+'OpticalAxis')
        axis.Label=name+' optical axis (+Z through cornea) — reference'
        frame.addObject(axis)
        tip=apex.z+6;start=back.z-3
        axis.Shape=Part.makeCompound([Part.makeLine(A.Vector(0,0,start),A.Vector(0,0,tip)),
            Part.makeLine(A.Vector(0,0,tip),A.Vector(.35,0,tip-.8)),
            Part.makeLine(A.Vector(0,0,tip),A.Vector(-.35,0,tip-.8))])
        for key,val in [('Direction',A.Vector(0,0,1)),('CornealApex',apex),('PosteriorPole',back)]:
            axis.addProperty('App::PropertyVector',key,'Eye datum');setattr(axis,key,val)
        axis.addProperty('App::PropertyBool','ExportForPrinting').ExportForPrinting=False
        axis.addProperty('App::PropertyString','Definition').Definition='Geometric symmetry axis; not calibrated visual axis or measured rotation center.'
        pose=frame.getGlobalPlacement();z=pose.Rotation.multVec(A.Vector(0,0,1))
        row={'origin_world_mm':list(pose.Base),'outward_world':list(z),'corneal_apex_world_mm':list(pose.multVec(apex)),
             'posterior_pole_world_mm':list(pose.multVec(back)),'max_anatomy_motion_mm':err,
             'apex_line_residual_mm':math.hypot(apex.x,apex.y),'frame_object':frame.Name,'axis_object':axis.Name}
        if sp=='rat':
            row['azimuth_from_skull_rostral_deg']=math.degrees(math.atan2(z.y,z.x))
            row['elevation_from_skull_XY_deg']=math.degrees(math.asin(z.z))
        reports[name]=row
    d.recompute();d.Label=cfg['revision']+' — eye optical axes'
    d.saveAs(str(out/(cfg['revision']+'.FCStd')))
    (out/'axis-validation.json').write_text(json.dumps({'units':'mm','species':sp,'eyes':reports,'shape_and_pose_preserved':True},indent=2))
    print(json.dumps(reports,indent=2));print('EYE_AXES_OK')

if __name__=='__main__':build(sys.argv[1])
