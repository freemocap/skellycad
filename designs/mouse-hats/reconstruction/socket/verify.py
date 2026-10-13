"""Run with pinned FreeCAD Python outside the GUI."""
from pathlib import Path
import json,runpy
import FreeCAD as App
import Part

HERE=Path(__file__).resolve().parent
WORKSPACE=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=WORKSPACE/'generated/mouse-hats/reconstruction/socket'
doc=App.openDocument(str(OUT/'01-socket-candidate.FCStd'))
source=Part.read(str(OUT/'source-local.brep'))
doc.recompute();shape=doc.UpperCollar.Shape.Solids[0];shape.check(True)
result=dict(source_volume_mm3=source.Volume,rebuilt_volume_mm3=shape.Volume,
            net_volume_difference_mm3=shape.Volume-source.Volume,
            source_faces=len(source.Faces),rebuilt_faces=len(shape.Faces),rebuilt_bop_check='passed',
            boolean_parity=False)
try:source.check(True);result['source_bop_check']='passed'
except Exception as error:result['source_bop_check']=str(error)
distance=runpy.run_path(str(HERE.parent/'camera_holder/validate.py'))['distances']
print('Checking sampled surfaces',flush=True)
result['source_to_rebuilt']=distance(source,shape)
result['rebuilt_to_source']=distance(shape,source)
result['edit_checks']=[]
for name,delta in [('CollarHeight',0.2),('CollarRadius',0.1),('BoreRadius',0.05)]:
    old=getattr(doc.Dimensions,name).Value
    setattr(doc.Dimensions,name,old+delta);doc.recompute()
    doc.UpperCollar.Shape.check(True)
    assert len(doc.UpperCollar.Shape.Solids)==1
    setattr(doc.Dimensions,name,old);doc.recompute();doc.UpperCollar.Shape.check(True)
    result['edit_checks'].append(dict(property=name,original_mm=old,tested_mm=old+delta))
result['standalone_reopen_edit_passed']=True
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
