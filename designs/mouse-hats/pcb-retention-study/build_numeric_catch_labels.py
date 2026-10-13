"""Emboss numeric dimensions on complete PCB-catch print tests (mm)."""
from pathlib import Path
import json,hashlib
import FreeCAD as A
import Part,MeshPart
ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'generated/mouse-hats/pcb-retention-study/height-geometry/with-catch'
OUT=SRC/'numeric-labels';OUT.mkdir(exist_ok=True)
font=Path('C:/Windows/Fonts/arialbd.ttf')
def text(txt,height,center,normal):
 groups=Part.makeWireString(txt,str(font.parent)+'/',font.name,height)
 faces=[Part.makeFace(w,'Part::FaceMakerBullseye') for w in groups if w]
 face=Part.makeCompound(faces);face.scale(height/face.BoundBox.YLength)
 b=face.BoundBox;face.translate(A.Vector(-(b.XMin+b.XMax)/2,-(b.YMin+b.YMax)/2,0))
 m=A.Matrix();m.A11=0;m.A12=0;m.A13=normal;m.A21=0;m.A22=1;m.A23=0;m.A31=-normal;m.A32=0;m.A33=0
 face=face.transformGeometry(m);face.translate(A.Vector(center[0]-normal*.05,center[1],center[2]))
 return face.extrude(A.Vector(normal*.45,0,0)),face.Area*.4
report={}
for letter,amount in [('H','0.5'),('T','1.0')]:
 src=SRC/('R11B-'+letter+'-with-catch.FCStd');d=A.openDocument(str(src))
 row={};shapes={}
 for name,x,n in [('Carrier',3.70677424482636,-1),('Cap',10.2870639964732,1)]:
  old=d.getObject(name).Shape
  outside=Part.makeBox(100,200,200,A.Vector(x-100 if n<0 else x,-100,-100))
  base=old.cut(d.getObject(name+'Emboss').Shape.common(outside)).removeSplitter()
  lines=[(letter+' +'+amount,2.5,[x,13.4,0]),('mm',1.4,[x,10.9,0])] if name=='Carrier' else [(letter,2.4,[x,15.2,-15.5]),('+'+amount,1.8,[x,12.4,-15.5]),('mm',1.3,[x,10.2,-15.5])]
  labels=[];expected=0
  for txt,h,center in lines:
   sh,v=text(txt,h,center,n);labels.append(sh);expected+=v
  new=base.multiFuse(labels).removeSplitter();new.check(True)
  assert new.isValid() and len(new.Solids)==1,(letter,name,len(new.Solids))
  assert abs(new.Volume-base.Volume-expected)<.002,(letter,name,new.Volume-base.Volume,expected)
  # Only outward identification changes; original underlying solid preserved.
  assert base.cut(new).Volume<1e-7
  assert new.common(d.ApproxPCB.Shape).Volume<1e-7
  shapes[name]=new;d.getObject(name).Shape=new
  d.getObject(name+'Emboss').Shape=Part.makeCompound(labels)
  row[name]={'text':[line[0] for line in lines],'added_label_mm3':new.Volume-base.Volume}
 assert abs(shapes['Carrier'].common(shapes['Cap']).Volume-.00221822553385)<1e-6
 assert abs(shapes['Carrier'].distToShape(d.Holder.Shape)[0]-.33172186266949)<1e-6
 d.recompute();d.saveAs(str(OUT/('R11B-'+letter+'-numeric-catch.FCStd')))
 for name,sh in [('carrier-and-holder',Part.makeCompound([shapes['Carrier'],d.Holder.Shape])),('cap',shapes['Cap'])]:
  f=OUT/('R11B-'+letter+'-plus-'+amount.replace('.','p')+'mm-with-catch-'+name+'.stl')
  mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.03,AngularDeflection=.15,Relative=False);mesh.write(str(f))
 report[letter]=row;print(letter,row,flush=True);A.closeDocument(d.Name)
(OUT/'numeric-label-validation.json').write_text(json.dumps(report,indent=2))
