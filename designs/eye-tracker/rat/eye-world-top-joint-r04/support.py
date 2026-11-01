from pathlib import Path
import sys,json,math,numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/eye-world-top-joint-r04';O=R/'generated/eye-tracker/rat/eye-world-top-joint-r04';sys.path.insert(0,str(R/'designs/eye-tracker/rat/refined-supports-r38'));from common import section,unit
cfg=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());T=np.array(cfg['mount_to_skull'])
def read(n):
 s=Part.Shape();s.read(str(O/(n+'.brep')));return s
carrier=read('clean-carrier');socket=read('top-socket');holder=read('top-stem-holder');root=(T@np.array([3.28706399647303,16.9,-16,1]))[:3]
# One continuous arch enters the socket wall radially, leaving its axial bore open.
poles=[A.Vector(*root),A.Vector(root[0],root[1],26.5),A.Vector(10.85,13,27),A.Vector(10.85,6.3,25),A.Vector(10.85,3.25,24.65)]
c=Part.BezierCurve();c.setPoles(poles);wires=[]
for i in range(33):
 u=i/32;p=c.value(u);t=unit(c.tangent(u)[0]);w=unit(A.Vector(1,0,0)-t*t.x);width=3.-1.4*math.exp(-(u/.12)**2);thick=3.-.4*u
 wires.append(section(p,t,w,width,thick,False))
beam=Part.makeLoft(wires[::2],True,False,False,3);seats=[beam.common(carrier).Volume,beam.common(socket).Volume];print('SEATS',seats,flush=True);assert min(seats)>.3
combined=carrier.multiFuse([beam,socket]).removeSplitter();assert combined.isValid() and len(combined.Solids)==1
report={'seating_mm3':seats,'poles_world_mm':[list(v) for v in poles],'joins':{},'collisions':{}}
# Concave junction blends add material at the root and at the socket wall.
for name,point in [('root',poles[0]),('socket',poles[-1])]:
 edges=sorted([e for e in combined.Edges if 1<e.Length<15 and (e.CenterOfMass-point).Length<4],key=lambda e:(e.CenterOfMass-point).Length)
 found=False
 for radius in [.8,.6,.4,.3]:
  for e in edges[:20]:
   try:trial=combined.makeFillet(radius,[e])
   except Exception:continue
   if not trial.isValid() or len(trial.Solids)!=1 or not .01<trial.Volume-combined.Volume<15:continue
   if trial.common(holder).Volume>1e-5:continue
   report['joins'][name]={'radius_mm':radius,'added_mm3':trial.Volume-combined.Volume};combined=trial;found=True;break
  if found:break
 assert found,('No blend',name)
for n in ['Ribbon','camera_pcb','M4_lens','IR_LED','IR_LED_001','top-stem-holder']:
 s=read(n);v=combined.common(s).Volume;report['collisions'][n]=v;assert v<1e-5,(n,v)
# A cylindrical bore check independently protects access through the existing socket.
bore=Part.makeCylinder(2.0,12,A.Vector(10.85,.861,19),A.Vector(0,0,1));assert beam.common(bore).Volume<1e-5
combined.exportBrep(str(O/'supported-carrier.brep'));beam.exportBrep(str(O/'world-support.brep'));report['carrier_valid']=True;report['carrier_solids']=len(combined.Solids);(O/'support-validation.json').write_text(json.dumps(report,indent=2));print(report,flush=True)

