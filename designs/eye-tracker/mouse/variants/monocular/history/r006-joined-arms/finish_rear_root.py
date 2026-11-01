import FreeCAD as A,Part,json
from pathlib import Path
out=Path('generated/eye-tracker/mouse/joined-arms-r06');base=Part.Shape();base.read(str(out/'unblended.brep'));shape=Part.Shape();shape.read(str(out/'blended.brep'))
for mode,ids,radius in [('chamfer',[4,10,12],.2),('fillet',[7],.3),('fillet',[12],.1)]:
 edges=[min(shape.Edges,key=lambda e:(e.CenterOfMass-base.Edges[i-1].CenterOfMass).Length+abs(e.Length-base.Edges[i-1].Length)) for i in ids]
 try:
  result=shape.makeChamfer(radius,edges) if mode=='chamfer' else shape.makeFillet(radius,edges);result.limitTolerance(1e-6);result.check(True);assert result.isValid() and len(result.Solids)==1
  print('PASS',mode,ids,radius,result.Volume-shape.Volume,flush=True);result.exportBrep(str(out/'finished.brep'));report=json.loads((out/'fillets.json').read_text());report=[x for x in report if x['joint']!='rear_root'];report.append({'joint':'rear_root','method':mode,'radius_or_size_mm':radius,'edges_in_unblended':ids,'volume_change_mm3':result.Volume-shape.Volume});(out/'fillets.json').write_text(json.dumps(report,indent=2));break
 except Exception as e:print('FAIL',mode,ids,str(e)[:100],flush=True)
