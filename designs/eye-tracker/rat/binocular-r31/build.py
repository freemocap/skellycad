"""Rebuild R31 sequentially using the pinned FreeCAD Python executable."""
from pathlib import Path
import subprocess,sys
here=Path(__file__).resolve().parent
for script in ['audit_baseline.py','place.py','central.py','ribbons.py','arms.py','validate.py']:
 subprocess.run([sys.executable,str(here/script)],check=True,cwd=here.parents[3])
print('Native build complete. Run check_eyes.py with the tooling Python, then render.py with this runtime.')
