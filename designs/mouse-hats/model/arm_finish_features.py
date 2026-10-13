"""Small additive junction fillets selected by attachment geometry, not edge IDs."""
import json
import FreeCAD as App
from attachment_arm_features import unit


def unique_edge(shape, center, length):
    matches = [e for e in shape.Edges
               if (e.CenterOfMass-center).Length < 1e-5 and abs(e.Length-length) < 1e-5]
    if len(matches) != 1:
        raise ValueError('Attachment edge changed; review the junction before finishing')
    return matches[0]


def tray_edges(shape, rear, top):
    """Three inside rear-root edges; one inside top-root edge. Flush sides stay flush."""
    edges = []
    for data, sides in [(rear, [(0, 1), (0, -1), (1, 0)]), (top, [(-1, 0)])]:
        a = data['arm']; tangent = unit(a['root_tangent'])
        w = unit(a['root_width_direction']); h = unit(w.cross(tangent))
        center = App.Vector(*a['root_mm']) + tangent*data['embed_mm']
        for sw, sh in sides:
            midpoint = center + w*(sw*a['root_width_mm']/2) + h*(sh*a['root_thickness_mm']/2)
            length = a['root_thickness_mm'] if sw else a['root_width_mm']
            edges.append(unique_edge(shape, midpoint, length))
    return edges


def collar_edges(shape, data, collar_radius):
    """Intersection edges at the collar exterior within the arm's axial band."""
    origin = App.Vector(*data['socket_center_mm']); axis = unit(data['socket_axis'])
    low = data['attachment_height_mm']-data['socket_thickness_mm']/2
    high = data['attachment_height_mm']+data['socket_thickness_mm']/2
    edges = []
    for edge in shape.Edges:
        if len(edge.Vertexes) != 2:
            continue
        selected = True
        for vertex in edge.Vertexes:
            v = vertex.Point-origin; height = v.dot(axis)
            radius = (v-axis*height).Length
            if abs(radius-collar_radius) > 1e-5 or not low-1e-5 <= height <= high+1e-5:
                selected = False
        if selected:
            edges.append(edge)
    if len(edges) != 8:
        raise ValueError(f'Expected eight collar junction edges, found {len(edges)}')
    return edges


class JunctionFillets:
    def __init__(self, obj, base, rear, top, settings):
        for name, value in [('Base', base), ('RearArm', rear), ('TopArm', top)]:
            obj.addProperty('App::PropertyLink', name, 'Sources'); setattr(obj, name, value)
        for name, key in [('TrayRootRadius', 'tray_root_radius_mm'),
                          ('SocketRootRadius', 'socket_root_radius_mm'),
                          ('CollarRadius', 'collar_outer_radius_mm')]:
            obj.addProperty('App::PropertyLength', name, 'Finishing'); setattr(obj, name, settings[key])
        obj.setEditorMode('CollarRadius', 1)
        obj.Proxy = self

    def execute(self, obj):
        rear = json.loads(obj.RearArm.DesignJSON); top = json.loads(obj.TopArm.DesignJSON)
        shape = obj.Base.Shape.copy()
        if not 0 <= obj.TrayRootRadius.Value <= .5 or not 0 <= obj.SocketRootRadius.Value <= .3:
            raise ValueError('Conservative radius limits: tray 0–0.5 mm, socket 0–0.3 mm')
        if obj.TrayRootRadius.Value:
            shape = shape.makeFillet(obj.TrayRootRadius.Value, tray_edges(shape, rear, top))
        if obj.SocketRootRadius.Value:
            shape = shape.makeFillet(obj.SocketRootRadius.Value,
                                     collar_edges(shape, rear, obj.CollarRadius.Value))
        shape.check(True)
        if not shape.isValid() or len(shape.Solids) != 1:
            raise ValueError('Junction fillets must produce one valid solid')
        obj.Shape = shape

    def dumps(self): return None
    def loads(self, state): pass
