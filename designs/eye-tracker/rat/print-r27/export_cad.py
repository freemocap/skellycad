from pathlib import Path
import json,hashlib,sys
import FreeCAD as A,Part,Mesh,MeshPart
ROOT=Path.cwd();HERE=ROOT/'designs/eye-tracker/rat/print-r27';OUT=ROOT/'generated/eye-tracker/rat/print-r27';OUT.mkdir(parents=True,exist_ok=True)
m=json.loads((HERE.parent/'aligned-tip-r27/review.json').read_text());src=ROOT/m['native_checkpoint'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(src))
for name in ['RatDesignSkull','RatLeftSclera','RatLeftCornea','RatRightSclera','RatRightCornea']:
 ob=d.getObject(name);mesh=Mesh.Mesh(ob.Mesh);mesh.transform(ob.getGlobalPlacement().multiply(ob.Placement.inverse()).toMatrix());mesh.write(str(OUT/(name+'.stl')))
def world(name):
 ob=d.getObject(name);s=ob.Shape.copy();s.Placement=ob.getGlobalPlacement();return s
base=world('skull_mount_Baseplate');MeshPart.meshFromShape(Shape=base,LinearDeflection=.02,AngularDeflection=.1,Relative=False).write(str(OUT/'baseplate-world.stl'))
cfg=json.loads((HERE.parent/'oval-camera-r21/solution.json').read_text());inv=A.Placement(A.Matrix(*sum(cfg['mount_to_skull'],[]))).inverse()
def local(name):return world(name).transformed(inv.toMatrix())
carrier=local('FinishedCarrier');holder=local('eye_primary_Holder')
# Remove previous raised lettering only from the label strip, down to the tray rear face.
carrier=carrier.cut(Part.makeBox(.66,3.5,26,A.Vector(3.04677424482636,11.5,-13))).removeSplitter()
# Same exterior tray face and lettering orientation as historical mouse labels.
font=Path('C:/Windows/Fonts/arialbd.ttf')
letters=Part.makeWireString('RAT R27',str(font.parent)+'/',font.name,3.0)
def polygon(w):
 points=w.discretize(Deflection=.01)
 if (points[0]-points[-1]).Length>1e-9:points.append(points[0])
 return Part.makePolygon(points)
faces=[Part.makeFace([polygon(w) for w in ws],'Part::FaceMakerBullseye') for ws in letters if ws]
face=Part.makeCompound(faces);face.scale(3.0/face.BoundBox.YLength)
b=face.BoundBox;face.translate(A.Vector(-(b.XMin+b.XMax)/2,-(b.YMin+b.YMax)/2,0))
mat=A.Matrix();mat.A11=0;mat.A12=0;mat.A13=-1;mat.A21=0;mat.A22=1;mat.A23=0;mat.A31=1;mat.A32=0;mat.A33=0
face=face.transformGeometry(mat);face.translate(A.Vector(3.75677424482636,13.25,0))
label=face.extrude(A.Vector(-.45,0,0));labeled=carrier.fuse(label).removeSplitter();labeled.limitTolerance(1e-6);labeled.check(True)
assert labeled.isValid() and len(labeled.Solids)==1,(len(labeled.Solids),face.BoundBox)
assert labeled.Volume>carrier.Volume
print('Label solid passed',flush=True)
for name in ['eye_primary_Holder','eye_primary_Cap','eye_primary_Clip','RibbonCandidate']:
 print('Checking label against',name,flush=True)
 assert label.common(local(name)).Volume<1e-6,name
assert labeled.common(holder).Volume<1e-6
report={'label':'RAT R27','height_mm':3,'relief_mm':.4,'added_volume_mm3':labeled.Volume-carrier.Volume,'holder_gap_mm':labeled.distToShape(holder)[0],'source_manifest':m}
pr=OUT/'hardware';pr.mkdir(exist_ok=True)
for name,shape in [('RAT-R27-carrier-and-holder',Part.makeCompound([labeled,holder])),('RAT-R27-carrier',labeled),('RAT-R27-holder',holder),('RAT-R27-cap',local('eye_primary_Cap')),('RAT-R27-clip',local('eye_primary_Clip')),('RAT-R27-baseplate',local('skull_mount_Baseplate'))]:
 print('Meshing',name,flush=True)
 shape=shape.copy();shape.translate(A.Vector(0,0,-shape.BoundBox.ZMin));mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.04,AngularDeflection=.15,Relative=False);print(name,'closed',mesh.isSolid(),'facets',mesh.CountFacets,flush=True);assert mesh.isSolid() and not mesh.hasSelfIntersections(),name;mesh.write(str(pr/(name+'.stl')))
world=labeled.copy();world.Placement=A.Placement(A.Matrix(*sum(cfg['mount_to_skull'],[]))).multiply(world.Placement);sys.path.insert(0,str(ROOT/'designs/eye-tracker/shared/targeting'));from replace_camera import assign;assign(d.FinishedCarrier,world)
d.saveAs(str(OUT/'RAT-R27-complete-assembly.FCStd'))
(OUT/'hardware-validation.json').write_text(json.dumps(report,indent=2))
print('Label and hardware passed',flush=True)

