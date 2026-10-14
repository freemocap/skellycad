"""Finish fixture junctions using geometric signatures, never changing arm thickness."""
from pathlib import Path
import json
import FreeCAD as A,Part,MeshPart

def finish(recipe_path,out):
 cfg=json.loads(Path(recipe_path).read_text());out=Path(out);shape=Part.Shape();shape.read(str(out/'unblended.brep'));original=shape.copy();arms=json.loads((out/'arms.json').read_text());jobs=list(cfg['root_blends'])
 for name in ['UpperSupport','RearRibbonGuard']:
  arm=arms[name];c=A.Vector(*arm['socket_center_mm']);n=A.Vector(*arm['socket_axis']);v=A.Vector(*arm['arm']['radial_direction']);t=v.cross(n);height=arm['attachment_height_mm'];edges=[]
  for e in original.Edges:
   p=e.CenterOfMass-c;x,y,z=p.dot(v),p.dot(t),p.dot(n)
   if 1.8<x<2.7 and abs(y)<1.501 and (abs(z-height)<1e-5 or abs(abs(z-height)-1.1)<1e-5) and (abs(e.Length-2.2)<.001 or abs(e.Length-3.1805)<.002):edges.append(e)
  assert len(edges)==4,(name,len(edges))
  jobs.append({'name':name+'_socket','method':'chamfer' if name=='UpperSupport' else 'fillet','size_mm':.05 if name=='UpperSupport' else .3,'edge_signatures':[{'center_mm':list(e.CenterOfMass),'length_mm':e.Length} for e in edges]})
 report=[]
 for job in jobs:
  matches=[]
  for ref in job['edge_signatures']:
   def score(e):return (e.CenterOfMass-A.Vector(*ref['center_mm'])).Length+abs(e.Length-ref['length_mm'])
   edge=min(shape.Edges,key=score);assert score(edge)<1e-4,(job['name'],score(edge));matches.append(edge)
  operation=shape.makeFillet if job['method']=='fillet' else shape.makeChamfer
  candidate=operation(job['size_mm'],matches);candidate.limitTolerance(1e-6);candidate.check(True);assert candidate.isValid() and len(candidate.Solids)==1;report.append(dict(job,volume_change_mm3=candidate.Volume-shape.Volume));shape=candidate;print('finished',job['name'],flush=True)
 # Preserve R08 cosmetic cleanup on the unchanged tray back face.
 shape=shape.cut(Part.makeBox(3.70677424482636-3.2,3.7,5.8,A.Vector(3.2,11.4,-2.9))).removeSplitter();shape.limitTolerance(1e-6);shape.check(True)
 mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.03,AngularDeflection=.12,Relative=False);print('carrier mesh',mesh.isSolid(),mesh.hasSelfIntersections(),flush=True);assert mesh.isSolid() and not mesh.hasSelfIntersections()
 shape.exportBrep(str(out/'finished.brep'));(out/'junctions.json').write_text(json.dumps(report,indent=2));return shape
