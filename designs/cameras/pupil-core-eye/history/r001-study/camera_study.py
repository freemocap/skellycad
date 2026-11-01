"""Shared camera geometry study. Run with FreeCAD Python or through open.FCMacro."""
from pathlib import Path
import json, math, hashlib
import FreeCAD as App
import Part, Mesh
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
OUT=ROOT/'generated/eye-tracker/shared/camera-study-r01'
V=App.Vector

def load_scene():
    data=json.loads((HERE/'blender-scene.json').read_text())
    assert hashlib.sha256((HERE.parent/'pupil-core-eye-camera.blend').read_bytes()).hexdigest()==data['source_sha256'], 'Re-export modified Blender source first'
    return {o['name']:o for o in data['objects']}

def boundary(vertices, triangles):
    counts={}
    for tri in triangles:
        for a,b in zip(tri,tri[1:]+tri[:1]):
            key=tuple(sorted((a,b))); counts[key]=counts.get(key,0)+1
    edges=[e for e,c in counts.items() if c==1]
    loop=[edges[0][0]]
    while edges:
        edge=next(e for e in edges if loop[-1] in e)
        edges.remove(edge); loop.append(edge[1] if edge[0]==loop[-1] else edge[0])
    assert loop[0]==loop[-1]
    return Part.makePolygon([V(*vertices[i]) for i in loop])

def rigid_shape(o, origin):
    vertices=[[p[i]-origin[i] for i in range(3)] for p in o['vertices']]
    if max(p[2] for p in vertices)-min(p[2] for p in vertices)<1e-8:
        # Preserve the complete supplied outline, including sensor board notch.
        shape=Part.Face(boundary(vertices,o['triangles'])).extrude(V(0,0,-.25))
    else:
        mesh=Mesh.Mesh([[V(*vertices[i]) for i in tri] for tri in o['triangles']])
        shape=Part.Shape(); shape.makeShapeFromMesh(mesh.Topology,1e-6)
        shape=Part.makeSolid(shape).removeSplitter()
    assert shape.isValid() and len(shape.Solids)==1 and shape.Volume>0, o['name']
    return shape

def ribbon_shape(length,width,thickness,degrees):
    """Exact cylindrical bend: neutral mid-surface is isometric to a rectangle."""
    if not 0<=degrees<=180: raise ValueError('Bend angle must be between 0 and 180 degrees')
    if min(length,width,thickness)<=0: raise ValueError('Dimensions must be positive')
    a=math.radians(degrees)
    if a<1e-8:
        return Part.makeBox(width,length,thickness,V(-width/2,0,-thickness/2)), V(0,length,0), App.Rotation(), None
    r=length/a
    if r<=thickness/2: raise ValueError('Bend radius is smaller than half the thickness')
    def point(radius,angle): return V(-width/2,radius*math.sin(angle),r-radius*math.cos(angle))
    inner,outer=r-thickness/2,r+thickness/2
    edges=[Part.Arc(point(inner,0),point(inner,a/2),point(inner,a)).toShape(),
           Part.makeLine(point(inner,a),point(outer,a)),
           Part.Arc(point(outer,a),point(outer,a/2),point(outer,0)).toShape(),
           Part.makeLine(point(outer,0),point(inner,0))]
    shape=Part.Face(Part.Wire(edges)).extrude(V(width,0,0))
    return shape,V(0,r*math.sin(a),r*(1-math.cos(a))),App.Rotation(V(1,0,0),degrees),r

class RibbonProxy:
    def __init__(self,obj):obj.Proxy=self
    def execute(self,obj):
        shape,end,rotation,r=ribbon_shape(obj.FreeLength.Value,obj.Width.Value,obj.Thickness.Value,obj.BendDegrees)
        obj.Shape=shape
        obj.Head.Placement=App.Placement(end,rotation)
        obj.RadiusDescription='Straight' if r is None else f'{r:.4f} mm (neutral surface)'
    def dumps(self):return None
    def loads(self,state):pass

def add_shape(doc,parent,name,shape,color):
    obj=doc.addObject('PartDesign::Feature',name.replace('-','_').replace('.','_'))
    obj.Label=name;obj.Shape=shape;parent.addObject(obj)
    obj.addProperty('App::PropertyString','SourceName','Evidence').SourceName=name
    if App.GuiUp:obj.ViewObject.ShapeColor=color
    return obj

def create_camera(doc,name,degrees=90,offset=(0,0,0),scene=None):
    scene=load_scene() if scene is None else scene
    ribbon=scene['ribbon']['vertices']
    x0=min(p[0] for p in ribbon);x1=max(p[0] for p in ribbon)
    y0=min(p[1] for p in ribbon);y1=max(p[1] for p in ribbon)
    origin=((x0+x1)/2,y0,0);head_origin=(origin[0],y1,0)
    root=doc.addObject('App::Part',name);root.Label=f'{name} - {degrees:g} degrees'
    root.Placement.Base=V(*offset)
    main=doc.addObject('App::Part',name+'Main');main.Label='Main PCB + connector (rigid)';root.addObject(main)
    head=doc.addObject('App::Part',name+'Head');head.Label='Camera PCB + lens + LEDs (rigid)';root.addObject(head)
    colors={'PCB':(.13,.42,.22),'camera-pcb':(.22,.5,.3),'M4-lens':(.13,.15,.19),'JST-4pin':(.92,.9,.8),'IR-LED':(.7,.2,.25),'IR-LED.001':(.7,.2,.25)}
    for label,o in scene.items():
        if label=='ribbon':continue
        is_main=label in ('PCB','JST-4pin')
        add_shape(doc,main if is_main else head,label,rigid_shape(o,origin if is_main else head_origin),colors[label])
    flex=doc.addObject('PartDesign::FeaturePython',name+'Ribbon');flex.Label='Ribbon - edit BendDegrees';root.addObject(flex)
    flex.addProperty('App::PropertyFloatConstraint','BendDegrees','Routing').BendDegrees=(degrees,0,180,1)
    for prop,value in [('FreeLength',y1-y0),('Width',x1-x0),('Thickness',.15)]:
        flex.addProperty('App::PropertyLength',prop,'Routing');setattr(flex,prop,value);flex.setEditorMode(prop,1)
    flex.addProperty('App::PropertyLink','Head','Routing').Head=head;flex.setEditorMode('Head',1)
    flex.addProperty('App::PropertyString','RadiusDescription','Routing');flex.setEditorMode('RadiusDescription',1)
    flex.addProperty('App::PropertyString','Limitations','Evidence').Limitations='Provisional mm scale; 0.15 mm ribbon and 0.25 mm boards assumed. Prescribed bend, not equilibrium or certified bend radius.'
    RibbonProxy(flex)
    if App.GuiUp:
        flex.ViewObject.Proxy=0
        flex.ViewObject.ShapeColor=(.87,.52,.08)
    # Optical direction is a provisional +Z normal to the head PCB.
    lens=scene['M4-lens']['vertices']
    center=[sum(p[i] for p in lens)/len(lens)-head_origin[i] for i in range(3)]
    guide=add_shape(doc,head,'Optical direction - provisional',Part.makeCylinder(.10,7,V(*center)),(.1,.6,1.))
    guide.addProperty('App::PropertyString','Purpose').Purpose='Guide only; source has no optical calibration'
    doc.recompute()
    return root,flex

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    doc=App.newDocument('CameraFlexStudyR01');doc.Label='Camera study R01 - straight / 90 / 180 degrees'
    records=[]
    for i,angle in enumerate((0,90,180)):
        root,flex=create_camera(doc,'Camera'+str(angle),angle,(i*44,0,0))
        length=flex.FreeLength.Value;width=flex.Width.Value;t=flex.Thickness.Value
        assert flex.Shape.isValid() and len(flex.Shape.Solids)==1
        assert abs(flex.Shape.Volume-length*width*t)<1e-6
        radius=None if angle==0 else length/math.radians(angle)
        assert radius is None or abs(radius*math.radians(angle)-length)<1e-12
        # Exercise recomputation and verify rigid head follows the ribbon endpoint.
        assert (flex.Head.Placement.Base-ribbon_shape(length,width,t,angle)[1]).Length<1e-9
        records.append({'angle_degrees':angle,'neutral_length_mm':length,'neutral_radius_mm':radius,'volume_mm3':flex.Shape.Volume,'head_origin_mm':list(flex.Head.Placement.Base),'valid_solid':True})
    doc.recompute()
    native=OUT/'camera-flex-study-r01.FCStd';doc.saveAs(str(native))
    doc.Label='Camera study R01 - straight / 90 / 180 degrees';doc.save()
    # STEP is a static geometry snapshot; the native macro retains parametric behavior.
    solids=[o for o in doc.Objects if o.TypeId in ('PartDesign::Feature','PartDesign::FeaturePython') and not o.Label.startswith('Optical direction')]
    copies=[]
    for obj in solids:
        shape=obj.Shape.copy();shape.Placement=obj.getGlobalPlacement();copies.append(shape)
    Part.makeCompound(copies).exportStep(str(OUT/'camera-flex-study-r01.step'))
    (OUT/'validation.json').write_text(json.dumps({'status':'Geometric study only','variants':records,'solid_count':len(copies),'native':str(native)},indent=2))
    if App.GuiUp:
        import FreeCADGui as Gui
        Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll();Gui.updateGui()
        Gui.activeDocument().activeView().saveImage(str(OUT/'preview.png'),1400,1000,'White')
    return doc

if __name__=='__main__':build()
