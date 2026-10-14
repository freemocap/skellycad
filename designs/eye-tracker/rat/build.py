"""Build Monocular rat with shared, unchanged mouse hardware in FreeCAD GUI Python."""
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
from shared.assembly import build_assembly

OUT = ROOT / 'generated/eye-tracker/rat/monocular-r01'
assembly = build_assembly(HERE / 'assembly.json', OUT)
doc = assembly.document
print('MONOCULAR_RAT_BUILD_OK', flush=True)
