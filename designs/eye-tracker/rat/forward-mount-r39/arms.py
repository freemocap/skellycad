from pathlib import Path
import sys,json,itertools,zipfile,numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/forward-mount-r39';O=R/'generated/eye-tracker/rat/forward-mount-r39';sys.path.insert(0,str(S.parent/'refined-supports-r38'));from common import make,unit,curve,params
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
cfg=json.loads((S/'recipe.json').read_text());T=np.array(cfg['mount_to_skull']);inv=np.linalg.inv(T);d=A.openDocument(str(O/('04-arms-working.FCStd' if (O/'04-arms-partial.json').exists() else '02-camera-and-ribbon-study.FCStd')));old=json.loads((S.parent/'refined-supports-r38/04-junctions.json').read_text())
def move(s,t):return s.transformed(A.Matrix(*np.asarray(t).ravel().tolist()))
def local(o):return move(world(o),inv)
def read(n):s=Part.Shape();s.read(str(O/(n+'.brep')));return s
central=local(d.CentralCarrier);obs={p.stem:read(p.stem) for p in O.glob('*.brep') if p.stem!='central' and not p.stem.endswith('RetainedSocket')};cuts=[]
for side in ['Right','Left']:
 b=obs[side+'PCB'].BoundBox;cuts.append(Part.makeBox(b.XLength+.1,b.YLength+.1,b.ZLength+.1,A.Vector(b.XMin-.05,b.YMin-.05,b.ZMin-.05)))
cut=Part.makeCompound(cuts);records=json.loads((O/'04-arms-partial.json').read_text()) if (O/'04-arms-partial.json').exists() else {};accepted=[]
obmeshes={n:MeshPart.meshFromShape(Shape=s,LinearDeflection=.02,AngularDeflection=.1,Relative=False) for n,s in obs.items()}
for side in ['Right','Left']:
 D=A.Placement(A.Matrix(*np.array(cfg['sides'][side]['head_delta_r38']).ravel().tolist()));socket=local(d.getObject(side+'RetainedSocket'));sign=1 if side=='Right' else -1
 for tail in ['UpperSupport','LowerSupport']:
  key=side+tail
  if key in records:accepted.append(local(d.getObject(key)));continue
  ps=[A.Vector(*p) for p in old[key]['poles_mm']];root=ps[0];port=('LowerSupport' if tail=='UpperSupport' else 'UpperSupport') if side=='Left' else tail;endps=[A.Vector(*p) for p in old[side+port]['poles_mm']];tip=D.multVec(endps[-1]);rad=unit(D.Rotation.multVec(endps[-2]-endps[-1]));_,w,canonical,axis=params(side,port);canonical=D.Rotation.multVec(canonical);axis=D.Rotation.multVec(axis);candidates=[];fail={}
  for lift,out,handle,x in itertools.product([0,2,-2,4,-4,7,-7,10,-10],[3,5,8,11,15],[3,5,8,12,16],([0] if tail=='UpperSupport' and side=='Right' else [-12,-8,-4,0,4,8,12])):
   poles=[root,root+A.Vector(x,lift,sign*out),tip+rad*handle,tip];candidates.append((curve(poles).toShape().Length,poles))
  if side=='Left':
   for handle,x,y,z in itertools.product([3,5,8,12,16],[-16,-8,0,8,16],[-16,-8,0,8,16],[0,sign*10]):
    poles=[root,tip+rad*(handle*2)+A.Vector(x,y,z),tip+rad*handle,tip];candidates.append((curve(poles).toShape().Length,poles))
  for attempt,(length,poles) in enumerate(sorted(candidates,key=lambda item:item[0])):
   if attempt%10==0:print("SEARCH",key,attempt,fail,flush=True)
   pp=np.array([list(p) for p in poles]);u=np.linspace(0,1,101)[:,None];v=3*(1-u)**2*(pp[1]-pp[0])+6*(1-u)*u*(pp[2]-pp[1])+3*u*u*(pp[3]-pp[2]);a=6*(1-u)*(pp[2]-2*pp[1]+pp[0])+6*u*(pp[3]-2*pp[2]+pp[1]);k=np.linalg.norm(np.cross(v,a),axis=1)/np.maximum(np.linalg.norm(v,axis=1),1e-9)**3
   if max(k)>.5:fail['tight_curve']=fail.get('tight_curve',0)+1;continue
   try:s=make(poles,w,canonical,axis,.6).cut(cut).removeSplitter()
   except Exception:continue
   if not s.isValid() or len(s.Solids)!=1:continue
   mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
   if not mesh.isSolid() or mesh.hasSelfIntersections():fail['mesh']=fail.get('mesh',0)+1;continue
   bad=None
   for n,om in obmeshes.items():
    if not s.BoundBox.intersect(obs[n].BoundBox):continue
    both=mesh.copy();count=both.CountFacets;both.addMesh(om)
    if any((p[0]<count)!=(p[1]<count) for p in both.getSelfIntersections()):bad=n;break
   if bad:fail[bad]=fail.get(bad,0)+1;continue
   seats=[s.common(central).Volume,s.common(socket).Volume]
   if min(seats)<.3:fail['seat']=fail.get('seat',0)+1;continue
   if s.distToShape(obs[side+'-ribbon'])[0]<.35:continue
   mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
   if not mesh.isSolid() or mesh.hasSelfIntersections():fail['mesh']=fail.get('mesh',0)+1;continue
   if accepted:
    other=accepted[-1] if tail=='LowerSupport' else None
    if other is not None and s.cut(central).cut(socket).cut(Part.makeSphere(4,tip)).distToShape(other.cut(central).cut(socket).cut(Part.makeSphere(4,tip)))[0]<.3:continue
   fused=central.multiFuse([s,socket])
   if not fused.isValid() or len(fused.Solids)!=1:continue
   assign(d.getObject(key),move(s,T));accepted.append(s);records[key]={'poles_mm':[list(p) for p in poles],'length_mm':length,'socket_port_from_r38':port,'engagement_mm3':seats,'ribbon_gap_mm':s.distToShape(obs[side+'-ribbon'])[0],'root_width_mm':3.96,'root_thickness_mm':2.22,'tip_width_mm':2.92,'tip_thickness_mm':2.16,'edge_chamfer_mm':.2};print('ACCEPT',key,records[key],flush=True);break
  else:
   (O/'arm-failure.json').write_text(json.dumps({'key':key,'fail':fail},indent=2));raise RuntimeError((key,fail))
  d.recompute();d.saveAs(str(O/'04-arms-working.FCStd'));(O/'04-arms-partial.json').write_text(json.dumps(records,indent=2))
carrier=central.multiFuse(accepted+[local(d.getObject(s+'RetainedSocket')) for s in ['Right','Left']]).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1;assign(d.FinishedCarrier,move(carrier,T));d.recompute();p=O/'04-arms.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
(O/'04-arms.json').write_text(json.dumps(records,indent=2));A.closeDocument(d.Name)

