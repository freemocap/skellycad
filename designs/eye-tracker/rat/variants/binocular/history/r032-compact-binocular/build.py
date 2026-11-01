"""Run the R32 native stages in order using pinned FreeCAD Python."""
from pathlib import Path
import subprocess,sys
here=Path(__file__).resolve().parent
for script in ['lower.py','central.py','aim.py','ribbons.py','arms.py','validate.py','compare.py']:
 subprocess.run([sys.executable,str(here/script)],cwd=here.parents[3],check=True)
print('Run check_eyes.py with the tooling Python before review or export.')
