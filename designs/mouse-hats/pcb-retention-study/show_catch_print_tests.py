"""Show complete catch trials; gold is fused catch, green approximate PCB."""
from pathlib import Path
import FreeCAD as A,FreeCADGui as G
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'generated/mouse-hats/pcb-retention-study/height-geometry/with-catch'
d=A.newDocument('CompletePCBRetentionTests')
for letter,row in [('H',25),('T',0)]:
 s=A.openDocument(str(p/('R11B-'+letter+'-with-catch.FCStd')))
 for obj in s.Objects: obj.ViewObject.Visibility=False
 for name,color in [('Carrier',(.25,.65,.78)),('UpperCatch',(1.0,.65,.1)),('ApproxPCB',(.25,.7,.35)),('Holder',(.65,.4,.8)),('Cap',(.7,.6,.8))]:
  sh=s.getObject(name).Shape.copy()
  if name=='Carrier': sh=sh.cut(s.UpperCatch.Shape)
  sh.translate(A.Vector(0,row,-50 if name=='Cap' else 0))
  o=d.addObject('Part::Feature',letter+name);o.Shape=sh;o.ViewObject.ShapeColor=color
  if name=='ApproxPCB':o.ViewObject.Transparency=30
 a=d.addObject('App::Annotation','Label');a.LabelText=[letter+' +'+('0.5' if letter=='H' else '1.0')+' mm WITH upper catch'];a.Position=A.Vector(10,row+22,12);a.ViewObject.TextColor=(1.0,1.0,1.0);a.ViewObject.FontSize=14
A.setActiveDocument(d.Name);d.recompute()
n=A.Vector(1,.25,.1);u=A.Vector(0,1,0)
G.activeDocument().activeView().setCameraOrientation(A.Rotation(u.cross(n),u,n,'ZXY').Q)
G.activeDocument().activeView().fitAll()
d.saveAs(str(p/'catch-comparison.FCStd'))
