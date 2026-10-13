"""Verify separate STL units; do not package or rearrange their two shells."""
from pathlib import Path
import json,trimesh
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/rear-arm-r11';report={}
for key in json.loads((HERE/'settings.json').read_text())['variants']:
 name='R11'+key+'-carrier-and-holder.stl';m=trimesh.load_mesh(OUT/name);parts=m.split()
 assert m.is_watertight and m.is_winding_consistent and len(parts)==2,name
 report[key]={'filename':name,'watertight':True,'consistent_winding':True,'shells':2,'shell_volumes_mm3':[x.volume for x in parts]}
(OUT/'mesh-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('All five STLs have two watertight, consistently wound shells.')
