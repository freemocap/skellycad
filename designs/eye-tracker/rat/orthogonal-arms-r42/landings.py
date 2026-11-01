from support import *
import shutil,datetime
archive=O/('before-landings-'+datetime.datetime.now().strftime('%H%M%S'));archive.mkdir()
for name in ['04-arms.FCStd','04-arms-working.FCStd','04-arms.json']:
 shutil.copy2(O/name,archive/name)
d=load('04-arms-working');s=local(d.CentralCarrier);baseline=load('source');before=local(baseline.CentralCarrier).Volume;A.closeDocument(baseline.Name);added=[]
for side in [1,-1]:
 z=16.6 if side==1 else -20.
 for y,height in [(6.5,3.4),((15. if side==1 else 13.6),(2.6 if side==1 else 4.0))]:
  pad=Part.makeBox(1.8,height,3.4,A.Vector(2.38706399647303,y,z))
  edges=[e for e in pad.Edges if abs(e.Length-1.8)<1e-8]
  pad=pad.makeFillet(.6,edges);assert pad.isValid()
  added.append(pad)
from ribbon_envelope import ribbon_envelope
pars=json.loads((S.parent/'clear-view-r41/selected-pose.json').read_text())['parameters']
for i,side in enumerate(['Right','Left']):
 envelope,_,_=ribbon_envelope(pars[i*12:(i+1)*12]);envelope=moved(envelope,np.array(cfg['sides'][side]['board_transform']))
 added=[p.cut(envelope).removeSplitter() for p in added]
s=s.multiFuse(added).removeSplitter();assert s.isValid() and len(s.Solids)==1
for n,o in obstacles(d).items():
 assert s.common(o).Volume<1e-5,(n,s.common(o).Volume)
assign(d.CentralCarrier,moved(s,T));d.recompute();d.saveAs(str(O/'04-arms-working.FCStd'))
(O/'landings.json').write_text(json.dumps({'added_material_mm3':s.Volume-before,'thickness_mm':1.8,'outline_corner_radius_mm':.6,'outboard_limit_mount_z_mm':20.,'ribbon_relief_mm':.35},indent=2));A.closeDocument(d.Name)
