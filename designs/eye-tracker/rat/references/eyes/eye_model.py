"""Standalone rat eye: local material regions and right-handed XYZ guides.

No skull or species placement is required. Call create_eye in FreeCAD GUI Python.
Geometry/frame specification: r02/eye-definition.json and README.md.
"""
from pathlib import Path
import hashlib
import json
import FreeCAD as App
import Mesh
import Part

HERE = Path(__file__).resolve().parent


def create_eye(doc, name, label, cornea_color=(.12,.55,.75), sclera_color=(.94,.94,.92)):
    definition = json.loads((HERE/'r02/eye-definition.json').read_text())
    eye = doc.addObject('App::Part',name)
    eye.Label = label
    eye.addProperty('App::PropertyString','FrameDefinition').FrameDefinition = (
        'Origin: complete-envelope volume centroid. +Z anterior, +Y superior, +X=Y cross Z. Right-handed.')
    eye.addProperty('App::PropertyString','GeometryRevision').GeometryRevision = definition['revision']
    eye.addProperty('App::PropertyString','ModelScope').ModelScope = definition['tissue_note']
    for region,color in [('sclera',sclera_color),('cornea',cornea_color)]:
        spec=definition['components'][region]
        path=HERE/'r02'/spec['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==spec['sha256']
        obj=doc.addObject('Mesh::Feature',name+region.title())
        eye.addObject(obj)
        obj.Label=region.title()+' — schematic envelope region'
        obj.Mesh=Mesh.Mesh(str(path))
        obj.ViewObject.ShapeColor=color
    guides=doc.addObject('App::Part',name+'Axes')
    eye.addObject(guides)
    guides.Label='Local XYZ — display guides (toggle visibility)'
    for axis,vector,color in [('X',(1,0,0),(1.,.12,.12)),('Y',(0,1,0),(.1,.75,.15)),('Z',(0,0,1),(.12,.25,1.))]:
        direction=App.Vector(*vector)
        rod=Part.makeCylinder(.045,4.5,App.Vector(),direction)
        tip=Part.makeCone(.18,0.,.55,direction*4.5,direction)
        obj=doc.addObject('PartDesign::Feature',name+'Axis'+axis)
        guides.addObject(obj)
        obj.Label='+'+axis+' — '+{'X':'right-handed transverse','Y':'superior / up','Z':'anterior / corneal apex'}[axis]
        obj.Shape=rod.fuse(tip)
        obj.ViewObject.ShapeColor=color
    origin=doc.addObject('PartDesign::Feature',name+'Origin')
    guides.addObject(origin)
    origin.Label='Origin — complete-envelope volume centroid'
    origin.Shape=Part.makeSphere(.12)
    origin.ViewObject.ShapeColor=(1.,.8,.1)
    return eye


def oriented_frame(forward, up):
    """Construct a proper rotation with +Z forward and +Y projected up."""
    z=App.Vector(*forward)
    z.normalize()
    dorsal=App.Vector(*up)
    y=dorsal-z*dorsal.dot(z)
    if y.Length < 1e-8:
        raise ValueError('Up direction is parallel to the eye axis')
    y.normalize()
    x=y.cross(z)
    x.normalize()
    assert x.cross(y).dot(z)>1-1e-10
    rotation=App.Rotation(x,y,z,'ZXY')
    for unit,expected in [(App.Vector(1,0,0),x),(App.Vector(0,1,0),y),(App.Vector(0,0,1),z)]:
        assert (rotation.multVec(unit)-expected).Length<1e-9
    return rotation
