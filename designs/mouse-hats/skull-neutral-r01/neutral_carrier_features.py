"""R11B-derived joint translation; fixed tray roots, regenerated arms and socket."""
import json
import FreeCAD as App
import Part
from options_sweep import geometry as rear_geometry
from attachment_arm_features import geometry,unit
from options_root_edges import tray_edges

class RearwardNeutral:
    def __init__(self,obj,base,tray,socket,rear,top,settings,ballcenter):
        for name,link in [('Base',base),('Tray',tray),('Socket',socket),('RearArm',rear),('TopArm',top),('FinishedBase',base.Document.JunctionFillets)]:
            obj.addProperty('App::PropertyLink',name,'Sources');setattr(obj,name,link)
        for name,value in [('SocketArmWidth',settings['socket_arm_width_mm']),('SocketArmThickness',settings['socket_arm_thickness_mm']),
                           ('CollarRadius',settings['collar_radius_mm']),('BallClearance',settings['ball_radial_clearance_mm'])]:
            obj.addProperty('App::PropertyLength',name,'R03');setattr(obj,name,value)
        obj.addProperty('App::PropertyVector','BallCenter','R03');obj.BallCenter=App.Vector(*ballcenter);obj.setEditorMode('BallCenter',1)
        obj.addProperty('App::PropertyString','SweepJSON','R04')
        obj.addProperty('App::PropertyLength','ExtraDrop','R04')
        obj.addProperty('App::PropertyAngle','AttachmentAngle','R05');obj.AttachmentAngle=30
        obj.addProperty('App::PropertyLength','RootForward','R11');obj.RootForward=4.5062968498585
        obj.addProperty('App::PropertyLength','OuterBulge','R11');obj.OuterBulge=1.5
        obj.addProperty('App::PropertyLength','RootUp','R11');obj.RootUp=3.0
        obj.addProperty('App::PropertyLength','BandExtra','R11');obj.BandExtra=0.
        obj.addProperty('App::PropertyVector','JointShift','Eye alignment');obj.JointShift=App.Vector()
        obj.Proxy=self
    def execute(self,obj):
        if not 0<=obj.ExtraDrop.Value<=1.25:raise ValueError('Tested route interval: extra drop 0-1.25 mm')
        if not .25<=obj.BallClearance.Value<=.45:raise ValueError('Review outside 0.25-0.45 mm radial ball clearance')
        data=[json.loads(obj.RearArm.DesignJSON),json.loads(obj.TopArm.DesignJSON)]
        data[0]['arm']['root_mm'][2]+=obj.RootForward.Value
        s=json.loads(obj.SweepJSON)
        data[0]['arm']['root_mm'][1]=s['root_lower_y_mm']+s['root_width_mm']/2
        data[0]['arm']['root_width_mm']=s['root_width_mm']
        for d in data:d['socket_center_mm']=list(App.Vector(*d['socket_center_mm'])+obj.JointShift)
        n=unit(data[0]['socket_axis']);c=App.Vector(*data[0]['socket_center_mm'])
        # Add only outside the unchanged insert bore. The collar remains coaxial.
        collar=Part.makeCylinder(obj.CollarRadius.Value,3,c+n*2.4,n).cut(Part.makeCylinder(1.45,3,c+n*2.4,n))
        socket=obj.Socket.Shape.copy();socket.translate(obj.JointShift)
        socket=socket.fuse(collar).removeSplitter()
        arms=[]
        for arm_index,d in enumerate(data):
            # Extend the straight socket lead to meet the wider collar without corner overhang.
            d['attachment_radius_mm']=2.65;d['socket_lead_mm']=1.0
            d['socket_width_mm']=obj.SocketArmWidth.Value;d['socket_thickness_mm']=obj.SocketArmThickness.Value
            sweep=json.loads(obj.SweepJSON);sweep['attachment_angle_deg']=obj.AttachmentAngle.Value;sweep['root_forward_mm']=obj.RootForward.Value;sweep['outer_bulge_mm']=obj.OuterBulge.Value;sweep['root_up_mm']=obj.RootUp.Value;sweep['band_extra_mm']=obj.BandExtra.Value
            arms.append(rear_geometry(d,sweep,obj.ExtraDrop.Value)[0] if arm_index==0 else geometry(d,3.0,1.8)[0])
        # Complete tray reinforcements first, before attaching the new arms.
        extras=obj.Base.Shape.cut(obj.FinishedBase.Shape,.0001)
        tray=obj.Tray.Shape.fuse(extras,.0001).removeSplitter()
        tray.check(True)
        shape=tray.fuse(socket).fuse(arms[0]).fuse(arms[1]).removeSplitter()
        print('fused',shape.Volume,flush=True);shape.check(True)
        shape=shape.makeFillet(.5,tray_edges(shape,*data,which='top'))
        shape=shape.makeFillet(.2,tray_edges(shape,*data,which='rear'))
        print('tray blends',shape.Volume,flush=True);shape.check(True)
        edges=[]
        for edge in shape.Edges:
            if len(edge.Vertexes)!=2:continue
            points=[v.Point-c for v in edge.Vertexes]
            if all(abs((v-n*v.dot(n)).Length-obj.CollarRadius.Value)<1e-5 and 3.9-obj.SocketArmThickness.Value/2-1e-5<=v.dot(n)<=3.9+obj.SocketArmThickness.Value/2+1e-5 for v in points):edges.append(edge)
        if len(edges) not in [8,10]:raise ValueError('Socket boundary changed; inspect junction edges')
        shape=shape.makeFillet(.3,edges)
        print('collar blends',shape.Volume,flush=True);shape.check(True)
        shoulder=[e for e in shape.Edges if hasattr(e.Curve,'Radius') and abs((e.CenterOfMass-c).dot(n)-2.4)<1e-5 and e.Curve.Radius>2.4]
        if len(shoulder)!=2:raise ValueError('Lower collar transition edges: '+str([(e.Curve.Radius,e.Length,list(e.CenterOfMass)) for e in shoulder]))
        shape=shape.makeFillet(.2,[e for e in shoulder if e.Curve.Radius<2.5])
        print('shoulder',shape.Volume,flush=True);shape.check(True)
        clearance=Part.makeSphere(2.0+obj.BallClearance.Value,obj.BallCenter+obj.JointShift)
        shape=shape.cut(clearance).removeSplitter()
        shape.check(True)
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Expected one valid carrier')
        obj.Shape=shape
    def dumps(self):return None
    def loads(self,state):pass





