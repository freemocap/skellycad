"""Engrave the R32 L02 hardware; preserve its layout and matched parts (mm)."""
from pathlib import Path
import hashlib,json,zipfile,shutil
import FreeCAD as A,Part,MeshPart
R=Path.cwd(); OLD=R/'generated/eye-tracker/rat/print-r32-l02'; O=R/'generated/eye-tracker/rat/print-r32-l04'; O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((R/'designs/eye-tracker/rat/compact-binocular-r32/review.json').read_text())
assert sha(R/review['native_checkpoint'])==review['native_sha256']
m=json.loads((OLD/'manifest.json').read_text())
for n,h in m['files'].items(): assert sha(OLD/n)==h,n
d=A.openDocument(str(OLD/'RAT-R32-hardware-print.FCStd'))
main=d.CarrierAndTwoHolders.Shape.copy(); carrier=main.Solids[0]; holders=main.Solids[1:]
assert len(holders)==2
font=Path('C:/Windows/Fonts/ariblk.ttf')
letters=Part.makeWireString('RAT R32',str(font.parent)+'/',font.name,1.5)
def poly(w):
 p=w.discretize(Deflection=.005)
 if (p[0]-p[-1]).Length>1e-9:p.append(p[0])
 return Part.makePolygon(p)
face=Part.makeCompound([Part.makeFace([poly(w) for w in ws],'Part::FaceMakerBullseye') for ws in letters if ws])
face.scale(2.9/face.BoundBox.YLength)

z=8.873508702263146
face.translate(A.Vector(-face.BoundBox.Center.x,9.45-face.BoundBox.Center.y,z-.6))
tool=face.extrude(A.Vector(0,0,.65))
cut=carrier.cut(tool).removeSplitter()
assert cut.isValid() and len(cut.Solids)==1
removed=carrier.Volume-cut.Volume
assert abs(removed-face.Area*.6)<.001,(removed,face.Area*.6)
assert all(tool.common(h).Volume<1e-8 for h in holders)
newmain=Part.makeCompound([cut,*holders]); d.CarrierAndTwoHolders.Shape=newmain
d.Label='RAT R32 L04 - engraved R32-L02 layout'
d.recompute(); native=O/'RAT-R32-labeled-hardware.FCStd';d.saveAs(str(native))
with zipfile.ZipFile(native) as f:assert f.testzip() is None and 'Document.xml' in f.namelist()
H=O/'hardware';H.mkdir(exist_ok=True);report={}
for n,s,count in [('all-hardware',Part.makeCompound([newmain,d.RightClip.Shape,d.LeftClip.Shape]),5),('carrier-and-two-holders',newmain,3),('carrier',cut,1)]:
 mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False)
 assert mesh.isSolid() and not mesh.hasSelfIntersections(),n
 assert len(s.Solids)==count
 p=H/('RAT-R32-L04-'+n+'.stl');mesh.write(str(p))
 report[n]={'shells':count,'closed':True,'self_intersections':False,'sha256':sha(p)}
report.update({'units':'mm','label':'RAT R32','export_revision':'L04','depth_mm':.6,'letter_height_mm':face.BoundBox.YLength,'font':'Arial Black','removed_volume_mm3':removed,'font_sha256':sha(font),'source_review':review,'source_layout_manifest_sha256':sha(OLD/'manifest.json'),'matched_holders_and_flat_clips_unchanged':True})
(O/'validation.json').write_text(json.dumps(report,indent=2))
A.closeDocument(d.Name)
shutil.copy2(__file__,O/'label.py')
print(json.dumps(report,indent=2))


