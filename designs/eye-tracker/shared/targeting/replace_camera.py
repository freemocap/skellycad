"""Replace camera reference hardware in a hash-pinned complete assembly."""
from pathlib import Path
import sys, json, hashlib
import numpy as np
import FreeCAD as A, Part, MeshPart
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT/'designs/eye-tracker'))
from shared.camera import selected_model, checked_asset
from detailed_ribbon import ribbon_solid
import ribbon_geometry as g

def world(obj):
    sh = obj.Shape.copy()
    sh.Placement = obj.getGlobalPlacement()
    return sh

def assign(obj, sh):
    # A Shape's placement is local to its containing App::Part.
    parent_pose = obj.getGlobalPlacement().multiply(obj.Placement.inverse())
    sh = sh.copy()
    sh.Placement = parent_pose.inverse().multiply(sh.Placement)
    obj.Shape = sh

def build(recipe):
    recipe = Path(recipe).resolve()
    cfg = json.loads(recipe.read_text())
    selected = json.loads((ROOT/cfg['selected_species_manifest']).read_text())
    checked_asset({'path':selected['native_checkpoint'],'sha256':selected['native_sha256']})
    assert hashlib.sha256((ROOT/cfg['camera_manifest']).read_bytes()).hexdigest()==cfg['camera_manifest_sha256'], 'Camera selection changed; review recipe before reuse'
    model = selected_model()
    source = checked_asset(cfg['source'])
    d = A.openDocument(str(source))
    out = ROOT/'generated/eye-tracker'/cfg['species']/recipe.parent.name
    out.mkdir(parents=True, exist_ok=True)
    main_pose = d.PCB.getGlobalPlacement()
    head_pose = d.camera_pcb.getGlobalPlacement()
    old_axis = head_pose.Rotation.multVec(A.Vector(0,0,1))
    fixtures = ['FinishedCarrier','eye_primary_Holder','eye_primary_Cap','eye_primary_Clip','skull_mount_Baseplate','RetainedPCBTray','RetainedSocket','UpperSupport','RearRibbonGuard']
    before = {n:world(d.getObject(n)) for n in fixtures}
    old = {n:world(d.getObject(n)) for n in ['PCB','JST_4pin','camera_pcb','M4_lens','IR_LED','IR_LED_001','RibbonCandidate']}
    shift = A.Vector(0,31.283345794677736,.25)
    shapes={}
    for name,rec in model['parts'].items():
        s=Part.Shape();s.read(str(checked_asset(rec)));s.translate(-shift);shapes[name]=s
    boards=sorted(shapes['Red_PLA_boards'].Solids,key=lambda s:s.CenterOfMass.y)
    whites=sorted(shapes['White_PLA_connector_LEDs'].Solids,key=lambda s:s.CenterOfMass.y)
    leds=sorted(whites[1:],key=lambda s:s.CenterOfMass.x,reverse=True)
    replacements={'PCB':(boards[0],False),'camera_pcb':(boards[1],True),
                  'JST_4pin':(whites[0],False),'M4_lens':(shapes['Black_PLA_lens'],True),
                  'IR_LED':(leds[0],True),'IR_LED_001':(leds[1],True)}
    for name,(s,head) in replacements.items():
        s=s.copy()
        if head:s.translate(A.Vector(0,-32.85,0))
        s.Placement=(head_pose if head else main_pose).multiply(s.Placement)
        assign(d.getObject(name),s)
        d.getObject(name).Label={'M4_lens':'Selected R08 notched lens and holder','JST_4pin':'Selected R08 JST connector'}.get(name,name)
    # Retain the solved top surface and endpoint frames; flatten only the material offsets.
    rib,mesh,metric=ribbon_solid(cfg['ribbon_parameters'])
    mount_pose = main_pose.multiply(A.Placement(A.Vector(*g.BASE),A.Rotation(A.Vector(*g.FRAME[:,0]),A.Vector(*g.FRAME[:,1]),A.Vector(*g.FRAME[:,2]),'ZXY')).inverse())
    rib.Placement=mount_pose.multiply(rib.Placement)
    assign(d.RibbonCandidate,rib)
    endpoint,R=g.endpoint(cfg['ribbon_parameters'])
    endpoint_world=mount_pose.multVec(A.Vector(*endpoint[0]))
    assert (endpoint_world-head_pose.Base).Length<1e-5
    sensor_local=A.Vector(*model['optical_datum']['sensor_center_mm'])-shift-A.Vector(0,32.85,0)
    origin_local=A.Vector(*model['optical_datum']['origin_mm'])-shift-A.Vector(0,32.85,0)
    sensor=head_pose.multVec(sensor_local);origin=head_pose.multVec(origin_local)
    axis=d.addObject('Part::Feature','DetailedOpticalAxis')
    axis.Shape=Part.makeLine(origin,origin+old_axis*20)
    for n,v in [('Origin',origin),('SensorCenter',sensor),('Direction',old_axis)]:
        axis.addProperty('App::PropertyVector',n);setattr(axis,n,v)
    axis.addProperty('App::PropertyBool','ExportForPrinting').ExportForPrinting=False
    record=d.addObject('App::FeaturePython','DetailedCameraRecipe')
    record.addProperty('App::PropertyString','RecipeJSON').RecipeJSON=json.dumps(cfg)
    report={'revision':cfg['revision'],'camera_checkpoint':model['revision'],'units':'mm','source':cfg['source'],
            'endpoint_error_mm':(endpoint_world-head_pose.Base).Length,'surface_metric':metric,
            'endpoint_frames_preserved':True,'thickness_mm':.25,'fixed_interfaces':{},'camera_interference':{},'ribbon_interference':{},'physical_fit_verified':False}
    for name,baseline in before.items():
        sh=world(d.getObject(name));diff=0.0 if sh.isSame(baseline) else sh.cut(baseline).Volume+baseline.cut(sh).Volume
        assert diff<1e-6,name
        report['fixed_interfaces'][name]={'difference_mm3':diff}
    for name in replacements:
        sh=world(d.getObject(name));assert sh.isValid()
        for fixture in fixtures[:5]:
            v=sh.common(before[fixture]).Volume;inherited=old[name].common(before[fixture]).Volume
            report['camera_interference'][name+'/'+fixture]={'overlap_mm3':v,'previous_overlap_mm3':inherited}
        sh.exportBrep(str(out/(name+'-world.brep')))
        MeshPart.meshFromShape(Shape=sh,LinearDeflection=.04,AngularDeflection=.12,Relative=False).write(str(out/(name+'-world.stl')))
    for name in fixtures[:5]+list(replacements):
        sh=world(d.getObject(name));v=rib.common(sh).Volume
        report['ribbon_interference'][name]={'overlap_mm3':v,'previous_overlap_mm3':old['RibbonCandidate'].common(before[name] if name in before else old[name]).Volume}
        print(cfg['species'],name,'ribbon overlap',v,flush=True)
    report['status']='Detailed geometry review; holder and ribbon clearance require hardware fitting'
    report['new_interferences']={k:v for k,v in report['camera_interference'].items() if v['overlap_mm3']>v['previous_overlap_mm3']+1e-6}
    report['ribbon_clear']=all(v['overlap_mm3']<1e-6 for v in report['ribbon_interference'].values())
    if cfg['species']=='rat':
        target=A.Vector(*json.loads(d.TargetRecipe.RecipeJSON)['target_center_world_mm']);delta=target-sensor
        report['aim']={'miss_mm':delta.cross(old_axis).Length,'forward_mm':delta.dot(old_axis)}
        assert report['aim']['miss_mm']<1e-6
    else:
        previous=head_pose.multVec(A.Vector(.088458776473999,5.7195234298706055,1))
        assert (sensor-previous).cross(old_axis).Length<1e-6
        report['aim']={'original_axis_line_preserved':True}
    rib.exportBrep(str(out/'RibbonCandidate-world.brep'))
    mesh.transform(mount_pose.toMatrix());mesh.write(str(out/'RibbonCandidate-world.stl'))
    d.recompute();d.Label=cfg['revision']+' - detailed camera'
    d.saveAs(str(out/(cfg['revision']+'.FCStd')))
    (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DETAILED_CAMERA_BUILT',out,flush=True)

if __name__=='__main__':build(sys.argv[1])
