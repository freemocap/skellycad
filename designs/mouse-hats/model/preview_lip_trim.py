"""Proposed snip locations only; no baseline or assembly geometry is changed."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/model/lip-trim'
OUT.mkdir(parents=True,exist_ok=True)
path=ROOT/'generated/mouse-hats/reconstruction/main-carrier/01-tray-mount-candidate.FCStd'
source=next((d for d in App.listDocuments().values() if d.FileName and Path(d.FileName).resolve()==path.resolve()),None)
if source is None: source=App.openDocument(str(path))
# The 1 mm shoulder sits above the receiving baseplate, between Y=5 and Y=6.
# Proposed snips finish flush with the stem's two flat sides, parallel to its length.
low=-3.3315379403202114
high=3.2544620596798137
lip=source.MountSection02_0.Shape
tools=Part.makeBox(40,40,20,App.Vector(-10,-10,high)).fuse(
      Part.makeBox(40,40,20,App.Vector(-10,-10,low-20)))
removed=lip.common(tools)
removed.check(True)
assert len(removed.Solids)==2
section=source.PCBTrayAndMount.Shape.common(Part.makeBox(30,15,14,App.Vector(-10,0,-7)))
remaining=section.cut(removed)
remaining.check(True)
doc=App.newDocument('LipSnipProposal')
doc.Label='Lip corner trim — proposed material in red'
body=doc.addObject('Part::Feature','MountCloseup')
body.Label='Unchanged stem and remaining lip — inspection section'
body.Shape=remaining
body.ViewObject.ShapeColor=(0.2,0.75,0.9)
tips=doc.addObject('Part::Feature','ProposedSnips')
tips.Label='RED: proposed two lip corners to remove — confirm location'
tips.Shape=removed
tips.ViewObject.ShapeColor=(1.0,0.15,0.1)
for obj in (body,tips): obj.ViewObject.LineColor=(0.1,0.1,0.1)
doc.recompute()
Gui.Selection.clearSelection()
view=Gui.activeDocument().activeView()
view.setCameraOrientation(App.Rotation(App.Vector(1,0,0),90).Q)
view.fitAll()
doc.saveAs(str(OUT/'lip-snip-proposal.FCStd'))
view.saveImage(str(OUT/'proposal.png'),1000,750,'Current')
print('Proposed removal volume:',removed.Volume,'mm3; 2 corners. Source untouched.')
