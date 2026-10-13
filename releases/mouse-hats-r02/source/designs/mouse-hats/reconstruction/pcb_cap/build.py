"""Rebuild RightCap with native sketches, extrusions, union and drilled holes."""
from pathlib import Path
import json
import FreeCAD as App
import Part,Sketcher
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/pcb-cap'

def profile(doc,name,points,direction):
    origin=App.Vector(*points[0])
    rotation=App.Rotation(App.Vector(0,0,1),direction)
    local=[rotation.inverted().multVec(App.Vector(*v)-origin) for v in points]
    obj=doc.addObject('Sketcher::SketchObject',name)
    for p,q in zip(local,local[1:]+local[:1]):
        assert abs(p.z)<1e-7
        i=obj.addGeometry(Part.LineSegment(App.Vector(p.x,p.y,0),App.Vector(q.x,q.y,0)),False)
        obj.addConstraint(Sketcher.Constraint('Block',i))
    obj.Placement=App.Placement(origin,rotation)
    return obj

def main(save=True):
    p=json.loads((HERE/'parameters.json').read_text())
    doc=App.newDocument('PCBCapRebuild58')
    dims=doc.addObject('App::FeaturePython','Dimensions')
    for name,value in [('CoverThickness',1),('VentRadius',p['holes'][1]['radius_mm']),('SideHoleRadius',p['holes'][0]['radius_mm'])]:
        dims.addProperty('App::PropertyLength',name,'Dimensions');setattr(dims,name,value)
    construction=doc.addObject('App::DocumentObjectGroup','Construction')
    parts=[]
    for f in p['features']:
        delta=App.Vector(*f['extrusion_mm']);length=delta.Length;direction=delta/length
        sketch=profile(doc,f['name']+'Profile',f['profile_mm'],direction)
        solid=doc.addObject('Part::Extrusion',f['name'])
        solid.Base=sketch;solid.Dir=direction;solid.Solid=True;solid.LengthFwd=length
        if f['name'] in ['UpperCover','LowerCover']:
            solid.setExpression('LengthFwd','Dimensions.CoverThickness')
        parts.append(solid);construction.addObjects([sketch,solid])
    shell=doc.addObject('Part::MultiFuse','CapShell')
    shell.Shapes=parts;shell.Refine=True
    cutters=[]
    for h in p['holes']:
        tool=doc.addObject('Part::Cylinder',h['name']+'Tool')
        axis=App.Vector(*h['axis'])
        # Extend beyond both surfaces so thickness edits retain through-holes.
        tool.Placement=App.Placement(App.Vector(*h['origin_mm'])-axis,App.Rotation(App.Vector(0,0,1),axis))
        tool.Height=h['length_mm']+2
        control='SideHoleRadius' if h['name']=='SideHole' else 'VentRadius'
        tool.setExpression('Radius','Dimensions.'+control)
        cutters.append(tool)
    holes=doc.addObject('Part::Compound','HoleTools');holes.Links=cutters
    final=doc.addObject('Part::Cut','PCBCap')
    final.Label='Rebuilt PCB cap — 58 RightCap'
    final.Base=shell;final.Tool=holes;final.Refine=True
    construction.addObjects([shell,holes]+cutters)
    doc.recompute();final.Shape.check(True)
    assert len(final.Shape.Solids)==1
    if App.GuiUp:
        for obj in doc.Objects:obj.Visibility=False
        final.Visibility=True
        final.ViewObject.ShapeColor=(0.2,0.8,0.9);final.ViewObject.LineColor=(0.12,0.18,0.2)
    OUT.mkdir(parents=True,exist_ok=True)
    if save:doc.saveAs(str(OUT/'01-pcb-cap-candidate.FCStd'))
    print('Built',final.Shape.Volume,'mm3;',len(final.Shape.Faces),'faces',flush=True)
    return doc

if __name__=='__main__':main()
