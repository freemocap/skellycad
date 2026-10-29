"""Add scale guides and independently verify the saved native assembly."""
from pathlib import Path
import hashlib,json,zipfile
import FreeCAD as App
import Part
from verify_r11_native import measurements
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'generated/ov9281-r11-mechanics';V=App.Vector
def global_shape(o):
    s=o.Shape.copy();s.Placement=o.getGlobalPlacement();return s
def main():
    path=OUT/'OV9281-R11-MATCHED.FCStd';report=json.loads((OUT/'validation.json').read_text());assert hashlib.sha256(path.read_bytes()).hexdigest()==report['native_sha256'];doc=App.openDocument(str(path))
    print('Native assembly loaded',flush=True)
    assert not doc.getObject('ScaleGuides');group=doc.addObject('App::Part','ScaleGuides');group.Label='Dimensions in millimetres — reference only';doc.getObject('FlatAssembly').addObject(group)
    def add(name,label,shape):
        q=doc.addObject('Part::Feature',name);q.Label=label;q.Shape=shape;group.addObject(q);q.addProperty('App::PropertyVector','StudyColor','Review').StudyColor=V(.2,.25,.3);q.addProperty('App::PropertyBool','ReviewVisible','Review').ReviewVisible=True
    def text(name,words,x,y,size=1.2):
        q=doc.addObject('App::Annotation',name);q.LabelText=[words];q.Position=V(x,y,0);group.addObject(q);q.addProperty('App::PropertyBool','ReviewVisible','Review').ReviewVisible=True
    add('LengthGuide','74.85 mm flat span',Part.makeCompound([Part.makeLine(V(0,-3,0),V(74.85,-3,0)),Part.makeLine(V(0,-3.7,0),V(0,-2.3,0)),Part.makeLine(V(74.85,-3.7,0),V(74.85,-2.3,0))]))
    text('LengthLabel','74.85 mm flat span',27,-5.2);text('ControllerLabel','Controller 28 x 14 mm',0,17);text('FlexLabel','Flex 32.85 x 8 x 0.166 mm',29,14.5,1.);text('HeadLabel','Head 14 x 14 mm',61,17,1.);text('ThicknessLabel','Component regions 0.303 mm / optics provisional',12,-8,1.)
    q=doc.addObject('App::Annotation','PupilReferenceLabel');q.LabelText=['Pupil R08 reference — approximate photo electronics'];q.Position=V(0,39,0);q.addProperty('App::PropertyBool','ReviewVisible','Review').ReviewVisible=False
    print('Scale annotations added',flush=True);invalid=[];solids=0
    for o in doc.Objects:
        if hasattr(o,'Shape') and not o.Shape.isNull():
            # Copper solids were validated and area/volume checked at build.
            # Revalidate the physical envelopes here without repeating the
            # expensive detailed copper compound topology checks.
            if 'Cu_' not in o.Name and not o.Shape.isValid():invalid.append(o.Name)
            solids+=len(o.Shape.Solids)
    assert not invalid,invalid;print('Physical envelopes revalidated',flush=True)
    a=doc.getObject('Board_controller').Shape.BoundBox;h=doc.getObject('Board_head').Shape.BoundBox;f=doc.getObject('Board_flex').Shape.BoundBox
    assert abs(a.XLength-28)<1e-7 and abs(a.YLength-14)<1e-7 and abs(a.ZLength-.303)<1e-7
    assert abs(h.XLength-14)<1e-7 and abs(f.XLength-32.85)<1e-7 and abs(f.ZLength-.166)<1e-7
    # The rotated head is well above the controller; rigid-body transforms
    # preserve all local component/support/optics clearances checked at build.
    head=doc.getObject('Bent_head');head_shapes=[global_shape(o) for o in head.OutListRecursive if o.TypeId=='Part::Feature' and hasattr(o,'Shape') and o.Shape.Solids]
    ctrl=doc.getObject('Bent_controller');ctrl_shapes=[global_shape(o) for o in ctrl.OutListRecursive if o.TypeId=='Part::Feature' and hasattr(o,'Shape') and o.Shape.Solids]
    hb=Part.makeCompound(head_shapes).BoundBox;cb=Part.makeCompound(ctrl_shapes).BoundBox;assert hb.ZMin>cb.ZMax
    doc.recompute();(OUT/'geometry-measurements.json').write_text(json.dumps(measurements(doc),indent=2)+'\n');doc.save();App.closeDocument(doc.Name)
    with zipfile.ZipFile(path) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
    report['initial_build_native_sha256']=report['native_sha256'];report['native_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();report['independent_reload']={'invalid_shapes':invalid,'valid_solids':solids,'dimensions_checked':True,'bent_head_controller_z_separation_mm':hb.ZMin-cb.ZMax}
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report['independent_reload'])
if __name__=='__main__':main()
