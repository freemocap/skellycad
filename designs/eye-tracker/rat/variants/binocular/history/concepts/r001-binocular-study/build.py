"""Build three concept assemblies; guides and closures are not print designs."""
from pathlib import Path
import json,hashlib,sys
import numpy as np
import FreeCAD as A,Part,Mesh
ROOT=Path.cwd();HERE=ROOT/'designs/eye-tracker/rat/binocular-study-r01';OUT=ROOT/'generated/eye-tracker/rat/binocular-study-r01';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'designs/eye-tracker/shared/targeting'))
from poses import aim_sensor,axis_error
for path in ['designs/eye-tracker/rat/active-model.json','designs/eye-tracker/rat/targeted-r03/review.json']:
 manifest=json.loads((ROOT/path).read_text());assert hashlib.sha256((ROOT/manifest['native_checkpoint']).read_bytes()).hexdigest()==manifest['native_sha256']
src=A.openDocument(str(ROOT/manifest['native_checkpoint']));cfg=json.loads(src.TargetRecipe.RecipeJSON);T=np.array(cfg['mount_to_skull']);Ti=np.linalg.inv(T)
right=np.array(json.loads((ROOT/'generated/eye-tracker/rat/targeted-r03/target.json').read_text())['sensor_in_skull']);F=np.diag([1,-1,1]);lens=F@np.array(cfg['lens_position_world_mm']);left=aim_sensor([.75,8.35,0],lens,cfg['lens_local_mm'],F@right[:3,:3]@np.diag([-1,1,1]));D=left@np.linalg.inv(right)
def placement(t):return A.Placement(A.Matrix(*np.asarray(t).ravel().tolist()))
def moved(shape,t):
 s=shape.copy();s.Placement=placement(t).multiply(s.Placement);return s
def worldpoint(p):return A.Vector(*(T[:3,:3]@np.array(p)+T[:3,3]))
def add(doc,name,shape,color):
 o=doc.addObject('Part::Feature',name);o.Shape=shape;o.addProperty('App::PropertyString','StudyStatus');o.StudyStatus='Concept only; not fabrication validated';return o
# FreeCAD headless saves geometry; GUI macro sets all display properties.
report={'units':'mm','source':manifest['native_checkpoint'],'source_sha256':manifest['native_sha256'],'camera_left_transform':left.tolist(),'left_aim':axis_error(left,cfg['lens_local_mm'],[.75,8.35,0]),'options':{}}
for key,gap,closure in [('A',2.,'Shared clip bonnet'),('B',3.,'Shared through-bolt bonnet'),('C',4.,'Independent covers')]:
 d=A.newDocument('Binocular'+key);colors={}
 def put(n,s,c):colors[n]=c;return add(d,n,s,c)
 for n in ['StandardSkull','RightEyeSclera','RightEyeCornea','LeftEyeSclera','LeftEyeCornea']:
  original=src.getObject(n);m=Mesh.Mesh(original.Mesh);m.transform(original.getGlobalPlacement().toMatrix());o=d.addObject('Mesh::Feature',n);o.Mesh=m;colors[n]=(.8,.79,.73) if n=='StandardSkull' else ((.9,.94,.96) if 'Sclera' in n else (.12,.3,.4))
 put('Baseplate',src.skull_mount_Baseplate.Shape,(.6,.6,.65))
 # Real second board: proper 180 degree turn about mount Y, opposing ribbon exit.
 flip=np.eye(4);flip[:3,:3]=np.diag([-1,1,-1]);center=np.array([5.41206399647304,12.78,1.075]);flip[:3,3]=center-flip[:3,:3]@center+np.array([-gap-.25,0,0]);boardD=T@flip@Ti
 for side,delta in [('Right',np.eye(4)),('Left',D)]:
  col=(.25,.48,.76) if side=='Right' else (.75,.42,.2)
  for n in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']:
   put(side+n,moved(src.getObject(n).Shape,delta),col)
  for ob in src.MeasuredSensorHead.Group:
   if ob.Name=='M4_nominal_reference':continue
   put(side+ob.Name,moved(ob.Shape,delta),(.12,.4,.21) if ob.Name=='camera_pcb' else (.15,.15,.17))
  for ob in src.MeasuredMainPCB.Group:put(side+ob.Name,moved(ob.Shape,np.eye(4) if side=='Right' else boardD),(.15,.48,.24))
  a=np.array(cfg['lens_position_world_mm']) if side=='Right' else lens;b=np.array([.75,-8.35 if side=='Right' else 8.35,0])
  put(side+'OpticalAxis',Part.makeLine(A.Vector(*a),A.Vector(*b)),(1,0,0))
 # Open spacer skeleton: two long edge rails and two end ties, center left open.
 xmin=5.28706399647304-gap;depth=gap
 frame=Part.makeCompound([Part.makeBox(depth,1.1,33,A.Vector(xmin,y,-15.4)) for y in [7.18,17.28]]+[Part.makeBox(depth,11.2,1.1,A.Vector(xmin,7.18,z)) for z in [-15.4,16.5]])
 put('OpenSpacerFrame',moved(frame,T),(.58,.62,.67))
 # Established rectangular arm sections, with conceptual paths to the retained sockets.
 arms=json.loads((ROOT/'generated/eye-tracker/rat/targeted-r03/arms.json').read_text())
 for side,delta in [('Right',np.eye(4)),('Left',D)]:
  for armname in ['UpperSupport','RearRibbonGuard']:
   ar=arms[armname];c=np.array(ar['socket_center_mm']);n=np.array(ar['socket_axis']);v=np.array(ar['arm']['radial_direction']);end=worldpoint(c+n*ar['attachment_height_mm']+v*ar['attachment_radius_mm']);end=placement(delta).multVec(end)
   sign=1 if side=='Right' else -1
   root=worldpoint([5.287-gap/2,17.8 if armname=='UpperSupport' else 7.3,16.3 if side=='Right' else -14.3])
   mid=(root+end)*.5;mid.z+=3 if armname=='UpperSupport' else -4
   if key=='C' and armname=='RearRibbonGuard':mid.x-=3
   curve=Part.BezierCurve();curve.setPoles([root,root+(mid-root)*.9,mid,end]);wires=[]
   for t in np.linspace(0,1,25):
    p=curve.value(float(t));tangent=curve.tangent(float(t))[0];width=A.Vector(1,0,0);width=width-tangent*width.dot(tangent);width.normalize();height=tangent.cross(width);height.normalize();pts=[p+width*x+height*y for x,y in [(-1.5,-.9),(1.5,-.9),(1.5,.9),(-1.5,.9),(-1.5,-.9)]];wires.append(Part.makePolygon(pts))
   put(side+armname+'Concept',Part.makeLoft(wires,True,False),(.25,.48,.76) if side=='Right' else (.75,.42,.2))
  start=worldpoint([5.53706399647303,12.78,16.5]);start=placement(np.eye(4) if side=='Right' else boardD).multVec(start)
  finish=placement(np.eye(4) if side=='Right' else D).multVec(A.Vector(*right[:3,3]));mid=(start+finish)*.5;mid.x-=5
  curve=Part.BezierCurve();curve.setPoles([start,start+A.Vector(-5,0,2),mid,finish]);put(side+'RibbonRouteGuide',curve.toShape(),(.9,.55,.08))
  report['options'].setdefault(key,{}).setdefault('ribbon_chord_mm',{})[side]=(finish-start).Length
 # Caps are an open-bottom hood; large long windows expose the boards.
 x0=xmin-1.2;total=gap+2.9
 def hood():
  outer=Part.makeBox(total,13,34.4,A.Vector(x0,6.3,-16.1));inner=Part.makeBox(total-1.6,13,32.8,A.Vector(x0+.8,5.5,-15.3));s=outer.cut(inner)
  for x in [x0-.1,x0+total-.9]:s=s.cut(Part.makeBox(1,7,23,A.Vector(x,9,-10.5)))
  return s
 cap=hood()
 if key=='B':
  bolt=Part.makeCylinder(1,total+3,A.Vector(x0-1.5,17.9,0),A.Vector(1,0,0));cap=cap.cut(Part.makeCylinder(1.15,total+4,A.Vector(x0-2,17.9,0),A.Vector(1,0,0)))
  put('NominalM2BoltEnvelope',moved(bolt,T),(.7,.7,.72))
 if key=='C':
  for idx,(lo,hi) in enumerate([(x0,xmin+gap/2),(xmin+gap/2,x0+total)]):put('IndependentCover'+str(idx+1),moved(cap.common(Part.makeBox(hi-lo,15,36,A.Vector(lo,6,-17))),T),(.6,.65,.7))
 else:put('SharedBonnet',moved(cap,T),(.6,.65,.7))
 if key=='A':
  for z in [-13,13]:put('SnapEnvelope'+str(abs(z))+('Front' if z>0 else 'Rear'),moved(Part.makeBox(total,1.2,2,A.Vector(x0,16.9,z)),T),(.85,.3,.5))
 report['options'][key].update({'bare_board_back_gap_mm':gap,'closure':closure,'status':'Concept; ribbon guides not fixed-length sheets; arms and closures not collision/strength validated'})
 d.addObject('App::FeaturePython','ConceptNotes').addProperty('App::PropertyString','Description');d.ConceptNotes.Description=report['options'][key]['status'];d.recompute();d.saveAs(str(OUT/('binocular-'+key+'.FCStd')))
 (OUT/('colors-'+key+'.json')).write_text(json.dumps(colors));A.closeDocument(d.Name)
(OUT/'study.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
