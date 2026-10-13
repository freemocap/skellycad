"""Outward rail and clip-seat thickening; preserve the sensor cavity."""
import json
import FreeCAD as App
import Part


class ThickerWalls:
    def __init__(self,obj,base,parameters,extra):
        obj.addProperty('App::PropertyLink','Base','Construction');obj.Base=base
        obj.addProperty('App::PropertyString','ParametersJSON','Construction');obj.ParametersJSON=json.dumps(parameters)
        obj.addProperty('App::PropertyLength','OutwardThickness','Walls');obj.OutwardThickness=extra
        obj.Proxy=self

    def execute(self,obj):
        p=json.loads(obj.ParametersJSON);extra=obj.OutwardThickness.Value
        if not 0<=extra<=.7:raise ValueError('Outward addition must be 0–0.7 mm')
        if extra==0:obj.Shape=obj.Base.Shape.copy();return
        # Copy the actual outer rail/clip-seat profiles outward. Union with the
        # original preserves the sensor cavity while widening the entire exterior,
        # including the clip seat. Ball and neck are excluded above plate height.
        xleft,xright=p['rail_inner_x_mm'];z0=p['rail_bottom_z_mm']-.1
        height=p['plate_z_mm'][1]-z0
        left=obj.Base.Shape.common(Part.makeBox(xleft+20,40,height,App.Vector(-20,-20,z0)),.0001)
        right=obj.Base.Shape.common(Part.makeBox(20,40,height,App.Vector(xright,-20,z0)),.0001)
        left.translate(App.Vector(-extra,0,0));right.translate(App.Vector(extra,0,0))
        shape=obj.Base.Shape.multiFuse([left,right]).removeSplitter()
        shape.check(True)
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Walls must join original holder')
        obj.Shape=shape

    def dumps(self):return None
    def loads(self,state):pass
