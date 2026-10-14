from pathlib import Path
import FreeCAD as A,Part,json
out=Path('generated/eye-tracker/mouse/inset-arm-r08');base=Part.Shape();base.read('generated/eye-tracker/mouse/joined-arms-r06/unblended.brep');shape=Part.Shape();shape.read(str(out/'unblended.brep'));report=[]
cfg=json.loads((out/'arms.json').read_text())['UpperSupport'];shift=A.Vector(*cfg['socket_axis'])*-1.1
for name,ids,size,mode in [('upper_root',[177],.35,'fillet'),('rear_stem',[337,339,23,338],.3,'fillet'),('upper_stem',[302,325,326,332],.05,'chamfer'),('rear_root',[4,10,12],.2,'chamfer')]:
 refshape=Part.Shape();refshape.read(str(out/'unblended.brep'))
 refs=[(refshape if name=='upper_stem' else base).Edges[i-1].copy() for i in ids]
 edges=[min(shape.Edges,key=lambda e:(e.CenterOfMass-ref.CenterOfMass).Length+abs(e.Length-ref.Length)) for ref in refs]
 print(name,'match scores',[(e.CenterOfMass-ref.CenterOfMass).Length+abs(e.Length-ref.Length) for e,ref in zip(edges,refs)],flush=True)
 for radius in [size,size*.66,size*.33]:
  try:
   candidate=shape.makeFillet(radius,edges) if mode=='fillet' else shape.makeChamfer(radius,edges);candidate.limitTolerance(1e-6);candidate.check(True);assert candidate.isValid() and len(candidate.Solids)==1
   report.append(dict(joint=name,method=mode,size_mm=radius,volume_change_mm3=candidate.Volume-shape.Volume));shape=candidate;print(name,'PASS',radius,flush=True);break
  except Exception as e:print(name,'FAIL',radius,str(e)[:100],flush=True)
 else:raise RuntimeError(name+' could not be blended')
label=Part.makeBox(3.70677424482636-3.2,3.7,5.8,A.Vector(3.2,11.4,-2.9));shape=shape.cut(label).removeSplitter();shape.limitTolerance(1e-6);shape.check(True)
shape.exportBrep(str(out/'finished.brep'));(out/'fillets.json').write_text(json.dumps(report,indent=2))


