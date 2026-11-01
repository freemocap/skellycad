from pathlib import Path
import sys
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'))
from refine import refine
refine(R/'generated/eye-tracker/rat/targeted-r02')
