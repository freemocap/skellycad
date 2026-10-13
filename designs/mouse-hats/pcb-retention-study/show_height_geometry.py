"""Show three whole-assembly height variants and their matching caps."""
from pathlib import Path
import sys,json
import FreeCAD as A,FreeCADGui as G
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file());OUT=ROOT/'generated/mouse-hats/pcb-retention-study/height-geometry'
sys.path.insert(0,str(HERE))
from height_features import backing
p=json.loads((HERE.parent/'reconstruction/main_carrier/profiles.json').read_text())['features'][0]['profiles_mm']
d=A.newDocument('PCBHeightComparison');d.Label='R11B tray height - original / +0.5 / +1 mm STUDIES'
for amount,row in [(0,60),(.5,30),(1.0,0)]:
 src=A.openDocument(str(OUT/('height-'+str(amount).replace('.','p')+'.FCStd')))
 for o in src.Objects:
  if hasattr(o,'ViewObject'):o.ViewObject.Visibility=False
 src.HeightCarrier.ViewObject.Visibility=True
 group=d.addObject('App::Part','Height'+str(amount).replace('.','p'));group.Label='Upper edge +'+str(amount)+' mm'
 def add(name,shape,color,trans=0,shift=None):
  o=d.addObject('Part::Feature',name);o.Shape=shape.copy();group.addObject(o)
  if shift:o.Placement.Base=shift
  o.ViewObject.ShapeColor=color;o.ViewObject.LineColor=(.12,.16,.18);o.ViewObject.Transparency=trans
  return o
 add('Carrier',src.R11BReference.Shape,(.28,.63,.76))
 if amount:add('AddedTrayMaterial',backing(p,amount).cut(backing(p,0)).removeSplitter(),(1.0,.66,.12))
 add('WholePCB',src.ApproxPCB.Shape,(.22,.7,.32),12)
 add('Connector',src.Connector.Shape,(.94,.94,.88))
 add('Holder',src.Holder.Shape,(.65,.43,.76))
 add('Clip',src.ClipReference.Shape,(.65,.43,.76))
 cap=add('MatchingCap',src.HeightCap.Shape,(.7,.65,.82),0,A.Vector(0,0,-53))
 cap.Label='Matching cap - shifted aside for DISPLAY ONLY'
 group.Placement.Base=A.Vector(0,row,0)
 for text,z in [('R11B / upper edge +'+str(amount)+' mm',5),('Matching cap (display offset)',-47)]:
  o=d.addObject('App::Annotation','Label');o.LabelText=[text];o.Position=A.Vector(12,row+23,z);o.ViewObject.TextColor=(.95,.95,.95);o.ViewObject.FontSize=14;o.ViewObject.Visibility=True
A.setActiveDocument(d.Name);d.recompute()
n=A.Vector(1,.15,.05);u=A.Vector(0,1,0);G.activeDocument().activeView().setCameraOrientation(A.Rotation(u.cross(n),u,n,'ZXY').Q);G.activeDocument().activeView().fitAll();d.saveAs(str(OUT/'height-comparison.FCStd'))
