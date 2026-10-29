from pathlib import Path
import sys,json,hashlib,zipfile
import FreeCAD as A,Part,MeshPart,Mesh
R=Path.cwd();S=R/'designs/eye-tracker/rat/print-r38';O=R/'generated/eye-tracker/rat/print-r38';O.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((S.parent/'refined-supports-r38/review.json').read_text());p=R/m['native_checkpoint'];assert sha(p)==m['native_sha256']
assert json.loads((p.parent/'validation.json').read_text())['passed']
d=A.openDocument(str(p));cfg=json.loads((S.parent/'refined-supports-r38/recipe.json').read_text());T=A.Placement(A.Matrix(*sum(cfg['mount_to_skull'],[])))
rot=A.Rotation(A.Vector(1,0,0),90).multiply(A.Rotation(A.Vector(0,1,0),-90));P=A.Placement(A.Vector(),rot).multiply(T.inverse())
names=['Carrier','RightHolder','LeftHolder','RightClip','LeftClip'];source=['FinishedCarrier','Righteye_primary_Holder','Lefteye_primary_Holder','Righteye_primary_Clip','Lefteye_primary_Clip']
original=[world(d.getObject(n)) for n in source];shapes=[s.transformed(P.toMatrix()) for s in original[:3]]
b=Part.makeCompound(shapes).BoundBox;v=A.Vector(-b.Center.x,-b.Center.y,-b.ZMin)
for s in shapes:s.translate(v)
main=Part.makeCompound(shapes)
for i,old in enumerate(original[3:]):
 faces=[f for f in old.Faces if isinstance(f.Surface,Part.Plane) and len(f.Edges)>=10];assert len(faces)==2
 candidates=[]
 for face in faces:
  r=A.Rotation(face.normalAt(0,0),A.Vector(0,0,-1));mat=A.Placement(A.Vector(),r).toMatrix();candidate=old.transformed(mat);flat=face.transformed(mat)
  if flat.BoundBox.ZLength<1e-6 and abs(flat.BoundBox.ZMin-candidate.BoundBox.ZMin)<1e-6:candidates.append((face.Area,candidate))
 assert candidates,'No broad clip face seats on bed'
 s=max(candidates,key=lambda item:item[0])[1];b=s.BoundBox
 s.translate(A.Vector(main.BoundBox.XMax+8-b.XMin,(-1 if i==0 else 1)*(b.YLength+5)/2-b.Center.y,-b.ZMin));shapes.append(s)
for i,s in enumerate(shapes):
 assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-original[i].Volume)<1e-5
 for other in shapes[i+1:]:assert s.common(other).Volume<1e-7
report={'revision':'RAT R38','units':'mm','source_checkpoint':m['native_checkpoint'],'source_sha256':m['native_sha256'],'geometry_changes':'Rigid print placement only','clips_flat':True,'physical_strength_verified':False,'files':{}}
printdoc=A.newDocument('RatR38PrintLayout')
for name,s in zip(names,shapes):o=printdoc.addObject('Part::Feature',name);o.Shape=s
printdoc.recompute();native=O/'RAT-R38-arms-flat-print.FCStd';printdoc.saveAs(str(native))
with zipfile.ZipFile(native) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
allshape=Part.makeCompound(shapes)
for name,s in [('all-hardware-arms-flat',allshape),('carrier-and-two-holders-arms-flat',main)]+list(zip([n.lower() for n in names],shapes)):
 mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False)
 assert mesh.isSolid() and not mesh.hasSelfIntersections(),name
 p=O/('RAT-R38-'+name+'.stl');mesh.write(str(p));reloaded=Mesh.Mesh(str(p));assert reloaded.isSolid() and not reloaded.hasSelfIntersections()
 report['files'][p.name]={'sha256':sha(p),'closed':True,'self_intersections':False,'shells':len(s.Solids)}
report['layout_dimensions_mm']=[allshape.BoundBox.XLength,allshape.BoundBox.YLength,allshape.BoundBox.ZLength];report['native_sha256']=sha(native)
(O/'validation.json').write_text(json.dumps(report,indent=2));A.closeDocument(printdoc.Name);A.closeDocument(d.Name);print(json.dumps(report,indent=2))

