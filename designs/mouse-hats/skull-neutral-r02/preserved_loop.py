"""Retain R11B rear-arm shape relative to joint, extending only its tray connection."""
import copy
import FreeCAD as App,Part
from options_sweep import geometry as original_geometry
from attachment_arm_features import unit,rectangle

def geometry(data,settings,drop,shift):
 d=copy.deepcopy(data)
 d['socket_center_mm']=list(App.Vector(*d['socket_center_mm'])-shift)
 original,path,details=original_geometry(d,settings,drop)
 moved=original.copy();moved.translate(shift)
 a=d['arm'];root=App.Vector(*a['root_mm']);t=unit(a['root_tangent']);w=unit(a['root_width_direction'])
 # Overlap the translated original's straight root lead by 0.1 mm.
 end=root+shift+t*.1
 start=root+t*(d['embed_mm']+d['root_lead_mm'])
 reach=(end-start).Length/3
 curve=Part.BezierCurve();curve.setPoles([start,start+t*reach,end-t*reach,end])
 wires=[]
 for i in range(17):
  u=i/16;center=curve.value(u);tangent=curve.tangent(u)[0]
  width=App.Rotation(t,tangent).multVec(w)
  wires.append(rectangle(center,tangent,width,a['root_width_mm'],a['root_thickness_mm']))
 rootcap=rectangle(root,t,w,a['root_width_mm'],a['root_thickness_mm'])
 extension=Part.makeLoft([rootcap,wires[0]],True,True).fuse(Part.makeLoft(wires,True,False,False,3)).removeSplitter()
 result=extension.fuse(moved,.0001).removeSplitter();result.check(True)
 if not result.isValid() or len(result.Solids)!=1:raise ValueError('Extended rear arm must be one valid solid')
 translated_path=path.copy();translated_path.translate(shift)
 return result,translated_path,dict(details,method='Rigidly translated original R11B loop plus cubic tray extension',extension_length_mm=curve.toShape().Length+(start-root).Length,extension_overlap_mm=.1),moved,extension
