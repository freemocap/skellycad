"""Local rear backing reinforcement; no changes to the seated stem below it."""
import json
import FreeCAD as App
import Part


def reinforcement(settings, extra):
    p = settings; x = p['backing_rear_x_mm']; z = p['center_z_mm']-p['width_mm']/2
    xy = [(x+p['embed_mm'], p['start_y_mm']),
          (x-extra, p['start_y_mm']),
          (x-extra, p['taper_start_y_mm']),
          (x, p['end_y_mm']),
          (x+p['embed_mm'], p['end_y_mm'])]
    points = [App.Vector(a, b, z) for a,b in xy]
    pad = Part.Face(Part.makePolygon(points+[points[0]])).extrude(App.Vector(0,0,p['width_mm']))
    # Ease the longitudinal outside corners of the reinforcement itself; leave
    # its buried attachment edges intact. The core tray is never cut by this.
    edges = []
    for edge in pad.Edges:
        a,b = [v.Point for v in edge.Vertexes]
        if abs(a.z-b.z)<1e-7 and a.x<=x+1e-7 and b.x<=x+1e-7 and abs(a.y-b.y)>1:
            edges.append(edge)
    return pad.makeFillet(p['edge_radius_mm'], edges)


class StemReinforcement:
    def __init__(self, obj, base, settings):
        obj.addProperty('App::PropertyLink', 'Base', 'Construction'); obj.Base=base
        obj.addProperty('App::PropertyString', 'DesignJSON', 'Construction'); obj.DesignJSON=json.dumps(settings)
        obj.addProperty('App::PropertyLength', 'ExtraBacking', 'Reinforcement'); obj.ExtraBacking=settings['extra_backing_mm']
        obj.Proxy=self

    def execute(self,obj):
        if not .4<=obj.ExtraBacking.Value<=.8:
            raise ValueError('Extra backing must be 0.4–0.8 mm; other sizes require review')
        pad=reinforcement(json.loads(obj.DesignJSON),obj.ExtraBacking.Value)
        shape=obj.Base.Shape.fuse(pad).removeSplitter()
        shape.check(True)
        if not shape.isValid() or len(shape.Solids)!=1:
            raise ValueError('Reinforced carrier must be one valid solid')
        obj.Shape=shape

    def dumps(self):return None
    def loads(self,state):pass
