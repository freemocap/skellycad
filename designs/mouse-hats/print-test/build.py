"""First print-test revisions: longer PCB retainers and outward holder walls."""
from pathlib import Path
import sys,json,runpy
import FreeCAD as App
import Part,MeshPart

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
MODEL=HERE.parent/'model';RECON=HERE.parent/'reconstruction'
sys.path.insert(0,str(HERE));sys.path.insert(0,str(MODEL))
runpy.run_path(str(MODEL/'build_mount.py'))['load_modules']()
import attachment_arm_features,arm_finish_features,stem_blend_features
from retention_features import LongerRetainers
OUT=ROOT/'generated/mouse-hats/print-test/r01';OUT.mkdir(parents=True,exist_ok=True)


def frame(entry):
    p=entry['local_to_assembly']
    return App.Placement(App.Vector(*p['translation_mm']),App.Rotation(*p['quaternion_xyzw']))


def overlap(a,b,tolerance=.0001):
    # Isolate OCCT's tolerance updates between successive coincident-face checks.
    aa=Part.Shape();aa.importBrepFromString(a.exportBrepToString())
    bb=Part.Shape();bb.importBrepFromString(b.exportBrepToString())
    common=aa.common(bb,tolerance)
    return common.Volume


def main():
    settings=json.loads((HERE/'settings.json').read_text());report={}
    carrier=App.openDocument(str(ROOT/'generated/mouse-hats/arms/stem-blend/stem-blended-carrier.FCStd'))
    profiles=json.loads((RECON/'main_carrier/profiles.json').read_text())['features']
    profiles=[p for p in profiles if p['name'] in ['LeftLip','RightLip','LowerPCBStop']]
    final=carrier.addObject('Part::FeaturePython','LongerPCBRetainers')
    final.Label='Carrier — PCB retainers +1.5 / +0.7 mm'
    LongerRetainers(final,carrier.BlendedCarrier,profiles,settings['pcb_tab_extension_mm'],settings['lower_pcb_tab_extension_mm'])
    carrier.recompute();final.Shape.check(True)
    added=final.Shape.cut(carrier.BlendedCarrier.Shape,.001)
    removed=carrier.BlendedCarrier.Shape.cut(final.Shape,.001)
    report['carrier']={'added_mm3':added.Volume,'removed_mm3':removed.Volume}
    assert removed.Volume<1e-6
    for label,file,name in [('cap','pcb-cap/01-pcb-cap-candidate.FCStd','PCBCap'),
                            ('baseplate','baseplate/01-baseplate-candidate.FCStd','Baseplate')]:
        other=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction'/file))
        volume=final.Shape.common(other.getObject(name).Shape,.001).Volume
        report['carrier'][label+'_overlap_mm3']=volume
        assert volume<1e-6,(label,volume)
        App.closeDocument(other.Name)
    carrier.Label='PRINT TEST — longer PCB retention'
    carrier.saveAs(str(OUT/'carrier.FCStd'))
    from holder_features import ThickerWalls
    original=json.loads((RECON/'camera_holder/parameters.json').read_text())
    holder=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction/camera-holder/01-holder-candidate.FCStd'))
    old=holder.TrimHolderSide.Shape.copy()
    safe=holder.addObject('Part::FeaturePython','ThickerHolderWalls')
    safe.Label='Holder — outward walls +0.5 mm; original interior'
    ThickerWalls(safe,holder.TrimHolderSide,original,settings['holder_outward_wall_addition_mm'])
    holder.recompute();safe.Proxy.execute(safe);shape=safe.Shape;shape.check(True)
    added=shape.cut(old,.0001);removed=old.cut(shape,.0001)
    inside=Part.makeBox(original['rail_inner_x_mm'][1]-original['rail_inner_x_mm'][0],40,40,
                        App.Vector(original['rail_inner_x_mm'][0],-20,-10))
    clipdoc=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction/camera-clip/03-complete-clip.FCStd'))
    entries={p['name']:p for p in json.loads((MODEL/'current-parts.json').read_text())['parts']}
    from clip_features import WiderClip
    clipbase=holder.addObject('Part::Feature','OriginalClip');clipbase.Shape=clipdoc.RightCrown.Shape.copy()
    wideclip=holder.addObject('Part::FeaturePython','ExtendedClip');wideclip.Label='Clip — crosspiece extended 1 mm, intact arms moved outward'
    WiderClip(wideclip,clipbase,safe);holder.recompute();wideclip.Proxy.execute(wideclip);wideclip.Shape.check(True)
    shape=safe.Shape.copy()
    clip=wideclip.Shape.copy()
    clip.Placement=frame(entries['Holder']).inverse().multiply(frame(entries['Clip'])).multiply(clip.Placement)
    report['holder']={'added_mm3':added.Volume,'removed_mm3':removed.Volume,
        'original_holder_vs_extended_clip_overlap_mm3':overlap(old,clip),
        'clip_overlap_mm3':overlap(shape,clip),
        'new_material_clip_overlap_mm3':overlap(added,clip),
        'added_inside_sensor_rail_envelope_mm3':added.common(inside,.0001).Volume}
    assert removed.Volume<1e-6 and report['holder']['added_inside_sensor_rail_envelope_mm3']<1e-6
    assert report['holder']['clip_overlap_mm3']<.01,report
    report['holder']['clip_fit_note']='Tiny inherited-skew contact; no macroscopic interference. Inspect in print test.'
    holder.Label='PRINT TEST — outward holder walls'
    holder.saveAs(str(OUT/'holder.FCStd'))
    for name,solid in [('carrier',final.Shape),('holder',shape),('clip',wideclip.Shape)]:
        mesh=MeshPart.meshFromShape(Shape=solid,LinearDeflection=settings['stl_linear_deflection_mm'],
                                   AngularDeflection=settings['stl_angular_deflection_radians'],Relative=False)
        assert mesh.isSolid(),name
        mesh.write(str(OUT/(name+'.stl')))
        report.setdefault(name,{})
        report[name]['valid']=solid.isValid();report[name]['solid_count']=len(solid.Solids)
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')

    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
