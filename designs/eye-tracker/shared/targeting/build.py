"""Build the ribbon and unblended carrier; reject invalid interfaces."""
from pathlib import Path
import json,numpy as np
import FreeCAD as A,Part
from ribbon import ribbon_solid
import ribbon_geometry as g

def build(out):
 out=Path(out);solved=json.loads((out/'solve.json').read_text());target=np.array(json.loads((out/'target.json').read_text())['sensor_in_mount']);pos,R=g.endpoint(solved['parameters']);assert np.linalg.norm(pos[0]-target[:3,3])<1e-5 and np.linalg.norm(R-target[:3,:3])<1e-5
 rib,mesh,metric=ribbon_solid(solved['parameters']);rib.exportBrep(str(out/'ribbon.brep'));mesh.write(str(out/'ribbon.stl'));shapes={};overlaps={}
 for name in ['RetainedPCBTray','RetainedSocket','eye_primary_Holder','eye_primary_Cap','eye_primary_Clip','skull_mount_Baseplate','UpperSupport','RearRibbonGuard']:
  sh=Part.Shape();sh.read(str(out/(name+'.brep')));shapes[name]=sh;overlaps[name]=rib.common(sh).Volume;print('ribbon overlap',name,overlaps[name],flush=True)
 assert max(overlaps.values())<1e-6,'Ribbon intersects hardware; refine pose or route before assembly'
 carrier=shapes['RetainedPCBTray'].multiFuse([shapes[x] for x in ['RetainedSocket','UpperSupport','RearRibbonGuard']]).removeSplitter();carrier.limitTolerance(1e-6);carrier.check(True);assert carrier.isValid() and len(carrier.Solids)==1,'Arms must attach tray to socket as one solid';carrier.exportBrep(str(out/'unblended.brep'))
 report={'units':'mm','ribbon':dict(solved,metric=metric,closed=mesh.isSolid(),self_intersection=mesh.hasSelfIntersections(),overlaps_mm3=overlaps),'unblended_carrier_solids':len(carrier.Solids)};(out/'build-validation.json').write_text(json.dumps(report,indent=2));return report
