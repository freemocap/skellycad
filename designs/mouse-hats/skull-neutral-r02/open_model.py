"""Load feature dependencies before opening the R02 candidate."""
from pathlib import Path
import sys
import FreeCAD as App
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
HERE=Path(__file__).parent
for p in [HERE,HERE.parent/'model',HERE.parent/'rear-arm-r11']:sys.path.insert(0,str(p))
import neutral_r02_features
doc=App.openDocument(str(ROOT/'generated/mouse-hats/skull-neutral-r02/ribbon-space-study.FCStd'))
