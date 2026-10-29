from pathlib import Path
import json,hashlib,zipfile,sys
import FreeCAD as A
R=Path.cwd(); S=R/'designs/eye-tracker/rat/binocular-r31'; O=R/'generated/eye-tracker/rat/binocular-r31'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'))
from replace_camera import world
records={}
for label,path in [('selected','designs/eye-tracker/rat/active-model.json'),('source','designs/eye-tracker/rat/separated-arms-r30/review.json')]:
 m=json.loads((R/path).read_text()); p=R/m['native_checkpoint']; m['observed_sha256']=hashlib.sha256(p.read_bytes()).hexdigest(); m['hash_matches']=m['observed_sha256']==m['native_sha256']; assert m['hash_matches'] or label=='selected'
 with zipfile.ZipFile(p) as z: assert z.testzip() is None and 'Document.xml' in z.namelist()
 records[label]=m
sys.path.insert(0,str(R/'designs/eye-tracker'))
from shared.camera import selected_model
records['camera']=selected_model();records['units']='mm';records['constraints']={'cap':'deferred','configuration':'binocular','baseplate':'preserve R30 mating interface and anatomy placement','camera_handedness':'proper rotations only; no reflected physical camera geometry','supports':'retain R30 separated protective arm style','ribbon':'32.85 mm neutral length, 4 mm width; retain detailed model thickness and minimum bend limits','physical_fit_verified':False}
(S/'baseline.json').write_text(json.dumps(records,indent=2))
d=A.openDocument(str(R/records['source']['native_checkpoint']))
M=A.Placement(A.Matrix(*sum(json.loads((R/'designs/eye-tracker/rat/oval-camera-r21/solution.json').read_text())['mount_to_skull'],[])))
report={}
for o in d.Objects:
 if hasattr(o,'getGlobalPlacement') and hasattr(o,'Shape') and not o.Shape.isNull():
  s=world(o).transformed(M.inverse().toMatrix());b=s.BoundBox
  report[o.Name]={'bounds':[b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax],'volume':s.Volume,'solids':len(s.Solids),'pose':list(o.getGlobalPlacement().toMatrix().A)}
 elif hasattr(o,'Mesh'):report[o.Name]={'mesh_facets':o.Mesh.CountFacets,'pose':list(o.getGlobalPlacement().toMatrix().A)}
(O/'inventory.json').write_text(json.dumps(report,indent=2));A.closeDocument(d.Name)
print(json.dumps({n:report[n] for n in ['PCB','RetainedPCBTray','skull_mount_Baseplate','FinishedCarrier','RibbonCandidate','camera_pcb','RightEyeSclera','LeftEyeSclera'] if n in report},indent=2));print('BASELINE_VERIFIED')


