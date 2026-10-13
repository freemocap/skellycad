"""Fit a low-complexity quintic guide to V5 centers with fixed R03 end tangents."""
from pathlib import Path
import json,math
import numpy as np
from scipy.optimize import lsq_linear
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
p=json.loads((HERE.parent/'model/attachment-arms.json').read_text())
a=p['rear'];root=np.array(a['root_mm']);t0=np.array(a['root_tangent']);n=np.array(p['socket_axis']);r=np.array(a['radial_direction'])
start=root+t0*(p['embed_mm']+p['root_lead_mm'])
end=np.array(p['socket_center_mm'])+n*p['attachment_height_mm']+r*2.65
stop=end+r*1.0;t1=-r
pts=np.array([s['center_mm'] for s in json.loads((HERE.parent/'model/v5-recovered-sections.json').read_text())['arms']['rear']['sections']])[::-1]
# Trim the old embedded tray end; start near the new straight lead exit.
pts=pts[np.linalg.norm(pts-start,axis=1)>0.0]
pts=pts[np.arange(len(pts))>=np.argmin(np.linalg.norm(pts-start,axis=1))]
s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(pts,axis=0),axis=1))];s/=s[-1]
u=np.linspace(0,1,81);target=np.array([np.interp(u,s,pts[:,i]) for i in range(3)]).T
# Endpoint correction brings the legacy ends to the accepted R03 attachments.
target+=(1-u[:,None])*(start-target[0])+u[:,None]*(stop-target[-1])
basis=np.array([math.comb(5,i)*u**i*(1-u)**(5-i) for i in range(6)]).T
# Unknowns: start handle, end handle, and two unconstrained interior poles.
M=np.zeros((len(u),3,8));M[:,:,0]=basis[:,1,None]*t0;M[:,:,1]=-basis[:,4,None]*t1
for j in range(3):M[:,j,2+j]=basis[:,2];M[:,j,5+j]=basis[:,3]
fixed=(basis[:,0]+basis[:,1])[:,None]*start+(basis[:,4]+basis[:,5])[:,None]*stop
lo=np.r_[1.,1.,[-30]*6];hi=np.r_[15.,15.,[40]*6];hi[7]=27.0  # prevent a hump beyond the socket in Z
fit=lsq_linear(M.reshape(-1,8),(target-fixed).ravel(),bounds=(lo,hi));v=fit.x
poles=np.array([start,start+t0*v[0],v[2:5],v[5:8],stop-t1*v[1],stop])
result={'units':'mm','baseline':'R03','source':'registered V5 rear-arm section centers',
 'centerline_type':'degree-5 Bezier; fixed R03 end positions and tangents',
 'fit_rms_mm':float(np.sqrt(np.mean(np.sum((basis@poles-target)**2,axis=1)))),
 'poles_mm':poles.tolist(),
 'variants':{'A':{'label':'V5-guided sweep','extra_drop_mm':0.0},'B':{'label':'Extra ribbon space','extra_drop_mm':1.25}},
 'extra_drop_direction':[0,-1,0],
 'note':'Extra drop moves only the two interior poles, scaled for a 1.25 mm midpoint change; endpoints/tangents fixed. Ribbon is not modeled.'}
(HERE/'settings.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))



