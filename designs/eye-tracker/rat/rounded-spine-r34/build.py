"""Rounded through-windows and a supported, shallow revision label (mm)."""
from pathlib import Path
import json,hashlib,zipfile
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/rounded-spine-r34';O=R/'generated/eye-tracker/rat/rounded-spine-r34';O.mkdir(parents=True,exist_ok=True)
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
 cutter=Part.makeBox(b.XLength,b.YLength-.9,1.4,A.Vector(b.XMin,b.YMin,7.573508702263144))
 vertical=[e for e in cutter.Edges if e.BoundBox.ZLength>1.39]
 cutter=cutter.makeFillet(1.,vertical);cutters.append(cutter)
new=new.cut(Part.makeCompound(cutters)).removeSplitter()
font=Path('C:/Windows/Fonts/ariblk.ttf')
def poly(w):
 pts=w.discretize(Deflection=.005)
 if (pts[0]-pts[-1]).Length>1e-9:pts.append(pts[0])
 return Part.makePolygon(pts)
letters=Part.makeWireString('RAT R34',str(font.parent)+'/',font.name,2.4)
text=Part.makeCompound([Part.makeFace([poly(w) for w in ws],'Part::FaceMakerBullseye') for ws in letters if ws]);text.scale(2.4/text.BoundBox.YLength)
text.translate(A.Vector(-text.BoundBox.Center.x,8.974158191574633-text.BoundBox.Center.y,8.573508702263146))
tool=text.extrude(A.Vector(0,0,.35));before=new.Volume;new=new.cut(tool).removeSplitter()
assert abs(before-new.Volume-text.Area*.3)<.002
assert new.isValid() and len(new.Solids)==1
assert all(new.common(c).Volume<1e-7 for c in cutters)
assert all(new.common(h).Volume<1e-7 for h in main.Solids[1:])
mesh=MeshPart.meshFromShape(Shape=new,LinearDeflection=.04,AngularDeflection=.15,Relative=False);assert mesh.isSolid() and not mesh.hasSelfIntersections()
d=A.newDocument('RatRoundedSpineR34');d.Label='RAT R34 - rounded windows and supported label - REVIEW'
for name,s in [('Carrier',new),('RightHolder',main.Solids[1]),('LeftHolder',main.Solids[2]),('RightClip',src.RightClip.Shape),('LeftClip',src.LeftClip.Shape)]:
 o=d.addObject('Part::Feature',name);o.Shape=s
d.recompute();p=O/'RAT-R34-rounded-spine-review.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
report={'units':'mm','native_checkpoint':str(p.relative_to(R)),'native_sha256':sha(p),'parent_review':parent,'unengraved_baseline_sha256':sha(baseline/'RAT-R32-hardware-print.FCStd'),'window_corner_radius_mm':1.,'window_height_mm':4.6,'label':'RAT R34','letter_height_mm':2.4,'engraving_depth_mm':.3,'material_beneath_text_mm':.9,'label_edge_and_window_margin_mm':.8,'label_rail_width_mm':4.,'through_windows':2,'valid_single_carrier':True,'mesh_closed':True,'mesh_self_intersections':False,'holders_and_clips_unchanged':True,'status':'Review; physical print pending'}
(S/'review.json').write_text(json.dumps(report,indent=2));(O/'validation.json').write_text(json.dumps(report,indent=2))
A.closeDocument(d.Name);A.closeDocument(src.Name);print('Saved R34: rounded through-windows, 0.8 mm label margins, 0.9 mm label floor')
