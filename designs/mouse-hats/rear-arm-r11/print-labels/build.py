"""Emboss permanent option letters onto the exterior tray back and export units."""
from pathlib import Path
import json,hashlib
import FreeCAD as App
import Part,MeshPart
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
SOURCE=ROOT/'generated/mouse-hats/rear-arm-r11'
OUT=SOURCE/'labeled';OUT.mkdir(exist_ok=True)
font=Path('C:/Windows/Fonts/arialbd.ttf')
settings={'units':'mm','font':str(font),'font_sha256':hashlib.sha256(font.read_bytes()).hexdigest(),'letter_height_mm':3.5,'relief_mm':.4,'embed_mm':.05,'back_plane_x_mm':3.70677424482636,'center_y_mm':14.1,'center_z_mm':0.0}
(HERE/'settings.json').write_text(json.dumps(settings,indent=2)+'\n')
reports={}
for key in 'ABCDE':
 src=App.openDocument(str(SOURCE/('r11'+key.lower()+'-assembly.FCStd')))
 carrier=src.Carrier.Shape;holder=src.Holder.Shape
 wires=Part.makeWireString(key,str(font.parent)+'/',font.name,3.5)[0]
 face=Part.makeFace(wires,'Part::FaceMakerBullseye')
 face.scale(settings['letter_height_mm']/face.BoundBox.YLength)
 bounds=face.BoundBox;face.translate(App.Vector(-(bounds.XMin+bounds.XMax)/2,-(bounds.YMin+bounds.YMax)/2,0))
 # Text horizontal -> global +Z, vertical -> +Y; normal points outward (-X).
 m=App.Matrix();m.A11=0;m.A12=0;m.A13=-1;m.A21=0;m.A22=1;m.A23=0;m.A31=1;m.A32=0;m.A33=0
 face=face.transformGeometry(m)
 face.translate(App.Vector(settings['back_plane_x_mm']+settings['embed_mm'],settings['center_y_mm'],settings['center_z_mm']))
 label=face.extrude(App.Vector(-settings['relief_mm']-settings['embed_mm'],0,0))
 labeled=carrier.fuse(label).removeSplitter();labeled.check(True)
 expected=face.Area*settings['relief_mm'];added=labeled.Volume-carrier.Volume
 assert labeled.isValid() and len(labeled.Solids)==1
 assert abs(added-expected)<.002,(key,added,expected)
 assert labeled.common(holder).Volume<1e-6
 for name in ['ClipReference','CapReference','BaseplateReference']:
  assert label.common(src.getObject(name).Shape).Volume<1e-6,(key,name)
 doc=App.newDocument('R11'+key+'Labeled');doc.Label='R11'+key+' - embossed print unit'
 for name,shape in [('Carrier',labeled),('Holder',holder)]:
  ob=doc.addObject('Part::Feature',name);ob.Shape=shape.copy()
 doc.Carrier.addProperty('App::PropertyString','OptionID','Identity');doc.Carrier.OptionID=key
 doc.Carrier.addProperty('App::PropertyLength','LetterHeight','Identity');doc.Carrier.LetterHeight=3.5
 doc.Carrier.addProperty('App::PropertyLength','LabelRelief','Identity');doc.Carrier.LabelRelief=.4
 doc.recompute();doc.saveAs(str(OUT/('R11'+key+'-labeled.FCStd')))
 mesh=MeshPart.meshFromShape(Shape=Part.makeCompound([labeled,holder]),LinearDeflection=.03,AngularDeflection=.15,Relative=False)
 assert mesh.isSolid();mesh.write(str(OUT/('R11'+key+'-labeled-carrier-and-holder.stl')))
 reports[key]={'valid':True,'carrier_solids':1,'label_height_mm':3.5,'label_relief_mm':.4,'added_volume_mm3':added,'expected_label_added_volume_mm3':expected,'holder_gap_mm':labeled.distToShape(holder)[0],'no_label_overlap_with_accessories':True}
 print(key,json.dumps(reports[key]),flush=True)
 App.closeDocument(doc.Name);App.closeDocument(src.Name)
(OUT/'label-validation.json').write_text(json.dumps(reports,indent=2)+'\n')
