from support import *
def spline_edge(e):
 try:return isinstance(e.Curve,Part.BSplineCurve)
 except TypeError:return False

d=load('04-arms');s=local(d.FinishedCarrier);obs=obstacles(d);rec=json.loads((O/'04-arms.json').read_text());report={}
for name,r in rec.items():
 for end,idx in [('root',0),('socket',-1)]:
  p=A.Vector(*r['poles_mm'][idx]);candidates=sorted([e for e in s.Edges if spline_edge(e) and .8<e.Length<5 and (e.CenterOfMass-p).Length<2.2],key=lambda e:(e.CenterOfMass-p).Length)
  accepted=None
  for radius in [.4,.25,.15]:
   for e in candidates[:8]:
    try:trial=s.makeFillet(radius,[e])
    except Exception:continue
    if not trial.isValid() or len(trial.Solids)!=1:continue
    change=trial.cut(s)
    if any(change.common(o).Volume>1e-5 for o in obs.values()):continue
    mesh=MeshPart.meshFromShape(Shape=trial,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
    if not mesh.isSolid() or mesh.hasSelfIntersections():continue
    accepted=trial;report[name+'-'+end]={'radius_mm':radius,'selected_seam_length_mm':e.Length,'added_volume_mm3':change.Volume,'removed_volume_mm3':s.cut(trial).Volume};print('FILLET_ACCEPTED',name,end,report[name+'-'+end],flush=True);break
   if accepted is not None:break
  if accepted is None:report[name+'-'+end]={'native_fillet':False,'finish':'Smooth flared loft transition and 0.2 mm longitudinal edge chamfers retained'};print('FLARED_TRANSITION_RETAINED',name,end,flush=True)
  else:s=accepted
assign(d.FinishedCarrier,moved(s,T));save(d,'04-finished',report)

