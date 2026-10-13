"""Native holder candidate: plate, rails, returns and analytic ball/root revolution."""
from pathlib import Path
import json, math, runpy
import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher

HERE=Path(__file__).resolve().parent
WORKSPACE=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
profile=runpy.run_path(str(HERE.parent/'camera_clip/build_base.py'))['profile']


def main():
    p=json.loads((HERE/'parameters.json').read_text())
    assert 'CameraHolderRebuild58' not in App.listDocuments()
    doc=App.newDocument('CameraHolderRebuild58')
    body=doc.addObject('PartDesign::Body','CameraHolder')
    dims=doc.addObject('App::FeaturePython','Dimensions')
    dims.addProperty('App::PropertyString','Note','Source')
    dims.Note='Profile dimensions are build inputs in parameters.json; fixed arc sketch preserves baseline.'
    dims.addProperty('App::PropertyLength','PlateThickness','Dimensions')
    dims.PlateThickness=p['plate_z_mm'][1]-p['plate_z_mm'][0]
    def ycut(z):
        n,d=p['clip_end_plane'];return (d-n[2]*z)/n[1]
    def left(z):
        n,d=p['left_bevel_plane'];return (d-n[2]*z)/n[0]
    def right(z):
        n,d=p['right_bevel_plane'];return (d-n[2]*z)/n[0]
    xmin,xmax=p['outer_x_mm'];ymin,ymax=p['outer_y_mm'];end=p['clip_start_y_mm']
    floor,top=p['plate_z_mm'];mid=top-0.5
    previous=None
    def loft(name,pts1,z1,pts2,z2,placement=None):
        nonlocal previous
        a=profile(body,name+'Start',pts1,z1);b=profile(body,name+'End',pts2,z2)
        if placement:
            a.Placement=placement.multiply(a.Placement);b.Placement=placement.multiply(b.Placement)
        doc.recompute()
        f=body.newObject('PartDesign::AdditiveLoft',name)
        f.Profile=a;f.Sections=[b];f.Ruled=True;f.Refine=True
        doc.recompute()
        assert f.Shape.isValid() and len(f.Shape.Solids)==1,name
        a.Visibility=False;b.Visibility=False
        if previous:previous.Visibility=False
        previous=f
        return f
    def outline(z,beveled):
        l=left(z) if beveled else p['lip_x_mm'][0]
        r=right(z) if beveled else p['lip_x_mm'][1]
        cut=ycut(z)
        return [[xmin,ymax],[xmax,ymax],[xmax,end],[r,end],[r,cut],
                [xmax,cut],[xmax,ymin],[xmin,ymin],[xmin,cut],[l,cut],[l,end],[xmin,end]]
    loft('PlateBeveledSeat',outline(floor,True),floor,outline(mid,False),mid)
    loft('PlateTop',outline(mid,False),mid,outline(top,False),top)
    doc.PlateTopEnd.setExpression('Placement.Base.z',f'{floor:.17g} mm + Dimensions.PlateThickness')
    # Rail ends follow the measured source planes, including the small left step.
    for side,(a,b) in enumerate([(xmin,p['rail_inner_x_mm'][0]),(p['rail_inner_x_mm'][1],xmax)]):
        prefix=['Left','Right'][side]
        def rear(z,lower=False):
            if side==0 and lower:
                n,d=p['left_lower_end_plane']
                ca=(d-n[0]*a-n[2]*z)/n[1];cb=(d-n[0]*b-n[2]*z)/n[1]
            else:ca=cb=ycut(z)
            return [[a,ymin],[b,ymin],[b,cb],[a,ca]]
        loft(prefix+'RearRail',rear(floor),floor,rear(0),0)
        loft(prefix+'RearFoot',rear(0,True),0,rear(p['rail_bottom_z_mm'],True),p['rail_bottom_z_mm'])
        rect=[[a,end],[b,end],[b,ymax],[a,ymax]]
        loft(prefix+'FrontRail',rect,floor,rect,p['rail_bottom_z_mm'])
    # Rear inward returns have a five-corner ramp profile in Y/Z, extruded across X.
    orient=App.Rotation(App.Vector(0,1,0),App.Vector(0,0,1),App.Vector(1,0,0),'ZXY')
    for name,a,b in [('Left',p['rail_inner_x_mm'][0],p['return_inner_x_mm'][0]),
                     ('Right',p['return_inner_x_mm'][1],p['rail_inner_x_mm'][1])]:
        pts=p['return_yz_mm']
        loft(name+'RearReturn',pts,a,pts,b,App.Placement(App.Vector(),orient))
    # Revolved neck is the inner arc of a torus, tangent to the spherical ball.
    # Nominal tangent circles; imported major radius differs from 4 mm by 2.14e-6 mm.
    R=4.0;r=p['neck_minor_radius_mm'];br=p['ball_radius_mm']
    c=App.Vector(*p['neck_center_mm']);axis=App.Vector(*p['neck_axis_up'])
    # Analytic root arc avoids an unstable fillet at the clipped plate edge.
    # This axisymmetric blend is an explicit approximation to source BSplines.
    fr=p.get('root_blend_radius_mm',1.25)
    rootz=(top-c.z)/axis.z
    fz=rootz+fr
    fx=R-math.sqrt((r-fr)**2-fz*fz)
    contact=App.Vector(R+(fx-R)*r/(r-fr),fz*r/(r-fr),0)
    basez=-1.2
    start=App.Vector(fx,basez,0)
    tangent=App.Vector(R*br/(br+r),3-br*3/(br+r),0)
    sketch=body.newObject('Sketcher::SketchObject','BallNeckProfile')
    points=[App.Vector(0,basez,0),start]
    sketch.addGeometry(Part.LineSegment(points[0],start),False)
    sketch.addGeometry(Part.LineSegment(start,App.Vector(fx,rootz,0)),False)
    sketch.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(fx,fz,0),App.Vector(0,0,1),fr),
        math.atan2(contact.y-fz,contact.x-fx),3*math.pi/2),False)
    sketch.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(R,0,0),App.Vector(0,0,1),r),
        math.atan2(tangent.y,tangent.x-R),math.atan2(contact.y,contact.x-R)),False)
    sketch.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(0,3,0),App.Vector(0,0,1),br),
        math.atan2(tangent.y-3,tangent.x),math.pi/2),False)
    sketch.addGeometry(Part.LineSegment(App.Vector(0,3+br,0),points[0]),False)
    for i in range(6):sketch.addConstraint(Sketcher.Constraint('Block',i))
    normal=App.Vector(1,0,0).cross(axis)
    sketch.Placement=App.Placement(c,App.Rotation(App.Vector(1,0,0),axis,normal,'YXZ'))
    sketch.setExpression('Placement.Base.z',f'{c.z:.17g} mm + Dimensions.PlateThickness - 1 mm')
    doc.recompute()
    neck=body.newObject('PartDesign::Revolution','BallAndNeck')
    neck.Profile=sketch;neck.ReferenceAxis=(sketch,['V_Axis']);neck.Angle=360;neck.Refine=True
    doc.recompute()
    assert neck.Shape.isValid() and len(neck.Shape.Solids)==1
    previous.Visibility=False;sketch.Visibility=False
    trimtop=c.z+contact.y*axis.z
    trim=profile(body,'HolderSidePlane',[[-trimtop,-30],[30,-30],[30,30],[-trimtop,30]],0)
    trim.Placement=App.Placement(App.Vector(xmin,0,0),App.Rotation(App.Vector(0,0,1),App.Vector(1,0,0)))
    trim.setExpression('Placement.Base.z','Dimensions.PlateThickness - 1 mm')
    doc.recompute()
    final=body.newObject('PartDesign::Pocket','TrimHolderSide')
    final.Profile=trim;final.Length=20;final.Refine=True
    doc.recompute()
    assert final.Shape.isValid() and len(final.Shape.Solids)==1
    neck.Visibility=False;trim.Visibility=False
    if final.ViewObject:
        final.ViewObject.ShapeColor=(0.3,0.75,0.85)
    doc.recompute()
    print('Finished holder',final.Shape.Volume,len(final.Shape.Faces))
    return doc
