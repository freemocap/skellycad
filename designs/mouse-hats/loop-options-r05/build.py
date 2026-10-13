"""Three lower-root loop sizes; native shapes and labeled printable comparison pack."""
from pathlib import Path
import json,hashlib,sys,copy
import FreeCAD as App,FreeCADGui as Gui,Part,MeshPart
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
for p in [HERE,HERE.parent/'model',HERE.parent/'rear-arm-r11']:sys.path.insert(0,str(p))
from geometry import build_geometry
s=json.loads((HERE/'settings.json').read_text());source=ROOT/s['source_checkpoint']
assert hashlib.sha256(source.read_bytes()).hexdigest()==s['source_sha256']
src=next((d for d in App.listDocuments().values() if Path(d.FileName)==source),None) or App.openDocument(str(source))
OUT=ROOT/'generated/mouse-hats/loop-options-r05';OUT.mkdir(parents=True,exist_ok=True)
font=Path('C:/Windows/Fonts/arialbd.ttf')
def remove_text(shape,name,x,normal):
 tool=Part.Shape();tool.read(str(HERE/(name+'Emboss.brep')))
 outside=Part.makeBox(100,200,200,App.Vector(x-100 if normal<0 else x,-100,-100))
 return shape.cut(tool.common(outside)).removeSplitter()
def label(letter):
 face=Part.makeFace(Part.makeWireString(letter,str(font.parent)+'/',font.name,3.5)[0],'Part::FaceMakerBullseye')
 face.scale(3.5/face.BoundBox.YLength);b=face.BoundBox;face.translate(App.Vector(-(b.XMin+b.XMax)/2,-(b.YMin+b.YMax)/2,0))
 mat=App.Matrix();mat.A11=0;mat.A12=0;mat.A13=-1;mat.A21=0;mat.A22=1;mat.A23=0;mat.A31=1;mat.A32=0;mat.A33=0
 face=face.transformGeometry(mat);face.translate(App.Vector(3.75677424482636,13.2,0))
 return face.extrude(App.Vector(-.45,0,0))
def add(doc,name,sh,color,visible=True):
 o=doc.addObject('Part::Feature',name);o.Shape=sh.copy();o.ViewObject.ShapeColor=color;o.Visibility=visible;return o
def export(name,sh):
 MeshPart.meshFromShape(Shape=sh,LinearDeflection=.03,AngularDeflection=.15,Relative=False).write(str(OUT/(name+'.stl')))
cap=remove_text(src.Cap.Shape,'Cap',10.2870639964732,1)
report={'source':str(source.relative_to(ROOT)),'source_sha256':s['source_sha256'],'units':'mm, mm3','variants':{},'common_cap_label_removed':True}
review=App.newDocument('LoopOptionsR05');review.Label='R05 PRINT TEST — A compact / B medium / C roomy'
plate=[]
for index,(letter,variant) in enumerate(s['variants'].items()):
 params=copy.deepcopy(s);params['root_handle_mm']=params['socket_handle_mm']=variant['handle_mm']
 carrier,arm,path=build_geometry(params,src,HERE/'socket-source.brep')
 clean=remove_text(carrier,'Carrier',3.70677424482636,-1);old_label_volume=carrier.Volume-clean.Volume;mark=label(letter)
 carrier=clean.fuse(mark).removeSplitter();carrier.check(True)
 assert carrier.isValid() and len(carrier.Solids)==1
 assert cap.isValid() and len(cap.Solids)==1
 checks={n:carrier.common(src.getObject(n).Shape).Volume for n in ['Holder','Clip','Baseplate','ApproxPCB']}
 assert max(checks.values())<1e-6
 assert src.UpperCatch.Shape.cut(carrier).Volume<1e-6 and src.UpperRail.Shape.cut(carrier).Volume<1e-6
 assert abs(carrier.common(cap).Volume-src.Carrier.Shape.common(src.Cap.Shape).Volume)<1e-6
 assert carrier.common(src.OpticalAxis.Shape).Length<1e-6
 d=App.newDocument('R05_'+letter);d.Label='R05 '+letter+' — '+variant['description']
 for name,sh,color,vis in [('Carrier',carrier,(.2,.75,.8),True),('Holder',src.Holder.Shape,(.62,.45,.8),True),('Cap',cap,(.85,.65,.2),False),('Clip',src.Clip.Shape,(.85,.65,.2),False),('Baseplate',src.Baseplate.Shape,(.75,.65,.35),False),('RearArm',arm,(.2,.75,.8),False)]:add(d,name,sh,color,vis)
 d.recompute();d.saveAs(str(HERE/('R05-'+letter+'.FCStd')))
 pair=Part.makeCompound([carrier,src.Holder.Shape]);export('R05-'+letter+'-'+variant['description'].lower()+'-carrier-and-holder',pair)
 shifted=pair.copy();shifted.translate(App.Vector(index*55,0,-pair.BoundBox.ZMin));plate.append(shifted)
 for name,sh,color in [('Carrier',carrier,(.2,.75,.8)),('Holder',src.Holder.Shape,(.62,.45,.8))]:
  display=sh.copy();display.translate(App.Vector(0,index*40,0));add(review,letter+name,display,color)
 report['variants'][letter]={'description':variant['description'],'handle_mm':variant['handle_mm'],'rearward_projection_mm':3.70677424482636-arm.BoundBox.XMin,'curved_path_length_mm':path.Length,'holder_gap_mm':carrier.distToShape(src.Holder.Shape)[0],'intersections_mm3':checks,'carrier_volume_mm3':carrier.Volume,'old_label_removed_mm3':old_label_volume,'carrier_valid':True}
 print(letter,report['variants'][letter],flush=True)
export('R05-ABC-comparison-plate',Part.makeCompound(plate))
for name,sh in [('shared-matching-cap',cap),('shared-camera-clip',src.Clip.Shape),('shared-baseplate',src.Baseplate.Shape)]:export('R05-'+name,sh)
App.setActiveDocument(review.Name);review.recompute();Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
review.saveAs(str(HERE/'R05-ABC-comparison.FCStd'))
(HERE/'validation.json').write_text(json.dumps(report,indent=2));print(str(OUT))
