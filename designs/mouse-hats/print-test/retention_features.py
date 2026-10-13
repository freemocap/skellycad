"""Extend the existing PCB retainer profiles along Z; preserve their XY gaps."""
import json
import FreeCAD as App
import Part


class LongerRetainers:
    def __init__(self,obj,base,profiles,length,lower_length):
        obj.addProperty('App::PropertyLink','Base','Construction');obj.Base=base
        obj.addProperty('App::PropertyString','ProfilesJSON','Construction');obj.ProfilesJSON=json.dumps(profiles)
        obj.addProperty('App::PropertyLength','Extension','PCB retention');obj.Extension=length
        obj.addProperty('App::PropertyLength','LowerExtension','PCB retention');obj.LowerExtension=lower_length
        obj.Proxy=self

    def execute(self,obj):
        length=obj.Extension.Value
        if not 0<=length<=2:raise ValueError('PCB extension must be 0–2 mm')
        if not 0<=obj.LowerExtension.Value<=.7:raise ValueError('Lower extension must be 0–0.7 mm to clear the cap')
        if length==0 and obj.LowerExtension.Value==0:obj.Shape=obj.Base.Shape.copy();return
        shapes=[]
        for feature in json.loads(obj.ProfilesJSON):
            # Existing upper lips point toward -Z; opposite stop toward +Z.
            direction=1 if feature['name']=='LowerPCBStop' else -1
            length=obj.LowerExtension.Value if direction==1 else obj.Extension.Value
            if length==0:continue
            points=[App.Vector(*p) for p in feature['profiles_mm'][0]]
            for p in points:p.z-=direction*.02
            section=Part.Face(Part.makePolygon(points+[points[0]]))
            shapes.append(section.extrude(App.Vector(0,0,direction*(length+.02))))
        shape=obj.Base.Shape.multiFuse(shapes).removeSplitter()
        shape.check(True)
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Retainers must join the carrier')
        obj.Shape=shape

    def dumps(self):return None
    def loads(self,state):pass
