from pathlib import Path
import trimesh,numpy as np,json
O=Path('generated/eye-tracker/rat/forward-mount-r39');r=json.loads((O/'label-region.json').read_text());report={'passed':False,'parts':{}}
for n in ['CentralCarrier','FinishedCarrier']:
 a,b=[trimesh.load_mesh(O/(n+'-label-'+s+'.stl')) for s in ['before','after']];rng=np.random.default_rng(39);p=rng.uniform(a.bounds[0],a.bounds[1],(2000,3));outside=np.any((p<np.array(r['min'])-.05)|(p>np.array(r['max'])+.05),axis=1);p=p[outside];diff=int(np.count_nonzero(a.contains(p)!=b.contains(p)));assert diff==0,(n,diff);report['parts'][n]={'samples':len(p),'occupancy_differences':diff};print(n,len(p),diff,flush=True)
report['passed']=True;(O/'label-audit.json').write_text(json.dumps(report,indent=2))

