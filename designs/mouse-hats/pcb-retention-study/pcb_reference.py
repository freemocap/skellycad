"""Common fit-derived PCB reference for current retention studies (mm)."""
from pathlib import Path
import json
import FreeCAD as A
import Part
PARAMETERS=json.loads(Path(__file__).with_name('pcb-reference.json').read_text())
def board_shape():
 p=PARAMETERS
 return Part.makeBox(p['board_thickness_mm'],p['board_width_mm'],p['board_length_mm'],A.Vector(*p['board_underside_origin_mm']))
