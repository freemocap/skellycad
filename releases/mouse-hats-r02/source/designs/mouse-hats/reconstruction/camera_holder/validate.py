"""Surface-sample comparison; original STEP has BOP errors, so Boolean parity is not claimed."""
from pathlib import Path
import json,math
import FreeCAD as App
import FreeCADGui as Gui
import Part

HERE=Path(__file__).resolve().parent
WORKSPACE=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=WORKSPACE/'generated/mouse-hats/reconstruction/camera-holder'


def samples(shape):
    points=[]
    failed_edges=0
    for face in shape.Faces:
        verts,tris=face.tessellate(0.03)
        points.extend(verts)
        for a,b,c in tris:
            center=(verts[a]+verts[b]+verts[c])/3
            # Project triangle centers back onto their CAD face's supporting surface.
            try:
                u,v=face.Surface.parameter(center)
                points.append(face.valueAt(u,v))
            except Exception:
                pass
    for edge in shape.Edges:
        try:
            points.extend(edge.discretize(Number=9))
        except Exception:
            failed_edges+=1
            points.extend(v.Point for v in edge.Vertexes)
    unique={tuple(round(c,7) for c in point):point for point in points}
    return list(unique.values()),failed_edges


def distances(source,target):
    # Compare to faces, not solid interiors (which would falsely report zero).
    surface=Part.makeCompound(target.Faces)
    points,failed_edges=samples(source)
    # Bound the expensive CAD distance queries; retain total candidate count.
    candidate_count=len(points)
    if len(points)>240:
        points=[points[round(i*(len(points)-1)/239)] for i in range(240)]
    values=[Part.Vertex(point).distToShape(surface)[0] for point in points]
    return dict(samples=len(values),candidate_samples=candidate_count,edge_discretization_failures=failed_edges,
                max_mm=max(values),rms_mm=math.sqrt(sum(v*v for v in values)/len(values)))


def main(source):
    OUT.mkdir(parents=True,exist_ok=True)
    doc=App.getDocument('CameraHolderRebuild58')
    rebuilt=doc.TrimHolderSide.Shape.Solids[0]
    rebuilt.check(True)
    try:
        source.check(True); source_check='passed'
    except Exception as error:
        source_check=str(error)
    report=dict(source_volume_mm3=source.Volume,rebuilt_volume_mm3=rebuilt.Volume,
                net_volume_difference_mm3=rebuilt.Volume-source.Volume,
                source_faces=len(source.Faces),rebuilt_faces=len(rebuilt.Faces),
                source_bop_check=source_check,rebuilt_bop_check='passed',
                boolean_parity='not established: source BOP failures make differences unreliable')
    report['source_to_rebuilt']=distances(source,rebuilt)
    report['rebuilt_to_source']=distances(rebuilt,source)
    old=doc.Dimensions.PlateThickness.Value
    originalheight=rebuilt.BoundBox.ZLength
    doc.Dimensions.PlateThickness=old+0.1;doc.recompute()
    changed=doc.TrimHolderSide.Shape
    changed.check(True)
    assert abs(changed.BoundBox.ZLength-originalheight-0.1)<1e-5
    doc.Dimensions.PlateThickness=old;doc.recompute()
    doc.TrimHolderSide.Shape.check(True)
    report['plate_thickness_edit_mm']=[old,old+0.1,old]
    ref=doc.addObject('Part::Feature','SourceReference')
    ref.Label='58 holder reference - display offset 14 mm'
    ref.Shape=source
    ref.Placement.Base.x+=14
    ref.ViewObject.ShapeColor=(0.85,0.65,0.25)
    doc.Label='Camera holder - native reconstruction candidate'
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    doc.recompute()
    doc.saveAs(str(OUT/'01-holder-candidate.FCStd'))
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    source.exportBrep(str(OUT/'source-local.brep'))
    print(json.dumps(report,indent=2))
    return report
