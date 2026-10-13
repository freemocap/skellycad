import FreeCAD as App, Part
from flared_arm import geometry,unit
from options_root_edges import tray_edges

def build_geometry(s,src,socket_path):
 shift=App.Vector(*s['joint_shift_mm']);data=[s['rear_data'],s['top_data']]
 for d in data:
  d['socket_center_mm']=list(App.Vector(*d['socket_center_mm'])+shift)
  d.update(attachment_height_mm=s['body_attachment_height_mm'],attachment_radius_mm=s['body_attachment_radius_mm'],socket_lead_mm=1.,socket_width_mm=3.,socket_thickness_mm=2.2)
 rear=data[0];rear['sections']=41
 rear['plugward_flare_deg']=s['plugward_flare_deg']
 rear['arm'].update(root_mm=s['root_mm'],root_handle_mm=s['root_handle_mm'],socket_handle_mm=s['socket_handle_mm'],root_width_mm=s['root_width_mm'],root_thickness_mm=s['root_thickness_mm'])
 rear['arm']['radial_direction']=list(App.Rotation(unit(rear['socket_axis']),s['attachment_angle_deg']).multVec(unit(rear['arm']['radial_direction'])))
 arm,_,_,path,twist=geometry(rear,s['body_width_mm'],s['body_thickness_mm'])
 top=geometry(data[1],3.,1.8)[0]
 socket=Part.Shape();socket.read(str(socket_path));socket.translate(shift)
 n=unit(rear['socket_axis']);c=App.Vector(*rear['socket_center_mm'])
 # The added stem collar is no longer needed; retain the original socket body/stem.
 # Remove only the old rear-root protrusion from the saved T3 tray region.
 root_trim=Part.makeBox(53.70677424482636,4.5,3.5,App.Vector(-50,10.3,14.5))
 tray=src.T3ProtectedTray.Shape.cut(root_trim).removeSplitter()
 carrier=tray.fuse(top).fuse(socket).fuse(arm).removeSplitter();carrier.check(True)
 assert carrier.isValid() and len(carrier.Solids)==1
 print('basic fusion',carrier.Volume,flush=True)
 # The saved T3 tray already includes the original top-root junction blend.
 plane=3.70677424482636;cy=s['root_mm'][1];cz=s['root_mm'][2]
 edges=[e for e in carrier.Edges if all(abs(v.Point.x-plane)<1e-5 for v in e.Vertexes)
        and abs(e.CenterOfMass.y-cy)<1.31 and abs(e.CenterOfMass.z-cz)<1.6
        and (abs(e.CenterOfMass.y-cy)>1.2 or e.CenterOfMass.z<cz-.5)]
 assert len(edges)==3,[(e.CenterOfMass,e.Length) for e in edges]
 carrier=carrier.makeFillet(.2,edges)
 print('root fillets',carrier.Volume,flush=True)
 # Exploratory body junctions use direct overlapping sweeps, no stem-junction fillets.
 carrier=carrier.cut(Part.makeSphere(2+s['ball_clearance_mm'],App.Vector(*s['ball_center_mm']))).removeSplitter()
 carrier.check(True);assert carrier.isValid() and len(carrier.Solids)==1
 return carrier,arm,path
