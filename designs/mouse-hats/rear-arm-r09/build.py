"""Build R09A: wide tapered root and one-sided outer band."""
from pathlib import Path
import sys,json,runpy
import FreeCAD as App
import Part,MeshPart
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
for p in [HERE,HERE.parent/'model',HERE.parent/'print-test',HERE.parent/'print-test-r03']:sys.path.insert(0,str(p))
runpy.run_path(str(HERE.parent/'model/build_mount.py'))['load_modules']()
import attachment_arm_features,arm_finish_features,stem_blend_features,retention_features,socket_revision_features
from gap_carrier_features import GapRoot
from gap_sweep import geometry as rear_geometry
OUT=ROOT/'generated/mouse-hats/rear-arm-r09';OUT.mkdir(parents=True,exist_ok=True)
sweep=json.loads((HERE/'settings.json').read_text());r03=json.loads((HERE.parent/'print-test-r03/settings.json').read_text())
pose=json.loads((ROOT/'generated/mouse-hats/print-test/r01/holder-pose.json').read_text())
reference=App.openDocument(str(ROOT/'generated/mouse-hats/print-test/r03/print-in-place-review.FCStd'))
reports={}
for key,variant in sweep['variants'].items():
    if len(sys.argv)>1 and key!=sys.argv[1]:continue
    doc=App.openDocument(str(ROOT/'generated/mouse-hats/print-test/r03/carrier.FCStd'))
    obj=doc.addObject('Part::FeaturePython','RibbonClearanceCarrier')
    GapRoot(obj,doc.LongerPCBRetainers,doc.TrayReference,doc.SocketReference,doc.RearArm,doc.TopArm,r03,pose['ball_center_mm'])
    obj.RootUp=sweep['root_up_mm'];obj.RootForward=sweep['root_forward_mm'];obj.OuterBulge=sweep['outer_bulge_mm'];obj.AttachmentAngle=sweep['attachment_angle_deg'];obj.SweepJSON=json.dumps(sweep);obj.ExtraDrop=variant['extra_drop_mm'];doc.recompute()
    shape=obj.Shape;shape.check(True)
    data=json.loads(doc.RearArm.DesignJSON);data['arm']['root_mm'][2]+=sweep['root_forward_mm'];data['arm']['root_mm'][1]=sweep['root_lower_y_mm']+sweep['root_width_mm']/2;data['arm']['root_width_mm']=sweep['root_width_mm'];data.update(attachment_radius_mm=2.65,socket_lead_mm=1.,socket_width_mm=3.,socket_thickness_mm=2.2)
    arm,path,details=rear_geometry(data,sweep,variant['extra_drop_mm'])
    report={**details,'valid':shape.isValid(),'solids':len(shape.Solids),'volume_mm3':shape.Volume,
      'holder_overlap_mm3':shape.common(reference.Holder.Shape,0).Volume,
      'minimum_holder_gap_mm':shape.distToShape(reference.Holder.Shape)[0]}
    print(key,json.dumps(report),flush=True)
    assert report['valid'] and report['solids']==1 and report['holder_overlap_mm3']<1e-6
    rear=doc.addObject('Part::Feature','RearSweepInspection');rear.Shape=arm
    line=doc.addObject('Part::Feature','RearCenterline');line.Shape=path
    doc.Label='R09'+key+' - '+variant['label'];doc.recompute();doc.saveAs(str(OUT/('r09'+key.lower()+'-carrier.FCStd')))
    reports[key]=report
    (OUT/('validation-'+key+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    App.closeDocument(doc.Name)
(OUT/'validation.json').write_text(json.dumps(reports,indent=2)+'\n')

