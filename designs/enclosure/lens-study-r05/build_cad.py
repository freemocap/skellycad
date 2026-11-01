"""Native FreeCAD study: preserved R01 frame, five camera poses, exact frustum cells."""
from pathlib import Path
import hashlib
import itertools
import json
import os
import traceback
import zipfile
import FreeCAD as App
import FreeCADGui as Gui
import Part
import numpy as np
from PySide import QtCore, QtWidgets
from geometry import basis, frustum_vertices, visibility

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'generated/enclosure/lens-study-r05'
BASE=ROOT/'generated/enclosure/starter-cube-r01'
V=App.Vector
COLORS=[(.18,.52,.85),(.95,.46,.16),(.58,.32,.77),(.12,.65,.54),(.82,.64,.10)]
Gui.showMainWindow()
Gui.getMainWindow().hide()
app=QtWidgets.QApplication.instance()
app.setQuitOnLastWindowClosed(False)


def solid(vertices):
    vertices=[V(*p) for p in vertices]
    faces=[]
    for indices in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        p=[vertices[i] for i in indices]
        faces.append(Part.Face(Part.makePolygon(p+[p[0]])))
    s=Part.makeSolid(Part.makeShell(faces))
    if s.Volume<0:s.reverse()
    assert s.isValid() and s.Volume>0
    return s


def build():
    (OUT/'cad-validation.json').write_text(json.dumps({'status':'running'})+'\n')
    cameras=json.loads((OUT/'selected-layout.json').read_text())['cameras']
    assert all(250 <= c['position_mm'][2] <= 300 for c in cameras[:4]), 'Corner camera height must be 250-300 mm'
    record=json.loads((BASE/'validation.json').read_text())
    native=BASE/'starter-cube-r01.FCStd'
    assert hashlib.sha256(native.read_bytes()).hexdigest()==record['sha256'], 'R01 file changed from recorded hash'
    baseline=App.openDocument(str(native))
    parts=[(o.Name,o.Shape.copy(),o.ViewObject.ShapeColor) for o in baseline.Objects
           if o.TypeId=='PartDesign::Feature' and (o.Name.startswith(('Post_','Rail','Joint','CrossbarJoint')) or o.Name=='TopCenterCrossbar')]
    App.closeDocument(baseline.Name)
    doc=App.newDocument('LensStudyR05')
    doc.Label='LENS R05 - ideal geometry - floor/lower 200 mm priority'
    groups={name:doc.addObject('App::DocumentObjectGroup',name) for name in
        ('Frame','CameraEnvelopes','MountConcepts','UsableFrustums','FullFrustums','ClippedViews','OverlapCells','OverlapSummary')}
    def add(name,shape,group,color,visible=True,transparency=0):
        o=doc.addObject('PartDesign::Feature',name);o.Shape=shape;groups[group].addObject(o)
        o.ViewObject.ShapeColor=color;o.ViewObject.LineColor=color;o.ViewObject.Transparency=transparency;o.Visibility=visible
        return o
    for name,shape,color in parts:add(name,shape,'Frame',color)
    doc.recompute();path=OUT/'lens-study-r05.FCStd';doc.saveAs(str(path))
    offset=np.array([20,20,20])
    cube=Part.makeBox(500,500,500,V(*offset))
    lower=Part.makeBox(500,500,200,V(*offset))
    add('PriorityLower200mm',lower,'OverlapSummary',(.55,.70,.70),False,90)
    clipped=[];bodies=[];frustums=[]
    for i,c in enumerate(cameras):
        p=np.array(c['position_mm'])+offset;axes=basis(c);f=axes[2]
        local=np.array([[x,y,z] for z in (-45,-15) for x,y in ((-18,-15),(18,-15),(18,15),(-18,15))])
        body=solid(local@axes+p)
        lens=Part.makeCylinder(15,40,V(*(p-f*40)),V(*f))
        for distance in (8,20,32):
            lens=lens.fuse(Part.makeCylinder(17,4,V(*(p-f*distance)),V(*f)))
        assembly=body.fuse(lens)
        o=add(c['id']+'_Camera',assembly,'CameraEnvelopes',COLORS[i]);bodies.append(o)
        for key,value in [('OpticalCenterMM',c['position_mm']),('AimPointMM',c['target_mm']),('SensorMM',c['sensor_mm']),('Pixels',c['pixels'])]:
            o.addProperty('App::PropertyString',key,'Optics');setattr(o,key,json.dumps(value))
        o.addProperty('App::PropertyLength','FocalLength','Optics');o.FocalLength=c['focal_mm']
        o.addProperty('App::PropertyString','Status');o.Status='Idealized generic camera, not vendor geometry; position is optical center'
        back=p-f*45
        if i<4:
            # Joint at rear body to upright inner face; rod is a mounting reservation.
            anchor=np.array([20 if p[0]<270 else 520,10 if p[1]<270 else 530,back[2]])
        else:anchor=np.array([270,270,520])
        d=back-anchor
        add(c['id']+'_Support',Part.makeCylinder(4,float(np.linalg.norm(d)),V(*anchor),V(*d)), 'MountConcepts',(.85,.48,.13))
        for usable,group in ((False,'FullFrustums'),(True,'UsableFrustums')):
            shape=solid(frustum_vertices(c,usable)+offset)
            obj=add(c['id']+'_'+group,shape,group,COLORS[i],False,90)
            if usable:
                frustums.append(shape)
                clip=shape.common(cube,1e-6)
                assert not clip.isNull() and clip.isValid(), c['id']
                clipped.append(clip)
                obj=add(c['id']+'_ClippedView',clip,'ClippedViews',COLORS[i],False,88)
                obj.ViewObject.DisplayMode='Flat Lines';obj.ViewObject.LineWidth=2;obj.ViewObject.Transparency=88
                obj.Label=c['id']+' frustum - '+['blue','orange','purple','teal','gold'][i]
        axis=Part.makePolygon([V(*p),V(*(np.array(c['target_mm'])+offset))])
        add(c['id']+'_OpticalAxis',axis,'UsableFrustums',COLORS[i],False)
    doc.recompute();doc.save()
    # Partition arena by camera membership; disjoint interiors avoid double counting.
    from polyclip import box_faces, clip as plane_clip, planes
    def poly_solid(faces):
        fs=[]
        for face in faces:
            points=[V(*p) for p in face]
            try:fs.append(Part.Face(Part.makePolygon(points+[points[0]])))
            except Part.OCCError:pass
        if len(fs)<4:return None
        shape=Part.makeSolid(Part.makeShell(fs))
        if shape.Volume<0:shape.reverse()
        return shape if shape.Volume>1e-5 else None
    polycells=[(0,box_faces(offset,offset+500))]
    for i,c in enumerate(cameras):
        next_cells=[]
        for mask,faces in polycells:
            remaining=faces
            for normal,distance in planes(c,basis(c),offset):
                outside=plane_clip(remaining,-normal,-distance)
                if outside:next_cells.append((mask,outside))
                remaining=plane_clip(remaining,normal,distance)
                if not remaining:break
            if remaining:next_cells.append((mask|(1<<i),remaining))
        polycells=next_cells
        print(f'Camera {i+1}: {len(polycells)} convex cells',flush=True)
    cells=[]
    for mask,faces in polycells:
        shape=poly_solid(faces)
        if shape is not None:cells.append((mask,shape))
    assert abs(sum(s.Volume for m,s in cells)-cube.Volume)<cube.Volume*1e-7
    for mask,s in cells:
        o=add(f'Cell_{mask:05b}_{mask.bit_count()}views',s,'OverlapCells',(.35,.65,.4),False,85)
        o.addProperty('App::PropertyString','Cameras');o.Cameras=','.join(c['id'] for i,c in enumerate(cameras) if mask&(1<<i))
    volumes={}
    for n in (2,3,4,5):
        shapes=[s for m,s in cells if m.bit_count()>=n]
        compound=Part.makeCompound(shapes)
        add(f'AtLeast{n}Views_GeometricOnly',compound,'OverlapSummary',(.18,.70,.46),n==5,75)
        volumes[str(n)]={'cube_pct':100*sum(s.Volume for s in shapes)/cube.Volume,
                        'lower_pct':100*sum(s.common(lower).Volume for s in shapes)/lower.Volume}
    # Independently compare CAD classification with analytic projection at random points.
    rng=np.random.default_rng(20261029);points=rng.uniform(0,500,(120,3))
    for i,c in enumerate(cameras):
        expected=visibility(c,points)[0]
        actual=np.array([clipped[i].isInside(V(*(p+offset)),1e-7,True) for p in points])
        assert np.array_equal(expected,actual),c['id']
    clashes=[]
    frame=[doc.getObject(name) for name,s,color in parts]
    for body in bodies:
        for member in frame:
            if body.Shape.common(member.Shape).Volume>1e-5:clashes.append([body.Name,member.Name])
    assert not clashes,clashes
    assert all(s.isValid() for m,s in cells)
    doc.recompute();doc.save();App.closeDocument(doc.Name)
    doc=App.openDocument(str(path));Gui.activateWorkbench('PartWorkbench');Gui.updateGui()
    view=Gui.activeDocument().activeView()
    rot=App.Rotation(V(),V(0,0,1),V(1,-1,.7),'ZYX');pos=V(270,270,270)+rot.multVec(V(0,0,2000));a=rot.Axis
    view.setCamera('#Inventor V2.1 ascii\nOrthographicCamera { position %s %s %s orientation %s %s %s %s nearDistance 1 farDistance 4000 focalDistance 2000 aspectRatio 1.4 height 950 }'%(pos.x,pos.y,pos.z,a.x,a.y,a.z,rot.Angle))
    Gui.updateGui();view.saveImage(str(OUT/'frustums.png'),1400,1000,'White')
    for o in doc.ClippedViews.Group:o.Visibility=False
    for o in doc.OverlapSummary.Group:o.Visibility=False
    view.saveImage(str(OUT/'layout.png'),1400,1000,'White')
    for o in doc.ClippedViews.Group:o.Visibility=False
    doc.getObject('AtLeast5Views_GeometricOnly').Visibility=True
    doc.save();App.closeDocument(doc.Name)
    with zipfile.ZipFile(path) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
    doc=App.openDocument(str(path));assert all(o.Shape.isValid() for o in doc.Objects if o.TypeId=='PartDesign::Feature');App.closeDocument(doc.Name)
    report={'status':'pass','baseline_sha256':record['sha256'],'native_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'frame_solids_copied':len(parts),'camera_count':5,'body_frame_collisions':clashes,'membership_cells':len(cells),
        'partition_volume_error_mm3':sum(s.Volume for m,s in cells)-cube.Volume,'analytic_CAD_classification_checks':600,
        'exact_geometric_coverage':volumes,'zip_integrity':True,'reopen_valid':True,'task_documents_closed':True,
        'scope':'Exact frustum overlap only; does not include body occlusion, feature size, ray angle, animals, tether or optics errors'}
    (OUT/'cad-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    (OUT/'cad-error.txt').unlink(missing_ok=True)
    print(json.dumps(report,indent=2),flush=True)


def run():
    status=1
    try:build();status=0
    except Exception:
        (OUT/'cad-error.txt').write_text(traceback.format_exc())
        (OUT/'cad-validation.json').write_text(json.dumps({'status':'failed','error':traceback.format_exc()})+'\n')
        traceback.print_exc()
    finally:
        for name in list(App.listDocuments()):App.closeDocument(name)
        os._exit(status)

QtCore.QTimer.singleShot(0,run)
app.exec()
