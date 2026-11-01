from pathlib import Path
import sys,json,hashlib,zipfile,numpy as np
import FreeCAD as A, Part, Mesh, MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/eye-world-ribbon-r02';O=R/'generated/eye-tracker/rat/eye-world-ribbon-r02';P=R/'generated/eye-tracker/rat/lowered-cameras-r43'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from detailed_ribbon import ribbon_solid
c=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());src=json.loads((S.parent/'lowered-cameras-r43/review.json').read_text());source=R/src['native_checkpoint'];assert hashlib.sha256(source.read_bytes()).hexdigest()==src['native_sha256'];T=np.array(c['mount_to_skull']);B=T@np.array(c['sides']['Left']['board_transform']);old=np.array(c['sides']['Left']['head']);d=A.openDocument(str(source))
def move(s,t):return s.transformed(A.Matrix(*np.asarray(t).ravel().tolist()))
def world(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s

def asset(n):
 s=Part.Shape();s.read(str(P/(n+'.brep')));return s
carrier=world(d.FinishedCarrier).cut(Part.makeBox(150,100,150,A.Vector(-60,0,-60))).fuse(world(d.CentralCarrier)).removeSplitter();carrier.exportBrep(str(O/'Carrier.brep'))
fixed={'Carrier':carrier,'Baseplate':world(d.Baseplate),'RightHolder':world(d.Righteye_primary_Holder),'RightClip':world(d.Righteye_primary_Clip)}
for side in ['Left','Right']:
 for n in (['PCB','JST_4pin'] if side=='Left' else ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001','-ribbon']):fixed[side+n]=move(asset(side+n),T)
rightview=move(asset('Right-view-keepout'),T)
reports=[]
for i,rec in enumerate(json.loads((O/'candidates.json').read_text())):
 print('CANDIDATE',i,flush=True);rr={'index':i,'pose':rec,'collisions':{},'views':{},'passed':False};reports.append(rr)
 try:
  ribbon,mesh,metric=ribbon_solid(rec['parameters'],nx=6,ny=150);ribbon=move(ribbon,B);H=np.array(rec['head_world']);D=H@np.linalg.inv(old);moving={'Ribbon':ribbon}
  for n in ['camera_pcb','M4_lens','IR_LED','IR_LED_001']:moving[n]=move(asset('Left'+n),D)
  for n,s in moving.items():
   for k,t in fixed.items():
    if not s.BoundBox.intersect(t.BoundBox):continue
    v=s.common(t).Volume
    if v>1e-5:rr['collisions'][n+'/'+k]=v
  for n in ['camera_pcb','M4_lens','IR_LED','IR_LED_001']:
   v=ribbon.common(moving[n]).Volume
   if v>1e-5:rr['collisions']['Ribbon/'+n]=v
  lens=A.Vector(*rec['lens_world_mm']);cone=Part.makeCone(1.6,15,25,lens+A.Vector(2.2,0,0),A.Vector(1,0,0))
  for label,view in [('world',cone),('eye',rightview)]:
   for n,s in {**fixed,**moving}.items():
    if not s.BoundBox.intersect(view.BoundBox):continue
    v=s.common(view).Volume
    if v>1e-5:rr['views'][label+'/'+n]=v
  rr['surface_metric']=metric
  # Existing fixtures are checked separately; their fit does not dictate camera pose.
  rr['existing_fixture_collisions']={}
  for tail in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']:
   sh=move(world(d.getObject('Left'+tail)),D@np.linalg.inv(T))
   sh.exportBrep(str(O/('candidate-'+str(i)+'-'+tail+'.brep')))
   for n,t in {**fixed,'Ribbon':ribbon}.items():
    if not sh.BoundBox.intersect(t.BoundBox):continue
    v=sh.common(t).Volume
    if v>1e-5:rr['existing_fixture_collisions'][tail+'/'+n]=v
  if not rr['collisions'] and not rr['views']:
   # Explicit dense-skull crossing check for changed physical camera and ribbon.
   sk=d.RatDesignSkull.Mesh.copy();sk.Placement=d.RatDesignSkull.getGlobalPlacement();rr['skull_crossings']={}
   for n,s in moving.items():
    mm=MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False);count=mm.CountFacets;mm.addMesh(sk);cross=sum((a[0]<count)!=(a[1]<count) for a in mm.getSelfIntersections());rr['skull_crossings'][n]=cross
   rr['passed']=not any(rr['skull_crossings'].values())
  if rr['passed']:
   for n,s in moving.items():s.exportBrep(str(O/(n+'.brep')))
   (S/'selected-pose.json').write_text(json.dumps(rec,indent=2));(O/'selected-validation.json').write_text(json.dumps(rr,indent=2))
  print('RESULT',rr,flush=True)
 except Exception as e:rr['error']=repr(e);print(rr,flush=True)
 (O/'validation-candidates.json').write_text(json.dumps(reports,indent=2))
 if rr['passed']:break
A.closeDocument(d.Name)
assert any(r['passed'] for r in reports),'No collision-free ribbon-driven candidate'
