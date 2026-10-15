from pathlib import Path
import json,hashlib
import FreeCAD as A,Part,Mesh,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/mouse/print-r21';O=R/'generated/eye-tracker/mouse/print-r21';O.mkdir(parents=True,exist_ok=True);H=O/'hardware';H.mkdir(exist_ok=True);m=json.loads((S.parent/'active-model.json').read_text());src=R/m['native_checkpoint'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['native_sha256'];d=A.openDocument(str(src))
for side in ['Eye1','Eye2']:
 for region in ['Sclera','Cornea']:
  o=d.getObject(side+region);mesh=Mesh.Mesh(o.Mesh);mesh.transform(o.getGlobalPlacement().multiply(o.Placement.inverse()).toMatrix());mesh.write(str(O/(side+region+'.stl')))
def world(n):
 o=d.getObject(n);s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s
base=world('skull_mount_Baseplate');MeshPart.meshFromShape(Shape=base,LinearDeflection=.02,AngularDeflection=.10,Relative=False).write(str(O/'baseplate-world.stl'))
M=A.Placement(A.Matrix(*sum(json.loads((S.parent/'skull-clearance-r18/placement.json').read_text())['transform'],[]))).inverse();shapes={}
for key,n in [('carrier','FinishedCarrier'),('holder','eye_primary_Holder'),('clip','eye_primary_Clip')]:
 s=world(n);s.Placement=M.multiply(s.Placement);shapes[key]=s
pair=Part.makeCompound([shapes['carrier'],shapes['holder']]);offset=A.Vector(0,0,-pair.BoundBox.ZMin);report={'source':m,'units':'mm','hardware_pair_shift_mm':list(offset),'holder_gap_mm':shapes['carrier'].distToShape(shapes['holder'])[0],'files':{}}
assert shapes['carrier'].common(shapes['holder']).Volume<1e-6
for name,s in [('MOUSE-R21-carrier-and-holder',pair),('MOUSE-R21-camera-clip',shapes['clip'])]:
 s=s.copy();s.translate(offset if 'carrier' in name else A.Vector(0,0,-s.BoundBox.ZMin));mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.03,AngularDeflection=.12,Relative=False);assert mesh.isSolid() and not mesh.hasSelfIntersections(),name;mesh.write(str(H/(name+'.stl')));report['files'][name]={'closed':True,'self_intersections':False,'facets':mesh.CountFacets}
(O/'hardware-validation.json').write_text(json.dumps(report,indent=2));print('HARDWARE PASS',report['holder_gap_mm'])
