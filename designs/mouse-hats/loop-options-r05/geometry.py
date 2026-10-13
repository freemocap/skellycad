import FreeCAD as App, Part
from attachment_arm_features import geometry,unit
from options_root_edges import tray_edges

def build_geometry(s,src,socket_path):
 shift=App.Vector(*s['joint_shift_mm']);data=[s['rear_data'],s['top_data']]
 for d in data:
  d['socket_center_mm']=list(App.Vector(*d['socket_center_mm'])+shift)
  d.update(attachment_radius_mm=2.65,socket_lead_mm=1.,socket_width_mm=3.,socket_thickness_mm=2.2)
 rear=data[0];rear['sections']=41
 rear['arm'].update(root_mm=s['root_mm'],root_handle_mm=s['root_handle_mm'],socket_handle_mm=s['socket_handle_mm'],root_width_mm=s['root_width_mm'],root_thickness_mm=s['root_thickness_mm'])
 rear['arm']['radial_direction']=list(App.Rotation(unit(rear['socket_axis']),s['attachment_angle_deg']).multVec(unit(rear['arm']['radial_direction'])))
 arm,_,_,path,twist=geometry(rear,s['body_width_mm'],s['body_thickness_mm'])
 top=geometry(data[1],3.,1.8)[0]
 socket=Part.Shape();socket.read(str(socket_path));socket.translate(shift)
 n=unit(rear['socket_axis']);c=App.Vector(*rear['socket_center_mm'])
 collar=Part.makeCylinder(s['collar_radius_mm'],3,c+n*2.4,n).cut(Part.makeCylinder(1.45,3,c+n*2.4,n))
 socket=socket.fuse(collar).removeSplitter()
 # Remove only the old rear-root protrusion from the saved T3 tray region.
 root_trim=Part.makeBox(53.70677424482636,4.5,3.5,App.Vector(-50,10.3,14.5))
 tray=src.T3ProtectedTray.Shape.cut(root_trim).removeSplitter()
 carrier=tray.fuse(top).fuse(socket).fuse(arm).removeSplitter();carrier.check(True)
 assert carrier.isValid() and len(carrier.Solids)==1
 print('basic fusion',carrier.Volume,flush=True)
 # The saved T3 tray already includes the original top-root junction blend.
 carrier=carrier.makeFillet(.2,tray_edges(carrier,*data,which='rear'))
 print('root fillets',carrier.Volume,flush=True)
 edges=[]
 for edge in carrier.Edges:
  if len(edge.Vertexes)!=2:continue
  points=[v.Point-c for v in edge.Vertexes]
  if all(abs((v-n*v.dot(n)).Length-s['collar_radius_mm'])<1e-5 and 2.8-1e-5<=v.dot(n)<=5+1e-5 for v in points):edges.append(edge)
 assert len(edges) in [8,10],len(edges)
 carrier=carrier.makeFillet(.3,edges)
 shoulder=[e for e in carrier.Edges if hasattr(e.Curve,'Radius') and abs((e.CenterOfMass-c).dot(n)-2.4)<1e-5 and 2.4<e.Curve.Radius<2.5]
 assert len(shoulder)==1
 carrier=carrier.makeFillet(.2,shoulder)
 carrier=carrier.cut(Part.makeSphere(2+s['ball_clearance_mm'],App.Vector(*s['ball_center_mm']))).removeSplitter()
 carrier.check(True);assert carrier.isValid() and len(carrier.Solids)==1
 return carrier,arm,path
