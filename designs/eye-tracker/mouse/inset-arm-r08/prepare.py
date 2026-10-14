import FreeCAD as A,Part,json,sys,hashlib
from pathlib import Path
r=Path.cwd();out=r/'generated/eye-tracker/mouse/inset-arm-r08';sys.path.insert(0,str(r/'designs/mouse-hats/b-flared-loop-r07'));from flared_arm import rectangle,unit,geometry
m=json.loads((r/'designs/eye-tracker/mouse/active-model.json').read_text());assert hashlib.sha256((r/m['native_checkpoint']).read_bytes()).hexdigest()==m['native_sha256']
p=json.loads((r/'designs/eye-tracker/mouse/joined-arms-r06/print-test.json').read_text());assert hashlib.sha256((r/p['native_checkpoint']).read_bytes()).hexdigest()==p['native_sha256']
d=A.openDocument(str(r/p['native_checkpoint']));cfgs=json.loads((r/'designs/eye-tracker/mouse/inset-arm-r08/input-parameters.json').read_text())['arms'];tray=d.RetainedPCBTray.Shape;socket=d.RetainedSocket.Shape.copy();socket.fixTolerance(1e-6);socket.check(True)
arms={};anchors=[]
for name,cfg in cfgs.items():
 if name=='UpperSupport':cfg['attachment_height_mm']=4.2
 n=unit(cfg['socket_axis']);radial=unit(cfg['arm']['radial_direction']);c=A.Vector(*cfg['socket_center_mm']);end=c+n*cfg['attachment_height_mm']+radial*cfg['attachment_radius_mm'];target=unit(radial.cross(n))
 original=geometry(cfg,cfg['body_width_mm'],cfg['body_thickness_mm'])[0] if name=='UpperSupport' else d.getObject(name).Shape
 old=rectangle(end+radial*.25,-radial,target,3.,2.2);deep=rectangle(end-radial*.8,-radial,target,3.,2.2)
 arms[name]=original.fuse(Part.makeLoft([old,deep],True,True)).removeSplitter();anchors.extend([A.Vector(*cfg['arm']['root_mm']),end]);print(name,'socket overlap',arms[name].common(socket).Volume,'ribbon overlap',arms[name].common(d.RibbonCandidate.Shape).Volume,'ribbon gap',arms[name].distToShape(d.RibbonCandidate.Shape)[0],flush=True)
 arms[name].exportBrep(str(out/(name+'.brep')))
fused=tray.fuse(socket).fuse(arms['UpperSupport']).fuse(arms['RearRibbonGuard']).removeSplitter();fused.limitTolerance(1e-6);fused.check(True);assert fused.isValid() and len(fused.Solids)==1
fused.exportBrep(str(out/'unblended.brep'));(out/'arms.json').write_text(json.dumps(cfgs,indent=2));(out/'anchors.json').write_text(json.dumps([list(x) for x in anchors]))
print('PASS solid',flush=True)
