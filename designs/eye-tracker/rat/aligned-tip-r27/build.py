from pathlib import Path
import sys,json,hashlib,math
import numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/aligned-tip-r27';O=R/'generated/eye-tracker/rat/aligned-tip-r27';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
sys.path.insert(0,str(R/'designs/eye-tracker/shared/compact-guard-r02'));from guard import unit,rectangle
m=json.loads((S.parent/'blended-arm-r26/review.json').read_text());assert hashlib.sha256((R/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(R/m['native_checkpoint']))
sol=json.loads((S.parent/'oval-camera-r21/solution.json').read_text());M=A.Placement(A.Matrix(*sum(sol['mount_to_skull'],[])));H=np.array(sol['head'])
names=['RetainedPCBTray','RetainedSocket','eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','PCB','JST_4pin','camera_pcb','M4_lens','skull_mount_Baseplate','RibbonCandidate'];sh={n:world(d.getObject(n)).transformed(M.inverse().toMatrix()) for n in names}
cfg=json.loads((S.parent/'oval-camera-r21/arms.json').read_text())['RearRibbonGuard'];sc=A.Vector(*cfg['socket_center_mm']);axis=unit(cfg['socket_axis']);root=A.Vector(4.5,11.8,16.8)
# One curve from the embedded tray root to the socket: no separate elbow or connector loft.
radial=unit(A.Vector(-.85483722,-.29828025,.42459653));radial=unit(radial-axis*radial.dot(axis));tip=sc+axis*3.7+radial*1.5
poles=[root,root+A.Vector(-12,0,18),tip+radial*22,tip]
def flat_section(c,t,w,width,thickness,r=.2):
 n=unit(w.cross(t));a=width/2;b=thickness/2
 xy=[(a-r,b),(-a+r,b),(-a,b-r),(-a,-b+r),(-a+r,-b),(a-r,-b),(a,-b+r),(a,b-r)]
 points=[c+w*x+n*y for x,y in xy];return Part.makePolygon(points+[points[0]])
curve=Part.BezierCurve();curve.setPoles(poles);w=A.Vector(0,1,0);old=None;wires=[];frames=[]
for i in range(65):
 u=i/64;c=curve.value(u);t=curve.tangent(u)[0]
 if old is not None:w=A.Rotation(old,t).multVec(w)
 w=unit(w-t*w.dot(t));old=t;frames.append((c,t,w))
tipnormal=A.Vector(*H[:3,2]);tipwidth=unit(frames[-1][1].cross(tipnormal))
if tipwidth.dot(frames[-1][2])<0:tipwidth=-tipwidth
angle=math.degrees(math.atan2(frames[-1][1].dot(frames[-1][2].cross(tipwidth)),frames[-1][2].dot(tipwidth)))
for i,(c,t,w) in enumerate(frames):
 u=i/64;v=max(0,min(1,(u-.15)/.85));w=A.Rotation(t,angle*(3*v*v-2*v**3)).multVec(w)
 width=2.6+1.8*(1-u)**2
 thickness=1.8-.2*(3*u*u-2*u**3)
 wires.append(flat_section(c,t,w,width,thickness))
arm=Part.makeLoft(wires[::4],True,False,False,3);assert arm.isValid() and len(arm.Solids)==1
report={'source':m,'units':'mm','poles_mm':[[v.x,v.y,v.z] for v in poles],'arm_ribbon_gap_mm':arm.distToShape(sh['RibbonCandidate'])[0],'checks':{}}
for n,s in sh.items():report['checks'][n]=arm.common(s).Volume
print(report,flush=True);print('collision',arm.common(sh['RibbonCandidate']).BoundBox,flush=True);(O/'validation.json').write_text(json.dumps(report,indent=2))
for n in names:
 if n not in ['RetainedPCBTray','RetainedSocket']:assert report['checks'][n]<1e-5,(n,report['checks'][n])
assert report['checks']['RetainedPCBTray']>.1 and report['checks']['RetainedSocket']>.1
carrier=sh['RetainedPCBTray'].fuse(sh['RetainedSocket']).fuse(arm).removeSplitter();carrier=carrier.cut(Part.makeBox(.50677424482636,3.7,5.8,A.Vector(3.2,11.4,-2.9))).cut(Part.makeBox(1.4,4.5,3.2,A.Vector(4.8,10.53,16.4))).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1

rootedges=[e for e in carrier.Edges if abs(e.BoundBox.XMin-3.70677424482636)<.001 and abs(e.BoundBox.XMax-3.70677424482636)<.001 and e.BoundBox.ZMin>15.5 and e.BoundBox.ZMax<18.5 and e.BoundBox.YLength>3 and e.BoundBox.YMin>9 and e.BoundBox.YMax<14.1]
carrier=carrier.makeFillet(.4,rootedges).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1
socketedges=[e for e in carrier.Edges if (e.CenterOfMass-sc).Length<4 and type(e.Curve).__name__=='BSplineCurve' and 2.8<(e.CenterOfMass-sc).dot(axis)<3.1]
assert len(socketedges)==1
carrier=carrier.makeFillet(.35,socketedges).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1
report['root_fillet_mm']=.4;report['socket_fillet_mm']=.35
report['tip_width_mm']=2.6;report['tip_thickness_mm']=1.6;report['width_frame_rotation_deg']=angle;report['finished_ribbon_overlap_mm3']=carrier.common(sh['RibbonCandidate']).Volume;report['finished_ribbon_gap_mm']=carrier.distToShape(sh['RibbonCandidate'])[0]
for n in ['PCB','eye_primary_Holder','camera_pcb','M4_lens']:assert carrier.common(sh[n]).Volume<1e-5
(O/'validation.json').write_text(json.dumps(report,indent=2))
assert carrier.common(sh['RibbonCandidate']).Volume<1e-6
assign(d.FinishedCarrier,carrier.transformed(M.toMatrix()));assign(d.SingleTaperedArm,arm.transformed(M.toMatrix()))
for label,s in [('carrier',world(d.FinishedCarrier)),('ribbon',world(d.RibbonCandidate))]:
 mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False);print(label,mesh.isSolid(),mesh.getSelfIntersections()[:3],flush=True);assert mesh.isSolid() and not mesh.hasSelfIntersections();mesh.write(str(O/(label+'.stl')))
d.Label='Rat R27 - ribbon-facing tapered socket join';d.recompute();d.saveAs(str(O/'ET-RAT-ALIGNED-TIP-R27.FCStd'));print('SAVED',flush=True)














