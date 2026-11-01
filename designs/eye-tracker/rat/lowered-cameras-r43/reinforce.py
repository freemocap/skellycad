"""Add a broad concave bevel beside the small left upper root corner fillet."""
from support import *
d=load('04-finished');s=local(d.FinishedCarrier);rec=json.loads((O/'04-finished.json').read_text());p=A.Vector(*json.loads((O/'04-arms.json').read_text())['LeftUpperSupport']['poles_mm'][0]);obs={n:o for n,o in obstacles(d).items() if 'camera-access' not in n}
edges=[]
for e in s.Edges:
 try:
  if isinstance(e.Curve,Part.BSplineCurve) and 2<e.Length<4 and (e.CenterOfMass-p).Length<2.5:edges.append(e)
 except TypeError:pass
for size in [.8,.6,.5]:
 for e in edges:
  try:t=s.makeChamfer(size,[e])
  except Exception:continue
  if not t.isValid() or len(t.Solids)!=1 or t.Volume-s.Volume<.03:continue
  region=Part.makeBox(12,12,12,p-A.Vector(6,6,6));portion=t.common(region)
  if any(portion.common(o).Volume>1e-5 for o in obs.values() if region.BoundBox.intersect(o.BoundBox)):continue
  ok=False
  for l,a in [(.02,.1),(.04,.15),(.08,.2),(.03,.12),(.05,.15)]:
   mesh=MeshPart.meshFromShape(Shape=t,LinearDeflection=l,AngularDeflection=a,Relative=False)
   if mesh.isSolid() and not mesh.hasSelfIntersections():ok=True;break
  if not ok:continue
  rec['LeftUpperSupport-root-reinforcement']={'type':'concave junction chamfer','chamfer_mm':size,'seam_length_mm':e.Length,'net_added_material_mm3':t.Volume-s.Volume};assign(d.FinishedCarrier,moved(t,T));save(d,'04-reinforced',rec);print(rec['LeftUpperSupport-root-reinforcement']);raise SystemExit(0)
raise RuntimeError('No valid broad root reinforcement')
