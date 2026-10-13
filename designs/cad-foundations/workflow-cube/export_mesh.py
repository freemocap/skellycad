"""Export the reviewed cut from the live FreeCAD document, in millimetres."""
from pathlib import Path
import json
import hashlib
import FreeCAD as App
import MeshPart


def export_reviewed_cut():
    root = next(p for p in Path(__file__).resolve().parents if (p / 'tools/cad/toolchain.json').is_file())
    doc = App.getDocument('WorkflowCube')
    doc.recompute()
    part = doc.getObject('BlockWithHole')
    assert part is not None and part.Shape.isValid()
    assert len(part.Shape.Solids) == 1
    bounds = part.Shape.BoundBox
    dims = [bounds.XLength, bounds.YLength, bounds.ZLength]
    assert all(abs(a-b) < 1e-7 for a, b in zip(dims, [24, 20, 36])), 'Reconcile changed dimensions before export.'
    out = root / 'generated' / 'workflow-cube'
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'block-with-hole-mm.stl'
    # Absolute chordal deflection in mm; angular deflection in radians.
    mesh = MeshPart.meshFromShape(Shape=part.Shape, LinearDeflection=0.05,
                                  AngularDeflection=0.15, Relative=False)
    mesh.write(str(target))
    metadata = {
        'object': part.Name, 'source_document': doc.FileName,
        'units': 'mm (STL has no embedded units; import as mm)',
        'extents_mm': dims, 'linear_deflection_mm': 0.05,
        'angular_deflection_radians': 0.15,
        'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'triangles': mesh.CountFacets,
    }
    (out / 'export.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(str(target))
    print(json.dumps(metadata))


if __name__ == '__main__':
    export_reviewed_cut()
