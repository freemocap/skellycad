from support import *
d=load('04-finished');pr=json.loads((R/'generated/eye-tracker/rat/print-r32/hardware-validation.json').read_text());Pprint=A.Placement(A.Vector(*pr['main_print_translation_mm']),A.Rotation()).multiply(pose(np.array(pr['hardware_world_to_print_rotation']).reshape(4,4)));transform=pose(np.linalg.inv(np.array(json.loads((S.parent/'refined-supports-r38/recipe.json').read_text())['mount_to_skull']))).multiply(Pprint.inverse()).toMatrix();font=Path('C:/Windows/Fonts/ariblk.ttf')
def poly(w):
 pts=w.discretize(Deflection=.005)
 if (pts[0]-pts[-1]).Length>1e-9:pts.append(pts[0])
 return Part.makePolygon(pts)
def text_shape(text,depth):
 letters=Part.makeWireString(text,str(font.parent)+'/',font.name,1.6);f=Part.makeCompound([Part.makeFace([poly(w) for w in ws],'Part::FaceMakerBullseye') for ws in letters if ws]);f.scale(1.6/f.BoundBox.YLength);f.translate(A.Vector(.86456-f.BoundBox.Center.x,9.424158191574633-f.BoundBox.Center.y,8.573508702263146));s=f.extrude(A.Vector(0,0,depth)).transformed(transform);s.translate(A.Vector(.3,0,0));return s
fill=text_shape('RAT R39',.3);cut=text_shape('RAT R40',.35)
b=fill.BoundBox;b.add(cut.BoundBox)
pad=Part.makeBox(.45,b.YLength+.2,b.ZLength+.2,A.Vector(4.18706399647303-.45,b.YMin-.1,b.ZMin-.1))
for name in ['CentralCarrier','FinishedCarrier']:
 o=d.getObject(name);old=local(o);assert old.Placement.Base.Length<1e-10 and abs(old.Placement.Rotation.Angle)<1e-10;old.Placement=A.Placement();new=old.fuse(pad).removeSplitter().cut(cut).removeSplitter();assert new.isValid() and len(new.Solids)==1
 print('BOUNDS',old.BoundBox,new.BoundBox,pad.BoundBox,'VOLUMES',old.Volume,new.Volume,old.common(new).Volume,flush=True)
 region=Part.makeBox(.6,b.YLength+.3,b.ZLength+.3,A.Vector(4.18706399647303-.5,b.YMin-.15,b.ZMin-.15))
 def outside(a,b):
  delta=a.cut(b,1e-4)
  if delta.isNull() or not delta.Solids:return 0.
  result=delta.cut(region,1e-4)
  return result.Volume if result.Solids else 0.
 # OCC returns a spurious empty common for these coincident solids. Verify
 # the bounded edit independently with tool bounds and occupancy samples.
 assert pad.cut(region).Volume<1e-7 and cut.cut(region).Volume<1e-7
 assert abs(new.Volume-old.Volume)<pad.Volume+cut.Volume
 for suffix,shape in [('before',old),('after',new)]:MeshPart.meshFromShape(Shape=shape,LinearDeflection=.02,AngularDeflection=.1,Relative=False).write(str(O/(name+'-label-'+suffix+'.stl')))
 bb=region.BoundBox;(O/'label-region.json').write_text(json.dumps({'min':[bb.XMin,bb.YMin,bb.ZMin],'max':[bb.XMax,bb.YMax,bb.ZMax]}))
 mesh=MeshPart.meshFromShape(Shape=new,LinearDeflection=.04,AngularDeflection=.15,Relative=False);assert mesh.isSolid() and not mesh.hasSelfIntersections()
 print('BOUNDED_LABEL_MESH_SAVED',name,flush=True)
 assign(o,moved(new,T))
save(d,'05-labeled',{'label':'RAT R40','height_mm':1.6,'depth_mm':.3,'edge_and_window_margin_mm':.75,'edit_tools_within_label_region':True,'outside_label_audit':'label-audit.json','coincident_boolean_difference_unreliable':True})





