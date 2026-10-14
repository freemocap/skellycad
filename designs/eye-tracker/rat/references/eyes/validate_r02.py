"""Reopen R02 native documents with the pinned FreeCAD Python; no desktop GUI."""
from pathlib import Path
import json
import FreeCAD as App
import Mesh
import Part

HERE=Path(__file__).resolve().parent
for filename,names in [('rat-eye-definition-r02.FCStd',['RatEye']),
                       ('rat-skull-eyes-placement-r02.FCStd',['RightEye','LeftEye'])]:
    doc=App.openDocument(str(HERE/'r02'/filename))
    try:
        for name in names:
            eye=doc.getObject(name)
            assert eye.TypeId=='App::Part'
            rotation=eye.Placement.Rotation
            x,y,z=[rotation.multVec(v) for v in [App.Vector(1,0,0),App.Vector(0,1,0),App.Vector(0,0,1)]]
            assert abs(x.cross(y).dot(z)-1)<1e-10
            assert max(abs(x.dot(y)),abs(y.dot(z)),abs(x.dot(z)))<1e-10
            regions=[doc.getObject(name+s) for s in ['Sclera','Cornea']]
            assert [o.Mesh.CountFacets for o in regions]==[49536,24576]
            origin=doc.getObject(name+'Origin')
            children=regions+[origin]+[doc.getObject(name+'Axis'+axis) for axis in 'XYZ']
            before=[o.getGlobalPlacement().Base for o in children]
            original=App.Placement(eye.Placement)
            eye.Placement.Base=eye.Placement.Base+App.Vector(1,2,3)
            doc.recompute()
            for o,base in zip(children,before):
                assert (o.getGlobalPlacement().Base-base-App.Vector(1,2,3)).Length<1e-8
            eye.Placement=original
            assert (origin.getGlobalPlacement().Base-eye.Placement.Base).Length<1e-8
            for axis,expected in zip('XYZ',[x,y,z]):
                obj=doc.getObject(name+'Axis'+axis)
                unit={'X':App.Vector(1,0,0),'Y':App.Vector(0,1,0),'Z':App.Vector(0,0,1)}[axis]
                assert (obj.getGlobalPlacement().Rotation.multVec(unit)-expected).Length<1e-8
        print(filename+': frame, material regions and parent movement passed')
    finally:
        App.closeDocument(doc.Name)
