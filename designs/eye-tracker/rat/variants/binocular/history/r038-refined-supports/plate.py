from common import *
import shutil
d=load('02-lower');old=local(d.CentralCarrier);xmin=2.68706399647303;xmax=xmin+1.2
slab=Part.makeBox(1.2,11.1,60,A.Vector(xmin,6.5,-30));spine=old.common(slab)
copies=[]
for dx in [-.3,0,.3]:s=spine.copy();s.translate(A.Vector(dx,0,0));copies.append(s)
new=copies[0].multiFuse(copies[1:])
stem=old.common(Part.makeBox(40,26.5,60,A.Vector(-20,-20,-30)))
pieces=[stem]
for x,dx in [(-20,-.3),(xmax,.3)]:
 width=xmin+20 if dx<0 else 20-xmax
 s=old.common(Part.makeBox(width,30,60,A.Vector(x,6.5,-30)));s.translate(A.Vector(dx,0,0));pieces.append(s)
new=new.multiFuse(pieces).removeSplitter();assert new.isValid() and len(new.Solids)==1
assign(d.CentralCarrier,moved(new,T));new.exportBrep(str(O/'central.brep'))
for f in PO.glob('*.brep'):
 if f.name not in ['central.brep','carrier.brep']:shutil.copy2(f,O/f.name)
for side,dx in [('Right',.3),('Left',-.3)]:
 components={}
 for name in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001']:
  s=Part.Shape();s.read(str(O/(side+'-'+name+'.brep')))
  if name in ['PCB','JST_4pin']:s.translate(A.Vector(dx,0,0))
  components[name]=s;s.exportBrep(str(O/(side+'-'+name+'.brep')))
  assert s.common(new).Volume<1e-5,(side,name,s.common(new).Volume)
 cam=d.getObject(side+'Camera');cam.PhysicalParts[0].Shape=Part.makeCompound([components['PCB'],components['camera_pcb']]);cam.PhysicalParts[2].Shape=Part.makeCompound([components[n] for n in ['JST_4pin','IR_LED','IR_LED_001']])
 cfg['sides'][side]['board_transform'][0][3]+=dx
carrier=rebuild(d);carrier.exportBrep(str(O/'carrier.brep'))
cfg.update(revision='ET-RAT-REFINED-SUPPORTS-R38',source_complete_assembly=json.loads((P/'review.json').read_text()),pcb_support_thickness_mm=1.8,main_pcb_outward_shift_each_mm=.3)
(S/'recipe.json').write_text(json.dumps(cfg,indent=2))
report={'units':'mm','old_support_thickness_mm':1.2,'new_support_thickness_mm':1.8,'increase_percent':50,'pcbs_and_retaining_features_shift_each_mm':.3,'camera_heads_unchanged':True,'skull_baseplate_unchanged':True,'central_valid_single_solid':True,'old_central_volume_mm3':old.Volume,'new_central_volume_mm3':new.Volume}
save(d,'plate-working',report)
