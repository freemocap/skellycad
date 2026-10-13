"""Blend the existing stem slope directly into the tray; no overlay pad."""
import json
import FreeCAD as App


class StemBlend:
    def __init__(self, obj, base, settings):
        obj.addProperty('App::PropertyLink', 'Base', 'Construction'); obj.Base=base
        obj.addProperty('App::PropertyString', 'DesignJSON', 'Construction')
        obj.DesignJSON=json.dumps(settings)
        obj.addProperty('App::PropertyLength', 'RootBlendRadius', 'Reinforcement')
        obj.RootBlendRadius=settings['root_blend_radius_mm']
        obj.Proxy=self

    def execute(self,obj):
        p=json.loads(obj.DesignJSON); radius=obj.RootBlendRadius.Value
        if not 1.5<=radius<=3:
            raise ValueError('Root blend radius must be 1.5–3 mm; other sizes need review')
        base=obj.Base.Shape
        center=App.Vector(*p['junction_center_mm'])
        edges=[e for e in base.Edges if (e.CenterOfMass-center).Length<1e-5
               and abs(e.Length-p['junction_width_mm'])<1e-5]
        if len(edges)!=1:
            raise ValueError('Stem/tray junction changed; review before applying blend')
        # OCCT constructs a rolling-radius surface tangent to the existing slope
        # and tray face, including its end transitions. No independent patch.
        shape=base.makeFillet(radius,edges)
        shape.check(True)
        if not shape.isValid() or len(shape.Solids)!=1:
            raise ValueError('Stem blend must produce one valid solid')
        obj.Shape=shape

    def dumps(self):return None
    def loads(self,state):pass
