"""Apply a label within the existing R35 rail, without altering window geometry."""
from pathlib import Path
import FreeCAD as A,Part,MeshPart
import json,hashlib,zipfile
R=Path.cwd();S=R/'designs/eye-tracker/rat/labeled-spine-r36';O=R/'generated/eye-tracker/rat/labeled-spine-r36';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((S.parent/'rounded-spine-r35/review.json').read_text());p=R/m['native_checkpoint'];assert sha(p)==m['native_sha256']
src=A.openDocument(str(p));old=src.Carrier.Shape.copy()
font=Path('C:/Windows/Fonts/ariblk.ttf')
def poly(w):
 p=w.discretize(Deflection=.005)
 if (p[0]-p[-1]).Length>1e-9:p.append(p[0])
 return Part.makePolygon(p)
letters=Part.makeWireString('RAT R36',str(font.parent)+'/',font.name,1.6)
face=Part.makeCompound([Part.makeFace([poly(w) for w in ws],'Part::FaceMakerBullseye') for ws in letters if ws]);face.scale(1.6/face.BoundBox.YLength)
# Existing upper rail spans y=7.874158..10.974158. No material added for text.
face.translate(A.Vector(.86456-face.BoundBox.Center.x,9.424158191574633-face.BoundBox.Center.y,8.573508702263146))
tool=face.extrude(A.Vector(0,0,.35));new=old.cut(tool).removeSplitter()
assert new.isValid() and len(new.Solids)==1
assert new.cut(old).Volume<1e-7
b=tool.BoundBox
label_region=Part.makeBox(b.XLength+.02,b.YLength+.02,b.ZLength+.02,A.Vector(b.XMin-.01,b.YMin-.01,b.ZMin-.01))
assert old.cut(new).cut(label_region).Volume<1e-7
assert abs(old.Volume-new.Volume-face.Area*.3)<.002
# The entire pair of original window envelopes is unchanged, including rounding.
for x in [-12.63544,2.86456]:
 box=Part.makeBox(11.5,5.5,1.4,A.Vector(x,2.374158191574633,7.573508702263144))
 assert old.common(box).cut(new).Volume<1e-7
mesh=MeshPart.meshFromShape(Shape=new,LinearDeflection=.04,AngularDeflection=.15,Relative=False);assert mesh.isSolid() and not mesh.hasSelfIntersections()
d=A.newDocument('RatLabeledSpineR36');d.Label='RAT R36 - symmetric windows, label within existing rail'
for name in ['Carrier','RightHolder','LeftHolder','RightClip','LeftClip']:
 o=d.addObject('Part::Feature',name);o.Shape=new if name=='Carrier' else src.getObject(name).Shape.copy()
d.recompute();p=O/'RAT-R36-labeled-spine-review.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
report={'units':'mm','native_checkpoint':str(p.relative_to(R)),'native_sha256':sha(p),'parent_review':m,'label':'RAT R36','height_mm':1.6,'depth_mm':.3,'edge_and_window_margin_mm':.75,'material_beneath_label_mm':.9,'windows_unchanged_from_r35':True,'only_change_is_text_engraving':True,'mesh_closed':True,'mesh_self_intersections':False}
(S/'review.json').write_text(json.dumps(report,indent=2));(O/'validation.json').write_text(json.dumps(report,indent=2));A.closeDocument(d.Name);A.closeDocument(src.Name);print('R36 verified: only text engraving changed; full-size rounded windows preserved')
