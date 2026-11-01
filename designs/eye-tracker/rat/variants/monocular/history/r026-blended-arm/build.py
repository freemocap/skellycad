from pathlib import Path
import sys,json,hashlib,math
import numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/blended-arm-r26';O=R/'generated/eye-tracker/rat/blended-arm-r26';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
sys.path.insert(0,str(R/'designs/eye-tracker/shared/compact-guard-r02'));from guard import unit,rectangle
m=json.loads((S.parent/'joined-arm-r25/review.json').read_text());assert hashlib.sha256((R/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(R/m['native_checkpoint']))
sol=json.loads((S.parent/'oval-camera-r21/solution.json').read_text());M=A.Placement(A.Matrix(*sum(sol['mount_to_skull'],[])));H=np.array(sol['head'])
names=['RetainedPCBTray','RetainedSocket','eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','PCB','JST_4pin','camera_pcb','M4_lens','skull_mount_Baseplate','RibbonCandidate'];sh={n:world(d.getObject(n)).transformed(M.inverse().toMatrix()) for n in names}
cfg=json.loads((S.parent/'oval-camera-r21/arms.json').read_text())['RearRibbonGuard'];sc=A.Vector(*cfg['socket_center_mm']);axis=unit(cfg['socket_axis']);root=A.Vector(4.5,12.78,16.8)
# One curve from the embedded tray root to the socket: no separate elbow or connector loft.
radial=unit(A.Vector(-.85483722,-.29828025,.42459653));radial=unit(radial-axis*radial.dot(axis));tip=sc+axis*4.6+radial*1.6
poles=[root,root+A.Vector(-12,0,18),tip+radial*22,tip]
def oval_section(c,t,w,width,thickness,r=.4):
 n=unit(w.cross(t))
 return Part.Wire([Part.Ellipse(c+w*width/2,c+n*thickness/2,c).toShape()])
curve=Part.BezierCurve();curve.setPoles(poles);w=A.Vector(0,1,0);old=None;wires=[]
for i in range(65):
 u=i/64;c=curve.value(u);t=curve.tangent(u)[0]
 if old is not None:w=A.Rotation(old,t).multVec(w)
 w=unit(w-t*w.dot(t));old=t
 width=3.4+2.6*math.exp(-(u/.24)**2)+1.4*math.exp(-((1-u)/.16)**2)
 thickness=1.8+.4*math.exp(-((1-u)/.16)**2)
 wires.append(oval_section(c,t,w,width,thickness))
arm=Part.makeLoft(wires[::4],True,False,False,3);assert arm.isValid() and len(arm.Solids)==1
report={'source':m,'units':'mm','poles_mm':[[v.x,v.y,v.z] for v in poles],'arm_ribbon_gap_mm':arm.distToShape(sh['RibbonCandidate'])[0],'checks':{}}
for n,s in sh.items():report['checks'][n]=arm.common(s).Volume
print(report,flush=True);print('collision',arm.common(sh['RibbonCandidate']).BoundBox,flush=True);(O/'validation.json').write_text(json.dumps(report,indent=2))
for n in names:
 if n not in ['RetainedPCBTray','RetainedSocket']:assert report['checks'][n]<1e-5,(n,report['checks'][n])
assert report['checks']['RetainedPCBTray']>.1 and report['checks']['RetainedSocket']>.1
carrier=sh['RetainedPCBTray'].fuse(sh['RetainedSocket']).fuse(arm).removeSplitter();carrier=carrier.cut(Part.makeBox(.50677424482636,3.7,5.8,A.Vector(3.2,11.4,-2.9))).cut(Part.makeBox(1.4,4.5,3.2,A.Vector(4.8,10.53,16.4))).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1

edges=[e for e in carrier.Edges if abs(e.BoundBox.XMin-3.70677424482636)<.001 and abs(e.BoundBox.XMax-3.70677424482636)<.001 and e.BoundBox.ZMin>15.5 and e.BoundBox.ZMax<18.5 and e.BoundBox.YMin>9 and e.BoundBox.YMax<16]
print('root edges',[(i,e.Length) for i,e in enumerate(edges)],flush=True)
carrier=carrier.makeFillet(.5,edges).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1
socket_edges=[e for e in carrier.Edges if type(e.Curve).__name__=='BSplineCurve' and (e.CenterOfMass-sc).Length<5 and 3<(e.CenterOfMass-sc).dot(axis)<6]
print('socket edges',[(e.Length,(e.CenterOfMass-sc).dot(axis)) for e in socket_edges],flush=True)
socket_blend=[e for e in socket_edges if 3.1<e.Length<3.25 and (e.CenterOfMass-sc).dot(axis)>3.85]
assert len(socket_blend)==1
carrier=carrier.makeFillet(.4,socket_blend).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1
report['socket_fillet_radius_mm']=.4
report['root_fillet_radius_mm']=.5;report['finished_ribbon_overlap_mm3']=carrier.common(sh['RibbonCandidate']).Volume;report['finished_ribbon_gap_mm']=carrier.distToShape(sh['RibbonCandidate'])[0]
for n in ['PCB','eye_primary_Holder','camera_pcb','M4_lens']:assert carrier.common(sh[n]).Volume<1e-5
(O/'validation.json').write_text(json.dumps(report,indent=2))
assert carrier.common(sh['RibbonCandidate']).Volume<1e-6
assign(d.FinishedCarrier,carrier.transformed(M.toMatrix()));assign(d.SingleTaperedArm,arm.transformed(M.toMatrix()))
for label,s in [('carrier',world(d.FinishedCarrier)),('ribbon',world(d.RibbonCandidate))]:
 mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False);print(label,mesh.isSolid(),mesh.getSelfIntersections()[:3],flush=True);assert mesh.isSolid() and not mesh.hasSelfIntersections();mesh.write(str(O/(label+'.stl')))
d.Label='Rat R26 - rounded arm and blended junctions';d.recompute();d.saveAs(str(O/'ET-RAT-BLENDED-ARM-R26.FCStd'));print('SAVED',flush=True)











