from support import *
def spline(e):
 try:return isinstance(e.Curve,Part.BSplineCurve)
 except TypeError:return False
d=load('04-finishing-working' if (O/'04-finishing-working.FCStd').exists() else '04-arms');s=local(d.FinishedCarrier);rec=json.loads((O/'04-arms.json').read_text());obs={n:o for n,o in obstacles(d).items() if 'camera-access' not in n};report=json.loads((O/'04-finishing-working.json').read_text()) if (O/'04-finishing-working.json').exists() else {}
for name in sorted(rec,key=lambda n:n!='LeftUpperSupport'):
 r=rec[name]
 for end,idx in [('root',0),('socket',-1)]:
  if name+'-'+end in report:continue
  print('JOIN',name,end,flush=True)
  p=A.Vector(*r['poles_mm'][idx]);edges=sorted([e for e in s.Edges if spline(e) and 1.3<e.Length<14 and (e.CenterOfMass-p).Length<(6 if end=='root' else 3)],key=lambda e:(e.CenterOfMass-p).Length)
  groups=[]
  for f in s.Faces:
   if not isinstance(f.Surface,(Part.Plane,Part.Cylinder)):continue
   group=[e for e in f.Edges if spline(e) and (e.CenterOfMass-p).Length<(5 if end=='root' else 3)]
   if len(group)>1:groups.append(group)
  groups.sort(key=lambda es:sum((e.CenterOfMass-p).Length for e in es)/len(es))
  groups += [[e] for e in edges[:14]]
  result=None
  for radius in ([1.,.8,.6,.5,.4] if end=='root' else [.6,.4,.3]):
   for ei,es in enumerate(groups):
    try:trial=s.makeFillet(radius,es)
    except Exception:continue
    if not trial.isValid() or len(trial.Solids)!=1:continue
    delta=trial.Volume-s.Volume
    if delta<(.03 if end=='root' else .005) or delta>15:continue
    print('TRIAL',name,end,radius,ei,delta,flush=True)
    bb=A.BoundBox()
    for edge in es:bb.add(edge.BoundBox)
    margin=3*radius+1
    region=Part.makeBox(bb.XLength+2*margin,bb.YLength+2*margin,bb.ZLength+2*margin,A.Vector(bb.XMin-margin,bb.YMin-margin,bb.ZMin-margin))
    portion=trial.common(region);assert portion.isValid()
    collisions=[n for n,o in obs.items() if region.BoundBox.intersect(o.BoundBox) and portion.common(o).Volume>1e-5]
    if collisions:print('COLLISION',collisions,flush=True);continue
    mesh_ok=False
    for lin,ang in [(.02,.1),(.04,.15),(.08,.2),(.01,.08)]:
     mesh=MeshPart.meshFromShape(Shape=trial,LinearDeflection=lin,AngularDeflection=ang,Relative=False)
     if mesh.isSolid() and not mesh.hasSelfIntersections():mesh_ok=True;break
    if not mesh_ok:print('MESH_REJECT',flush=True);continue
    result=trial;report[name+'-'+end]={'radius_mm':radius,'seam_length_mm':sum(e.Length for e in es),'seam_edges':len(es),'net_added_material_mm3':delta,'type':'concave junction fillet'};print('BLEND',name,end,report[name+'-'+end],flush=True);break
   if result is not None:break
  if result is None:raise RuntimeError(('No qualifying junction blend',name,end,[(e.Length,(e.CenterOfMass-p).Length) for e in edges]))
  s=result;assign(d.FinishedCarrier,moved(s,T));d.recompute();d.saveAs(str(O/'04-finishing-working.FCStd'));(O/'04-finishing-working.json').write_text(json.dumps(report,indent=2))
save(d,'04-finished',report)
