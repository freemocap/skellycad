"""Rebuild 58 Body44 from its measured axial profile and a parameterized collar."""
from pathlib import Path
import json
import FreeCAD as App
import FreeCADGui as Gui
import Part,Sketcher

HERE=Path(__file__).resolve().parent
WORKSPACE=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=WORKSPACE/'generated/mouse-hats/reconstruction/socket'


def main(source):
    assert 'SocketRebuild58' not in App.listDocuments()
    p=json.loads((HERE/'parameters.json').read_text())
    doc=App.newDocument('SocketRebuild58')
    body=doc.addObject('PartDesign::Body','Socket')
    dims=doc.addObject('App::FeaturePython','Dimensions')
    for name,value in [('CollarHeight',p['collar_height_mm']),('BoreRadius',p['bore_radius_mm']),
                       ('CollarRadius',p['collar_radius_mm'])]:
        dims.addProperty('App::PropertyLength',name,'Dimensions');setattr(dims,name,value)
    bottom=source.common(Part.makeBox(30,30,22.4,App.Vector(-15,-15,-20)))
    section=bottom.section(Part.makePlane(30,30,App.Vector(-15,0,-15),App.Vector(0,1,0)))
    edges=[e for e in section.Edges if e.CenterOfMass.x>0]
    wires=Part.sortEdges(edges)
    assert len(wires)==1 and Part.Wire(wires[0]).isClosed()
    sketch=body.newObject('Sketcher::SketchObject','MeasuredSocketProfile')
    rotation=App.Rotation(App.Vector(1,0,0),90)
    for edge in wires[0]:
        edge=edge.copy();edge.Placement=App.Placement(App.Vector(),rotation.inverted()).multiply(edge.Placement)
        c=edge.Curve
        if isinstance(c,Part.Line):
            geometry=Part.LineSegment(edge.Vertexes[0].Point,edge.Vertexes[-1].Point)
        elif isinstance(c,Part.Circle):
            geometry=Part.ArcOfCircle(c,edge.FirstParameter,edge.LastParameter)
        else:
            # Sectioning the imported surface yields dense degree-1 polylines.
            # Fit a smooth cubic rather than revolve their hundreds of C0 knots.
            geometry=Part.BSplineCurve()
            geometry.approximate(Points=edge.discretize(Number=201),DegMin=3,DegMax=3,Tolerance=1e-5)
        index=sketch.addGeometry(geometry,False)
        sketch.addConstraint(Sketcher.Constraint('Block',index))
    # STEP tolerances bridge a 0.000065 mm gap which Sketcher correctly rejects.
    # Preserve both measured endpoints and explicitly connect small open gaps.
    endpoints=[(i,j,sketch.getPoint(i,j)) for i in range(sketch.GeometryCount) for j in (1,2)]
    connected=set()
    for i,j,point in endpoints:
        others=[(point.distanceToPoint(q),k,l,q) for k,l,q in endpoints if k!=i]
        distance,k,l,q=min(others,key=lambda item:item[0])
        key=tuple(sorted([(i,j),(k,l)]))
        if distance>1e-7 and key not in connected:
            assert distance<0.001, 'Unexpected open section gap'
            idx=sketch.addGeometry(Part.LineSegment(point,q),False)
            sketch.addConstraint(Sketcher.Constraint('Block',idx))
            connected.add(key)
    sketch.Placement.Rotation=rotation
    doc.recompute()
    bowl=body.newObject('PartDesign::Revolution','SocketBowl')
    bowl.Profile=sketch;bowl.ReferenceAxis=(sketch,['V_Axis']);bowl.Angle=360;bowl.Refine=True
    doc.recompute()
    assert bowl.Shape.isValid() and len(bowl.Shape.Solids)==1
    ring=body.newObject('Sketcher::SketchObject','CollarProfile')
    ring.Placement.Base.z=p['collar_base_z_mm']
    for radius,name in [(p['collar_radius_mm'],'CollarRadius'),(p['bore_radius_mm'],'BoreRadius')]:
        i=ring.addGeometry(Part.Circle(App.Vector(),App.Vector(0,0,1),radius),False)
        ring.addConstraint(Sketcher.Constraint('Coincident',i,3,-1,1))
        c=ring.addConstraint(Sketcher.Constraint('Radius',i,radius))
        ring.setExpression('Constraints['+str(c)+']','Dimensions.'+name)
    doc.recompute()
    collar=body.newObject('PartDesign::Pad','UpperCollar')
    collar.Profile=ring;collar.setExpression('Length','Dimensions.CollarHeight');collar.Refine=True
    doc.recompute()
    assert collar.Shape.isValid() and len(collar.Shape.Solids)==1
    collar.Shape.check(True)
    sketch.Visibility=False;bowl.Visibility=False;ring.Visibility=False
    if collar.ViewObject:collar.ViewObject.ShapeColor=(0.3,0.75,0.85)
    OUT.mkdir(parents=True,exist_ok=True)
    doc.Label='Socket - revolved reconstruction'
    return doc
