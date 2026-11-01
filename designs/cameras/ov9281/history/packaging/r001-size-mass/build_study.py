"""Build an isolated native comparison. Run with bundled FreeCAD Python."""
from pathlib import Path
import json,sys,hashlib,zipfile
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'generated/ov9281-size-mass-r01'
V=App.Vector

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for path,digest in json.loads((HERE/'source-hashes.json').read_text(encoding="utf-8")).items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    sys.path.insert(0,str(ROOT/'designs/eye-tracker'))
    from shared.camera import add_camera
    data=json.loads((HERE/'packing.json').read_text(encoding="utf-8"));doc=App.newDocument('OV9281_Size_Mass_R01');report={'units':'mm','packing_only':True,'candidates':[]}
    def group(name,label):
        q=doc.addObject('App::Part',name);q.Label=label;return q
    def shape(parent,name,label,s,color=(.18,.20,.24),kind='reservation'):
        q=doc.addObject('Part::Feature',name);q.Label=label;q.Shape=s;parent.addObject(q)
        q.addProperty('App::PropertyVector','StudyColor','Review').StudyColor=V(*color)
        q.addProperty('App::PropertyString','EvidenceType','Review').EvidenceType=kind
        return q
    def label(parent,name,text,x,y,size=1.6):
        wires=Part.makeWireString(text,'C:/Windows/Fonts/arial.ttf',size,0)
        s=Part.makeCompound([Part.makeFace(letter,'Part::FaceMakerBullseye') for letter in wires if letter]);s.translate(V(x,y,0));return shape(parent,name,text,s,(.16,.18,.22),'dimension label in mm')
    def dim(parent,name,x0,x1,y,text):
        segments=[Part.makeLine(V(x0,y,0),V(x1,y,0)),Part.makeLine(V(x0,y-.6,0),V(x0,y+.6,0)),Part.makeLine(V(x1,y-.6,0),V(x1,y+.6,0))]
        shape(parent,name,text,Part.makeCompound(segments),(.25,.3,.35),'dimension guide');label(parent,name+'Text',text,x0+.5,y+.7,1.1)

    pupil=add_camera(doc,'PupilR08',App.Placement(V(0,120,0),App.Rotation(V(0,0,1),-90)))
    for q in pupil.PhysicalParts:
        color=(.55,.16,.15) if 'boards' in q.Name else ((.85,.64,.15) if 'ribbon' in q.Name else ((.15,.15,.18) if 'lens' in q.Name else (.8,.8,.75)))
        q.addProperty('App::PropertyVector','StudyColor','Review').StudyColor=V(*color)
    chips=group('PupilPhotoChips','Supplemental photo-based chip envelopes, not measured parts');pupil.addObject(chips)
    for i,(x,y,w,l,h) in enumerate(json.loads((HERE/'pupil-electronics-envelopes.json').read_text(encoding="utf-8"))['chip_layout_xywhh_mm']):
        shape(chips,'PupilChip'+str(i),'Photo-based chip envelope '+str(i+1),Part.makeBox(w,l,h,V(x,y,.25)),kind='Approximate photo proportions, not calibrated dimensions or a BOM')
    notes=group('ComparisonLabels','Dimensions and study notes')
    label(notes,'Title','SIZE / MASS STUDY - TETHER EXCLUDED',-8,139,2.2)
    label(notes,'PupilTitle','Pupil reference: selected R08 + photo chip envelopes',-8,128)
    dim(notes,'PupilLength',.4333457947,79.1333457947,112,'78.70 mm board-to-head outline; controller width 9 mm')
    label(notes,'PupilMass','~0.7 g reported; native print-material volumes are not camera mass',-8,109,1.2)

    baseline=group('R10Reference','R10 preserved native geometry - placement/component envelopes')
    src=App.openDocument(str(ROOT/'generated/ov9281-r10-mechanics-02/OV9281-R10-MATCHED-REVIEW.FCStd'))
    copied=0
    for o in src.Objects:
        if o.TypeId not in ['Part::Feature','PartDesign::Feature'] or not hasattr(o,'Shape') or not o.Shape.Solids:continue
        if o.Name.startswith('PupilReference'):continue
        if not {'controller','head','flex_study'}.intersection(q.Name for q in o.InListRecursive):continue
        s=o.Shape.copy();s.Placement=o.getGlobalPlacement();s.translate(V(0,100,0))
        color=(.85,.65,.16) if o.Name.startswith('flex') else ((.1,.42,.38) if 'Substrate' in o.Name else ((.72,.48,.22) if 'Copper' in o.Name else ((.15,.35,.55) if 'Lens' in o.Name or 'Filter' in o.Name else (.2,.2,.23))))
        shape(baseline,'R10_'+o.Name,o.Label,s,color,'Copied selected R10 geometry; package reservations are not component CAD');copied+=1
    existing_holder=src.getObject('HolderStudy').Shape.copy()
    App.closeDocument(src.Name);App.setActiveDocument(doc.Name)
    report['r10_copied_leaf_shapes']=copied
    label(notes,'R10Title','R10: 32 x 20 controller / 14 x 14 head / existing routing',-8,103)
    dim(notes,'R10Length',0,76,77,'76 mm flat span; 20 mm maximum board width')

    for v,row in zip(data['variants'],[59,29,-1]):
        name=v['id'];g=group('Candidate'+name,name+' - '+v['name']+' - UNROUTED PACKING STUDY');L,W=v['controller_mm'];HL,HW=v['head_mm'];FL,FW=v['free_flex_mm'];t=v['rigid_thickness_mm'];ft=v['flex_thickness_mm'];hx=L+FL;origins={'controller':(0,row-W/2),'head':(hx,row-HW/2)}
        bodies=[]
        for board,(BL,BW) in [('controller',(L,W)),('head',(HL,HW))]:
            bx,by=origins[board];shape(g,name+board,board+f' {BL} x {BW} x {t} mm',Part.makeBox(BL,BW,t,V(bx,by,0)),(.12,.48,.43),'Proposed substrate outline; internal stackup not modeled')
        shape(g,name+'Flex',f'Free flex {FL} x {FW} x {ft} mm',Part.makeBox(FL,FW,ft,V(L,row-FW/2,t if name=='A' else (t-ft)/2)),(.85,.65,.16),'Free neck outline; copper routing and bend behavior unvalidated')
        for p in v['parts']:
            bx,by=origins[p['board']];x,y,w,h=p['rect_mm'];z=t if p['source_side']=='F' else -p['height_mm'];s=Part.makeBox(w,h,p['height_mm'],V(bx+x,by+y,z));color=(.85,.85,.75) if p['reference'] in ['J101','D201','D202'] else ((.19,.26,.37) if p['reference']=='U1' else (.18,.20,.24))
            obj=shape(g,name+p['board']+p['reference'],p['board']+'/'+p['reference']+' '+p['assumption'],s,color,'Courtyard prism; mass comes from package assumptions, not this volume');obj.addProperty('App::PropertyString','SourceFootprint','Lineage').SourceFootprint=p['source_footprint'];bodies.append((p,s))
        # Locally stiffened flex: reserve real underside space, not just mass.
        stiffeners=[]
        if name=='C':
            cs=Part.makeBox(10,10,.15,V(7.8,row-5,-.15))
            hs=Part.makeBox(8,8,.15,V(hx+HL/2-4,row-4,-.15)).cut(Part.makeBox(6.5,6.5,.17,V(hx+HL/2-3.25,row-3.25,-.16)))
            stiffeners=[('controller',cs),('head',hs)]
            for board,st in stiffeners:
                shape(g,name+board+'Stiffener','Local support - strength unqualified',st,(.68,.65,.5),'Stiffener geometry; material and adhesion unselected')
                for p,s in bodies:
                    if p['board']==board:assert s.common(st).Volume<1e-7,(p['reference'],'stiffener collision')
        # Hollow lightweight support with a sensor clearance pocket and filter seat.
        cx=hx+HL/2;cy=row
        frame=Part.makeBox(8,8,1.15,V(cx-4,cy-4,t+.05)).cut(Part.makeBox(6.5,6.5,1.17,V(cx-3.25,cy-3.25,t+.04)))
        collar=Part.makeCylinder(3.55,2.1,V(cx,cy,t+1.2)).cut(Part.makeCylinder(3.025,2.12,V(cx,cy,t+1.19)))
        seat=Part.makeCylinder(3.05,.05,V(cx,cy,t+1.23)).cut(Part.makeCylinder(2.5,.07,V(cx,cy,t+1.22)))
        holder=frame.fuse(collar).fuse(seat).removeSplitter()
        if name=='A':
            # Retain the exact current holder rather than estimating its shape.
            holder=existing_holder.copy();holder.translate(V(cx-7.3325,cy+6.043,t-.511))
        lens=Part.makeCylinder(3,2.65,V(cx,cy,t+1.83));filt=Part.makeCylinder(2.6,.2,V(cx,cy,t+1.28))
        shape(g,name+'Holder','Hollow support study - thread and attachment unqualified',holder,(.36,.22,.43),'New support reservation, not a qualified lens holder')
        shape(g,name+'Lens','6 mm lens envelope - close focus unproven',lens,(.16,.36,.58),'CH2021A envelope only; 10-20 mm focus unqualified')
        shape(g,name+'Filter','IR filter reservation - coating unselected',filt,(.2,.65,.7),'Filter size reservation, not an optical transmission specification')
        collision=[]
        for p,s in bodies:
            if p['board']=='head':
                for label_,other in [('holder',holder),('lens',lens),('filter',filt)]:
                    volume=s.common(other).Volume
                    if volume>1e-7:collision.append([p['reference'],label_,volume])
        assert not collision,(name,collision)
        assert holder.isValid() and len(holder.Solids)==1,(name,'holder topology')
        assert holder.common(lens).Volume<1e-7 and holder.common(filt).Volume<1e-7
        exitbox=Part.makeBox(8,7.8,3,V(-8,row-W/2+.25,0));shape(g,name+'TetherExit','Connector mating / tether exit space - cable excluded',Part.makeCompound(exitbox.Edges),(.35,.5,.7),'Clearance guide; no qualified cable or strain relief')
        # Reserve the unchanged electrical function of the five programming pads.
        guide=Part.makeBox(7.2,2.2,.05,V(.25,row+W/2-2.45,-.05));shape(g,name+'Programming','Underside programming pad reservation',guide,(.8,.57,.18),'Pad-zone reservation; unrouted')
        label(notes,name+'Title',name+': '+v['name']+f' | {L} x {W} controller / {HL} x {HW} head',-8,row+W/2+3)
        dim(notes,name+'Length',0,L+FL+HL,row-W/2-3,f'{L+FL+HL:.2f} mm flat span / free flex {FL:.2f} x {FW} mm')
        label(notes,name+'Thickness',f'Board {t:.3f} mm / flex {ft:.3f} mm; two-sided courtyard reservations',-8,row-W/2-6,1.2)
        report['candidates'].append({'id':name,'holder_volume_mm3':holder.Volume,'holder_mass_g_at_1_2_density':holder.Volume*.0012,'lens_holder_radial_clearance_mm':.025 if name!='A' else None,'filter_seat_radial_overlap_mm':.1 if name!='A' else None,'sensor_to_filter_bottom_clearance_mm':.28,'filter_to_lens_bottom_clearance_mm':.35,'nominal_barrel_axial_overlap_mm':1.47 if name!='A' else 1.90,'barrel_axial_overlap_at_1mm_extension_mm':.47 if name!='A' else .90,'physical_reservation_overlap_count':0,'holder_valid_solid':True,'component_count':len(bodies),'strain_relief_strength':'unvalidated; assembly mass allowance only','maximum_lens_front_above_substrate_bottom_mm':t+4.48,'body_mass_not_derived_from_courtyard_prisms':True,'stiffener_volume_mm3':sum(st.Volume for _,st in stiffeners),'stiffener_component_overlap_count':0})
    label(notes,'Limits','PACKING ONLY: new routing, real parts, optics, stiffness and measured mass remain unqualified.',-8,-19,1.4)
    doc.recompute();invalid=[];count=0
    for o in doc.Objects:
        if o.TypeId in ['Part::Feature','PartDesign::Feature'] and hasattr(o,'Shape') and not o.Shape.isNull():
            count+=1
            if not o.Shape.isValid():invalid.append(o.Name)
    assert not invalid,invalid
    path=OUT/'OV9281-SIZE-MASS-R01.FCStd';doc.recompute();doc.saveAs(str(path));App.closeDocument(doc.Name)
    with zipfile.ZipFile(path) as z:assert 'Document.xml' in z.namelist() and z.testzip() is None
    report.update({'native_path':str(path.relative_to(ROOT)).replace('\\','/'),'native_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'valid_shapes':count,'invalid_shapes':invalid,'native_zip_verified':True,'source_hashes_unchanged':True,'units':'mm','not_a_routed_electrical_revision':True})
    (HERE/'geometry-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
