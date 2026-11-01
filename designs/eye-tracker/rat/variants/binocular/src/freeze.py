"""Freeze the GUI-saved review after checking its geometry against validation."""
from support import *
import hashlib,shutil
m=json.loads((S/'review.json').read_text());target=R/m['native_checkpoint'];review=O/'RAT-R43-current-complete-review.FCStd'
assert json.loads((O/'validation.json').read_text())['passed']
assert json.loads((O/'containment.json').read_text())['passed']
a=A.openDocument(str(target));b=A.openDocument(str(review));checked=[]
for x in a.Objects:
 y=b.getObject(x.Name);assert y is not None
 if hasattr(x,'getGlobalPlacement'):
  assert np.allclose(x.getGlobalPlacement().toMatrix().A,y.getGlobalPlacement().toMatrix().A,atol=1e-12,rtol=0),x.Name
 if hasattr(x,'Shape'):
  u=x.Shape;v=y.Shape;assert u.isNull()==v.isNull()
  if not u.isNull():
   assert [len(u.Faces),len(u.Edges),len(u.Vertexes),len(u.Solids)]==[len(v.Faces),len(v.Edges),len(v.Vertexes),len(v.Solids)],x.Name
   assert abs(u.Volume-v.Volume)<1e-7 and abs(u.Area-v.Area)<1e-7,x.Name
   assert np.allclose([list(q.Point) for q in u.Vertexes],[list(q.Point) for q in v.Vertexes],atol=1e-9,rtol=0),x.Name
 if hasattr(x,'Mesh'):assert x.Mesh.Topology==y.Mesh.Topology,x.Name
 for key in ['Origin','Direction','SensorCenter']:
  if key in x.PropertiesList and hasattr(getattr(x,key),'x'):assert np.allclose(list(getattr(x,key)),list(getattr(y,key)),atol=1e-12,rtol=0),(x.Name,key)
 checked.append(x.Name)
A.closeDocument(a.Name);A.closeDocument(b.Name)
with zipfile.ZipFile(review) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
shutil.copy2(review,target);m['native_sha256']=hashlib.sha256(target.read_bytes()).hexdigest();m['frozen_after_gui_save']=True;(S/'review.json').write_text(json.dumps(m,indent=2));(O/'freeze-audit.json').write_text(json.dumps({'passed':True,'checked_objects':checked,'native_sha256':m['native_sha256'],'geometry_and_placements_match_validated_document':True},indent=2));print('GUI review frozen; geometry unchanged:',len(checked),'objects')
