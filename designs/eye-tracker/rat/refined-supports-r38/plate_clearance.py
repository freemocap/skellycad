from common import *
d=load('03-plate');obs=obstacles(d);report=json.loads((O/'plate-working.json').read_text());report['root_clearance_removal_mm3']={}
for side in ['Right','Left']:
 b=obs[side+'PCB'].BoundBox;tool=Part.makeBox(b.XLength+.1,b.YLength+.1,b.ZLength+.1,A.Vector(b.XMin-.05,b.YMin-.05,b.ZMin-.05))
 for tail in ['UpperSupport','LowerSupport']:
  o=d.getObject(side+tail);old=local(o)
  if old.common(obs[side+'PCB']).Volume<1e-6:continue
  new=old.cut(tool).removeSplitter();assert new.isValid() and len(new.Solids)==1;assign(o,moved(new,T));report['root_clearance_removal_mm3'][side+tail]=old.Volume-new.Volume
c=rebuild(d)
for name,s in obs.items():assert c.common(s).Volume<1e-5,(name,c.common(s).Volume)
save(d,'03-plate',report);print('PLATE_AND_PCB_FIT_PASS',report)
