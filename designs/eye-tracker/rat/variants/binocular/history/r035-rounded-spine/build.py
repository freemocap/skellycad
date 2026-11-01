"""Full-size rounded through-windows; no label-driven geometry changes (mm)."""
from pathlib import Path
import json,hashlib,zipfile
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/rounded-spine-r35';O=R/'generated/eye-tracker/rat/rounded-spine-r35';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=json.loads((S.parent/'open-spine-r33/review.json').read_text());assert sha(R/parent['native_checkpoint'])==parent['native_sha256']
baseline=R/'generated/eye-tracker/rat/print-r32-l02';m=json.loads((baseline/'manifest.json').read_text());p=baseline/'RAT-R32-hardware-print.FCStd';assert sha(p)==m['files'][p.name]
src=A.openDocument(str(p));main=src.CarrierAndTwoHolders.Shape;old=main.Solids[0];new=old.copy();cutters=[]
faces=[f for f in old.Faces if isinstance(f.Surface,Part.Plane) and f.Area>40 and abs(f.BoundBox.ZMin-7.873508702263144)<1e-6 and f.BoundBox.ZLength<1e-6]
assert len(faces)==2
for f in faces:
 b=f.BoundBox
 # Restore only the window envelope before cutting a rounded opening through it.
 fill=Part.makeBox(b.XLength,b.YLength,1.2,A.Vector(b.XMin,b.YMin,7.673508702263144))
 new=new.fuse(fill).removeSplitter()
 cutter=Part.makeBox(b.XLength,b.YLength,1.4,A.Vector(b.XMin,b.YMin,7.573508702263144))
 vertical=[e for e in cutter.Edges if e.BoundBox.ZLength>1.39]
 cutter=cutter.makeFillet(1.,vertical);cutters.append(cutter)
new=new.cut(Part.makeCompound(cutters)).removeSplitter()
assert new.isValid() and len(new.Solids)==1
assert all(new.common(c).Volume<1e-7 for c in cutters)
assert all(new.common(h).Volume<1e-7 for h in main.Solids[1:])
mesh=MeshPart.meshFromShape(Shape=new,LinearDeflection=.04,AngularDeflection=.15,Relative=False);assert mesh.isSolid() and not mesh.hasSelfIntersections()
d=A.newDocument('RatRoundedSpineR35');d.Label='RAT R35 - full-size rounded windows, no label - REVIEW'
for name,s in [('Carrier',new),('RightHolder',main.Solids[1]),('LeftHolder',main.Solids[2]),('RightClip',src.RightClip.Shape),('LeftClip',src.LeftClip.Shape)]:
 o=d.addObject('Part::Feature',name);o.Shape=s
d.recompute();p=O/'RAT-R35-rounded-spine-review.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
report={'units':'mm','native_checkpoint':str(p.relative_to(R)),'native_sha256':sha(p),'parent_review':parent,'unengraved_baseline_sha256':sha(baseline/'RAT-R32-hardware-print.FCStd'),'window_corner_radius_mm':1.,'window_height_mm':5.5,'window_width_mm':11.5,'label':None,'functional_geometry_changed_for_text':False,'through_windows':2,'valid_single_carrier':True,'mesh_closed':True,'mesh_self_intersections':False,'holders_and_clips_unchanged':True,'status':'Review; physical print pending'}
(S/'review.json').write_text(json.dumps(report,indent=2));(O/'validation.json').write_text(json.dumps(report,indent=2))
A.closeDocument(d.Name);A.closeDocument(src.Name);print('Saved R35: original window envelopes restored; label removed')
