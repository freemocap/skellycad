from support import *
def spline_edge(e):
 try:return isinstance(e.Curve,Part.BSplineCurve)
 except TypeError:return False
d=load('04-finished');s=local(d.FinishedCarrier);report=json.loads((O/'04-finished.json').read_text());joints=json.loads((O/'04-arms.json').read_text())
for key,record in list(report.items()):
 if 'radius_mm' in record:continue
 name,end=key.rsplit('-',1);p=A.Vector(*joints[name]['poles_mm'][0 if end=='root' else -1]);candidates=sorted([e for e in s.Edges if spline_edge(e) and .8<e.Length<5 and (e.CenterOfMass-p).Length<2.3],key=lambda e:(e.CenterOfMass-p).Length)
 accepted=None
 for size in [.3,.2,.15]:
  for e in candidates[:12]:
   try:trial=s.makeChamfer(size,[e])
   except Exception:continue
   if not trial.isValid() or len(trial.Solids)!=1:continue
   mesh=MeshPart.meshFromShape(Shape=trial,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
   if not mesh.isSolid() or mesh.hasSelfIntersections():continue
   accepted=trial;report[key]={'chamfer_mm':size,'seam_length_mm':e.Length,'removed_volume_mm3':s.cut(trial).Volume};print('CHAMFER_ACCEPTED',key,report[key],flush=True);break
  if accepted is not None:break
 if accepted is None:raise RuntimeError('No accepted finishing edge at '+key)
 s=accepted
assign(d.FinishedCarrier,moved(s,T));save(d,'04-finished',report)
