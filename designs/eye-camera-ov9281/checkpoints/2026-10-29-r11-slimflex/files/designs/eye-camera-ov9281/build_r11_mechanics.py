"""Build a matched regional assembly from audited R11 native geometry.

Run in the pinned FreeCAD Python runtime. Saved documents are closed after
integrity/geometry checks; a separate review macro opens the requested result.
"""
from pathlib import Path
import hashlib,json,math,sys,zipfile
import FreeCAD as App
import Part
ROOT=Path(__file__).resolve().parents[2];PCB=ROOT/'generated/ov9281-r11-electronics';OUT=ROOT/'generated/ov9281-r11-mechanics';SPEC=ROOT/'designs/eye-camera-ov9281/electronics/r11';V=App.Vector
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wire(points,z=0):
    vectors=[]
    for x,y in points:
        q=V(x,14-y,z)
        if not vectors or (q-vectors[-1]).Length>1e-6:vectors.append(q)
    if (vectors[-1]-vectors[0]).Length<1e-6:vectors.pop()
    assert len(vectors)>=3
    return Part.makePolygon(vectors+[vectors[0]])
def prism(points,z,h):return Part.Face(wire(points,z)).extrude(V(0,0,h))
def rect(bounds,z,h):
    x0,y0,x1,y1=bounds;return Part.makeBox(x1-x0,y1-y0,h,V(x0,14-y1,z))
def main():
    assert not (OUT/'OV9281-R11-MATCHED.FCStd').exists();OUT.mkdir(exist_ok=True)
    data=json.loads((PCB/'native-geometry.json').read_text());assert sha(PCB/'camera.kicad_pcb')==data['board_sha256'];assert json.loads((SPEC/'board-validation.json').read_text())['status']=='pass'
    placement=json.loads((SPEC/'placement.json').read_text());t=.303;ft=.166;hx=60.85
    doc=App.newDocument('OV9281_R11');doc.Label='OV9281 R11 — routed C SLIM.flex assembly';doc.saveAs(str(OUT/'OV9281-R11-MATCHED.FCStd'))
    def group(name,label,parent=None):
        obj=doc.addObject('App::Part',name);obj.Label=label
        if parent:parent.addObject(obj)
        return obj
    def add(parent,name,label,shape,color=(.15,.17,.20),visible=True,evidence='Engineering geometry'):
        obj=doc.addObject('Part::Feature',name);obj.Label=label;obj.Shape=shape;parent.addObject(obj)
        obj.addProperty('App::PropertyVector','StudyColor','Review').StudyColor=V(*color);obj.addProperty('App::PropertyBool','ReviewVisible','Review').ReviewVisible=visible
        obj.addProperty('App::PropertyString','Evidence','Review').Evidence=evidence
        assert not shape.isNull() and shape.isValid(),name
        return obj
    flat=group('FlatAssembly','R11 COMPLETE ASSEMBLY — flat, audited PCB');regions={n:group('Flat_'+n,n.capitalize(),flat) for n in ['controller','flex','head']};physical={n:[] for n in regions};cu_objects=[]
    outlines={'controller':[(0,0),(27,0),(28,3),(28,11),(27,14),(0,14)],'flex':[(28,3),(hx,3),(hx,11),(28,11)],'head':[(hx,3),(hx+1,0),(hx+14,0),(hx+14,14),(hx+1,14),(hx,11)]}
    board_shapes={}
    for name in regions:
        bottom=(t-ft)/2 if name=='flex' else 0;height=ft if name=='flex' else t
        s=prism(outlines[name],bottom,height);board_shapes[name]=s
        obj=add(regions[name],'Board_'+name,f'{name}: finished construction envelope, {height:.3f} mm',s,(.64,.44,.13) if name=='flex' else (.10,.39,.31),evidence='Audited outline; exterior envelope contains the separately displayed copper. Do not sum both volumes for mass.');physical[name].append(obj)
    # Layer heights preserve the central core and the thinner free neck.
    layers={'F.Cu':(.2525,.025),'In1.Cu':(.2145,.018),'In2.Cu':(.1765,.018),'In3.Cu':(.1085,.018),'In4.Cu':(.0705,.018),'B.Cu':(.0255,.025)}
    copper_validation={}
    for region,layer_rows in data['copper'].items():
        cg=group('Copper_'+region,'Native copper layers — optional visibility',regions[region])
        for layer,row in layer_rows.items():
            if not row['polygons']:continue
            z,height=layers[layer];solids=[]
            for index,poly in enumerate(row['polygons']):
                wires=[wire(poly['outer'],z)]+[wire(h,z) for h in poly['holes']]
                face=Part.makeFace(wires,'Part::FaceMakerBullseye');assert face.isValid(),(region,layer,index)
                solids.append(face.extrude(V(0,0,height)))
            s=Part.makeCompound(solids);expected=row['area_mm2']*height
            assert abs(s.Volume-expected)<max(.0001,expected*.001),(region,layer,s.Volume,expected)
            obj=add(cg,'Cu_'+region+'_'+layer.replace('.','_'),layer+' — actual saved copper',s,(.76,.48,.17),layer in ['F.Cu','B.Cu'],evidence='Native pads, traces, filled vias, planes and tapers; polygon approximation <=0.002 mm.');cu_objects.append(obj);physical[region].append(obj)
            copper_validation[region+'/'+layer]={'volume_mm3':s.Volume,'native_area_mm2':row['area_mm2'],'area_volume_agreement':True}
        print('Copper',region,'complete',flush=True)
    components={};bodies=[]
    for row in data['components']:
        if not row['populated'] or row['height_max_mm']<=0:continue
        region=row['region'];height=row['height_max_mm'];bottom=t if row['side']=='F' else -height;s=rect(row['body_bounds_mm'],bottom,height)
        color=(.90,.88,.78) if row['reference'] in ['J101','D201','D202'] else ((.16,.26,.39) if row['reference']=='U1' else (.12,.13,.15))
        obj=add(regions[region],'Part_'+row['reference'],row['reference']+' — '+row['mpn']+' / '+row['side'],s,color,evidence=row['body_evidence']);physical[region].append(obj);components[row['reference']]=obj;bodies.append((row,s))
        obj.addProperty('App::PropertyString','MPN','Component').MPN=row['mpn'];obj.addProperty('App::PropertyString','NativeReference','Component').NativeReference=row['reference']
    support_shapes=[];support_volumes={}
    for region in ['controller','head']:
        bounds=placement['stiffeners']['controller' if region=='controller' else 'head_outer'];holes=placement['stiffeners']['controller_windows'] if region=='controller' else [placement['stiffeners']['head_inner']]
        for kind,z,height,color in [('adhesive',-.05,.05,(.67,.58,.32)),('FR4',-.15,.1,(.60,.61,.45))]:
            s=rect(bounds,z,height)
            for hole in holes:s=s.cut(rect(hole,z-.01,height+.02))
            s=s.removeSplitter();assert len(s.Solids)==1
            obj=add(regions[region],region+'_'+kind,region+' local support — '+kind,s,color);physical[region].append(obj);support_shapes.append((region,s));support_volumes[region+'/'+kind]=s.Volume
    cx,cy=hx+7,7;optics=group('Optics','PROVISIONAL optics and retention envelope',regions['head'])
    frame=Part.makeBox(8,8,1.15,V(cx-4,cy-4,t+.05)).cut(Part.makeBox(6.5,6.5,1.17,V(cx-3.25,cy-3.25,t+.04)))
    collar=Part.makeCylinder(3.55,2.1,V(cx,cy,t+1.2)).cut(Part.makeCylinder(3.025,2.12,V(cx,cy,t+1.19)))
    seat=Part.makeCylinder(3.05,.05,V(cx,cy,t+1.23)).cut(Part.makeCylinder(2.5,.07,V(cx,cy,t+1.22)))
    holder=frame.fuse(collar).fuse(seat).removeSplitter();assert len(holder.Solids)==1
    adhesive=Part.makeBox(8,8,.05,V(cx-4,cy-4,t)).cut(Part.makeBox(6.5,6.5,.07,V(cx-3.25,cy-3.25,t-.01)))
    lens=Part.makeCylinder(3,2.65,V(cx,cy,t+1.83));filt=Part.makeCylinder(2.6,.2,V(cx,cy,t+1.28))
    optical_shapes={'Holder':holder,'HolderBond':adhesive,'LensEnvelope':lens,'FilterEnvelope':filt}
    for name,s in optical_shapes.items():
        obj=add(optics,name,name+' — optics/assembly unqualified',s,(.22,.25,.32) if name=='Holder' else (.15,.44,.57),evidence='Retained compact study envelope; no qualified lens thread, filter coating, 10–20 mm focus or physical fit.');physical['head'].append(obj)
    axis=add(optics,'OpticalAxis','Axis through U1 footprint datum — sensor plane assumed',Part.makeLine(V(cx,cy,t+1),V(cx,cy,t+10)),(.9,.25,.12),False)
    # Independent clearance checks use geometry, not the placement reservation log.
    collisions=[]
    for i,(r,s) in enumerate(bodies):
        for rr,ss in bodies[i+1:]:
            if s.BoundBox.intersect(ss.BoundBox) and s.common(ss).Volume>1e-7:collisions.append([r['reference'],rr['reference']])
        for region,st in support_shapes:
            if r['region']==region and s.common(st).Volume>1e-7:collisions.append([r['reference'],region+' support'])
        if r['region']=='head':
            for name,other in optical_shapes.items():
                if s.common(other).Volume>1e-7:collisions.append([r['reference'],name])
    assert not collisions,collisions
    travel=[]
    for dz in [0,.5,1.0]:
        moved=lens.copy();moved.translate(V(0,0,dz));assert moved.common(holder).Volume<1e-7 and moved.common(filt).Volume<1e-7
        travel.append({'extension_mm':dz,'axial_overlap_mm':1.47-dz,'collision':False})
    access=group('AssemblyAccess','Assembly/access guides — hidden by default',flat)
    probe=rect([.5,11.45,8.3,13.7],-3,3);probe_hits=[r['reference'] for r,s in bodies if s.common(probe).Volume>1e-7];assert not probe_hits,probe_hits
    add(access,'ProgrammingAccess','J103 underside probe approach; fixture unqualified',Part.makeCompound(probe.Edges),(.3,.55,.8),False)
    exitbox=Part.makeBox(8,7.8,3,V(-8,3.1,0));add(access,'TetherExit','JST mating direction; external tether excluded',Part.makeCompound(exitbox.Edges),(.3,.55,.8),False)
    # A separate complete installation configuration bends only the free neck.
    bent=group('BentAssembly','R11 COMPLETE ASSEMBLY — 90 degree installation study (hidden)');bend_parts=[]
    for region in ['controller','head']:
        g=group('Bent_'+region,region,bent)
        for original in physical[region]:
            q=add(g,'Bent_'+original.Name,original.Label,original.Shape.copy(),tuple(original.StudyColor),False,original.Evidence);bend_parts.append((region,q))
    radius=2.5;straight=10.;arc_length=math.pi*radius/2;remaining=32.85-straight-arc_length;bx=28+straight;zc=t/2;center=V(bx,3,zc+radius);ri=radius-ft/2;ro=radius+ft/2
    inner0=V(bx,3,zc+ft/2);inner1=V(bx+ri,3,zc+radius);outer0=V(bx,3,zc-ft/2);outer1=V(bx+ro,3,zc+radius)
    edges=[Part.Arc(inner0,V(bx+ri/math.sqrt(2),3,zc+radius-ri/math.sqrt(2)),inner1).toShape(),Part.makeLine(inner1,outer1),Part.Arc(outer1,V(bx+ro/math.sqrt(2),3,zc+radius-ro/math.sqrt(2)),outer0).toShape(),Part.makeLine(outer0,inner0)]
    arc=Part.Face(Part.Wire(edges)).extrude(V(0,8,0));straight_shape=Part.makeBox(straight,8,ft,V(28,3,zc-ft/2));vertical=Part.makeBox(ft,8,remaining,V(bx+radius-ft/2,3,zc+radius));flex=straight_shape.fuse(arc).fuse(vertical).removeSplitter();assert flex.isValid() and len(flex.Solids)==1
    add(bent,'BentFlex','2.5 mm neutral-radius flex; construction envelope',flex,(.7,.49,.13),False,evidence='Length-preserving 90 degree static installation example. Internal bent copper omitted; flat native geometry remains authoritative.')
    head_origin=V(bx+radius,0,zc+radius+remaining);rotation=App.Rotation(V(0,1,0),-90);head_place=App.Placement(head_origin-rotation.multVec(V(hx,0,zc)),rotation)
    doc.getObject('Bent_head').Placement=head_place
    bend_clearances=[]
    for region,q in bend_parts:
        if q.Name.startswith('Bent_Cu_'):continue
        s=q.Shape.copy()
        if region=='head':s.Placement=head_place.multiply(s.Placement)
        common=s.common(flex).Volume
        if common>1e-6:bend_clearances.append([q.Name,common])
    assert not bend_clearances,bend_clearances
    # Keep the accepted complete Pupil assembly together, with optional photo
    # electronics added as a clearly separate reference-only group.
    sys.path.insert(0,str(ROOT/'designs/eye-tracker'));from shared.camera import add_camera,selected_model
    model=selected_model();pupil=add_camera(doc,'PupilReference',App.Placement(V(0,0,0),App.Rotation(V(0,0,1),-90)));pupil.Label='REFERENCE — selected complete Pupil R08 (hidden)'
    reference_shapes=[]
    for o in pupil.PhysicalParts:
        s=o.Shape.copy();s.Placement=o.getGlobalPlacement();reference_shapes.append(s)
    bb=Part.makeCompound(reference_shapes).BoundBox
    pupil.Placement.Base=V(-bb.XMin,25-bb.YMin,0)
    chips=group('PupilPhotoElectronics','Approximate photo chip envelopes; not measured BOM',pupil)
    photo=json.loads((ROOT/'designs/eye-camera-ov9281/packaging/size-mass-r01/pupil-electronics-envelopes.json').read_text())
    for i,(x,y,w,l,h) in enumerate(photo['chip_layout_xywhh_mm']):add(chips,'PupilPhotoChip'+str(i),'Photo-derived component envelope',Part.makeBox(w,l,h,V(x,y,.25)),visible=False,evidence='Approximate photo proportions; not measured parts or Pupil manufacturing CAD.')
    metadata=doc.addObject('App::FeaturePython','ReviewStatus');metadata.Label='READ FIRST — offline candidate; tether excluded from mass'
    for name,value in [('BoardSHA256',data['board_sha256']),('OpticsStatus','Provisional: close-focus IR lens/filter and retention unqualified'),('MassBoundary','Whole module including PCB, optics, supports, connector and LEDs; external tether excluded'),('PhysicalStatus','No built hardware, measured mass or demonstrated fit')]:metadata.addProperty('App::PropertyString',name,'Review');setattr(metadata,name,value)
    doc.recompute();native=OUT/'OV9281-R11-MATCHED.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    with zipfile.ZipFile(native) as z:assert 'Document.xml' in z.namelist() and z.testzip() is None
    report={'units':'mm','board_sha256':data['board_sha256'],'geometry_transfer_sha256':sha(PCB/'native-geometry.json'),'native_path':str(native.relative_to(ROOT)),'native_sha256':sha(native),'native_zip_verified':True,'outline_mm':{'controller':[28,14],'head':[14,14],'free_flex':[32.85,8],'flat_length':74.85},'component_body_envelopes':len(bodies),'copper':copper_validation,'support_volumes_mm3':support_volumes,'optical_volumes_mm3':{n:s.Volume for n,s in optical_shapes.items()},'collisions':collisions,'programming_access_collisions':probe_hits,'optical_datum_mm':[cx,cy,t+1],'sensor_to_filter_gap_mm':.28,'filter_to_lens_gap_mm':.35,'lens_radial_space_mm':.025,'focus_travel_geometry':travel,'bend':{'angle_deg':90,'neutral_radius_mm':radius,'inner_radius_mm':radius-ft/2,'inner_radius_at_upper_thickness_mm':radius-.216/2,'straight_before_mm':straight,'arc_length_mm':arc_length,'straight_after_mm':remaining,'preserved_neutral_length_mm':straight+arc_length+remaining,'head_placement':{'translation_mm':list(head_place.Base),'quaternion':list(head_place.Rotation.Q)},'collisions':bend_clearances,'dynamic_flex_qualified':False},'pupil_revision':model['revision'],'pupil_checkpoint_sha256':model['native_checkpoint']['sha256'],'physical_fit_verified':False,'optics_qualified':False,'manufacturing_ready':False,'limitations':['Component bodies are conservative native fabrication-outline bounding prisms with selected maximum heights, not exact component CAD.','Board envelopes contain embedded copper; sum of displayed volumes is not module mass.','Optical XY uses U1 footprint datum; image-plane Z, filter coating, close focus and lens locking remain provisional.','The bent configuration preserves neck length and clears rigid parts; it does not model copper strain, adhesive stress, fatigue or assembly tolerances.','Pupil geometry and its photo chip envelopes are reference approximations, not reverse-engineered manufacturing drawings.']}
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('Saved and closed',native,flush=True)
if __name__=='__main__':main()
