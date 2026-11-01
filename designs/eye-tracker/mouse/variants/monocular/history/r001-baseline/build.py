"""Build the monocular mouse from shared camera/mount assets and species configuration."""
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(HERE.parent) not in sys.path:
    sys.path.insert(0, str(HERE.parent))
from shared.assembly import build_assembly
from shared.validation import compare_mouse_baseline

OUT = ROOT / 'generated/eye-tracker/mouse/shared-r01'
assembly = build_assembly(HERE / 'assembly.json', OUT)
doc = assembly.document
report = compare_mouse_baseline(assembly)
(OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print('MOUSE_SHARED_BUILD_OK', flush=True)
