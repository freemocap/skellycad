from pathlib import Path
import sys,json,numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/eye-world-top-joint-r04';O=R/'generated/eye-tracker/rat/eye-world-top-joint-r04';cfg=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());T=np.array(cfg['mount_to_skull']);H=np.array(json.loads((S/'selected-pose.json').read_text())['head_world']);rec=json.loads((R/'generated/eye-tracker/rat/lowered-cameras-r43/04-arms.json').read_text())
def move(s,t):return s.transformed(A.Matrix(*np.asarray(t).ravel().tolist()))
def read(n):
 s=Part.Shape();s.read(str(O/(n+'.brep')));return s
def spline(e):
 try:return isinstance(e.Curve,Part.BSplineCurve)
 except TypeError:return False
s=move(read('supported-carrier'),np.linalg.inv(T));report={}
for name in ['RightUpperSupport','RightLowerSupport']:
 for end,index in [('root',0),('socket',-1)]:
  p=A.Vector(*rec[name]['poles_mm'][index]);edges=sorted([e for e in s.Edges if spline(e) and 1<e.Length<14 and (e.CenterOfMass-p).Length<4],key=lambda e:(e.CenterOfMass-p).Length);done=False
  for rad in [.65,.6,.4,.3]:
   for e in edges[:16]:
    try:trial=s.makeChamfer(rad,[e]) if name=='RightUpperSupport' and end=='root' else s.makeFillet(rad,[e])
    except Exception:continue
    if trial.isValid() and len(trial.Solids)==1 and .01<trial.Volume-s.Volume<10:
     report[name+'-'+end]={'radius_or_chamfer_mm':rad,'added_mm3':trial.Volume-s.Volume};s=trial;done=True;break
   if done:break
  assert done,(name,end)
move(s,T).exportBrep(str(O/'finished-carrier.brep'));holder=move(read('top-stem-holder'),np.linalg.inv(H));anchor=A.Vector(4.35,6.76724,-.65);edges=sorted([e for e in holder.Edges if (e.CenterOfMass-anchor).Length<4 and 1<e.Length<15],key=lambda e:(e.CenterOfMass-anchor).Length)
for e in edges:
 try:trial=holder.makeFillet(.4,[e])
 except Exception:continue
 if trial.isValid() and len(trial.Solids)==1 and .01<trial.Volume-holder.Volume<5:
  report['world-stem-root']={'radius_mm':.4,'added_mm3':trial.Volume-holder.Volume};holder=trial;break
assert 'world-stem-root' in report
move(holder,H).exportBrep(str(O/'finished-holder.brep'))
report['meshes']={}
for name,shape in [('Carrier',s),('WorldHolder',holder)]:
 for lin,ang in [(.02,.1),(.04,.15),(.01,.08),(.03,.12),(.08,.2)]:
  mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=lin,AngularDeflection=ang,Relative=False)
  if mesh.isSolid() and not mesh.hasSelfIntersections():break
 else:raise RuntimeError(('Mesh defect',name))
 report['meshes'][name]={'closed':True,'self_intersections':False,'linear_deflection_mm':lin,'angular_deflection_rad':ang,'frame':'mount' if name=='Carrier' else 'head'}
 print('MESH',name,flush=True)
(O/'finishing-validation.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
