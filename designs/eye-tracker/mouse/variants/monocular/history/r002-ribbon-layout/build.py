"""Build an arm-free camera layout study; no accepted checkpoint is changed."""
from pathlib import Path
import json,sys,hashlib
import FreeCAD as A,Part,Mesh
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(HERE))
import geometry as g
OUT=ROOT/'generated/eye-tracker/mouse/ribbon-layout-r02'

def build():
 manifest=json.loads((HERE.parent/'active-model.json').read_text());assert hashlib.sha256((ROOT/manifest['native_checkpoint']).read_bytes()).hexdigest()==manifest['native_sha256']
 candidate=json.loads((OUT/'candidates.json').read_text())[0];p=candidate['parameters']
 d=A.openDocument(str(ROOT/'generated/eye-tracker/mouse/camera-fit-r01/mouse-camera-fit-r01.FCStd'))
 for name in ['RibbonRouteGuide','eye_primary_Holder','eye_primary_Carrier','eye_primary_Clip','eye_primary_OpticalAxis','eye_primary_LensDatum','eye_primary_ApproxPCB','eye_primary_UpperCatch','eye_primary_UpperRail','eye_primary_SideLedge']:
  ob=d.getObject(name)
  if ob:d.removeObject(name)
 traypath=ROOT/'designs/eye-tracker/shared/mounts/r10-monocular/tray.brep';mount=json.loads((traypath.parent/'mount.json').read_text());assert hashlib.sha256(traypath.read_bytes()).hexdigest()==mount['parts']['tray']['sha256']
 tray=d.addObject('Part::Feature','RetainedPCBTray');tray.Shape=Part.Shape();sh=Part.Shape();sh.read(str(traypath));tray.Shape=sh
 pos,R=g.endpoint(p);rot=A.Rotation(A.Vector(*R[:,0]),A.Vector(*R[:,1]),A.Vector(*R[:,2]),'ZXY');head=d.getObject('MeasuredSensorHead');head.Placement=A.Placement(A.Vector(*pos[0]),rot)
 nx,ny=8,132;flat=np.array([[x,y,0.] for y in np.linspace(0,g.L,ny+1) for x in np.linspace(-2,2,nx+1)])
 vertices,_=g.evaluate(p,flat);eps=1e-5;dx=(g.evaluate(p,flat+[eps,0,0])[0]-g.evaluate(p,flat-[eps,0,0])[0])/(2*eps);dy=(g.evaluate(p,flat+[0,eps,0])[0]-g.evaluate(p,flat-[0,eps,0])[0])/(2*eps)
 normals=np.cross(dx,dy);normals/=np.linalg.norm(normals,axis=1)[:,None]
 metric={'max_local_length_error':float(max(abs(np.linalg.norm(dx,axis=1)-1).max(),abs(np.linalg.norm(dy,axis=1)-1).max())),'max_local_shear':float(abs((dx*dy).sum(1)).max())}
 faces=[]
 for j in range(ny):
  for i in range(nx):
   a=j*(nx+1)+i;b=a+1;c=a+nx+1;e=c+1;faces.extend([(a,b,e),(a,e,c)])
 count=len(vertices);vv=np.vstack([vertices+normals*.075,vertices-normals*.075]);ff=list(faces)+[tuple(i+count for i in f[::-1]) for f in faces]
 border=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
 for a,b in zip(border,border[1:]+border[:1]):ff.extend([(a,a+count,b+count),(a,b+count,b)])
 mesh=Mesh.Mesh([[A.Vector(*vv[i]) for i in f] for f in ff]);surface=Part.Shape();surface.makeShapeFromMesh(mesh.Topology,1e-7);solid=Part.makeSolid(surface)
 ribbon=d.addObject('Part::Feature','RibbonCandidate');ribbon.Shape=solid
 hardware={'tray':tray.Shape,'cap':d.getObject('eye_primary_Cap').Shape,'baseplate':d.getObject('skull_mount_Baseplate').Shape}
 for parent in [d.getObject('MeasuredMainPCB'),head]:
  for ob in parent.Group:
   if not hasattr(ob,'Shape'):continue
   sh=ob.Shape.copy();sh.Placement=ob.getGlobalPlacement();hardware[ob.Name]=sh
 overlaps={}
 for name,sh in hardware.items():
  overlaps[name]=solid.common(sh).Volume;print(name,overlaps[name],flush=True)
 anatomy={name:bool(solid.BoundBox.intersect(d.getObject(name).Mesh.BoundBox)) for name in ['Skull','Eye1','Eye2']}
 report=dict(candidate,source_checkpoint=manifest['native_checkpoint'],source_sha256=manifest['native_sha256'],units='mm',neutral_length_mm=g.L,width_mm=4,assumed_thickness_mm=.15,metric=metric,solid_valid=solid.isValid(),mesh_closed=mesh.isSolid(),self_intersection=mesh.hasSelfIntersections(),ribbon_overlaps_mm3=overlaps,anatomy_bounding_boxes_overlap=anatomy)
 report['ribbon_checks_pass']=report['solid_valid'] and report['mesh_closed'] and not report['self_intersection'] and max(overlaps.values())<1e-6 and not any(anatomy.values()) and metric['max_local_length_error']<1e-5
 (OUT/'validation.json').write_text(json.dumps(report,indent=2));np.savez(OUT/'ribbon.npz',vertices=vertices,faces=np.array(faces));mesh.write(str(OUT/'ribbon-candidate.stl'))
 target=np.array(json.loads((HERE.parent/'anatomy.json').read_text())['eye_target_mm']);ll=np.array(json.loads((OUT/'lens-local.json').read_text()));lens=pos[0]+R@ll
 axis=d.addObject('Part::Feature','CandidateOpticalAxis');axis.Shape=Part.makeLine(A.Vector(*lens),A.Vector(*(lens+R[:,2]*np.linalg.norm(target-lens))))
 d.recompute()
 if A.GuiUp:
  tray.ViewObject.ShapeColor=(.7,.72,.75);ribbon.ViewObject.ShapeColor=(.85,.42,.08);axis.ViewObject.LineColor=(.9,.1,.1)
  ribbon.Visibility=report['ribbon_checks_pass'];d.getObject('eye_primary_Cap').Visibility=True
  import FreeCADGui as G
  G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();G.updateGui();G.activeDocument().activeView().saveImage(str(OUT/'assembly.png'),1400,1000,'White')
 d.saveAs(str(OUT/'mouse-arm-free-r02.FCStd'));d.Label='Mouse arm-free R02 - exploratory camera layout';d.save();print(json.dumps(report,indent=2),flush=True);return d
if __name__=='__main__':build()
