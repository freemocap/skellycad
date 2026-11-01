from pathlib import Path
import json,sys,numpy as np
import FreeCAD as A,Part,MeshPart,Mesh
R=Path.cwd();S=R/'designs/eye-tracker/rat/forward-mount-r39';O=R/'generated/eye-tracker/rat/forward-mount-r39';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));import ribbon_geometry as g
sel=json.loads((O/'selected-pose.json').read_text());cfg=json.loads((S/'recipe.json').read_text());T=A.Matrix(*np.array(cfg['mount_to_skull']).ravel().tolist());report={'passed':False,'model':'Piecewise cylindrical isometric sheet; no imposed axial material twist; oblique bend zones allowed','physical_fit_verified':False,'sides':{}}
obs={}
for p in O.glob('*.brep'):
 s=Part.Shape();s.read(str(p));obs[p.stem]=s
skull=Mesh.Mesh(str(O/'skull.stl'))
for i,side in enumerate(['Right','Left']):
 s=obs[side+'-ribbon'];bad={};checks={}
 for n,o in obs.items():
  if n==side+'-ribbon':continue
  v=s.common(o).Volume;checks[n]=v
  if v>1e-5:bad[n]=v
 assert not bad,bad
 mesh=MeshPart.meshFromShape(Shape=s.transformed(T),LinearDeflection=.04,AngularDeflection=.15,Relative=False);assert mesh.isSolid() and not mesh.hasSelfIntersections();n=mesh.CountFacets;mesh.addMesh(skull);cross=sum((p[0]<n)!=(p[1]<n) for p in mesh.getSelfIntersections());assert cross==0,(side,cross)
 p=np.array(sel['parameters'][i*12:(i+1)*12]).reshape(3,4);inside=float(min(p[:,0])-.25);assert inside>=3.5-1e-8
 assert g.zones(p.ravel())[-1][-1]<32.85
 report['sides'][side]={'neutral_sheet_length_mm':32.85,'width_mm':4,'thickness_mm':.25,'minimum_inside_radius_mm':inside,'imposed_material_twist_deg':0,'surface_metric':sel['ribbon_metric'][side],'checks_mm3':checks,'skull_crossings':cross,'bend_parameters':p.tolist()}
 print('RIBBON_PASS',side,inside,flush=True)
report['passed']=True;(O/'03-ribbon-validation.json').write_text(json.dumps(report,indent=2))
