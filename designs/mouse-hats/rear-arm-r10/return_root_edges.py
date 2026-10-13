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


def tray_edges(shape, rear, top, which="all"):
    """Two inside rear-root edges at the leading edge; one inside top-root edge."""
    edges = []
    for data, sides in [(rear, [(0, -1), (1, 0), (-1, 0)]), (top, [(-1, 0)])]:
        if which=='rear' and data is top:continue
        if which=='top' and data is rear:continue
        a = data['arm']; tangent = unit(a['root_tangent'])
        w = unit(a['root_width_direction']); h = unit(w.cross(tangent))
        center = App.Vector(*a['root_mm']) + tangent*data['embed_mm']
        for sw, sh in sides:
            midpoint = center + w*(sw*a['root_width_mm']/2) + h*(sh*a['root_thickness_mm']/2)
            length = a['root_thickness_mm'] if sw else a['root_width_mm']
            edges.append(unique_edge(shape, midpoint, length))
    return edges

