"""Export only needed embedded Antmicro footprints with KiCad's bundled Python.

Source: [@antmicroOv9281Board; @antmicroOv9281License]. Existing files are kept.
"""
from pathlib import Path
import re
import sys
import pcbnew

root = Path(__file__).resolve().parent
out = Path(sys.argv[1]).resolve()
needed = set(re.findall(r'\(property "Footprint" "Camera:([^"]+)"',
                       (out/'camera.kicad_sch').read_text(encoding='utf-8')))
board = pcbnew.LoadBoard(str(root/'reference/antmicro/ov9281-dual-camera-board.kicad_pcb'))
for fp in board.GetFootprints():
    name = str(fp.GetFPID().GetLibItemName())
    target = out/'Camera.pretty'/f'{name}.kicad_mod'
    if name in needed and not target.exists():
        pcbnew.FootprintSave(str(target.parent), fp)
print('Required embedded footprints exported; existing local files preserved.')
