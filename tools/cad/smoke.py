"""Verify native FreeCAD parameter editing and file round trips; not a product design."""
from pathlib import Path
import json
import FreeCAD as App
import Part
root = Path(__file__).resolve().parents[2]
out = root / "generated"
out.mkdir(exist_ok=True)
doc = App.newDocument("PlaygroundToolchainCheck")
box = doc.addObject("Part::Box", "TestBlock")
box.Length, box.Width, box.Height = 10, 6, 2
doc.recompute()
assert box.Shape.isValid() and abs(box.Shape.Volume - 120) < 1e-7
box.Length = 12
doc.recompute()
assert box.Shape.isValid() and abs(box.Shape.Volume - 144) < 1e-7
doc.saveAs(str(out / "toolchain-check.FCStd"))
Part.export([box], str(out / "toolchain-check.step"))
App.closeDocument(doc.Name)
doc = App.openDocument(str(out / "toolchain-check.FCStd"))
assert abs(doc.TestBlock.Length.Value - 12) < 1e-7
assert abs(doc.TestBlock.Shape.Volume - 144) < 1e-7
App.closeDocument(doc.Name)
shape = Part.read(str(out / "toolchain-check.step"))
assert shape.isValid() and abs(shape.Volume - 144) < 1e-7
(out / "smoke-check.json").write_text(json.dumps({"passed": True, "freecad": App.Version(), "checks": ["parameter change", "shape validity", "FCStd save/reopen", "STEP export/import"]}, indent=2))
print("CAD_SMOKE_OK")
