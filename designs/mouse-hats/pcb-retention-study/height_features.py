"""Isolated additive tray-height / rebuilt cap geometry prototype. Units: mm."""
import json,copy
import FreeCAD as App
import Part

def backing(profiles,offset):
    wires=[]
    for points in profiles:
        vs=[App.Vector(x,y+(offset if y>=15 else 0),z) for x,y,z in points]
        wires.append(Part.makePolygon(vs+[vs[0]]))
    return Part.makeLoft(wires,True,True)

def cap_geometry(parameters,offset):
    solids=[]
    for f in parameters['features']:
        vs=[App.Vector(x,y+(offset if y>=15 else 0),z) for x,y,z in f['profile_mm']]
        solids.append(Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(App.Vector(*f['extrusion_mm'])))
    s=solids[0].multiFuse(solids[1:]).removeSplitter()
    for h in parameters['holes']:
        x,y,z=h['origin_mm'];v=App.Vector(*h['axis'])
        o=App.Vector(x,y+(offset if y>=15 else 0),z)
        s=s.cut(Part.makeCylinder(h['radius_mm'],h['length_mm']+2,o-v,v))
    s=s.removeSplitter();s.check(True)
    if not s.isValid() or len(s.Solids)!=1:raise ValueError('Invalid cap')
    return s

class HeightCarrier:
    def __init__(self,obj,base,profiles):
        obj.addProperty('App::PropertyLink','Base','Source');obj.Base=base
        obj.addProperty('App::PropertyString','BackingProfilesJSON','Source');obj.BackingProfilesJSON=json.dumps(profiles)
        obj.addProperty('App::PropertyLength','TrayUpperEdgeOffset','Study');obj.TrayUpperEdgeOffset=0
        obj.Proxy=self
    def execute(self,obj):
        v=obj.TrayUpperEdgeOffset.Value
        if not 0<=v<=1:raise ValueError('Study range 0..1 mm')
        if v==0:obj.Shape=obj.Base.Shape.copy();return
        p=json.loads(obj.BackingProfilesJSON)
        extra=backing(p,v).cut(backing(p,0)).removeSplitter()
        s=obj.Base.Shape.fuse(extra).removeSplitter();s.check(True)
        if not s.isValid() or len(s.Solids)!=1:raise ValueError('Invalid carrier')
        obj.Shape=s
    def dumps(self):return None
    def loads(self,state):pass

class HeightCap:
    def __init__(self,obj,carrier,parameters):
        obj.addProperty('App::PropertyLink','Carrier','Source');obj.Carrier=carrier
        obj.addProperty('App::PropertyString','ProfilesJSON','Source');obj.ProfilesJSON=json.dumps(parameters)
        obj.Proxy=self
    def execute(self,obj):obj.Shape=cap_geometry(json.loads(obj.ProfilesJSON),obj.Carrier.TrayUpperEdgeOffset.Value)
    def dumps(self):return None
    def loads(self,state):pass
