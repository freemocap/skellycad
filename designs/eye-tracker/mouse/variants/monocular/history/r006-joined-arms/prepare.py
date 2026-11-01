import FreeCAD as A,Part,json,sys,hashlib
from pathlib import Path
r=Path.cwd();out=r/'generated/eye-tracker/mouse/joined-arms-r06';sys.path.insert(0,str(r/'designs/mouse-hats/b-flared-loop-r07'));from flared_arm import rectangle,unit
m=json.loads((r/'designs/eye-tracker/mouse/active-model.json').read_text());assert hashlib.sha256((r/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256']
d=A.openDocument(str(r/'generated/eye-tracker/mouse/restored-arms-r05/mouse-restored-arms-r05.FCStd'));cfgs=json.loads((r/'generated/eye-tracker/mouse/restored-arms-r05/validation.json').read_text())['arms'];tray=d.getObject('RetainedPCBTray').Shape;socket=d.getObject('RetainedSocket').Shape.copy();socket.fixTolerance(1e-6);socket.check(True)
arms={};anchors=[]
for name,cfg in cfgs.items():
 n=unit(cfg['socket_axis']);radial=unit(cfg['arm']['radial_direction']);c=A.Vector(*cfg['socket_center_mm']);end=c+n*cfg['attachment_height_mm']+radial*cfg['attachment_radius_mm'];target=unit(radial.cross(n))
 old=rectangle(end+radial*.25,-radial,target,3.,2.2);deep=rectangle(end-radial*.8,-radial,target,3.,2.2)
 extension=Part.makeLoft([old,deep],True,True);arms[name]=d.getObject(name).Shape.fuse(extension).removeSplitter();anchors.extend([A.Vector(*cfg['arm']['root_mm']),end]);print(name,'socket overlap',arms[name].common(socket).Volume,flush=True)
fused=tray.fuse(socket).fuse(arms['UpperSupport']).fuse(arms['RearRibbonGuard']).removeSplitter();print('fused',fused.isValid(),len(fused.Solids),flush=True)
fused.exportBrep(str(out/'unblended.brep'))
for i,e in enumerate([]):
 center=e.CenterOfMass;dist=min((center-p).Length for p in anchors)
 if dist<3:
  print(i+1,round(e.Length,3),tuple(round(x,3) for x in center),'anchor',min(range(4),key=lambda j:(center-anchors[j]).Length),str(type(e.Curve).__name__),flush=True)
for name,sh in arms.items():sh.exportBrep(str(out/(name+'.brep')))
(out/'anchors.json').write_text(json.dumps([list(x) for x in anchors]))

