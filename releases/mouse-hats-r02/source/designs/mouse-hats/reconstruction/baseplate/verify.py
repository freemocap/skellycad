"""Independent rebuild/reopen/edit, surface and mating-plane verification."""
from pathlib import Path
import json,sys,runpy,math
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/baseplate'
sys.path.insert(0,str(HERE))
import baseplate_features
fresh=runpy.run_path(str(HERE/'build.py'))['main'](save=False)
volume=fresh.Baseplate.Shape.Volume;App.closeDocument(fresh.Name)
doc=App.openDocument(str(OUT/'01-baseplate-candidate.FCStd'))
for obj in doc.Objects:obj.touch()
doc.recompute()
r=doc.Baseplate.Shape.copy();r.check(True)
assert len(r.Solids)==1 and abs(r.Volume-volume)<1e-7
s=Part.read(str(OUT/'source.brep'))
report=dict(units='mm',source='58 Baseplate (uncut)',source_volume_mm3=s.Volume,
    candidate_volume_mm3=r.Volume,volume_difference_mm3=r.Volume-s.Volume,
    source_faces=len(s.Faces),candidate_faces=len(r.Faces),solid_count=len(r.Solids),
    candidate_deeper_check='passed',full_boolean_parity=False,physical_fit_validated=False)
try:s.check(True);report['source_deeper_check']='passed'
except Exception as e:report['source_deeper_check']=str(e)
distance=runpy.run_path(str(HERE.parent/'camera_holder/validate.py'))['distances']
print('Sampling surfaces',flush=True)
report['source_to_candidate']=distance(s,r)
report['candidate_to_source']=distance(r,s)
sample_fn=runpy.run_path(str(HERE.parent/'camera_holder/validate.py'))['samples']
points,_=sample_fn(s)
selected=[points[round(i*(len(points)-1)/239)] for i in range(240)]
surface=Part.makeCompound(r.Faces)
outliers=[]
for p in selected:
    v=Part.Vertex(p);error=v.distToShape(surface)[0]
    if error>0.0001:
        outliers.append(dict(point_mm=list(p),deviation_mm=error,distance_to_source_face32_mm=v.distToShape(s.Faces[32])[0]))
report['sampled_outliers_above_0_0001_mm']=outliers
report['all_sampled_outliers_on_source_face32']=all(p['distance_to_source_face32_mm']<1e-7 for p in outliers)
report['source_face32_area_mm2']=s.Faces[32].Area
report['edit_checks']=[]
for name,delta in [('BoreRadius',0.1),('SkullStockDepth',0.5)]:
    old=getattr(doc.Baseplate,name).Value
    setattr(doc.Baseplate,name,old+delta);doc.recompute()
    edited=doc.Baseplate.Shape;edited.check(True)
    assert len(edited.Solids)==1 and abs(edited.Volume-r.Volume)>0.1
    report['edit_checks'].append(dict(property=name,original_mm=old,tested_mm=old+delta))
    setattr(doc.Baseplate,name,old);doc.recompute()
doc.Baseplate.Shape.check(True)
assert abs(doc.Baseplate.Shape.Volume-r.Volume)<1e-7
report['display_stage_checks']=[]
for stage in ['Stock','Outer body','Receiving pocket','Finished']:
    doc.Baseplate.DisplayStage=stage;doc.recompute();doc.Baseplate.Shape.check(True)
    assert len(doc.Baseplate.Shape.Solids)==1
    report['display_stage_checks'].append(stage)
assert abs(doc.Baseplate.Shape.Volume-r.Volume)<1e-7
stem=Part.read(str(ROOT/'generated/mouse-hats/inspection/carrier-source.brep'))
report['mating_planes']=[]
for base_index,stem_index in [(25,26),(26,77)]:
    f=s.Faces[base_index];n=f.normalAt(0,0);d=n.dot(f.CenterOfMass)
    matches=[g for g in r.Faces if isinstance(g.Surface,Part.Plane) and g.normalAt(0,0).dot(n)>1-1e-10 and abs(n.dot(g.CenterOfMass)-d)<1e-7]
    assert matches
    mate=stem.Faces[stem_index]
    offset=abs(n.dot(mate.CenterOfMass)-d)
    report['mating_planes'].append(dict(source_base_face_zero_based=base_index,
        source_stem_face_zero_based=stem_index,rebuilt_plane_preserved=True,
        stem_plane_offset_mm=offset,opposed_normal_dot=n.dot(mate.normalAt(0,0)),
        insertion_draft_degrees=math.degrees(math.asin(abs(n.y)))))
sys.path.insert(0,str(HERE.parent/'main_carrier'))
import carrier_features
tray=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction/main-carrier/01-tray-mount-candidate.FCStd'))
overlap=r.common(tray.PCBTrayAndMount.Shape,0.001)
report['seated_rebuilt_pair_interference_volume_mm3']=overlap.Volume
report['interface_boolean_tolerance_mm']=0.001
if overlap.Solids:overlap.check(True)
report['independent_rebuild_reopen_edit_restore']='passed'
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
