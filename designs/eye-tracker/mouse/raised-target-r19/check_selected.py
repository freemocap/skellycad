from pathlib import Path
import sys
import FreeCAD as A,Part,Mesh
R=Path.cwd();sys.path.insert(0,str(R/'designs/eye-tracker'));from shared.model import open_selected
from shared.validation import validate_selected
m,d=open_selected(R/'designs/eye-tracker/mouse/raised-target-r19/review.json');validate_selected(d,m);print('SELECTED LOADER + MATCHED PART VALIDATION PASS')
