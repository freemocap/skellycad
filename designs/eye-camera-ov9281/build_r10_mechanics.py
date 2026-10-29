"""Build a matched, explicitly provisional mechanical review from R10 copper."""
from pathlib import Path
import hashlib,json,sys,zipfile
import FreeCAD as App
import Part

ROOT=Path(__file__).resolve().parents[2]
PCB=ROOT/'generated/ov9281-r10-review-02'
EXPORTS=ROOT/'generated/ov9281-r10-exports-01'
OUT=ROOT/'generated/ov9281-r10-mechanics-01'
V=App.Vector
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add(doc,group,name,label,shape):
    obj=doc.addObject('PartDesign::Feature',name);obj.Label=label;obj.Shape=shape;group.addObject(obj);return obj
def main():
    assert not OUT.exists();OUT.mkdir()
    checked=json.loads((PCB/'validation.json').read_text())
    for n,h in checked['sha256'].items():assert sha(PCB/n)==h,n
    assert json.loads((EXPORTS/'source-record.json').read_text())['native_sha256']==checked['sha256']
    old=ROOT/'generated/ov9281-compact-optics-r05/OV9281-COMPACT-OPTICS-R05.FCStd'
    assert sha(old)=='eb083101f5dbcc08ed4a5cf10d9a102355b4233b7ac3bcf49b5c052aa16768bb'
    rows=json.loads((PCB/'component-reservations.json').read_text())
    assert rows['native_sha256']==checked['sha256']
    doc=App.newDocument('OV9281_R10_Review');doc.Label='OV9281 R10 — corrected copper and compact optics study'
    groups={};shapes={};step_hashes={};bounds={}
    for name in ['controller','head','flex-study']:
        p=EXPORTS/(name+'.step');s=Part.Shape();s.read(str(p));assert s.isValid() and s.Solids
        shapes[name]=s;step_hashes[name]=sha(p)
        bounds[name]={'z_min_mm':s.BoundBox.ZMin,'z_max_mm':s.BoundBox.ZMax,'export_height_mm':s.BoundBox.ZLength,'solid_count':len(s.Solids)}
    lift=shapes['controller'].BoundBox.ZMax-shapes['flex-study'].BoundBox.ZMin+.02
    for name,offset,angle in [('controller',(0,0,0),0),('head',(76,-1.25,0),-90),('flex-study',(29.2,-2,lift),0)]:
        group=doc.addObject('App::Part',name.replace('-','_'));group.Label=name+' — verified R10 native copper';groups[name]=group
        solids=sorted(shapes[name].Solids,key=lambda s:s.Volume,reverse=True)
        add(doc,group,group.Name+'Substrate','Native STEP substrate — '+name,solids[0])
        add(doc,group,group.Name+'Copper','Native STEP copper and export mask — '+name,Part.makeCompound(solids[1:]))
        group.Placement=App.Placement(V(*offset),App.Rotation(V(0,0,1),angle))
    reservations={};reservation_count={}
    for name in ['head','controller']:
        group=doc.addObject('App::Part',name+'Reservations');group.Label='Native courtyards — assumed component heights';groups[name].addObject(group)
        reservations[name]={};reservation_count[name]={'F':0,'B':0}
        for row in rows['boards'][name]:
            ref=row['reference']
            if (name,ref) in [('head','J201'),('controller','J103')]:continue
            x0,y0,x1,y1=row['bounds_xy_mm'];height=.8 if name=='head' and ref=='U1' else 1.0
            z=shapes[name].BoundBox.ZMax if row['side']=='F' else shapes[name].BoundBox.ZMin-height
            shape=Part.makeBox(x1-x0,y1-y0,height,V(x0,y0,z));reservations[name][ref]=(row['side'],shape)
            obj=add(doc,group,name+'_'+ref,ref+' '+row['side']+' — courtyard; '+str(height)+' mm assumed height',shape)
            obj.addProperty('App::PropertyString','Limit').Limit='Exact native courtyard bounding box and board side; assumed height, not manufacturer component CAD.'
            reservation_count[name][row['side']]+=1
    # STEP omits the specified coverlay thickness. These separate envelopes
    # represent the proposed material buildup, without changing exported copper.
    flex=groups['flex-study'];covers=doc.addObject('App::Part','FlexConstruction');flex.addObject(covers)
    covers.Label='Proposed coverlay and tip stiffeners — material qualification pending'
    add(doc,covers,'TopCoverlay','PI/adhesive coverlay envelope — 0.0275 mm',Part.makeBox(35.3,12.5,.0275,V(0,-12.5,.089)))
    add(doc,covers,'BottomCoverlay','Span coverlay envelope — removed over contact tips',Part.makeBox(30.3,12.5,.0275,V(2.5,-12.5,-.0515)))
    for x,name in [(0,'LeftStiffener'),(32.8,'RightStiffener')]:
        add(doc,covers,name,'Tip stiffener + adhesive allocation — 0.1595 mm',Part.makeBox(2.5,12.5,.1595,V(x,-12.5,.1165)))
    assert abs(.1165-(-.0515)-.168)<1e-8 and abs(.1165+.1595-(-.024)-.3)<1e-8
    head=groups['head'];cx,cy=6.95,-6.1
    sensor=next(r for r in rows['boards']['head'] if r['reference']=='U1')
    cx,cy=sensor['xy_mm'];top=shapes['head'].BoundBox.ZMax;dz=top-.57;image_plane=1.2+dz
    params=doc.addObject('App::FeaturePython','StudyParameters');params.Label='EDIT — assumed sensor plane and uncalibrated lens travel'
    for n,value in [('ImagePlaneHeight',image_plane),('FocusTravel',0),('DrawingTTL',3.85),('ThreadPitch',.35)]:params.addProperty('App::PropertyLength',n,'Optics');setattr(params,n,value)
    params.addProperty('App::PropertyString','Limit').Limit='CH2021A drawing envelope; sensor Z and holder are assumptions. Lens travel is not calibrated focus.'
    optics=doc.addObject('App::Part','CompactOptics');head.addObject(optics);optics.Label='Retained compact CH2021A optics envelope'
    lens=add(doc,optics,'LensEnvelope','CH2021A — diameter 6 x length 2.65 mm envelope',Part.makeCylinder(3,2.65,V(cx,cy,2.4+dz)))
    lens.setExpression('Placement.Base.z',f'StudyParameters.ImagePlaneHeight - {image_plane:.9f} mm + StudyParameters.FocusTravel')
    active=add(doc,optics,'ActiveArea','OV9281 image plane — height assumed',Part.makeBox(3.896,2.453,.01,V(cx-1.948,cy-1.2265,image_plane)))
    active.setExpression('Placement.Base.z',f'StudyParameters.ImagePlaneHeight - {image_plane:.9f} mm')
    bottom=top+.05;holder_top=4.3+dz;pocket_top=2.2+dz
    holder=Part.makeBox(8,8,holder_top-bottom,V(cx-4,cy-4,bottom)).cut(Part.makeBox(6.5,6.5,pocket_top-bottom+.01,V(cx-3.25,cy-3.25,bottom-.01))).cut(Part.makeCylinder(3.025,holder_top-pocket_top+.1,V(cx,cy,pocket_top))).removeSplitter()
    boxes={ref:s for ref,(side,s) in reservations['head'].items() if side=='F'};reliefs={}
    for ref,s in boxes.items():
        if holder.common(s).Volume<=1e-7:continue
        bb=s.BoundBox;height=holder_top-bottom+.1 if ref.startswith('D') else bb.ZLength+.2
        holder=holder.cut(Part.makeBox(bb.XLength+.2,bb.YLength+.2,height,V(bb.XMin-.1,bb.YMin-.1,bottom-.01))).removeSplitter();reliefs[ref]={'xy_margin_mm':.1,'height_mm':height}
    assert holder.isValid() and len(holder.Solids)==1
    add(doc,optics,'HolderStudy','8 mm holder study — thread and mounting unfinished',holder)
    filter_shape=Part.makeCylinder(2.6,.2,V(cx,cy,1.85+dz));add(doc,optics,'FilterReservation','Filter space — assumed 0.2 mm, part unselected',filter_shape)
    collisions={ref:holder.common(s).Volume for ref,s in boxes.items() if holder.common(s).Volume>1e-7};assert not collisions,collisions
    travel=[]
    for t in [0,.5,1.0]:
        params.FocusTravel=t;doc.recompute();assert abs(lens.Placement.Base.z-t)<1e-7
        moved=Part.makeCylinder(3,2.65,V(cx,cy,2.4+dz+t));a=holder.common(moved).Volume;b=filter_shape.common(moved).Volume;assert max(a,b)<1e-7
        travel.append({'travel_mm':t,'holder_overlap_mm3':a,'filter_overlap_mm3':b})
    params.FocusTravel=0;doc.recompute()
    sys.path.insert(0,str(ROOT/'designs/eye-tracker'));from shared.camera import add_camera,selected_model
    model=selected_model();datum=model['optical_datum']['sensor_center_mm']
    pupil=add_camera(doc,'PupilReference',App.Placement(V(70-datum[0],24-datum[1],top-datum[2]),App.Rotation()))
    pupil.Label='REFERENCE — complete accepted Pupil mock-up; hidden initially'
    path=OUT/'OV9281-R10-MATCHED-REVIEW.FCStd';doc.recompute();doc.saveAs(str(path));App.closeDocument(doc.Name)
    with zipfile.ZipFile(path) as z:assert 'Document.xml' in z.namelist() and z.testzip() is None
    result={'revision':'OV9281-R10-MATCHED-REVIEW','units':'mm','native_document':str(path),'native_sha256':sha(path),'pcb_source':str(PCB),'pcb_native_sha256':checked['sha256'],'step_sha256':step_hashes,'step_bounds':bounds,'optical_xy_mm':[cx,cy],'board_copper_top_z_mm':top,'prior_optics_native_sha256':sha(old),'pupil_checkpoint':model['revision'],'pupil_native_sha256':model['native_checkpoint']['sha256'],'component_reservation_counts':reservation_count,'assumptions':{'image_plane_z_mm':image_plane,'sensor_height_mm':.8,'other_component_height_mm':1,'flex_lift_mm':lift,'holder_outer_xy_mm':[8,8],'holder_bore_mm':6.05,'lens_diameter_mm':6,'lens_length_mm':2.65,'filter_thickness_mm':.2,'flex_span_thickness_mm':.168,'flex_tip_thickness_mm':.3},'reliefs':reliefs,'holder_courtyard_collisions_mm3':collisions,'focus_travel_geometry_checks':travel,'physical_fit_verified':False,'optics_qualified':False,'manufacturing_ready':False,'limits':['Actual R10 STEP copper, with separately labeled component and construction envelopes.','Flat flex position verifies XY alignment only; connector engagement and solder height remain unqualified.','Component heights, sensor Z, filter and holder mounting remain assumptions; smooth bore is thread space only.','Lens travel checks clearance only, not 10–20 mm or infrared focus.','KiCad STEP mask thickness differs from the flex construction; separate coverlay/stiffener envelopes represent the intended 0.168/0.300 mm buildup.']}
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
