"""Pose the camera holder inside the socket for a print-in-place review/export."""
from build import *
import holder_features,clip_features

def main():
    carrier=App.openDocument(str(OUT/'carrier.FCStd'))
    holder=App.openDocument(str(OUT/'holder.FCStd'))
    pose=json.loads((OUT/'holder-pose.json').read_text())
    r=pose['rotation_row_vector'];t=pose['translation_mm']
    rotation=App.Rotation(App.Vector(*r[0]),App.Vector(*r[1]),App.Vector(*r[2]),'ZXY')
    placement=App.Placement(App.Vector(*t),rotation)
    doc=App.newDocument('PrintInPlaceReview');doc.Label='PRINT TEST — assembled V5 camera pose'
    mainpart=doc.addObject('Part::Feature','Carrier');mainpart.Shape=carrier.LongerPCBRetainers.Shape.copy()
    head=doc.addObject('Part::Feature','Holder');head.Shape=holder.ThickerHolderWalls.Shape.copy()
    head.Placement=placement.multiply(head.Placement)
    collision=overlap(mainpart.Shape,head.Shape,0)
    report={'holder_carrier_overlap_mm3':collision,'pose_source':'V5 holder mesh, rigid fit with ball-center anchor',
            'holder_pose_fit_p70_mm':pose['p70_mm'],
            'minimum_separation_mm':mainpart.Shape.distToShape(head.Shape)[0]}
    entries={p['name']:p for p in json.loads((MODEL/'current-parts.json').read_text())['parts']}
    clip=doc.addObject('Part::Feature','ClipReference');clip.Shape=holder.ExtendedClip.Shape.copy()
    clip.Label='Clip — installed reference; print separately'
    clip.Placement=placement.multiply(frame(entries['Holder']).inverse()).multiply(frame(entries['Clip'])).multiply(clip.Placement)
    for name in ['Cap','Baseplate']:
        source=App.openDocument(str(ROOT/entries[name]['file']))
        shape=source.getObject(entries[name]['object']).Shape.copy()
        obj=doc.addObject('Part::Feature',name+'Reference');obj.Shape=shape
        obj.Label=name+' — fit reference; print separately'
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.03,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid()
        mesh.write(str(OUT/(name.lower()+'.stl')))
    doc.recompute()
    print(json.dumps(report),flush=True)
    doc.saveAs(str(OUT/'print-in-place-review.FCStd'))
    (OUT/'assembly-validation.json').write_text(json.dumps(report,indent=2))
    if collision>1e-6:
        print('Print-in-place export withheld: interference requires resolution.',flush=True)
        return
    compound=Part.makeCompound([mainpart.Shape,head.Shape])
    mesh=MeshPart.meshFromShape(Shape=compound,LinearDeflection=.03,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid()
    mesh.write(str(OUT/'carrier-and-holder-print-in-place.stl'))

if __name__=='__main__':main()
