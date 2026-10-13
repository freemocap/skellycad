"""Independent native-file, edit, geometric-parity and seated-interface checks."""
from pathlib import Path
import json,runpy,sys
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/pcb-cap'
fresh=runpy.run_path(str(HERE/'build.py'))['main'](save=False)
fresh_volume=fresh.PCBCap.Shape.Volume;App.closeDocument(fresh.Name)
doc=App.openDocument(str(OUT/'01-pcb-cap-candidate.FCStd'))
for obj in doc.Objects:obj.touch()
doc.recompute()
r=doc.PCBCap.Shape.Solids[0].copy();r.check(True)
assert len(r.Solids)==1 and abs(r.Volume-fresh_volume)<1e-7
s=Part.read(str(OUT/'source.brep'));s.check(True)
missing=s.cut(r,0.001);excess=r.cut(s,0.001)
differences={}
for name,shape in [('missing',missing),('excess',excess)]:
    try:
        if shape.Solids:shape.check(True)
        differences[name]=dict(valid=True,volume_mm3=shape.Volume)
    except Exception as error:
        differences[name]=dict(valid=False,error=str(error),volume_mm3=None)
report=dict(units='mm',source='58 RightCap',source_volume_mm3=s.Volume,
    candidate_volume_mm3=r.Volume,source_faces=len(s.Faces),candidate_faces=len(r.Faces),
    boolean_differences=differences,full_boolean_parity=False,
    source_and_candidate_deeper_check='passed',boolean_fuzzy_tolerance_added_mm=0.001,
    edit_checks=[],physical_fit_validated=False)
distance=runpy.run_path(str(HERE.parent/'camera_holder/validate.py'))['distances']
report['source_to_candidate']=distance(s,r)
report['candidate_to_source']=distance(r,s)
common=s.common(r,0.001)
try:
    common.check(True)
    report['common_volume_mm3']=common.Volume
except Exception as error:report['common_check_error']=str(error)
for name,delta in [('CoverThickness',0.1),('VentRadius',0.1),('SideHoleRadius',0.1)]:
    old=getattr(doc.Dimensions,name).Value
    setattr(doc.Dimensions,name,old+delta);doc.recompute()
    edited=doc.PCBCap.Shape;edited.check(True)
    assert len(edited.Solids)==1 and abs(edited.Volume-r.Volume)>0.01
    occupied=edited.common(doc.HoleTools.Shape).Volume
    assert abs(occupied)<1e-7,'A hole failed to remain open'
    report['edit_checks'].append(dict(property=name,original_mm=old,tested_mm=old+delta,hole_tool_overlap_mm3=occupied))
    setattr(doc.Dimensions,name,old);doc.recompute()
doc.PCBCap.Shape.check(True)
assert abs(doc.PCBCap.Shape.Volume-r.Volume)<1e-7
sys.path.insert(0,str(HERE.parent/'main_carrier'))
sys.path.insert(0,str(HERE.parent/'baseplate'))
import carrier_features,baseplate_features
traydoc=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction/main-carrier/01-tray-mount-candidate.FCStd'))
basedoc=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction/baseplate/01-baseplate-candidate.FCStd'))
tray=traydoc.PCBTrayAndMount.Shape.copy();base=basedoc.Baseplate.Shape.copy()
base.check(True);tray.check(True)
original_tray=Part.read(str(ROOT/'generated/mouse-hats/inspection/carrier-source.brep'))
report['interface_tolerance_mm']=0.001
for label,a,b in [('source_cap_source_carrier',s,original_tray),('rebuilt_cap_rebuilt_tray',r,tray),('rebuilt_base_rebuilt_stem',base,tray)]:
    overlap=a.common(b,0.001)
    if overlap.Solids:overlap.check(True)
    report[label+'_overlap_mm3']=overlap.Volume
review=ROOT/'generated/mouse-hats/reconstruction/assembly'
review.mkdir(parents=True,exist_ok=True)
for name,shape in [('baseplate',base),('tray-stem',tray),('pcb-cap',r)]:shape.exportBrep(str(review/(name+'.brep')))
report['independent_rebuild_reopen_recompute_edit_restore']='passed'
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
