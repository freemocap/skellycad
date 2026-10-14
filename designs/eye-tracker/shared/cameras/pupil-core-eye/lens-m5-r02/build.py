from pathlib import Path
import FreeCAD as A, Part, MeshPart, json, hashlib
V=A.Vector
ROOT=Path(__file__).resolve().parents[6];OUT=ROOT/'generated/eye-tracker/shared/lens-m5-r02';OUT.mkdir(parents=True,exist_ok=True)
source=ROOT/'generated/eye-tracker/shared/lens-m5-r01/IADIY-M5-SCALED-6p3mm.step'
holder=Part.Shape();holder.read(str(source))
# Visual mock lens. Heights remain within the existing holder rim.
barrel=Part.makeCylinder(2.24,2.72)
barrel=barrel.cut(Part.makeCylinder(1.55,.6,V(0,0,2.4)))
# Six small drive slots around the retaining ring.
for angle in range(0,360,60):
 slot=Part.makeBox(.5,.25,.25,V(1.83,-.125,2.58));slot.rotate(V(0,0,0),V(0,0,1),angle);barrel=barrel.cut(slot)
# Convex optical face represented by solid PLA, with a contrasting CAD appearance.
lens=Part.makeSphere(4,V(0,0,-1.2)).common(Part.makeCylinder(1.55,.4,V(0,0,2.4)))
barrel=barrel.cut(holder).cut(lens).removeSplitter()
whole=holder.fuse(barrel).fuse(lens).removeSplitter()
assert whole.isValid() and len(whole.Solids)==1
assert abs(whole.BoundBox.XLength-6.3)<1e-7
assert abs(whole.BoundBox.ZMax-2.95*6.3/6.5)<1e-7
for name,s in [('Housing',holder),('RetainingRing',barrel),('FakeLens',lens),('CompleteDummyLens',whole)]:
 assert s.isValid() and s.Volume>0
 s.exportStep(str(OUT/(name+'.step')))
mesh=MeshPart.meshFromShape(Shape=whole,LinearDeflection=.015,AngularDeflection=.08,Relative=False);assert mesh.isSolid();mesh.write(str(OUT/'FAKE-LENS-6p3mm-black-PLA.stl'))
(OUT/'validation.json').write_text(json.dumps({'units':'mm','valid':True,'single_solid':True,'closed_mesh':True,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'width':6.3,'rim_height':whole.BoundBox.ZMax,'lens_top':lens.BoundBox.ZMax,'print_material':'black PLA','functional_optics':False},indent=2))
print('FAKE_LENS_OK')
