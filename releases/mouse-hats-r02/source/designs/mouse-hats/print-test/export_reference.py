"""Export the unchanged holder tessellation for mesh pose analysis (pinned CAD Python)."""
from build import *
doc=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction/camera-holder/01-holder-candidate.FCStd'))
vertices,faces=doc.TrimHolderSide.Shape.tessellate(.03)
(OUT/'holder-reference-mesh.json').write_text(json.dumps({'vertices':[list(v) for v in vertices],'faces':faces}))
