"""Compare the unchanged R05C and the relocated rear attachment."""
from pathlib import Path
import sys,json
import FreeCAD as App
import FreeCADGui as Gui
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
for p in [HERE,HERE.parent/'rear-attachment-r05',HERE.parent/'model',HERE.parent/'print-test-r03',HERE.parent/'print-test']:sys.path.insert(0,str(p))
import forward_sweep,forward_carrier_features,attachment_sweep,sliding_attachment_features,socket_revision_features
OUT=ROOT/'generated/mouse-hats/rear-arm-r06'
ref=App.openDocument(str(ROOT/'generated/mouse-hats/print-test/r03/print-in-place-review.FCStd'))
doc=App.newDocument('ForwardRootReview');doc.Label='Rear arm attachment - R05C vs R06A forward root + wider loop'
for key,path,offset,color in [('R05C',ROOT/'generated/mouse-hats/rear-attachment-r05/r05c-carrier.FCStd',24,(.7,.7,.73)),('R06A',OUT/'r06a-carrier.FCStd',0,(.24,.74,.82))]:
 source=App.openDocument(str(path))
 group=doc.addObject('App::Part',key);group.Label=key+' - '+('original attachment' if key=='R05C' else 'forward root / wider loop')
 for name,shape,c in [('Carrier',source.RibbonClearanceCarrier.Shape,color),('Holder',ref.Holder.Shape,(.66,.45,.81)),('Clip',ref.ClipReference.Shape,(.85,.4,.35))]:
  ob=doc.addObject('Part::Feature',key+name);ob.Shape=shape.copy();group.addObject(ob);ob.ViewObject.ShapeColor=c;ob.ViewObject.LineColor=(.12,.16,.19)
 group.Placement.Base=App.Vector(0,offset,0)
 label=doc.addObject('App::Annotation','Label'+key);label.LabelText=[group.Label];label.Position=App.Vector(-9,offset-8,34);label.ViewObject.TextColor=(.95,.95,.95);label.ViewObject.FontSize=14;label.ViewObject.Visibility=True
App.setActiveDocument(doc.Name);doc.recompute()
Gui.activeDocument().activeView().viewTop();Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(OUT/'rear-attachment-review.FCStd'))
