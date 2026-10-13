"""Bounded verification in a separate pinned-runtime process, without GUI dispatch."""
from pathlib import Path
import json, runpy
import FreeCAD as App

HERE=Path(__file__).resolve().parent
WORKSPACE=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=WORKSPACE/'generated/mouse-hats/reconstruction/camera-holder'
OUT.mkdir(parents=True,exist_ok=True)
parameters=json.loads((HERE/'parameters.json').read_text())
reference=App.openDocument(str(WORKSPACE/'generated/mouse-hats/inspection/58-reference.FCStd'))
source=reference.getObject('Part__Feature002').Shape.copy()
frame=parameters['assembly_to_holder_frame']
source.Placement=App.Placement(App.Vector(*frame['translation_mm']),App.Rotation(*frame['quaternion_xyzw']))
print('Building independent reconstruction',flush=True)
doc=runpy.run_path(str(HERE/'build.py'))['main']()
shape=doc.TrimHolderSide.Shape.Solids[0]
shape.check(True)
report=dict(source_volume_mm3=source.Volume,rebuilt_volume_mm3=shape.Volume,
            net_volume_difference_mm3=shape.Volume-source.Volume,
            source_faces=len(source.Faces),rebuilt_faces=len(shape.Faces),
            rebuilt_bop_check='passed',boolean_parity=False)
try:source.check(True);report['source_bop_check']='passed'
except Exception as error:report['source_bop_check']=str(error)
distance=runpy.run_path(str(HERE/'validate.py'))['distances']
print('Sampling source to reconstruction',flush=True)
report['source_to_rebuilt']=distance(source,shape)
print(report['source_to_rebuilt'],flush=True)
print('Sampling reconstruction to source',flush=True)
report['rebuilt_to_source']=distance(shape,source)
print(report['rebuilt_to_source'],flush=True)
old=doc.Dimensions.PlateThickness.Value
height=shape.BoundBox.ZLength
doc.Dimensions.PlateThickness=old+0.1;doc.recompute()
doc.TrimHolderSide.Shape.check(True)
assert abs(doc.TrimHolderSide.Shape.BoundBox.ZLength-height-0.1)<1e-5
doc.Dimensions.PlateThickness=old;doc.recompute()
report['plate_thickness_edit_mm']=[old,old+0.1,old]
doc.saveAs(str(OUT/'holder-checked.FCStd'))
App.closeDocument(doc.Name)
reopened=App.openDocument(str(OUT/'holder-checked.FCStd'))
reopened.recompute();reopened.TrimHolderSide.Shape.check(True)
reopened.Dimensions.PlateThickness=old+0.1;reopened.recompute()
reopened.TrimHolderSide.Shape.check(True)
assert abs(reopened.TrimHolderSide.Shape.BoundBox.ZLength-height-0.1)<1e-5
report['standalone_reopen_edit_passed']=True
(OUT/'independent-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Independent verification complete',flush=True)
