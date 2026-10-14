from pathlib import Path
import FreeCAD as A, Part, MeshPart, json
V=A.Vector
ROOT=Path(__file__).resolve().parents[6];OUT=ROOT/'generated/eye-tracker/shared/lens-m5-r01';OUT.mkdir(parents=True,exist_ok=True)
# Reconstructed from IADIY 6.5 mm holder drawing [@iadiyM5HolderDrawing].
base=Part.makeBox(6.5,6.5,1.6,V(-3.25,-3.25,0))
# Drawing shows a round collar tangent to the square; corner radius approximated.
vertical=[e for e in base.Edges if abs(e.Vertexes[-1].Point.z-e.Vertexes[0].Point.z)>1.59]
base=base.makeFillet(.2,vertical)
shape=base.fuse(Part.makeCylinder(3.25,1.35,V(0,0,1.6)))
shape=shape.cut(Part.makeCylinder(2.3,3.2,V(0,0,-.1)))
helix=Part.makeHelix(.35,3.5,2.41)
profile=Part.Wire([Part.makeCircle(.13,V(2.41,0,0),V(0,1,0))])
groove=Part.Wire(helix.Edges).makePipeShell([profile],True,True);groove.translate(V(0,0,-.2))
shape=shape.cut(groove).removeSplitter()
# Pin spacing 5.7; diagonal arrangement inferred from the two-pin views.
for x,y in [(-2.85,-2.85),(2.85,2.85)]:shape=shape.fuse(Part.makeCylinder(.175,.5,V(x,y,-.5)))
shape=shape.removeSplitter();assert shape.isValid() and len(shape.Solids)==1
scale=6.3/6.5
scaled=shape.copy();scaled.scale(scale)
assert abs(scaled.BoundBox.XLength-6.3)<1e-7 and abs(scaled.BoundBox.YLength-6.3)<1e-7
for title,s in [('IADIY-M5-RECONSTRUCTED-6p5mm',shape),('IADIY-M5-SCALED-6p3mm',scaled)]:
 d=A.newDocument(title.replace('-','_'));d.Label=title
 o=d.addObject('PartDesign::Feature','ThreadedHolder');o.Shape=s
 o.addProperty('App::PropertyString','Provenance').Provenance='Reconstructed from supplied IADIY PDF; not manufacturer CAD. Rounded helical thread profile and pin arrangement approximated.'
 o.addProperty('App::PropertyFloat','ScaleFactor').ScaleFactor=scale if 'SCALED' in title else 1
 if A.GuiUp:o.ViewObject.ShapeColor=(.22,.22,.24)
 d.recompute();d.saveAs(str(OUT/(title+'.FCStd')));s.exportStep(str(OUT/(title+'.step')))
 m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.015,AngularDeflection=.08,Relative=False);assert m.isSolid();m.write(str(OUT/(title+'.stl')))
(OUT/'validation.json').write_text(json.dumps({'valid':True,'units':'mm','scale':scale,'square':6.3,'base_height':1.6*scale,'rim_height':2.95*scale,'scaled_nominal_thread_diameter':5*scale,'scaled_pitch':.35*scale,'fit_verified':False},indent=2))
print('SCALED_M5_HOLDER_OK')
