"""Lower the complete R31 hardware 2 mm, retaining anatomy and source files."""
from pathlib import Path
import sys,json,hashlib,zipfile
import FreeCAD as A,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/compact-binocular-r32';O=R/'generated/eye-tracker/rat/compact-binocular-r32'
sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from replace_camera import world
m=json.loads((S.parent/'binocular-r31/review.json').read_text());p=R/m['native_checkpoint'];assert hashlib.sha256(p.read_bytes()).hexdigest()==m['native_sha256']
selected=json.loads((S.parent/'active-model.json').read_text());selected['observed_sha256']=hashlib.sha256((R/selected['native_checkpoint']).read_bytes()).hexdigest()
d=A.openDocument(str(p));before=world(d.Baseplate);shift=A.Placement(A.Vector(0,0,-2),A.Rotation());moved=[]
for o in d.Objects:
 if o.TypeId=='App::Part' or (hasattr(o,'Shape') and hasattr(o,'Placement') and o.getParentGeoFeatureGroup() is None):
  o.Placement=shift.multiply(o.Placement);moved.append(o.Name)
after=world(d.Baseplate);expected=before.copy();expected.translate(A.Vector(0,0,-2));assert after.cut(expected).Volume+expected.cut(after).Volume<1e-6
sk=d.RatDesignSkull.Mesh.copy();sk.Placement=d.RatDesignSkull.getGlobalPlacement();crossings={}
for name,s in [('before',before),('lowered',after)]:
 mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False);n=mesh.CountFacets;mesh.addMesh(sk);crossings[name]=sum((v[0]<n)!=(v[1]<n) for v in mesh.getSelfIntersections())
assert crossings['lowered']>0,'Expected intentional baseplate/skull overlap'
report={'source':m,'selected_species_manifest':selected,'units':'mm','hardware_translation_world_mm':[0,0,-2],'moved_objects':moved,'baseplate_surface_crossings':crossings,'skull_contact_policy':{'Baseplate':'boolean_cut_stock'},'anatomy_unchanged':True,'boolean_cut_performed':False}
(S/'lowering.json').write_text(json.dumps(report,indent=2));d.Label='Rat R32 - lowered starting assembly';d.recompute();p=O/'lowered.FCStd';d.saveAs(str(p))
with zipfile.ZipFile(p) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
A.closeDocument(d.Name);print('LOWERED_AND_SAVED',crossings)
