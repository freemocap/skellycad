"""Static top-view comparison emphasizing the rear ribbon loop."""
from pathlib import Path
import FreeCAD as App,FreeCADGui as Gui
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/skull-neutral-r02'
sources=[next(d for d in App.listDocuments().values() if d.FileName.replace('\\','/').endswith(suffix)) for suffix in ['skull-neutral-r01/neutral-joint-study.FCStd','skull-neutral-r02/ribbon-space-study.FCStd']]
doc=App.newDocument('RibbonSpaceComparison');doc.Label='R01 / R02 — same eye aim, restored ribbon space'
for i,(src,x) in enumerate(zip(sources,[-23,23])):
 for name in ['NeutralCarrier','CenteredHolder','CenteredClip']:
  old=src.getObject(name);o=doc.addObject('Part::Feature',f'R0{i+1}'+name);o.Shape=old.Shape.copy();o.Placement.Base+=App.Vector(x,0,0)
  o.ViewObject.ShapeColor=(.55,.58,.6) if i==0 and name=='NeutralCarrier' else old.ViewObject.ShapeColor
 text=doc.addObject('App::Annotation',f'R0{i+1}Label');text.LabelText=['R01 — compressed rear loop' if i==0 else 'R02 — preserved R11B loop'];text.Position=App.Vector(x-15,22,0);text.ViewObject.TextColor=(.95,.95,.95);text.ViewObject.FontSize=14
doc.recompute();Gui.activeDocument().activeView().viewTop();Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(OUT/'ribbon-space-comparison.FCStd'))
Gui.activeDocument().activeView().saveImage(str(OUT/'ribbon-space-comparison.png'),1400,900,'Current')
