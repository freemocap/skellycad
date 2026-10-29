"""Import the supplied CIL829 model beside the frozen R08 PCB geometry.

Run with bundled FreeCAD Python. Supplier geometry is preserved, not corrected.
Drawing basis: [@commonlandsCil829Drawing; @commonlandsCil829Step].
The inherited sensor footprint places its active-area datum at the FP origin
[@antmicroOv9281Board]. Sensor image-plane height is an explicit assumption.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, zipfile
import FreeCAD as App
import Part

ROOT=Path(__file__).resolve().parents[2]
DESIGN=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def bounds(s):
    b=s.BoundBox
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def feature(doc,parent,name,label,shape):
    assert shape.isValid(),name
    obj=doc.addObject('PartDesign::Feature',name);obj.Label=label;obj.Shape=shape
    parent.addObject(obj)
    return obj

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--zip',type=Path,required=True)
    ap.add_argument('--pdf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();out=a.output.resolve();assert not out.exists(),'Preserve existing review outputs'
    out.mkdir(parents=True)
    for source in [a.zip,a.pdf]:shutil.copy2(source,out/source.name)
    with zipfile.ZipFile(a.zip) as archive:
        members=[n for n in archive.namelist() if n.lower().endswith(('.stp','.step'))]
        assert len(members)==1,members
        source=out/Path(members[0]).name;source.write_bytes(archive.read(members[0]))
    model=Part.Shape();model.read(str(source));assert model.isValid() and len(model.Solids)==5
    front=min(s.BoundBox.XMin for s in model.Solids)
    barrel=next(s for s in model.Solids if abs(s.BoundBox.YLength-10)<1e-5)
    cy=barrel.CenterOfMass.y
    length=max(s.BoundBox.XMax for s in model.Solids)-front
    assert abs(length-11.6)<.3 and abs(barrel.BoundBox.XLength-5)<.01
    # Local lens coordinates: X/Y transverse; Z points outward from image plane.
    transform=App.Placement(App.Vector(0,-cy,front+14.7),App.Rotation(App.Vector(0,1,0),90))
    native=DESIGN/'electronics/r08';baseline=json.loads((native/'validation.json').read_text())
    for name,h in baseline['sha256'].items():assert sha(native/name)==h,name
    export=ROOT/'generated/ov9281-r08-desktop';record=json.loads((export/'source-record.json').read_text())
    assert record['native_sha256']==baseline['sha256']
    step_record=json.loads((export/'review-status.json').read_text())
    doc=App.newDocument('OV9281_CIL829_Fit_Study');doc.Label='OV9281 + supplied CIL829 — lens fit study'
    params=doc.addObject('App::FeaturePython','OpticsParameters')
    params.Label='EDIT HERE — provisional image height and focus travel (mm)'
    for name,value in [('ImagePlaneHeight',1.2),('FocusTravel',0),('ThreadPitch',.35),('DrawingTTL',14.7)]:
        params.addProperty('App::PropertyLength',name,'Optics');setattr(params,name,value)
    params.addProperty('App::PropertyString','Qualification','Optics')
    params.Qualification='ImagePlaneHeight 1.2 mm is assumed. FocusTravel is a mechanical study parameter, not a calibrated working distance.'
    groups={}
    for name,offset,angle in [('controller',(0,0,0),0),('head',(76,-1.25,0),-90),('flex-study',(29.2,-2,.613),0)]:
        path=export/(name+'.step');assert sha(path)==step_record['boards'][name]['source_sha256']
        shape=Part.Shape();shape.read(str(path));solids=sorted(shape.Solids,key=lambda s:s.Volume,reverse=True)
        group=doc.addObject('App::Part',name.replace('-','_'));group.Label=name+' — frozen R08 copper';groups[name]=group
        feature(doc,group,name.replace('-','_')+'Substrate','PCB substrate',solids[0])
        feature(doc,group,name.replace('-','_')+'Copper','PCB copper',Part.makeCompound(solids[1:]))
        group.Placement=App.Placement(App.Vector(*offset),App.Rotation(App.Vector(0,0,1),angle))
    head=groups['head']
    slide=doc.addObject('App::Part','LensSlide');slide.Label='Supplied lens — adjustable Z, variant unverified';head.addObject(slide)
    slide.Placement.Base=App.Vector(7.3325,-6.043,1.2)
    slide.setExpression('Placement.Base.z','OpticsParameters.ImagePlaneHeight + OpticsParameters.FocusTravel')
    solid_records=[]
    for i,solid in enumerate(model.Solids):
        shape=solid.copy();shape.Placement=transform.multiply(shape.Placement)
        obj=feature(doc,slide,'LensSolid'+str(i),'Supplier solid '+str(i)+(' — flat optical element, identity unresolved' if i==0 else ''),shape)
        obj.addProperty('App::PropertyString','SourceSHA256','Provenance');obj.SourceSHA256=sha(source)
        solid_records.append({'index':i,'source_bounds_mm':bounds(solid),'volume_mm3':solid.Volume})
    datum=feature(doc,head,'ActiveAreaDatum','Sensor active area — XY from KiCad; Z assumed',Part.makeBox(3.896,2.453,.01,App.Vector(7.3325-1.948,-6.043-1.2265,1.2)))
    datum.setExpression('Placement.Base.z','OpticsParameters.ImagePlaneHeight - 1.2 mm')
    axis=feature(doc,head,'OpticalAxis','Optical axis — reference only',Part.makeLine(App.Vector(7.3325,-6.043,.6),App.Vector(7.3325,-6.043,19)))
    # A reference cylinder illustrates the interface without inventing a holder.
    envelope=feature(doc,head,'ThreadReference','M8 x 0.35 interface envelope — reference, not a manufactured holder',Part.makeCylinder(4,6.6,App.Vector(7.3325,-6.043,4.3)))
    envelope.setExpression('Placement.Base.z','OpticsParameters.ImagePlaneHeight - 1.2 mm + OpticsParameters.FocusTravel')
    doc.recompute()
    # The supplied CAD barrel matches the PDF envelope; labels and internal flat
    # element do not prove that this is the no-filter optical variant.
    lens=Part.makeCompound([o.Shape for o in slide.Group])
    assert lens.isValid()
    for travel in [0,.5,1.0]:
        params.FocusTravel=travel;doc.recompute()
        assert abs(slide.Placement.Base.z-(1.2+travel))<1e-8
    params.FocusTravel=0;doc.recompute()
    path=out/'OV9281-CIL829-FIT-STUDY.FCStd';doc.saveAs(str(path));App.closeDocument(doc.Name)
    result={'revision':'OV9281-CIL829-FIT-STUDY-01','units':'mm','native_document':str(path),
        'baseline':'OV9281-P4-R08','baseline_sha256':baseline['sha256'],
        'source_sha256':{x.name:sha(x) for x in [out/a.zip.name,out/a.pdf.name,source]},
        'drawing':{'part':'CIL829-F2.5-M08ANIR','revision':2,'date':'2024-08-12','front_diameter_mm':10,'mount_thread':'M8 x 0.35',
            'rear_length_mm':6.6,'back_to_image_plane_mm':3.1,'ttl_reference_mm':14.7,'assumed_coverglass_mm':.4,'filter':'No filter',
            'efl_mm':2.8,'f_number':2.55,'mass_g':1.4},
        'step':{'filename':source.name,'internal_product':'CIL829-F3.0-M08A650','valid':True,'solids':solid_records,
            'barrel_length_mm':length,'front_diameter_mm':barrel.BoundBox.YLength,'non_solid_reference_geometry_excluded':True},
        'checks':{'barrel_matches_drawing_dimensions':True,'all_solids_valid':True,'focus_parameter_recomputed_at_mm':[0,.5,1],
            'optical_xy_datum_mm':[7.3325,-6.043],'image_plane_z_mm_assumed':1.2},
        'unresolved':['STEP filename and internal product disagree with PDF variant; do not infer IR transmission from CAD.',
            'Flat 0.3 mm optical element in STEP is preserved; identity is not established.',
            'Sensor die height and coverglass stack not qualified; 1.2 mm image-plane height is a placement assumption.',
            'No close-focus calibration, 940 nm optical qualification, fitted holder or filter integration.',
            'R09 PCB routing remains a trial; this optical study uses the selected R08 copper.'],
        'physical_fit_demonstrated':False,'functional_camera_demonstrated':False}
    (out/'review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'document':str(path),'barrel_length_mm':length,'source_hash':sha(source)},indent=2))

if __name__=='__main__':main()
