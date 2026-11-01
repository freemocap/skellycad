from pathlib import Path
import json,numpy as np
import FreeCAD as A,Part
R=Path.cwd();S=R/'designs/eye-tracker/rat/eye-world-top-joint-r04';O=R/'generated/eye-tracker/rat/eye-world-top-joint-r04';cfg=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());T=np.array(cfg['mount_to_skull']);H=np.array(json.loads((S/'selected-pose.json').read_text())['head_world']);m=json.loads((S.parent/'lowered-cameras-r43/review.json').read_text());d=A.openDocument(str(R/m['native_checkpoint']));obj=d.Lefteye_primary_Clip;clip=obj.Shape.copy();clip.Placement=obj.getGlobalPlacement();D=H@np.linalg.inv(T@np.array(cfg['sides']['Left']['head']));clip=clip.transformed(A.Matrix(*D.ravel().tolist()));clip.exportBrep(str(O/'world-clip.brep'));A.closeDocument(d.Name)
def read(n):
 s=Part.Shape();s.read(str(O/(n+'.brep')));return s
report={}
for n in ['finished-carrier','finished-holder','Ribbon','camera_pcb','M4_lens','IR_LED','IR_LED_001']:
 v=clip.common(read(n)).Volume;report['clip/'+n]=v;assert v<(.008 if n=='finished-holder' else 1e-5),(n,v)
holder=read('finished-holder')
for n in ['camera_pcb','M4_lens','IR_LED','IR_LED_001']:
 v=holder.common(read(n)).Volume;report['holder/'+n]=v;assert v<(1.91319 if n=='M4_lens' else 1e-5),(n,v)
(O/'fixture-validation.json').write_text(json.dumps(report,indent=2));print(report)
