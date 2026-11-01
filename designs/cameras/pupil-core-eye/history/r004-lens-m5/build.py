from pathlib import Path
import FreeCAD as A, Part, MeshPart, json, hashlib
V=A.Vector
ROOT=Path(__file__).resolve().parents[6];OUT=ROOT/'generated/eye-tracker/shared/lens-m5-r04';OUT.mkdir(parents=True,exist_ok=True)
source=ROOT/'generated/eye-tracker/shared/lens-m5-r01/IADIY-M5-SCALED-6p3mm.step'
holder=Part.Shape();holder.read(str(source))
rim=2.95*6.3/6.5
# Straight screw-in barrel with no shoulder; user correction.
barrel=Part.makeCylinder(2.42,3.7)
# Explicit helical groove approximated by overlapping circular sweeps along a helix.
# Use interpolated path to control the sweep radius in mm.
import math
pts=[V(2.42*math.cos(t),2.42*math.sin(t),rim-.1+.33923*t/(2*math.pi)) for t in [i*2*math.pi/80 for i in range(241)]]
curve=Part.BSplineCurve();curve.interpolate(pts);path=Part.Wire([curve.toShape()])
profile=Part.Wire([Part.makeCircle(.12,pts[0],V(0,1,0))])
groove=path.makePipeShell([profile],True,True)
barrel=barrel.cut(groove)
# Straight barrel: no enlarged head or shoulder; top edge at measured 3.7 mm.
barrel=barrel.cut(Part.makeCylinder(1.7,.8,V(0,0,3.2)))
lens=Part.makeSphere(4,V(0,0,-.35)).common(Part.makeCylinder(1.7,.45,V(0,0,3.2)))
barrel=barrel.cut(holder).cut(lens).removeSplitter()
whole=holder.fuse(barrel).fuse(lens).removeSplitter()
assert whole.isValid() and len(whole.Solids)==1
assert abs(whole.BoundBox.XLength-6.3)<1e-7
assert abs(whole.BoundBox.ZMax-3.7)<1e-7
assert abs(barrel.BoundBox.XLength-4.84)<1e-7
assert abs(barrel.BoundBox.YLength-4.84)<1e-7
for name,s in [('Housing',holder),('ProtrudingLensBarrel',barrel),('FakeLens',lens),('CompleteDummyLens',whole)]:
 assert s.isValid() and s.Volume>0
 s.exportStep(str(OUT/(name+'.step')))
mesh=MeshPart.meshFromShape(Shape=whole,LinearDeflection=.015,AngularDeflection=.08,Relative=False);assert mesh.isSolid();mesh.write(str(OUT/'FAKE-CAMERA-LENS-6p3mm.stl'))
(OUT/'validation.json').write_text(json.dumps({'units':'mm','valid':True,'single_solid':True,'closed_mesh':True,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'width':6.3,'holder_rim_height':rim,'lens_top':lens.BoundBox.ZMax,'projection_above_holder':lens.BoundBox.ZMax-rim,'print_material':'black PLA','functional_optics':False,'barrel_top_mm':3.7,'barrel_diameter_mm':4.84,'barrel_top_source':'User measurement','diameter_is_approximate':True},indent=2))
print('PROTRUDING_LENS_OK')
