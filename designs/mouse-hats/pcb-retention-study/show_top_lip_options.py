"""Whole-board top-lip review with explicit optional height datum."""
from pathlib import Path
import FreeCAD as A,FreeCADGui as G
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file());OUT=ROOT/'generated/mouse-hats/pcb-retention-study'
d=A.openDocument(str(OUT/'top-lip-clearance-study.FCStd'))
for o in d.Objects:
 if not hasattr(o,'Shape'):continue
 o.ViewObject.Visibility=True;o.ViewObject.LineColor=(.12,.16,.18)
 if o.Name=='FixedCarrier':o.ViewObject.ShapeColor=(.27,.64,.78)
 elif o.Name=='WholePCB':o.ViewObject.ShapeColor=(.22,.7,.32);o.ViewObject.Transparency=12
 elif o.Name=='TopLip':o.ViewObject.ShapeColor=(1.0,.65,.12)
 elif o.Name in ['RemovedNose','CapConflict']:o.ViewObject.ShapeColor=(1.0,.15,.12);o.ViewObject.Visibility=False
 elif o.Name=='ConnectorEnvelope':o.ViewObject.ShapeColor=(.94,.94,.88)
 elif o.Name=='PlusOneTarget':o.ViewObject.LineColor=(1.0,.65,.12);o.ViewObject.LineWidth=3
 elif o.Name=='CurrentUpperEdge':o.ViewObject.LineColor=(.8,.8,.8);o.ViewObject.LineWidth=1
 elif o.Name in ['CandidateWithLip','CapReference']:o.ViewObject.ShapeColor=(.75,.75,.78);o.ViewObject.Transparency=80;o.ViewObject.Visibility=False
 else:o.ViewObject.ShapeColor=(.64,.43,.76)
for name,text,point in [('HeightLabel','Optional +1 mm upper-edge target (line only)',A.Vector(9,22,1)),('LipLabel','TOP LIP CONCEPT - current cap clashes',A.Vector(9,20,-4)),('NoseLabel','Circled nose now flush',A.Vector(9,3,-1))]:
 o=d.getObject(name) or d.addObject('App::Annotation',name);o.LabelText=[text];o.Position=point;o.ViewObject.TextColor=(.95,.95,.95);o.ViewObject.FontSize=14;o.ViewObject.Visibility=True
A.setActiveDocument(d.Name);d.recompute()
n=A.Vector(1,0,0);u=A.Vector(0,1,0);G.activeDocument().activeView().setCameraOrientation(A.Rotation(u.cross(n),u,n,'ZXY').Q);G.activeDocument().activeView().fitAll();d.save()
