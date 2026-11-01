"""Remove the two cavity skins from the R32 print-layout carrier, in mm."""
from pathlib import Path
import json,hashlib,zipfile
import FreeCAD as A,Part,MeshPart
R=Path.cwd(); O=R/'generated/eye-tracker/rat/open-spine-r33';O.mkdir(parents=True,exist_ok=True)
source=R/'generated/eye-tracker/rat/print-r32-l04/RAT-R32-labeled-hardware.FCStd'
review=json.loads((R/'designs/eye-tracker/rat/compact-binocular-r32/review.json').read_text())
assert hashlib.sha256((R/review['native_checkpoint']).read_bytes()).hexdigest()==review['native_sha256']
src=A.openDocument(str(source));main=src.CarrierAndTwoHolders.Shape.copy();old=main.Solids[0]
faces=[f for f in old.Faces if isinstance(f.Surface,Part.Plane) and f.Area>40 and abs(f.BoundBox.ZMin-7.873508702263144)<1e-6 and f.BoundBox.ZLength<1e-6]
assert len(faces)==2
tools=[]
for f in faces:
 b=f.BoundBox
 tools.append(Part.makeBox(b.XLength,b.YLength,1.4,A.Vector(b.XMin,b.YMin,7.573508702263144)))
new=old.cut(Part.makeCompound(tools)).removeSplitter()
assert new.isValid() and len(new.Solids)==1
assert all(new.common(t).Volume<1e-7 for t in tools)
assert all(t.common(h).Volume<1e-7 for t in tools for h in main.Solids[1:])
mesh=MeshPart.meshFromShape(Shape=new,LinearDeflection=.04,AngularDeflection=.15,Relative=False)
assert mesh.isSolid() and not mesh.hasSelfIntersections()
d=A.newDocument('RatOpenSpineR33');d.Label='RAT R33 - open central windows - REVIEW'
for name,s in [('Carrier',new),('RightHolder',main.Solids[1]),('LeftHolder',main.Solids[2]),('RightClip',src.RightClip.Shape),('LeftClip',src.LeftClip.Shape)]:
 o=d.addObject('Part::Feature',name);o.Shape=s
d.recompute();p=O/'RAT-R33-open-spine-review.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
report={'units':'mm','source':str(source.relative_to(R)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_checkpoint':str(p.relative_to(R)),'native_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'parent_complete_assembly':review,'removed_volume_mm3':old.Volume-new.Volume,'through_windows':2,'carrier_valid':True,'carrier_solids':1,'mesh_closed':True,'mesh_self_intersections':False,'holders_and_clips_unchanged':True,'status':'Review only; inherited RAT R32 engraving remains pending relocation; no print export'}
(O/'validation.json').write_text(json.dumps(report,indent=2));(R/'designs/eye-tracker/rat/open-spine-r33/review.json').write_text(json.dumps(report,indent=2))
A.closeDocument(d.Name);A.closeDocument(src.Name);print(json.dumps(report,indent=2))
