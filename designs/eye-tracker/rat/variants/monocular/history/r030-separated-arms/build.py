from pathlib import Path
import sys,json,hashlib,math,zipfile
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/separated-arms-r30';O=R/'generated/eye-tracker/rat/separated-arms-r30';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world,assign
m=json.loads((S.parent/'outer-arms-r29/review.json').read_text());p=R/m['native_checkpoint'];assert hashlib.sha256(p.read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(p));sol=json.loads((S.parent/'oval-camera-r21/solution.json').read_text());M=A.Placement(A.Matrix(*sum(sol['mount_to_skull'],[])))
names=['RetainedPCBTray','RetainedSocket','RibbonCandidate','eye_primary_Holder','eye_primary_Clip','camera_pcb','M4_lens','PCB','JST_4pin','eye_primary_Cap','skull_mount_Baseplate'];sh={n:world(d.getObject(n)).transformed(M.inverse().toMatrix()) for n in names}
def unit(v):
 v=A.Vector(v);v.normalize();return v
cfg=json.loads((S.parent/'oval-camera-r21/arms.json').read_text())['RearRibbonGuard'];sc=A.Vector(*cfg['socket_center_mm']);axis=unit(A.Vector(*cfg['socket_axis']));rad=unit(A.Vector(-.85483722,-.29828025,.42459653));rad=unit(rad-axis*rad.dot(axis))
def section(c,t,w,width,thick):
 n=unit(w.cross(t));a=width/2;b=thick/2;r=.2;xy=[(a-r,b),(-a+r,b),(-a,b-r),(-a,-b+r),(-a+r,-b),(a-r,-b),(a,-b+r),(a,b-r)];v=[c+w*x+n*y for x,y in xy];return Part.makePolygon(v+[v[0]])
def make(root,radial):
 tip=sc+axis*3.7+radial*2.3;poles=[root,root+A.Vector(-14,0,20),tip+radial*24,tip];curve=Part.BezierCurve();curve.setPoles(poles);frames=[];w=A.Vector(0,1,0);old=None
 for i in range(65):
  u=i/64;t=curve.tangent(u)[0]
  if old is not None:w=A.Rotation(old,t).multVec(w)
  w=unit(w-t*w.dot(t));frames.append((curve.value(u),t,w));old=t
 target=unit(radial.cross(axis))
 if target.dot(w)<0:target=-target
 angle=math.degrees(math.atan2(t.dot(w.cross(target)),w.dot(target)));wires=[]
 for i,(c,t,w) in enumerate(frames):
  u=i/64;f=u*u*(3-2*u);w=A.Rotation(t,angle*f).multVec(w);wires.append(section(c,t,w,2.2+.8*(1-u)**2,1.8))
 arm=Part.makeLoft(wires[::4],True,False,False,3);return arm,poles
arms=[];report={'source':m,'units':'mm','arms':{},'fixed':'R28 camera, ribbon, anatomy, baseplate, C01 clip, optical axes','outside_route':'R27 protective rearward route, split into two separated roots and collar attachments'}
for name,y,ang in [('UpperSupport',17.5,-10),('RearRibbonGuard',8.0,50)]:
 arm,poles=make(A.Vector(4.5,y,16.8),unit(A.Rotation(axis,ang).multVec(rad)));check={n:arm.common(s).Volume for n,s in sh.items()};gap=arm.distToShape(sh['RibbonCandidate'])[0];print(name,'gap',gap,'checks',check,flush=True)
 assert arm.isValid() and len(arm.Solids)==1
 assert check['RetainedPCBTray']>.1 and check['RetainedSocket']>.1
 assert all(v<1e-5 for n,v in check.items() if n not in ['RetainedPCBTray','RetainedSocket']);assert gap>.65
 arms.append(arm);assign(d.getObject(name),arm.transformed(M.toMatrix()));report['arms'][name]={'poles_mm':[list(v) for v in poles],'gap_mm':gap,'intersections_mm3':check}
# Check the individual supports BEFORE fusion; union validity cannot detect crossed arms.
arm_overlap=arms[0].common(arms[1]).Volume
free=[a.cut(sh['RetainedSocket']).cut(sh['RetainedPCBTray']) for a in arms]
free_overlap=free[0].common(free[1]).Volume;free_gap=free[0].distToShape(free[1])[0]
print('ARM PAIR',arm_overlap,free_overlap,free_gap,flush=True)
assert arm_overlap<1e-6 and free_overlap<1e-6 and free_gap>.3
report['arm_pair']={'overlap_mm3':arm_overlap,'free_span_overlap_mm3':free_overlap,'free_span_gap_mm':free_gap}
carrier=sh['RetainedPCBTray'].multiFuse([sh['RetainedSocket'],*arms]).removeSplitter();carrier=carrier.cut(Part.makeBox(.50677424482636,3.7,5.8,A.Vector(3.2,11.4,-2.9))).cut(Part.makeBox(1.4,4.5,3.2,A.Vector(4.8,10.53,16.4))).removeSplitter();assert carrier.isValid() and len(carrier.Solids)==1
report['finished_checks']={n:carrier.common(s).Volume for n,s in sh.items() if n not in ['RetainedPCBTray','RetainedSocket']};assert report['finished_checks']['RibbonCandidate']<1e-6;assert report['finished_checks']['eye_primary_Holder']<1e-6
assign(d.FinishedCarrier,carrier.transformed(M.toMatrix()));d.Label='Rat R30 - separated protective arms';d.recompute();path=O/'ET-RAT-SEPARATED-ARMS-R30.FCStd';d.saveAs(str(path))
with zipfile.ZipFile(path) as z:assert 'Document.xml' in z.namelist() and z.testzip() is None
mesh=MeshPart.meshFromShape(Shape=world(d.FinishedCarrier),LinearDeflection=.04,AngularDeflection=.15,Relative=False);assert mesh.isSolid() and not mesh.hasSelfIntersections();mesh.write(str(O/'carrier.stl'));sk=d.RatDesignSkull.Mesh.copy();sk.Placement=d.RatDesignSkull.getGlobalPlacement();n=mesh.CountFacets;mesh.addMesh(sk);cross=sum((x[0]<n)!=(x[1]<n) for x in mesh.getSelfIntersections());assert cross==0;report['skull_crossings']=cross;report['carrier_single_valid_solid']=True;report['mesh_closed_no_self_intersections']=True;(O/'validation.json').write_text(json.dumps(report,indent=2));(S/'recipe.json').write_text(json.dumps(report,indent=2));A.closeDocument(d.Name);print('SAVED',flush=True)





