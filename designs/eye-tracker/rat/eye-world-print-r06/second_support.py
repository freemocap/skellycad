from pathlib import Path
import sys,json,math,numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/eye-world-print-r06';O=R/'generated/eye-tracker/rat/eye-world-print-r06';P=O;sys.path.insert(0,str(R/'designs/eye-tracker/rat/refined-supports-r38'));from common import section,unit
cfg=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());T=np.array(cfg['mount_to_skull'])
def read(n):
 s=Part.Shape();s.read(str(P/(n+'.brep')));return s
carrier=read('finished-carrier');socket=read('top-socket');holder=read('finished-holder');root=(T@np.array([3.28706399647303,16.9,-.899537940320204,1]))[:3]
# One continuous arch enters the socket wall radially, leaving its axial bore open.
poles=[A.Vector(*root),A.Vector(root[0],root[1],23.5),A.Vector(6.5,root[1],24.65),A.Vector(9,root[1],24.65),A.Vector(10.4,root[1],24.65)]
c=Part.BezierCurve();c.setPoles(poles);wires=[]
for i in range(33):
 u=i/32;p=c.value(u);t=unit(c.tangent(u)[0]);w=A.Vector(0,1,0);width=2.8;thick=2.6-1.1*math.exp(-(u/.12)**2)
 wires.append(section(p,t,w,width,thick,False))
beam=Part.makeLoft(wires[::2],True,False,False,3);seats=[beam.common(carrier).Volume,beam.common(socket).Volume];print('SEATS',seats,flush=True);assert min(seats)>.3
combined=carrier.fuse(beam).removeSplitter();assert combined.isValid() and len(combined.Solids)==1
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
for n in ['Ribbon','camera_pcb','M4_lens','IR_LED','IR_LED_001','finished-holder','world-clip']:
 s=read(n);v=combined.common(s).Volume;report['collisions'][n]=v;assert v<1e-5,(n,v)
# A cylindrical bore check independently protects access through the existing socket.
bore=Part.makeCylinder(2.0,12,A.Vector(12.85,.861,19),A.Vector(0,0,1));assert beam.common(bore).Volume<1e-5
old=np.array(json.loads((P/'support-validation.json').read_text())['poles_world_mm']);a1=old[-2]-old[-1];a2=np.array(list(poles[-2]-poles[-1]));report['socket_approach_angle_degrees']=float(np.degrees(np.arccos(np.dot(a1,a2)/np.linalg.norm(a1)/np.linalg.norm(a2))));assert abs(report['socket_approach_angle_degrees']-90)<1e-6
combined.exportBrep(str(O/'finished-carrier.brep'));beam.exportBrep(str(O/'world-support.brep'));report['carrier_valid']=True;report['carrier_solids']=len(combined.Solids);(O/'second-support-validation.json').write_text(json.dumps(report,indent=2));print(report,flush=True)


inv=np.linalg.inv(T);local=combined.transformed(A.Matrix(*inv.ravel().tolist()))
for lin,ang in [(.04,.15),(.02,.1),(.08,.2)]:
 mesh=MeshPart.meshFromShape(Shape=local,LinearDeflection=lin,AngularDeflection=ang,Relative=False)
 if mesh.isSolid() and not mesh.hasSelfIntersections():break
else:raise RuntimeError('Carrier mesh defect')
report['mesh']={'closed':True,'self_intersections':False,'frame':'mount','linear_deflection_mm':lin,'angular_deflection_rad':ang};(O/'second-support-validation.json').write_text(json.dumps(report,indent=2));print('MESH_PASS',flush=True)
