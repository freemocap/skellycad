from pathlib import Path
import json,hashlib
import FreeCAD as A,Part,Mesh,MeshPart
ROOT=Path.cwd();HERE=ROOT/'designs/eye-tracker/rat/print-r04';OUT=ROOT/'generated/eye-tracker/rat/print-r04';OUT.mkdir(parents=True,exist_ok=True)
for path in ['designs/eye-tracker/rat/active-model.json','designs/eye-tracker/rat/targeted-r03/review.json']:
 m=json.loads((ROOT/path).read_text());assert hashlib.sha256((ROOT/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256']
d=A.openDocument(str(ROOT/m['native_checkpoint']))
for side in ['Right','Left']:
 for region in ['Sclera','Cornea']:
  ob=d.getObject(side+'Eye'+region);mesh=Mesh.Mesh(ob.Mesh);mesh.transform(ob.getGlobalPlacement().toMatrix());mesh.write(str(OUT/(side+region+'.stl')))
base=d.skull_mount_Baseplate.Shape
MeshPart.meshFromShape(Shape=base,LinearDeflection=.03,AngularDeflection=.12,Relative=False).write(str(OUT/'baseplate-world.stl'))
cfg=json.loads(d.TargetRecipe.RecipeJSON);inv=A.Placement(A.Matrix(*sum(cfg['mount_to_skull'],[]))).inverse()
def local(name):
 sh=d.getObject(name).Shape.copy();sh.Placement=inv.multiply(sh.Placement);return sh
carrier=local('FinishedCarrier');holder=local('eye_primary_Holder')
hardware=json.loads((ROOT/'designs/eye-tracker/mouse/inset-arm-r08/print-test.json').read_text());assert hashlib.sha256((ROOT/hardware['native_checkpoint']).read_bytes()).hexdigest()==hardware['native_sha256'];baseline=A.openDocument(str(ROOT/hardware['native_checkpoint']))
# Same exterior tray face and lettering orientation as historical mouse labels.
font=Path('C:/Windows/Fonts/arialbd.ttf')
letters=Part.makeWireString('RAT R04',str(font.parent)+'/',font.name,3.0)
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
assert abs(labeled.Volume-carrier.Volume-face.Area*.4)<.01
print('Label solid passed',flush=True)
for name in ['eye_primary_Holder','eye_primary_Cap','eye_primary_Clip','RibbonCandidate']:
 print('Checking label against',name,flush=True)
 assert label.common(local(name)).Volume<1e-6,name
report={'label':'RAT R04','height_mm':3,'relief_mm':.4,'added_volume_mm3':labeled.Volume-carrier.Volume,'holder_gap_mm':labeled.distToShape(holder)[0],'source_manifest':m}
pr=OUT/'hardware';pr.mkdir(exist_ok=True)
for name,shape in [('RAT-R04-carrier-and-holder',Part.makeCompound([labeled,holder])),('RAT-R04-carrier',labeled),('RAT-R04-holder',holder),('RAT-R04-cap',baseline.eye_primary_Cap.Shape),('RAT-R04-clip',baseline.eye_primary_Clip.Shape),('RAT-R04-baseplate',baseline.skull_mount_Baseplate.Shape)]:
 print('Meshing',name,flush=True)
 mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.03,AngularDeflection=.12,Relative=False);print(name,'closed',mesh.isSolid(),'facets',mesh.CountFacets,flush=True);assert mesh.isSolid(),name;mesh.write(str(pr/(name+'.stl')))
world=labeled.copy();world.Placement=A.Placement(A.Matrix(*sum(cfg['mount_to_skull'],[]))).multiply(world.Placement);d.FinishedCarrier.Shape=world
d.saveAs(str(OUT/'RAT-R04-complete-assembly.FCStd'))
(OUT/'hardware-validation.json').write_text(json.dumps(report,indent=2))
print('Label and hardware passed',flush=True)

