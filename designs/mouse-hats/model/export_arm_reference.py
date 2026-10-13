"""Export the current solid tray surface for mesh registration; pinned CAD Python."""
from pathlib import Path
import json,runpy
import FreeCAD as App
HERE=Path(__file__).resolve().parent
api=runpy.run_path(str(HERE/'build_mount.py'));api['load_modules']()
ROOT=api['ROOT'];OUT=ROOT/'generated/mouse-hats/arms'
OUT.mkdir(parents=True,exist_ok=True)
doc=App.openDocument(str(ROOT/'generated/mouse-hats/model/tray-cleanup/cleaned-tray.FCStd'))
vertices,faces=doc.CleanedTrayAndMount.Shape.tessellate(0.05)
(OUT/'tray-reference.json').write_text(json.dumps(dict(vertices=[list(v) for v in vertices],faces=faces)))
