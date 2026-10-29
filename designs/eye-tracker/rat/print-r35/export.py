"""Lay the matched R35 mechanism on its side so arm spans follow the bed."""
from pathlib import Path
import json,hashlib,zipfile,math
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/print-r35';O=R/'generated/eye-tracker/rat/print-r35';O.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((S.parent/'rounded-spine-r35/review.json').read_text());p=R/m['native_checkpoint'];assert sha(p)==m['native_sha256']
src=A.openDocument(str(p));names=['Carrier','RightHolder','LeftHolder'];shapes=[src.getObject(n).Shape.copy() for n in names]
before=Part.makeCompound(shapes);rotation=A.Rotation(A.Vector(1,0,0),90)
for s in shapes:s.rotate(A.Vector(),A.Vector(1,0,0),90)
b=Part.makeCompound(shapes).BoundBox;shift=A.Vector(-b.Center.x,-b.Center.y,-b.ZMin)
for s in shapes:s.translate(shift)
main=Part.makeCompound(shapes)
clips=[]
for i,n in enumerate(['RightClip','LeftClip']):
 s=src.getObject(n).Shape.copy();b=s.BoundBox
 s.translate(A.Vector(main.BoundBox.XMax+8-b.XMin,(-1 if i==0 else 1)*(b.YLength+5)/2-b.Center.y,-b.ZMin))
 assert abs(s.BoundBox.ZMin)<1e-7 and abs(s.BoundBox.ZLength-3.5)<1e-5
 clips.append(s)
allshape=Part.makeCompound([*shapes,*clips]);assert len(allshape.Solids)==5
for old,new in zip([src.getObject(n).Shape for n in names],shapes):assert abs(old.Volume-new.Volume)<1e-7
for i,s in enumerate(shapes+clips):
 for other in (shapes+clips)[i+1:]:assert s.common(other).Volume<1e-7
d=A.newDocument('RatR35ArmsFlatPrint');d.Label='RAT R35 - arms along print bed'
for n,s in zip(names+['RightClip','LeftClip'],shapes+clips):o=d.addObject('Part::Feature',n);o.Shape=s
d.recompute();native=O/'RAT-R35-arms-flat-print.FCStd';d.saveAs(str(native))
with zipfile.ZipFile(native) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
files={}
for name,s in [('RAT-R35-all-hardware-arms-flat',allshape),('RAT-R35-carrier-and-two-holders-arms-flat',main)]:
 mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False)
 assert mesh.isSolid() and not mesh.hasSelfIntersections()
 p=O/(name+'.stl');mesh.write(str(p));files[p.name]={'sha256':sha(p),'closed':True,'self_intersections':False,'shells':len(s.Solids)}
# Compare arc-length-weighted tangent inclinations from the inherited arm curves.
arms=json.loads((S.parent/'compact-binocular-r32/arms.json').read_text());angles={}
for name,rec in arms.items():
 poles=[A.Vector(*v) for v in rec['poles_mm']];oldsum=newsum=length=0.
 for i in range(200):
  t=(i+.5)/200
  v=(poles[1]-poles[0])*(3*(1-t)**2)+(poles[2]-poles[1])*(6*(1-t)*t)+(poles[3]-poles[2])*(3*t*t)
  q=A.Vector(-v.z,v.y,v.x);w=rotation.multVec(q);weight=v.Length
  oldsum+=math.degrees(math.asin(min(1,abs(q.z)/weight)))*weight
  newsum+=math.degrees(math.asin(min(1,abs(w.z)/weight)))*weight;length+=weight
 angles[name]={'before_mean_degrees_above_bed':oldsum/length,'after_mean_degrees_above_bed':newsum/length}
assert all(v['after_mean_degrees_above_bed']<v['before_mean_degrees_above_bed'] for v in angles.values())
report={'units':'mm','source_review':m,'rotation_about_previous_print_x_degrees':90,'matched_part_positions_preserved':True,'flat_clip_orientation_preserved':True,'before_mechanism_height_mm':before.BoundBox.ZLength,'after_mechanism_height_mm':main.BoundBox.ZLength,'layout_dimensions_mm':[allshape.BoundBox.XLength,allshape.BoundBox.YLength,allshape.BoundBox.ZLength],'arm_inclinations':angles,'files':files,'native_sha256':sha(native),'physical_strength_verified':False}
(O/'validation.json').write_text(json.dumps(report,indent=2));(S/'validation.json').write_text(json.dumps(report,indent=2));A.closeDocument(d.Name);A.closeDocument(src.Name);print(json.dumps(report['arm_inclinations'],indent=2));print('LAYOUT',report['layout_dimensions_mm'])
