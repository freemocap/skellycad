import FreeCAD as A,Part,json
from pathlib import Path
out=Path('generated/eye-tracker/mouse/joined-arms-r06');original=Part.Shape();original.read(str(out/'unblended.brep'));shape=original;report=[]
def match(ref):return min(shape.Edges,key=lambda e:(e.CenterOfMass-ref.CenterOfMass).Length+abs(e.Length-ref.Length))
for name,ids,radii in [('rear_root',[4,10,12],[.25,.2,.15]),('upper_root',[177],[.35,.25,.15]),('rear_stem',[337,339,23,338],[.3,.2,.1]),('upper_stem',[302,327,328],[.3,.2,.1])]:
 refs=[original.Edges[i-1] for i in ids];edges=[match(e) for e in refs]
 for radius in radii:
  try:
   candidate=shape.makeFillet(radius,edges);candidate.limitTolerance(1e-6);candidate.check(True)
   if not candidate.isValid() or len(candidate.Solids)!=1:raise ValueError('invalid result')
   change=candidate.Volume-shape.Volume;shape=candidate;report.append({'joint':name,'radius_mm':radius,'volume_change_mm3':change});print(name,'PASS',radius,change,flush=True);break
  except Exception as e:print(name,'failed',radius,str(e)[:80],flush=True)
 else:report.append({'joint':name,'failed':True})
shape.exportBrep(str(out/'blended.brep'));(out/'fillets.json').write_text(json.dumps(report,indent=2))

