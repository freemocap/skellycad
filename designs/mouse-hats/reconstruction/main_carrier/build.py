"""Rebuild the 58 PCB tray and mounting stem, deliberately excluding the old arm.

Run in the pinned FreeCAD runtime. The measured profile JSON is the only modeling
input; the STEP/BREP is used solely as an optional visible comparison reference.
"""
from pathlib import Path
import json,sys
import FreeCAD as App
import Part,Sketcher

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/main-carrier'
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
from carrier_features import ToleranceUnion

def sketch(doc,name,points):
    points=[App.Vector(*p) for p in points]
    origin=points[0]
    normal=App.Vector()
    for p,q in zip(points,points[1:]+points[:1]):normal+=p.cross(q)
    normal.normalize()
    rotation=App.Rotation(App.Vector(0,0,1),normal)
    local=[rotation.inverted().multVec(p-origin) for p in points]
    obj=doc.addObject('Sketcher::SketchObject',name)
    for p,q in zip(local,local[1:]+local[:1]):
        assert abs(p.z)<1e-5
        i=obj.addGeometry(Part.LineSegment(App.Vector(p.x,p.y,0),App.Vector(q.x,q.y,0)),False)
        obj.addConstraint(Sketcher.Constraint('Block',i))
    obj.Placement=App.Placement(origin,rotation)
    return obj

def main(save=True, profiles_data=None):
    params=profiles_data if profiles_data is not None else json.loads((HERE/'profiles.json').read_text())
    settings=json.loads((HERE/'parameters.json').read_text())
    doc=App.newDocument('TrayMountRebuild58')
    construction=doc.addObject('App::DocumentObjectGroup','Construction')
    dims=doc.addObject('App::FeaturePython','Dimensions')
    dims.addProperty('App::PropertyLength','VentRadius','PCB tray');dims.VentRadius=settings['vent_radius_mm']
    dims.addProperty('App::PropertyLength','VentSpacing','PCB tray');dims.VentSpacing=settings['vent_spacing_mm']
    solids=[]
    for feature in params['features']:
        name=feature['name']
        profiles=[sketch(doc,name+suffix,p) for suffix,p in zip(['Rear','Front'],feature['profiles_mm'])]
        item=doc.addObject('Part::Loft',name)
        item.Sections=profiles;item.Solid=True;item.Ruled=True
        construction.addObjects(profiles+[item]);solids.append(item)
    # Rear stem: intersect eight measured planes with a bounded stock box.
    stock=doc.addObject('Part::Box','RearStemStock')
    stock.Length=8;stock.Width=9.06588286441312-6;stock.Height=8
    stock.Placement.Base=App.Vector(-1,6,-4)
    construction.addObject(stock)
    for i,plane in enumerate(params['core_planes']):
        normal=App.Vector(*plane['normal'])
        rotation=App.Rotation(App.Vector(0,0,1),normal)
        tool=doc.addObject('Part::Box',f'StemPlaneTool{i}')
        tool.Length=100;tool.Width=100;tool.Height=100
        tool.Placement=App.Placement(normal*plane['offset_mm']+rotation.multVec(App.Vector(-50,-50,0)),rotation)
        cut=doc.addObject('Part::Cut',f'StemPlaneCut{i}')
        cut.Base=stock;cut.Tool=tool;cut.Refine=True
        construction.addObjects([tool,cut]);stock=cut
    notch=doc.addObject('Part::Box','StemTrayReliefTool')
    notch.Length=10;notch.Width=10;notch.Height=20
    notch.Placement.Base=App.Vector(4.287063996473026,8.16835866236362,-10)
    core=doc.addObject('Part::Cut','StemTrayRelief')
    core.Base=stock;core.Tool=notch;core.Refine=True
    construction.addObjects([notch,core]);solids.append(core)
    union=doc.addObject('Part::FeaturePython','TrayAndStemUnion')
    ToleranceUnion(union);union.Sources=solids
    union.JoinTolerance=settings['join_tolerance_mm']
    construction.addObject(union)
    tools=[]
    for i in range(2):
        hole=doc.addObject('Part::Cylinder',f'VentTool{i+1}')
        hole.Height=5;hole.setExpression('Radius','Dimensions.VentRadius')
        hole.Placement=App.Placement(App.Vector(2,11.9423591269588,-12.9033786820894),App.Rotation(App.Vector(0,1,0),90))
        if i:hole.setExpression('Placement.Base.z','-12.9033786820894 mm + Dimensions.VentSpacing')
        tools.append(hole)
    vents=doc.addObject('Part::MultiFuse','VentTools');vents.Shapes=tools
    result=doc.addObject('Part::Cut','PCBTrayAndMount')
    result.Label='PCB tray + mounting stem (arm omitted)'
    result.Base=union;result.Tool=vents;result.Refine=True
    construction.addObjects(tools+[vents])
    doc.recompute()
    assert result.Shape.isValid() and len(result.Shape.Solids)==1
    result.Shape.check(True)
    if App.GuiUp:
        for obj in construction.Group:obj.Visibility=False
        dims.Visibility=False
        result.ViewObject.ShapeColor=(0.2,0.8,0.9)
        result.ViewObject.LineColor=(0.12,0.18,0.2)
        result.Visibility=True
    OUT.mkdir(parents=True,exist_ok=True)
    doc.recompute()
    if save:doc.saveAs(str(OUT/'01-tray-mount-candidate.FCStd'))
    print('Built',result.Shape.Volume,'mm3;',len(result.Shape.Faces),'faces',flush=True)
    return doc

if __name__=='__main__':main()
