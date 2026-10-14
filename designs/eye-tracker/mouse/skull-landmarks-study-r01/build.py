from pathlib import Path
import json,hashlib
import FreeCAD as App,Mesh,Part
ROOT=Path.cwd();ST=ROOT/'designs/eye-tracker/mouse/skull-landmarks-study-r01';OUT=ROOT/'generated/eye-tracker/mouse/skull-landmarks-study-r01'
r=json.loads((ST/'validation.json').read_text());assert hashlib.sha256((ROOT/r['existing_skull_path']).read_bytes()).hexdigest()==r['existing_skull_sha256']
d=App.newDocument('MouseSkullLandmarksStudyR01');d.Label='Mouse skull landmarks — exploratory R01'
base=d.addObject('App::Part','ExistingSkullStudy');base.Label='Existing skull + tentative transferred landmarks'
m=d.addObject('Mesh::Feature','ExistingSkull');m.Mesh=Mesh.Mesh(str(ROOT/r['existing_skull_path']));base.addObject(m)
m.addProperty('App::PropertyString','SourceSha256','Provenance');m.SourceSha256=r['existing_skull_sha256']
atlas=d.addObject('App::Part','AtlasComparison');atlas.Label='Atlas comparison — registered, 30k triangles'
a=d.addObject('Mesh::Feature','AtlasSkull');a.Mesh=Mesh.Mesh(str(OUT/'atlas-skull-registered.stl'));atlas.addObject(a)
a.addProperty('App::PropertyString','AnatomicalStatus','Provenance');a.AnatomicalStatus='Population template segmentation; exploratory similarity alignment; not target landmark validated'
g=d.addObject('App::DocumentObjectGroup','TransferredLandmarks');base.addObject(g)
points=json.loads((ST/'landmarks.json').read_text())['landmarks']
for row in points:
 o=d.addObject('Part::Feature',row['id']);o.Label=row['id']+' — '+row['name'];p=App.Vector(*row['transferred_assembly_mm']);o.Shape=Part.Vertex(p);g.addObject(o)
 for name,value in [('AnatomicalName',row['name']),('NameStatus',row['name_status']),('RegistrationStatus',row['status']),('SourceLandmarkId',row['source_label'])]:o.addProperty('App::PropertyString',name,'Landmark');setattr(o,name,value)
 o.addProperty('App::PropertyVector','PositionMM','Landmark');o.PositionMM=p
 o.addProperty('App::PropertyVector','AtlasLPSMM','Landmark');o.AtlasLPSMM=App.Vector(*row['atlas_lps_mm'])
 o.addProperty('App::PropertyLength','NearestSurfaceDistance','Landmark');o.NearestSurfaceDistance=row['surface_distance_mm']
 o.addProperty('App::PropertyBool','ExportForPrinting','Landmark');o.ExportForPrinting=False
# Read-only source reference, offset nowhere: hidden by review macro to avoid duplicate surfaces.
a.addProperty('App::PropertyFloat','RegistrationUniformScale','Provenance');a.RegistrationUniformScale=r['uniform_scale']
d.recompute();path=OUT/'ET-MOUSE-SKULL-LANDMARKS-STUDY-R01.FCStd';d.saveAs(str(path));App.closeDocument(d.Name)
d=App.openDocument(str(path));assert len(d.getObject('TransferredLandmarks').Group)==45
for row in points:assert (d.getObject(row['id']).Shape.Vertexes[0].Point-App.Vector(*row['transferred_assembly_mm'])).Length<1e-10
assert d.ExistingSkull.Mesh.CountFacets==r['existing_faces'];App.closeDocument(d.Name)
(ST/'checkpoints').mkdir(exist_ok=True);import shutil;dest=ST/'checkpoints'/path.name;shutil.copy2(path,dest)
(ST/'native-validation.json').write_text(json.dumps({'native':str(dest.relative_to(ROOT)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'reopen_passed':True,'landmark_count':45,'existing_skull_facets_preserved':True,'landmark_coordinate_max_tolerance_mm':1e-10},indent=2));print(dest)
