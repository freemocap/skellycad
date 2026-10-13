"""Emboss matching H/T IDs and export two R11B height-test pairs."""
from pathlib import Path
import sys,json,hashlib
import FreeCAD as A
import Part,MeshPart
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
import height_features
SOURCE=ROOT/'generated/mouse-hats/pcb-retention-study/height-geometry'
OUT=SOURCE/'labeled';OUT.mkdir(exist_ok=True)
font=Path('C:/Windows/Fonts/arialbd.ttf')
settings={'units':'mm','font':str(font),'font_sha256':hashlib.sha256(font.read_bytes()).hexdigest(),'letter_height_mm':3.5,'relief_mm':.4,'embed_mm':.05,'variants':{'H':{'height_extra_mm':.5,'source':'height-0p5.FCStd'},'T':{'height_extra_mm':1.,'source':'height-1p0.FCStd'}},'carrier_label_center_mm':[3.70677424482636,14.1,0.0],'cap_label_center_mm':[10.2870639964732,12.5,-15.5]}
(HERE/'height-print-labels.json').write_text(json.dumps(settings,indent=2)+'\n')
def text_solid(letter,center,outward):
 face=Part.makeFace(Part.makeWireString(letter,str(font.parent)+'/',font.name,3.5)[0],'Part::FaceMakerBullseye')
 face.scale(3.5/face.BoundBox.YLength);b=face.BoundBox
 face.translate(A.Vector(-(b.XMin+b.XMax)/2,-(b.YMin+b.YMax)/2,0))
 # Viewer-readable on either external face: horizontal reverses with normal.
 m=A.Matrix();m.A11=0;m.A12=0;m.A13=outward;m.A21=0;m.A22=1;m.A23=0;m.A31=-outward;m.A32=0;m.A33=0
 face=face.transformGeometry(m);face.translate(A.Vector(center[0]-outward*.05,center[1],center[2]))
 return face.extrude(A.Vector(outward*.45,0,0)),face.Area*.4
reports={}
for letter,v in settings['variants'].items():
 srcpath=SOURCE/v['source'];before=hashlib.sha256(srcpath.read_bytes()).hexdigest()
 s=A.openDocument(str(srcpath));carrier=s.HeightCarrier.Shape;cap=s.HeightCap.Shape;holder=s.Holder.Shape
 tc,expectedc=text_solid(letter,settings['carrier_label_center_mm'],-1)
 tp,expectedp=text_solid(letter,settings['cap_label_center_mm'],1)
 nc=carrier.fuse(tc).removeSplitter();np=cap.fuse(tp).removeSplitter()
 for new,old,expected in [(nc,carrier,expectedc),(np,cap,expectedp)]:
  new.check(True);assert new.isValid() and len(new.Solids)==1
  assert abs(new.Volume-old.Volume-expected)<.002,(letter,new.Volume-old.Volume,expected)
 for label,neighbors in [(tc,[cap,holder,s.ClipReference.Shape,s.BaseplateReference.Shape]),(tp,[carrier,holder,s.ClipReference.Shape,s.BaseplateReference.Shape])]:
  assert all(label.common(n).Volume<1e-6 for n in neighbors)
 assert abs(nc.distToShape(holder)[0]-.33172186266949)<1e-6
 assert abs(nc.common(np).Volume-carrier.common(cap).Volume)<1e-6
 d=A.newDocument('HeightPrint'+letter);d.Label='R11B '+letter+' +'+str(v['height_extra_mm'])+' mm height TEST'
 for name,shape in [('Carrier',nc),('Holder',holder),('Cap',np),('CarrierEmboss',tc),('CapEmboss',tp)]:
  o=d.addObject('Part::Feature',name);o.Shape=shape.copy()
 for name in ['Carrier','Cap']:
  o=d.getObject(name);o.addProperty('App::PropertyString','TestID','Identity');o.TestID=letter
  o.addProperty('App::PropertyLength','HeightExtra','Identity');o.HeightExtra=v['height_extra_mm']
 d.recompute();d.saveAs(str(OUT/('R11B-'+letter+'-height-test.FCStd')))
 files=[]
 for name,shape in [('carrier-and-holder',Part.makeCompound([nc,holder])),('cap',np)]:
  filename='R11B-'+letter+'-plus-'+str(v['height_extra_mm']).replace('.','p')+'mm-'+name+'.stl'
  mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.03,AngularDeflection=.15,Relative=False)
  assert mesh.isSolid();mesh.write(str(OUT/filename));files.append(filename)
 reports[letter]={'height_extra_mm':v['height_extra_mm'],'carrier_label_added_mm3':nc.Volume-carrier.Volume,'cap_label_added_mm3':np.Volume-cap.Volume,'holder_gap_mm':nc.distToShape(holder)[0],'cap_contact_mm3':nc.common(np).Volume,'valid_single_solid_carrier_and_cap':True,'label_accessory_intersections_mm3':0,'files':files,'source_sha256':before}
 assert hashlib.sha256(srcpath.read_bytes()).hexdigest()==before
 print(letter,json.dumps(reports[letter]),flush=True)
 A.closeDocument(d.Name);A.closeDocument(s.Name)
(OUT/'label-validation.json').write_text(json.dumps(reports,indent=2)+'\n')
