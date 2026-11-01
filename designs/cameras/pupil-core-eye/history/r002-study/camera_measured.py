"""Measured camera R02; reuse the R01 bend geometry and named solid conversion."""
from pathlib import Path
import sys,json,math,hashlib
import FreeCAD as A, Part
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'study-r01'))
import camera_study as base
OUT=base.ROOT/'generated/eye-tracker/shared/camera-study-r02'

def build(output_dir=None, revision='r02', connector_selection=None):
 OUT=Path(output_dir) if output_dir else globals()['OUT']
 OUT.mkdir(parents=True,exist_ok=True)
 scene={o['name']:o for o in json.loads((HERE/'calibrated-scene.json').read_text())['objects']}
 measurements=json.loads((HERE/'measurements.json').read_text())
 assert hashlib.sha256((HERE/'caliper-sketch.jpg').read_bytes()).hexdigest()==measurements['sketch_sha256']
 d=A.newDocument('CameraMeasured'+revision.upper());records=[]
 for i,angle in enumerate((0,90,180)):
  root,flex=base.create_camera(d,'Measured'+str(angle),angle,(44*i,0,0),scene=scene)
  flex.Limitations='Caliper plan dimensions confirmed; board/ribbon thickness assumed. Connector identity and lens holder height/thread pitch unknown.'
  head=flex.Head
  # Nominal diameter reference only: preserve the supplied holder envelope.
  lens=next(o for o in head.Group if o.SourceName=='M4-lens')
  lens.Label='Lens holder envelope - source height unverified'
  box=lens.Shape.BoundBox
  barrel=base.add_shape(d,head,'M4 nominal diameter reference - not stock lens',Part.makeCylinder(2,.15,A.Vector((box.XMin+box.XMax)/2,(box.YMin+box.YMax)/2,box.ZMax)),(.30,.40,.55))
  barrel.addProperty('App::PropertyString','Evidence').Evidence='User identifies M4. Diameter reference only; 0.15 mm display height, thread pitch and actual barrel dimensions unknown.'
  connector=next(o for o in root.Group if o.TypeId=='App::Part' and 'Main' in o.Name)
  socket=next(o for o in connector.Group if o.SourceName=='JST-4pin')
  socket.Label='Connector envelope - exact part unknown'
  if connector_selection:
   source=HERE.parent/connector_selection['asset']
   assert hashlib.sha256(source.read_bytes()).hexdigest()==connector_selection['sha256']
   replacement=Part.Shape();replacement.read(str(source))
   assert replacement.isValid() and len(replacement.Solids)==1
   old=socket.Shape.BoundBox;b=replacement.BoundBox
   # Translate only. Preserve stock dimensions and the STEP's PCB seating plane Z=0.
   replacement.translate(A.Vector((old.XMin+old.XMax-b.XMin-b.XMax)/2,old.YMin-b.YMin,0))
   socket.Shape=replacement
   socket.Label='JST SH SM04B-SRSS-TB - provisional'
   socket.addProperty('App::PropertyString','SelectionStatus').SelectionStatus=connector_selection['status']
   flex.Limitations='Caliper plan dimensions confirmed; JST SH selected provisionally. Connector registration, board/ribbon thickness and lens holder dimensions unverified.'
  for a in [0,45,90,120,180]:
   flex.BendDegrees=a;d.recompute()
   assert flex.Shape.isValid() and len(flex.Shape.Solids)==1
   assert abs(flex.Shape.Volume-32.85*4*.15)<1e-7
   _,end,rot,radius=base.ribbon_shape(32.85,4,.15,a)
   assert (head.Placement.Base-end).Length<1e-8
  flex.BendDegrees=angle;d.recompute()
  mainboard=next(o for o in connector.Group if o.SourceName=='PCB').Shape.BoundBox
  hb=next(o for o in head.Group if o.SourceName=='camera-pcb').Shape.BoundBox
  assert abs(mainboard.XLength-9)<1e-8 and abs(mainboard.YLength-30.85)<1e-8
  assert abs(hb.XLength-6)<1e-8 and abs(hb.YLength-15)<1e-8
  records.append({'angle':angle,'ribbon_length_mm':flex.FreeLength.Value,'pcb_mm':[mainboard.XLength,mainboard.YLength],'head_mm':[hb.XLength,hb.YLength],'valid':True})
 # Keep imported components separate from the proposed camera: no guessed substitution.
 group=d.addObject('App::Part','ConnectorCandidates');group.Label='UNCONFIRMED connector candidates - KiCad CC-BY-SA 4.0 + exception'
 candidates=[]
 for i,p in enumerate([] if connector_selection else sorted((HERE/'connector-candidates').glob('*.step'))):
  shape=Part.Shape();shape.read(str(p));assert shape.isValid() and len(shape.Solids)>0
  b=shape.BoundBox;dims=[b.XLength,b.YLength,b.ZLength]
  shape.translate(A.Vector(130-b.XMin,i*12-b.YMin,-b.ZMin))
  obj=base.add_shape(d,group,'CANDIDATE '+p.stem,shape,(.88,.86,.76))
  obj.addProperty('App::PropertyString','FitStatus').FitStatus='Unidentified: do not use to establish camera mounting clearances'
  candidates.append({'file':p.name,'dimensions_mm':dims,'valid':True,'solids':len(shape.Solids),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 if connector_selection:d.removeObject(group.Name)
 d.recompute();path=OUT/('camera-measured-'+revision+'.FCStd');d.saveAs(str(path));d.Label='Camera '+revision.upper()+(' - provisional JST SH' if connector_selection else ' - caliper dimensions + connector candidates');d.save()
 parts=[]
 for o in d.Objects:
  if o.TypeId in ('PartDesign::Feature','PartDesign::FeaturePython') and not o.Label.startswith('Optical direction') and not o.Label.startswith('CANDIDATE'):
   sh=o.Shape.copy();sh.Placement=o.getGlobalPlacement();parts.append(sh)
 comp=Part.makeCompound(parts);comp.exportStep(str(OUT/('camera-measured-'+revision+'.step')))
 check=Part.Shape();check.read(str(OUT/('camera-measured-'+revision+'.step')));assert check.isValid() and len(check.Solids)==24
 (OUT/'validation.json').write_text(json.dumps({'passed':True,'variants':records,'connector_candidates':candidates,'connector_selection':connector_selection,'STEP_solids':len(check.Solids),'scope':'Geometry only; exact connector and lens holder not verified'},indent=2))
 if A.GuiUp:
  import FreeCADGui as G
  G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();G.updateGui()
  G.activeDocument().activeView().saveImage(str(OUT/'preview.png'),1400,1000,'White')
 return d
if __name__=='__main__':build()

