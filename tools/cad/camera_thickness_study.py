from pathlib import Path
import sys,json,hashlib
import FreeCAD as A,Part,MeshPart
R=Path.cwd();O=R/'generated/eye-tracker/shared/camera-thickness-study';O.mkdir(parents=True,exist_ok=True)
S=R/'designs/eye-tracker/shared/cameras/pupil-core-eye';m=json.loads((S/'active-model.json').read_text())
parts={}
for name,rec in m['parts'].items():
 p=R/rec['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'];sh=Part.Shape();sh.read(str(p));parts[name]=sh
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'))
from replace_camera import world
assemblies={}
for species,manifest in [('rat','designs/eye-tracker/rat/compact-guard-r19/review.json'),('mouse','designs/eye-tracker/mouse/active-model.json')]:
 rec=json.loads((R/manifest).read_text());p=R/rec['native_checkpoint'];assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['native_sha256'];assemblies[species]=A.openDocument(str(p))
report={}
for thickness in [.25,.375,.5,.75,1.0,1.25,1.5,2.0]:
 extra=thickness-.25;new={}
 for name,sh in parts.items():
  out=sh.copy()
  if name in ['Red_PLA_boards','Yellow_TPU_ribbon'] and extra:
   faces=[f for f in sh.Faces if abs(f.BoundBox.ZMin)<1e-6 and abs(f.BoundBox.ZMax)<1e-6]
   out=out.multiFuse([f.extrude(A.Vector(0,0,-extra)) for f in faces]).removeSplitter()
  new[name]=out
 row={'fit':{}}
 for species,d in assemblies.items():
  row['fit'][species]={}
  boards=sorted(new['Red_PLA_boards'].Solids,key=lambda s:s.CenterOfMass.y)
  for idx,(name,b) in enumerate(zip(['PCB','camera_pcb'],boards)):
   b=b.copy();b.translate(A.Vector(0,-31.283345794677736-(32.85 if idx else 0),-.25+extra));b.Placement=d.getObject(name).getGlobalPlacement().multiply(b.Placement)
   row['fit'][species][name]={}
   for fixture in ['FinishedCarrier','eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','eye_primary_UpperCatch','eye_primary_UpperRail','eye_primary_SideLedge']:
    v=b.common(world(d.getObject(fixture))).Volume
    row['fit'][species][name][fixture]=v
 for name,sh in new.items():
  sh.translate(A.Vector(0,0,extra));assert sh.isValid()
  mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.02,AngularDeflection=.1,Relative=False);assert mesh.isSolid();mesh.write(str(O/(str(thickness)+'-'+name+'.stl')))
 report[str(thickness)]=row
(O/'fit.json').write_text(json.dumps(report,indent=2));print({k:max(v for a in row['fit'].values() for b in a.values() for v in b.values()) for k,row in report.items()})
