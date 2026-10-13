"""Taper only the lower exterior stock of the accepted baseplate."""
import json
import FreeCAD as App
import Part


class TaperedBaseplate:
    def __init__(self,obj,base,profile,settings):
        obj.addProperty('App::PropertyLink','Base','Construction');obj.Base=base
        obj.addProperty('App::PropertyString','ProfileJSON','Construction');obj.ProfileJSON=json.dumps(profile)
        obj.addProperty('App::PropertyFloat','BottomScale','Taper');obj.BottomScale=settings['bottom_scale']
        obj.addProperty('App::PropertyDistance','TaperStartY','Taper');obj.TaperStartY=settings['taper_start_y_mm']
        obj.addProperty('App::PropertyDistance','BottomY','Taper');obj.BottomY=settings['bottom_y_mm']
        obj.setEditorMode('TaperStartY',1);obj.setEditorMode('BottomY',1)
        obj.Proxy=self

    def execute(self,obj):
        scale=obj.BottomScale
        if not .5<=scale<=1:raise ValueError('Bottom scale must be 0.5–1; other sizes require review')
        pts=json.loads(obj.ProfileJSON)
        center=App.Vector(sum(p[0] for p in pts)/len(pts),0,sum(p[2] for p in pts)/len(pts))
        def wire(y,s):
            points=[App.Vector(center.x+s*(p[0]-center.x),y,center.z+s*(p[2]-center.z)) for p in pts]
            return Part.makePolygon(points+[points[0]])
        low=obj.BottomY.Value;high=obj.TaperStartY.Value
        full=Part.Face(wire(low,1)).extrude(App.Vector(0,high-low,0))
        tapered=Part.makeLoft([wire(low,scale),wire(high,1)],True,True)
        removed_stock=full.cut(tapered)
        shape=obj.Base.Shape.cut(removed_stock).removeSplitter() if scale<1 else obj.Base.Shape.copy()
        shape.check(True)
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Taper must leave one valid solid')
        obj.Shape=shape

    def dumps(self):return None
    def loads(self,state):pass
