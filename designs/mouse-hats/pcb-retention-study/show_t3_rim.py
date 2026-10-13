from pathlib import Path
import FreeCAD as A,FreeCADGui as G
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'generated/mouse-hats/pcb-retention-study/height-geometry';OUT=P/'t3-rim'
d=A.newDocument('T3RimReview')
for path,row,label in [(P/'t2-grip/R11B-T2-grip.FCStd',28,'T2 - rail misses cap hook'),(OUT/'R11B-T3-rim.FCStd',0,'T3 - raised tray rail catches cap hook')]:
 s=A.openDocument(str(path))
 for obj in s.Objects:obj.ViewObject.Visibility=False
 for name,color in [('Carrier',(.25,.65,.8)),('Cap',(.65,.55,.8)),('Holder',(.65,.45,.75)),('ApproxPCB',(.4,.8,.5)),('UpperCatch',(1.0,.65,.1))]:
  sh=s.getObject(name).Shape.copy()
  if name=='Carrier':sh=sh.cut(s.UpperCatch.Shape)
  sh.translate(A.Vector(0,row,-50 if name=='Cap' else 0))
  o=d.addObject('Part::Feature',name);o.Shape=sh;o.ViewObject.ShapeColor=color if row==0 else (.6,.6,.6)
  if name=='ApproxPCB':o.ViewObject.Transparency=35
 a=d.addObject('App::Annotation','Label');a.LabelText=[label];a.Position=A.Vector(12,row+23,16);a.ViewObject.FontSize=14;a.ViewObject.TextColor=(1.0,1.0,1.0)
A.setActiveDocument(d.Name);d.recompute()
u=A.Vector(0,1,0);n=A.Vector(1,.25,.12)
G.activeDocument().activeView().setCameraOrientation(A.Rotation(u.cross(n),u,n,'ZXY').Q);G.activeDocument().activeView().fitAll()
d.saveAs(str(OUT/'T3-review.FCStd'))
