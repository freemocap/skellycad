"""Lesson 2: run after build.py, or with checkpoint 01 open in FreeCAD."""
from pathlib import Path
import json
import FreeCAD as App
import FreeCADGui as Gui

folder = Path(__file__).resolve().parent
assert not (folder / '02-linked-height.FCStd').exists(), 'Preserve existing checkpoint; use course replay.py.'
params = json.loads((folder / '02-parameters.json').read_text())
doc = App.getDocument('WorkflowCube')
cube = doc.getObject('Cube')
assert params['units'] == 'mm'
assert all(abs(v.Value - 20) < 1e-7 for v in (cube.Length, cube.Width, cube.Height)), 'Start from checkpoint 01.'
doc.openTransaction('Link height to length')
cube.setExpression('Height', 'Length * ' + str(params['height_to_length_ratio']))
cube.Label = 'Parametric block'
doc.recompute()
assert cube.Shape.isValid() and len(cube.Shape.Solids) == 1
assert abs(cube.Height.Value - 30) < 1e-7
assert abs(cube.Shape.Volume - 12000) < 1e-6
doc.commitTransaction()
Gui.Selection.clearSelection()
Gui.Selection.addSelection(cube)
Gui.activeDocument().activeView().fitAll()
doc.saveAs(str(folder / '02-linked-height.FCStd'))
print('Saved 20 x 20 x 30 mm solid. Height expression:', cube.ExpressionEngine)
