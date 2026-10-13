"""Run inside the pinned playground FreeCAD GUI. Dimensions are millimetres."""
from pathlib import Path
import json
import FreeCAD as App
import FreeCADGui as Gui

folder = Path(__file__).resolve().parent
assert not (folder / '01-cube.FCStd').exists(), 'Preserve existing checkpoint; use course replay.py.'
params = json.loads((folder / 'parameters.json').read_text())
assert params['units'] == 'mm'
assert 'WorkflowCube' not in App.listDocuments(), 'Checkpoint already open; edit its parameters instead.'
doc = App.newDocument('WorkflowCube')
cube = doc.addObject('Part::Box', 'Cube')
cube.Label = 'Cube (20 mm)'
cube.Length = params['length']
cube.Width = params['width']
cube.Height = params['height']
doc.recompute()
assert cube.Shape.isValid() and len(cube.Shape.Solids) == 1
assert abs(cube.Shape.Volume - 8000) < 1e-6
cube.ViewObject.ShapeColor = (0.25, 0.65, 0.85)
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(folder / '01-cube.FCStd'))
print('Checkpoint saved: valid single solid, 20 x 20 x 20 mm; volume 8000 mm^3.')
