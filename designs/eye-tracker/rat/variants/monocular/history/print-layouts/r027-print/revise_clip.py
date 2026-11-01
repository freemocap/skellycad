from pathlib import Path
import FreeCAD as A,Part,MeshPart,Mesh,json,hashlib
R=Path.cwd();O=R/'generated/eye-tracker/rat/print-r27';src=R/'designs/eye-tracker/rat/aligned-tip-r27/checkpoints/ET-RAT-ALIGNED-TIP-R27.FCStd';assert hashlib.sha256(src.read_bytes()).hexdigest()=='320921e03d42a1bd8a16b3a11b7b6d6c1cd6817b4b6286475f1c9db59127be8d';d=A.openDocument(str(src));pose=d.eye_primary_Clip.getGlobalPlacement()
# Rebuild the inherited U profile with extra span and longer, thicker arms.
L=.086;U=8.686;t=.95;tip=.65;h=4.5;bottom=3.5
pts=[(L-t,0),(U+t,0),(U+t,h),(U,h),(U-tip,4.0),(U-tip,bottom),(U,bottom),(U,1.5),(L,1.5),(L,bottom),(L+tip,bottom),(L+tip,4.0),(L,h),(L-t,h)]
v=[A.Vector(x,-3.5,z) for x,z in pts];v.append(v[0]);s=Part.Face(Part.makePolygon(v)).extrude(A.Vector(0,3.5,0))
# Keep the inherited sloped front clearance.
v=[A.Vector(-3,0,0),A.Vector(-3,1,0),A.Vector(-3,1,6),A.Vector(-3,-1.125,6),A.Vector(-3,0,0)];s=s.cut(Part.Face(Part.makePolygon(v)).extrude(A.Vector(16,0,0))).removeSplitter()
edges=[e for e in s.Edges if abs(e.CenterOfMass.z-1.5)<.01 and (abs(e.CenterOfMass.x-L)<.01 or abs(e.CenterOfMass.x-U)<.01) and e.Length>2]
s=s.makeFillet(.25,edges).removeSplitter();assert s.isValid() and len(s.Solids)==1
obstacles={}
for n in ['eye_primary_Holder','FinishedCarrier','RibbonCandidate']:
 o=d.getObject(n);q=o.Shape.copy();q.Placement=pose.inverse().multiply(o.getGlobalPlacement());obstacles[n]={'intersection_mm3':s.common(q).Volume,'gap_mm':s.distToShape(q)[0]}
print(obstacles,flush=True)
assert all(v['intersection_mm3']<.01 for v in obstacles.values()),obstacles
m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.02,AngularDeflection=.1,Relative=False);assert m.isSolid() and not m.hasSelfIntersections();m.write(str(O/'hardware/RAT-R27-clip.stl'));s.exportBrep(str(O/'revised-clip.brep'))
report={'revision':'R27 clip C01','units':'mm','arm_height_from_crossbar_mm':3.0,'previous_arm_height_mm':2.5,'arm_thickness_mm':.95,'previous_arm_thickness_mm':.75,'internal_span_mm':8.6,'previous_internal_span_mm':8.2,'catch_projection_mm':.65,'previous_catch_projection_mm':.5,'root_fillet_mm':.25,'checks':obstacles,'physical_fit_verified':False};(O/'clip-validation.json').write_text(json.dumps(report,indent=2))
nd=A.newDocument('RatR27ClipC01');o=nd.addObject('Part::Feature','Clip');o.Shape=s;nd.saveAs(str(O/'RAT-R27-clip-C01.FCStd'))

full=A.openDocument(str(O/'RAT-R27-complete-assembly.FCStd'));new=s.copy();new.Placement=pose;import sys;sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import assign;assign(full.eye_primary_Clip,new);full.save()

