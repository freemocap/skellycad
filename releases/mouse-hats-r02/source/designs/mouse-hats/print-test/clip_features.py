"""Lengthen the clip crosspiece; move intact retaining arms outward with the walls."""
import FreeCAD as App
import Part


class WiderClip:
    def __init__(self,obj,base,holder):
        obj.addProperty('App::PropertyLink','Base','Construction');obj.Base=base
        obj.addProperty('App::PropertyLink','Holder','Construction');obj.Holder=holder
        obj.Proxy=self

    def execute(self,obj):
        s=obj.Base.Shape;extra=obj.Holder.OutwardThickness.Value
        if extra==0:obj.Shape=s.copy();return
        middle=(s.BoundBox.XMin+s.BoundBox.XMax)/2
        left=s.common(Part.makeBox(middle+20,40,30,App.Vector(-20,-20,-10)),.0001)
        right=s.common(Part.makeBox(30,40,30,App.Vector(middle,-20,-10)),.0001)
        left.translate(App.Vector(-extra,0,0));right.translate(App.Vector(extra,0,0))
        wires=s.slice(App.Vector(1,0,0),middle)
        if len(wires)!=1:raise ValueError('Expected one central clip section')
        face=Part.Face(wires[0]);face.translate(App.Vector(-extra,0,0))
        bridge=face.extrude(App.Vector(2*extra,0,0))
        shape=left.multiFuse([bridge,right]).removeSplitter();shape.check(True)
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Clip must remain one solid')
        obj.Shape=shape

    def dumps(self):return None
    def loads(self,state):pass
