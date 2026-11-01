"""Validate and export the finished carrier with its matched print parts."""
from pathlib import Path
import json,hashlib
import FreeCAD as A,Part,MeshPart
ROOT=Path.cwd();OUT=ROOT/'generated/eye-tracker/mouse/seated-tip-r07';PRINT=OUT/'print';PRINT.mkdir(exist_ok=True)
d=A.openDocument(str(ROOT/'generated/eye-tracker/mouse/restored-arms-r05/mouse-restored-arms-r05.FCStd'))
shape=Part.Shape();shape.read(str(OUT/'finished.brep'));shape.check(True);assert shape.isValid() and len(shape.Solids)==1
original=d.getObject('StemSupportedCarrier').Shape;added=shape.cut(original);rows={}
for name in ['RibbonCandidate','eye_primary_Holder','eye_primary_Clip','eye_primary_Cap','skull_mount_Baseplate']:
 other=d.getObject(name).Shape;rows[name]={'added_overlap_mm3':added.common(other).Volume,'carrier_overlap_mm3':shape.common(other).Volume,'carrier_clearance_mm':shape.distToShape(other)[0]};print(name,rows[name],flush=True)
assert all(x['added_overlap_mm3']<1e-6 for x in rows.values())
assert rows['RibbonCandidate']['carrier_overlap_mm3']<1e-6 and rows['eye_primary_Holder']['carrier_overlap_mm3']<1e-6
ob=d.addObject('Part::Feature','FinishedCarrier');ob.Label='Finished carrier R07 - fused and blended';ob.Shape=shape
# Preserve the accepted bore through the stationary socket stem.
s=json.loads((ROOT/'designs/mouse-hats/b-flared-loop-r07/settings.json').read_text());n=A.Vector(*s['rear_data']['socket_axis']);c=A.Vector(*s['rear_data']['socket_center_mm'])+A.Vector(*s['joint_shift_mm']);bore=Part.makeCylinder(1.45,8,c+n*2.4,n);bore_overlap=added.common(bore).Volume;assert bore_overlap<1e-6
parts={'carrier-and-holder':Part.makeCompound([shape,d.getObject('eye_primary_Holder').Shape]),'matching-cap':d.getObject('eye_primary_Cap').Shape,'camera-clip':d.getObject('eye_primary_Clip').Shape,'baseplate':d.getObject('skull_mount_Baseplate').Shape}
exports={}
for name,sh in parts.items():
 mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.03,AngularDeflection=.12,Relative=False);path=PRINT/(name+'.stl');mesh.write(str(path));exports[name]={'file':path.name,'closed':mesh.isSolid(),'self_intersections':mesh.hasSelfIntersections(),'facets':mesh.CountFacets,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()};assert exports[name]['closed'] and not exports[name]['self_intersections'];print(name,exports[name],flush=True)
d.recompute();path=OUT/'mouse-seated-tip-r07.FCStd';d.saveAs(str(path));d.Label='Mouse R07 - finished arm junctions';d.save()
report={'revision':'ET-MOUSE-MONO-STEM-R07-print-test','units':'mm','carrier_valid':shape.isValid(),'carrier_solids':len(shape.Solids),'detailed_bop_check_pass':True,'checks':rows,'added_stem_bore_overlap_mm3':bore_overlap,'junction_finishing':json.loads((OUT/'fillets.json').read_text()),'native_file':path.name,'native_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'print_exports':exports,'status':'Geometry checked print-test candidate; physical strength and adjustment require testing.'}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));(PRINT/'manifest.json').write_text(json.dumps(report,indent=2))

