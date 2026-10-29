"""Build a compact mechanical study on checked R09 copper.

CH2021A dimensions: [@chuanganCh2021a]. Envelope only, no optical prescription.
Holder dimensions and component heights are explicit study assumptions.
"""
from pathlib import Path
import argparse, hashlib, json, sys
import FreeCAD as App
import Part

ROOT=Path(__file__).resolve().parents[2]
V=App.Vector
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add(doc,parent,name,label,shape):
    assert shape.isValid(),name
    obj=doc.addObject('PartDesign::Feature',name);obj.Label=label;obj.Shape=shape
    parent.addObject(obj);return obj

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--boards',type=Path,required=True)
    ap.add_argument('--exports',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--revision',choices=['R03','R04','R05'],default='R03')
    a=ap.parse_args();boards=a.boards.resolve();exports=a.exports.resolve();out=a.output.resolve()
    assert not out.exists(),'Choose a new revision directory'
    checked=json.loads((boards/'validation.json').read_text())
    for name,digest in checked['sha256'].items():assert sha(boards/name)==digest,name
    sources=json.loads((exports/'source-record.json').read_text())
    assert sources['native_sha256']==checked['sha256']
    interfaces=json.loads((exports/'head-interfaces.json').read_text())
    assert interfaces['source_sha256']==sha(boards/'head.kicad_pcb')
    out.mkdir(parents=True)
    revision=a.revision
    doc=App.newDocument('OV9281_Compact_Optics_'+revision)
    doc.Label='R09 PCB + compact CH2021A — clearance study '+revision
    parameters=doc.addObject('App::FeaturePython','StudyParameters')
    parameters.Label='EDIT — assumed sensor height and lens travel'
    for name,value in [('ImagePlaneHeight',1.2),('FocusTravel',0),('DrawingTTL',3.85),('ThreadPitch',.35)]:
        parameters.addProperty('App::PropertyLength',name,'Optics');setattr(parameters,name,value)
    parameters.addProperty('App::PropertyString','Limit','Optics')
    parameters.Limit='Lens envelope from drawing. ImagePlaneHeight and holder are assumptions. Travel is not calibrated focus.'
    groups={};step_hashes={};shapes={}
    for name in ['controller','head','flex-study']:
        path=exports/(name+'.step');shape=Part.Shape();shape.read(str(path))
        assert shape.isValid() and shape.Solids;shapes[name]=shape;step_hashes[name]=sha(path)
    lift=shapes['controller'].BoundBox.ZMax-shapes['flex-study'].BoundBox.ZMin+.02
    for name,offset,angle in [('controller',(0,0,0),0),('head',(76,-1.25,0),-90),('flex-study',(29.2,-2,lift),0)]:
        group=doc.addObject('App::Part',name.replace('-','_'));group.Label=name+' — actual R09 trial copper'
        groups[name]=group;solids=sorted(shapes[name].Solids,key=lambda s:s.Volume,reverse=True)
        add(doc,group,group.Name+'Substrate','Substrate — '+name,solids[0])
        add(doc,group,group.Name+'Copper','Copper — '+name,Part.makeCompound(solids[1:]))
        group.Placement=App.Placement(V(*offset),App.Rotation(V(0,0,1),angle))
    head=groups['head'];cx,cy=interfaces['optical_xy_mm'];top=shapes['head'].BoundBox.ZMax
    optics=doc.addObject('App::Part','CompactOptics');optics.Label='CH2021A envelope + proposed holder';head.addObject(optics)
    # Unscaled maximum body cylinder. Geometry does not imply lens elements or threads.
    lens=add(doc,optics,'LensEnvelope','CH2021A — diameter 6 x length 2.65 mm ENVELOPE',Part.makeCylinder(3,2.65,V(cx,cy,2.4)))
    lens.setExpression('Placement.Base.z','StudyParameters.ImagePlaneHeight - 1.2 mm + StudyParameters.FocusTravel')
    lens.addProperty('App::PropertyString','Evidence').Evidence='CH2021A drawing: M6 x 0.35, TTL 3.85, rear clearance 1.20. Not manufacturer STEP.'
    active=add(doc,optics,'ActiveArea','OV9281 image plane — Z assumed',Part.makeBox(3.896,2.453,.01,V(cx-1.948,cy-1.2265,1.2)))
    active.setExpression('Placement.Base.z','StudyParameters.ImagePlaneHeight - 1.2 mm')
    # Front component reservations are height assumptions; native courtyards stay exact in XY.
    reservations=doc.addObject('App::Part','ComponentReservations');reservations.Label='Front component clearance envelopes — assumed heights';head.addObject(reservations)
    boxes={}
    for row in interfaces['front_courtyard_rectangles']:
        x0,y0,x1,y1=row['bounds_xy_mm'];height=.8 if row['reference']=='U1' else 1.0
        shape=Part.makeBox(x1-x0,y1-y0,height,V(x0,y0,top))
        boxes[row['reference']]=shape
        obj=add(doc,reservations,'Reserved_'+row['reference'],row['reference']+' — courtyard, assumed '+str(height)+' mm height',shape)
        obj.addProperty('App::PropertyString','Limit').Limit='Native courtyard XY; assumed height, not component CAD'
    # Proposed 8 mm square shroud, 0.05 mm above copper; broad lower sensor pocket.
    bottom=top+.05;holder_top=4.3;pocket_top=2.2
    outer=Part.makeBox(8,8,holder_top-bottom,V(cx-4,cy-4,bottom))
    cavity=Part.makeBox(6.5,6.5,pocket_top-bottom+.01,V(cx-3.25,cy-3.25,bottom-.01))
    bore=Part.makeCylinder(3.025,holder_top-pocket_top+.1,V(cx,cy,pocket_top))
    holder=outer.cut(cavity).cut(bore).removeSplitter()
    initial_collisions={ref:holder.common(shape).Volume for ref,shape in boxes.items() if holder.common(shape).Volume>1e-7}
    reliefs={}
    for ref in initial_collisions:
        bb=boxes[ref].BoundBox
        height=holder_top-bottom+.1 if ref.startswith('D') else bb.ZLength+.2
        cut=Part.makeBox(bb.XLength+.2,bb.YLength+.2,height,V(bb.XMin-.1,bb.YMin-.1,bottom-.01))
        holder=holder.cut(cut).removeSplitter()
        reliefs[ref]={'xy_margin_mm':.1,'height_mm':height,'full_height':ref.startswith('D')}
    assert holder.isValid() and len(holder.Solids)==1,'Clearance pockets must leave a single connected holder'
    add(doc,optics,'HolderStudy','Proposed shroud with LED/transistor relief — thread and mounting unfinished',holder)
    # A thin transverse reserved filter space; optical filter is not selected.
    filter_shape=Part.makeCylinder(2.6,.2,V(cx,cy,1.85))
    add(doc,optics,'FilterReservation','Filter space — 0.2 mm assumed, no selected part',filter_shape)
    collisions={ref:holder.common(shape).Volume for ref,shape in boxes.items() if holder.common(shape).Volume>1e-7}
    travel_checks=[]
    for travel in [0,.5,1.0]:
        parameters.FocusTravel=travel;doc.recompute()
        assert abs(lens.Placement.Base.z-travel)<1e-8
        moved=Part.makeCylinder(3,2.65,V(cx,cy,2.4+travel))
        overlap=holder.common(moved).Volume
        assert overlap<1e-7,('lens-holder overlap',travel,overlap)
        assert moved.common(filter_shape).Volume<1e-7
        travel_checks.append({'travel_mm':travel,'lens_holder_overlap_mm3':overlap,
                             'axial_overlap_with_bore_mm':max(0,min(5.05+travel,holder_top)-max(2.4+travel,pocket_top))})
    parameters.FocusTravel=0;doc.recompute()
    # Complete matched Pupil module kept together for optional side-by-side review.
    sys.path.insert(0,str(ROOT/'designs/eye-tracker'))
    from shared.camera import add_camera, selected_model
    model=selected_model();sensor=model['optical_datum']['sensor_center_mm']
    pupil=add_camera(doc,'PupilReference',App.Placement(V(70-sensor[0],24-sensor[1],top-sensor[2]),App.Rotation(V(0,0,1),0)))
    pupil.Label='REFERENCE — complete accepted Pupil mock-up (toggle visibility)'
    assert not collisions,collisions
    path=out/('OV9281-COMPACT-OPTICS-'+revision+'.FCStd');doc.saveAs(str(path));App.closeDocument(doc.Name)
    result={'revision':'OV9281-COMPACT-OPTICS-'+revision,'units':'mm','native_document':str(path),'native_sha256':sha(path),
            'pcb_source':str(boards),'pcb_native_sha256':checked['sha256'],'step_sha256':step_hashes,
            'pupil_checkpoint':model['revision'],'pupil_native_sha256':model['native_checkpoint']['sha256'],
            'lens':'CH2021A dimension envelope only','lens_source':'chuanganCh2021a','optical_xy_mm':[cx,cy],
            'board_copper_top_z_mm':top,'assumptions':{'image_plane_z_mm':1.2,'sensor_reservation_height_mm':.8,'other_front_component_height_mm':1.0,
            'holder_outer_xy_mm':[8,8],'holder_top_z_mm':holder_top,'holder_bore_diameter_mm':6.05,'filter_thickness_mm':.2},
            'initial_holder_courtyard_collisions_mm3':initial_collisions,'reliefs':reliefs,
            'holder_courtyard_collisions_mm3':collisions,'focus_travel_geometry_checks':travel_checks,
            'physical_fit_verified':False,'optics_qualified':False,'manufacturing_ready':False,
            'limits':[str(checked['boards']['head']['unconnected_items'])+' head connections and '+str(sum(sum(x['violations_by_type'].values()) for x in checked['boards'].values()))+' DRC violations remain in source PCB trial.',
            'Smooth bore represents thread space only; usable thread engagement and mounting are not designed.',
            'Component reservations are not exact bodies; all courtyard collisions require resolution.',
            'No 10-20 mm or 940 nm focus validation; filter part and sensor Z are unqualified.']}
    (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'document':str(path),'holder_collisions':collisions,'focus_travel_checks':travel_checks},indent=2))
if __name__=='__main__':main()
