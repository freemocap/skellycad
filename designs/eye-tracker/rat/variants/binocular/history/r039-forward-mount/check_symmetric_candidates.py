from pathlib import Path
import sys,json,numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/forward-mount-r39';O=R/'generated/eye-tracker/rat/forward-mount-r39';OLD=R/'generated/eye-tracker/rat/refined-supports-r38';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world;from detailed_ribbon import ribbon_solid
cfg=json.loads((S/'recipe.json').read_text());T=np.array(cfg['mount_to_skull']);inv=np.linalg.inv(T);d=A.openDocument(str(O/'01-forward-mount.FCStd'))
def move(s,t):return s.transformed(A.Matrix(*np.asarray(t).ravel().tolist()))
central=move(world(d.CentralCarrier),inv);reports=[];OUT=O/'symmetric-fit';OUT.mkdir(exist_ok=True)
for idx,rec in enumerate(json.loads((O/'symmetric-roll-relaxed-distance.json').read_text())):
 obs={'central':central};ribs={};heads={};metrics={}
 for i,side in enumerate(['Right','Left']):
  H=inv@np.array(rec['heads_world'][i]);D=H@np.linalg.inv(np.array(cfg['sides'][side].get('previous_head',cfg['sides'][side]['head'])));heads[side]=H.tolist()
  for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001']:
   s=Part.Shape();s.read(str(OLD/(side+'-'+n+'.brep')));obs[side+n]=s if n in ['PCB','JST_4pin'] else move(s,D)
  for tail in ['eye_primary_Holder','eye_primary_Clip','RetainedSocket']:obs[side+tail]=move(move(world(d.getObject(side+tail)),inv),D)
  try:s,mesh,metric=ribbon_solid(rec['parameters'][i*12:(i+1)*12],nx=4,ny=100);ribs[side]=move(s,np.array(cfg['sides'][side]['board_transform']));metrics[side]=metric
  except Exception as e:print('INVALID_RIB',idx,side,str(e),flush=True);break
 if len(ribs)<2:continue
 # Native mesh intersection screening before expensive solid checks.
 bad={}
 for side,rib in ribs.items():
  rm=MeshPart.meshFromShape(Shape=rib,LinearDeflection=.04,AngularDeflection=.15,Relative=False)
  for n,s in obs.items():
   if not rib.BoundBox.intersect(s.BoundBox):continue
   mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.2,Relative=False);nf=rm.CountFacets;both=rm.copy();both.addMesh(mesh);cross=sum((p[0]<nf)!=(p[1]<nf) for p in both.getSelfIntersections())
   if cross:
    volume=rib.common(s).Volume
    if volume>1e-5:bad[side+'/'+n]={'crossings':cross,'volume':volume}
 print('CANDIDATE',idx,'COLLISIONS',bad,flush=True);reports.append({'candidate':idx,'mesh_crossings':bad,'metric':metrics})
 if idx==0 and all(n.endswith('/central') for n in bad):
  # Remove only bounded ribbon-exit interference plus 0.25 mm clearance.
  for side,rib in ribs.items():
   overlap=obs['central'].common(rib)
   if overlap.Volume>1e-7:
    b=overlap.BoundBox;tool=Part.makeBox(b.XLength+.5,b.YLength+.5,b.ZLength+.5,A.Vector(b.XMin-.25,b.YMin-.25,b.ZMin-.25))
    try:tool=tool.makeFillet(.2,tool.Edges)
    except Exception:pass
    obs['central']=obs['central'].cut(tool).removeSplitter()
  assert obs['central'].isValid() and len(obs['central'].Solids)==1
  assert all(obs['central'].common(rib).Volume<1e-6 for rib in ribs.values())
  rec['carrier_ribbon_exit_relief_mm']=.25
  for name,s in obs.items():s.exportBrep(str(OUT/(name+'.brep')))
  for side,s in ribs.items():s.exportBrep(str(OUT/(side+'-ribbon.brep')))
  rec.update(heads_mount=heads,ribbon_metric=metrics);(OUT/'selected-pose.json').write_text(json.dumps(rec,indent=2));break
(OUT/'candidate-collisions.json').write_text(json.dumps(reports,indent=2));A.closeDocument(d.Name)

