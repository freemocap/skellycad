from pathlib import Path
import json,numpy as np
import FreeCAD as A,Part,MeshPart
R=Path.cwd();S=R/'designs/eye-tracker/rat/eye-world-print-r06';O=R/'generated/eye-tracker/rat/eye-world-print-r06';cfg=json.loads((S.parent/'lowered-cameras-r43/recipe.json').read_text());T=np.array(cfg['mount_to_skull']);inv=A.Matrix(*np.linalg.inv(T).ravel().tolist())
pr=json.loads((R/'generated/eye-tracker/rat/print-r32/hardware-validation.json').read_text());Pprint=A.Placement(A.Vector(*pr['main_print_translation_mm']),A.Rotation()).multiply(A.Placement(A.Matrix(*np.array(pr['hardware_world_to_print_rotation']).ravel().tolist())));transform=A.Placement(A.Matrix(*np.linalg.inv(np.array(json.loads((S.parent/'refined-supports-r38/recipe.json').read_text())['mount_to_skull'])).ravel().tolist())).multiply(Pprint.inverse()).toMatrix();font=Path('C:/Windows/Fonts/ariblk.ttf')
def wire(w):
 pts=w.discretize(Deflection=.005)
 if (pts[0]-pts[-1]).Length>1e-9:pts.append(pts[0])
 return Part.makePolygon(pts)
def face(text):
 letters=Part.makeWireString(text,str(font.parent)+'/',font.name,1.6);f=Part.makeCompound([Part.makeFace([wire(w) for w in ws],'Part::FaceMakerBullseye') for ws in letters if ws]);f.scale(1.6/f.BoundBox.YLength);return f
old=face('RAT R43');new=face('RAT W06');scale=min(1.,old.BoundBox.XLength/new.BoundBox.XLength);mat=A.Matrix();mat.A11=scale;new=new.transformGeometry(mat)
def tool(f,depth):
 f.translate(A.Vector(.86456-f.BoundBox.Center.x,9.424158191574633-f.BoundBox.Center.y,8.573508702263146));s=f.extrude(A.Vector(0,0,depth)).transformed(transform);s.translate(A.Vector(.3,0,0));return s
fill=tool(old,.35);cut=tool(new,.35);b=fill.BoundBox;pad=Part.makeBox(.45,b.YLength+.2,b.ZLength+.2,A.Vector(4.18706399647303-.45,b.YMin-.1,b.ZMin-.1));region=Part.makeBox(.6,b.YLength+.3,b.ZLength+.3,A.Vector(4.18706399647303-.5,b.YMin-.15,b.ZMin-.15));assert cut.cut(region).Volume<1e-7
s=Part.Shape();s.read(str(O/'finished-carrier.brep'));s=s.transformed(inv);before=s.Volume;s.exportBrep(str(O/'unlabeled-carrier-mount.brep'));updated=s.fuse(pad).removeSplitter().cut(cut).removeSplitter();assert updated.isValid() and len(updated.Solids)==1;assert abs(updated.Volume-before)<pad.Volume+cut.Volume
updated.transformed(A.Matrix(*T.ravel().tolist())).exportBrep(str(O/'finished-carrier.brep'));(O/'label-validation.json').write_text(json.dumps({'text':'RAT W06','height_mm':1.6,'depth_mm':.35,'text_width_scale':scale,'functional_openings_changed':False,'label_tools_confined_to_existing_rail':True,'volume_delta_mm3':updated.Volume-before},indent=2));print('LABEL',updated.Volume-before,flush=True)
