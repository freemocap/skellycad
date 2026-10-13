"""Run after lesson 2. Capture the user's resize, then add a dependent cut."""
from pathlib import Path
import json
import math
import FreeCAD as App
import FreeCADGui as Gui

folder = Path(__file__).resolve().parent
assert not (folder / '03-resized-block.FCStd').exists(), 'Preserve existing checkpoint; use course replay.py.'
assert not (folder / '04-centered-hole.FCStd').exists(), 'Preserve existing checkpoint; use course replay.py.'
p = json.loads((folder / '03-parameters.json').read_text())
assert p['units'] == 'mm'
doc = App.getDocument('WorkflowCube')
assert doc.getObject('HoleTool') is None, 'Hole already exists.'
cube = doc.getObject('Cube')
# Record the user's manual edit in the reproducible recipe.
cube.Length = p['length']
cube.Width = p['width']
cube.setExpression('Height', 'Length * ' + str(p['height_to_length_ratio']))
doc.recompute()
doc.saveAs(str(folder / '03-resized-block.FCStd'))

doc.openTransaction('Add centered through hole')
tool = doc.addObject('Part::Cylinder', 'HoleTool')
tool.Label = 'Hole tool (8 mm diameter)'
tool.Radius = p['hole_diameter'] / 2
extension = p['cut_extension_each_end']
tool.setExpression('Height', 'Cube.Height + ' + str(2 * extension) + ' mm')
tool.setExpression('Placement.Base.x', 'Cube.Length / 2')
tool.setExpression('Placement.Base.y', 'Cube.Width / 2')
tool.Placement.Base.z = -extension
cut = doc.addObject('Part::Cut', 'BlockWithHole')
cut.Label = 'Block with centered hole'
cut.Base = cube
cut.Tool = tool
doc.recompute()
assert cut.Shape.isValid() and len(cut.Shape.Solids) == 1
expected = cube.Shape.Volume - math.pi * tool.Radius.Value**2 * cube.Height.Value
assert abs(cut.Shape.Volume - expected) < 1e-5
cube.Visibility = False
tool.Visibility = False
cut.ViewObject.ShapeColor = (0.25, 0.65, 0.85)
Gui.Selection.clearSelection()
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
doc.commitTransaction()
doc.saveAs(str(folder / '04-centered-hole.FCStd'))
print('Saved valid single solid: 24 x 20 x 36 mm, centered 8 mm through hole.')
print('Volume mm^3:', cut.Shape.Volume)
