"""Pin R11B reference and check dimension ownership without touching active CAD."""
from pathlib import Path
import hashlib,json,shutil
from upper_edge import UpperEdge
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/pcb-retention-study/r11b-datum-preflight';OUT.mkdir(parents=True,exist_ok=True)
selection=json.loads((HERE.parent/'rear-arm-r11/selection.json').read_text())
assert selection['selected_option']=='R11B'
src=ROOT/'generated/mouse-hats/rear-arm-r11/r11b-assembly.FCStd'
digest=hashlib.sha256(src.read_bytes()).hexdigest();dest=OUT/'r11b-assembly-frozen.FCStd'
if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
else:shutil.copy2(src,dest)
manifest={'selected_option':'R11B','source':src.relative_to(ROOT).as_posix(),'snapshot':dest.relative_to(ROOT).as_posix(),'sha256':digest,'purpose':'new baseline for upper-edge work; older R06 study preserved as history'}
(HERE/'r11b-reference-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
rows=[];zero=UpperEdge().datums()
for offset in [0,.5,1.0]:
 d=UpperEdge(tray_upper_edge_offset_mm=offset).datums()
 for k in ['pcb_upper_y_mm','catch_inner_tip_y_mm','catch_underside_x_mm','board_lift_clearance_mm']:assert d[k]==zero[k],k
 assert abs(d['tray_upper_y_mm']-zero['tray_upper_y_mm']-offset)<1e-10
 assert abs(d['cap_inner_wall_y_mm']-zero['cap_inner_wall_y_mm']-offset)<1e-10
 rows.append({'offset_mm':offset,**d})
report={'datum_arithmetic_checks_pass':True,'geometry_rebuild_implemented':False,'board_pose_verified':False,'rows':rows}
(OUT/'datum-preflight.json').write_text(json.dumps(report,indent=2)+'\n')
assert hashlib.sha256(src.read_bytes()).hexdigest()==digest
print(json.dumps(report,indent=2))
