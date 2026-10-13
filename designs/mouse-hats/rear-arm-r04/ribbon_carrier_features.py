"""R04 rear routing only; retain the R03 top arm and socket construction."""
import json
import FreeCAD as App
import Part
from rear_sweep import geometry as rear_geometry
from attachment_arm_features import geometry,unit
from arm_finish_features import tray_edges,collar_edges

class RibbonSweep:
    def __init__(self,obj,base,tray,socket,rear,top,settings,ballcenter):
        for name,link in [('Base',base),('Tray',tray),('Socket',socket),('RearArm',rear),('TopArm',top),('FinishedBase',base.Document.JunctionFillets)]:
            obj.addProperty('App::PropertyLink',name,'Sources');setattr(obj,name,link)
        for name,value in [('SocketArmWidth',settings['socket_arm_width_mm']),('SocketArmThickness',settings['socket_arm_thickness_mm']),
                           ('CollarRadius',settings['collar_radius_mm']),('BallClearance',settings['ball_radial_clearance_mm'])]:
            obj.addProperty('App::PropertyLength',name,'R03');setattr(obj,name,value)
        obj.addProperty('App::PropertyVector','BallCenter','R03');obj.BallCenter=App.Vector(*ballcenter);obj.setEditorMode('BallCenter',1)
        obj.addProperty('App::PropertyString','SweepJSON','R04')
        obj.addProperty('App::PropertyLength','ExtraDrop','R04')
        obj.Proxy=self
    def execute(self,obj):
        if not 0<=obj.ExtraDrop.Value<=1.25:raise ValueError('Tested route interval: extra drop 0-1.25 mm')
        if not .25<=obj.BallClearance.Value<=.45:raise ValueError('Review outside 0.25-0.45 mm radial ball clearance')
        data=[json.loads(obj.RearArm.DesignJSON),json.loads(obj.TopArm.DesignJSON)]
        n=unit(data[0]['socket_axis']);c=App.Vector(*data[0]['socket_center_mm'])
        # Add only outside the unchanged insert bore. The collar remains coaxial.
        collar=Part.makeCylinder(obj.CollarRadius.Value,3,c+n*2.4,n).cut(Part.makeCylinder(1.45,3,c+n*2.4,n))
        socket=obj.Socket.Shape.fuse(collar).removeSplitter()
        arms=[]
        for arm_index,d in enumerate(data):
            # Extend the straight socket lead to meet the wider collar without corner overhang.
            d['attachment_radius_mm']=2.65;d['socket_lead_mm']=1.0
            d['socket_width_mm']=obj.SocketArmWidth.Value;d['socket_thickness_mm']=obj.SocketArmThickness.Value
            arms.append(rear_geometry(d,json.loads(obj.SweepJSON),obj.ExtraDrop.Value)[0] if arm_index==0 else geometry(d,3.0,1.8)[0])
        shape=obj.Tray.Shape.fuse(socket).fuse(arms[0]).fuse(arms[1]).removeSplitter()
        shape=shape.makeFillet(.5,tray_edges(shape,*data))
        edges=[]
        for edge in shape.Edges:
            if len(edge.Vertexes)!=2:continue
            points=[v.Point-c for v in edge.Vertexes]
            if all(abs((v-n*v.dot(n)).Length-obj.CollarRadius.Value)<1e-5 and 3.9-obj.SocketArmThickness.Value/2-1e-5<=v.dot(n)<=3.9+obj.SocketArmThickness.Value/2+1e-5 for v in points):edges.append(edge)
        if len(edges) not in [8,10]:raise ValueError('Socket boundary changed; inspect junction edges')
        shape=shape.makeFillet(.3,edges)
        # Reuse the accepted stem/PCB-tab additions, whose parents did not change.
        extras=obj.Base.Shape.cut(obj.FinishedBase.Shape,.0001)
        shape=shape.fuse(extras).removeSplitter()
        shoulder=[e for e in shape.Edges if hasattr(e.Curve,'Radius') and abs((e.CenterOfMass-c).dot(n)-2.4)<1e-5 and e.Curve.Radius>2.4]
        if len(shoulder)!=2:raise ValueError('Expected two lower collar transition edges')
        shape=shape.makeFillet(.2,[e for e in shoulder if e.Curve.Radius<2.5])
        clearance=Part.makeSphere(2.0+obj.BallClearance.Value,obj.BallCenter)
        shape=shape.cut(clearance).removeSplitter()
        shape.check(True)
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Expected one valid carrier')
        obj.Shape=shape
    def dumps(self):return None
    def loads(self,state):pass





