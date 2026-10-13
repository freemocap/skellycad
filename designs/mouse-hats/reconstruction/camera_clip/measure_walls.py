"""Extract editable planar wall profiles, including the source's tiny front trim."""
from pathlib import Path
import json
import FreeCAD as App
import Part

HERE = Path(__file__).resolve().parent


def plane(face):
    n = face.normalAt(0,0)
    return n, n.dot(face.CenterOfMass)


def intersection(a,b,c):
    n1,d1=a; n2,d2=b; n3,d3=c
    return (n2.cross(n3)*d1+n3.cross(n1)*d2+n1.cross(n2)*d3)/n1.dot(n2.cross(n3))


def sketch_data(points, normal):
    origin = points[0]
    rotation = App.Rotation(App.Vector(0,0,1), normal)
    local = [rotation.inverted().multVec(p-origin) for p in points]
    assert max(abs(p.z) for p in local)<1e-6
    return dict(origin_mm=list(origin), rotation_xyzw=list(rotation.Q),
                points_xy_mm=[[p.x,p.y] for p in local])


def main():
    source = App.getDocument('CameraClipStudy58').SourceClip.Shape
    assert len(source.Faces)==18
    # IDs are pinned to this source revision and documented in measurements.
    front = plane(source.Faces[0])
    back = plane(source.Faces[14])
    trim = plane(source.Faces[1])
    upper = source.common(Part.makeBox(30,30,10,App.Vector(-10,-15,1.5))).removeSplitter()
    assert len(upper.Solids)==2
    walls=[]
    for solid in sorted(upper.Solids,key=lambda s:s.CenterOfMass.x):
        rear = next(f for f in solid.Faces if f.normalAt(0,0).dot(back[0])>1-1e-10)
        points = [v.Point for v in rear.OuterWire.OrderedVertexes]
        sideplanes=[]
        for p,q in zip(points,points[1:]+points[:1]):
            candidates=[]
            for face in solid.Faces:
                n,d=plane(face)
                if abs(n.dot(back[0]))>1-1e-10:
                    continue
                if abs(n.dot(p)-d)<1e-7 and abs(n.dot(q)-d)<1e-7:
                    candidates.append((n,d))
            assert len(candidates)==1, len(candidates)
            sideplanes.append(candidates[0])
        forward=[intersection(sideplanes[i-1],sideplanes[i],front) for i in range(len(points))]
        cap_forward=[intersection(sideplanes[i-1],sideplanes[i],trim) for i in range(len(points))]
        walls.append(dict(back=sketch_data(points,back[0]),
                          front=sketch_data(forward,front[0]),
                          cap_front=sketch_data(cap_forward,trim[0])))
    data=dict(units='mm', source='58nassembly.step / RightCamClip (1)',
              base_elevation_mm=1.5,walls=walls,
              trim_plane=dict(normal=list(trim[0]), offset_mm=trim[1]))
    (HERE/'wall_parameters.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Saved wall profiles:',[len(w['back']['points_xy_mm']) for w in walls])
