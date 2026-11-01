from pathlib import Path
import FreeCAD as A,Part,json,numpy as np
O=Path('generated/eye-tracker/rat/eye-world-tray-r03');P=Path('generated/eye-tracker/rat/eye-world-ribbon-r02')
def read(n,folder=O):
 s=Part.Shape();s.read(str(folder/(n+'.brep')));return s
c=read('CentralCarrier');f=read('FinishedCarrier');b=c.BoundBox;pad=.02
new=f
# Independent half-space cuts remove only appendage material outside the full
# central-holder bounding region. Never fuse coincident halves of that holder.
cutters=[Part.makeBox(200,100,200,A.Vector(-100,b.YMax+pad,-100)),
 Part.makeBox(100,100,200,A.Vector(b.XMax+pad,0,-100)),
 Part.makeBox(100,100,200,A.Vector(b.XMin-pad-100,0,-100)),
 Part.makeBox(200,100,100,A.Vector(-100,0,b.ZMax+pad)),
 Part.makeBox(200,100,100,A.Vector(-100,0,b.ZMin-pad-100))]
for i,tool in enumerate(cutters):
 print('CUT',i,flush=True);new=new.cut(tool).removeSplitter()
print('CARRIER',new.Volume,new.isValid(),len(new.Solids),flush=True);assert new.isValid() and len(new.Solids)==1
pts=c.tessellate(.05)[0];step=max(1,len(pts)//200);bad=[list(v) for v in pts[::step] if not new.isInside(v,1e-4,True)];print('central_missing_samples',len(bad),'of',len(pts[::step]),flush=True);assert not bad
new.exportBrep(str(O/'restored-carrier.brep'))
H=np.array(json.loads(Path('designs/eye-tracker/rat/eye-world-ribbon-r02/selected-pose.json').read_text())['head_world']);tray=read('stemless-tray-head').transformed(A.Matrix(*H.ravel().tolist()));tray.exportBrep(str(O/'world-stemless-tray.brep'))
report={'central_surface_samples_preserved':len(pts[::step]),'carrier_solids':len(new.Solids),'carrier_valid':new.isValid(),'tray_valid':tray.isValid(),'tray_solids':len(tray.Solids),'overlaps_mm3':{}}
for n in ['Ribbon','camera_pcb','M4_lens','IR_LED','IR_LED_001']:
 sh=read(n,P)
 for k,s in [('tray',tray),('carrier',new)]:
  v=s.common(sh).Volume;report['overlaps_mm3'][k+'/'+n]=v;print(k,n,v,flush=True)
print('tray/carrier',tray.common(new).Volume,flush=True);report['overlaps_mm3']['tray/carrier']=tray.common(new).Volume
(O/'repair-validation.json').write_text(json.dumps(report,indent=2))

