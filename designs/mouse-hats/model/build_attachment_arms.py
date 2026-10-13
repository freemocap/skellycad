"""Independent arm concept; CURRENT is unchanged until attachment/motion review."""
from pathlib import Path
import json,sys,runpy
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
api=runpy.run_path(str(HERE/'build_mount.py'));api['load_modules']()
from attachment_arm_features import SmoothArm,unit,geometry
ROOT=api['ROOT'];OUT=ROOT/'generated/mouse-hats/arms/attachments';OUT.mkdir(parents=True,exist_ok=True)

def main():
    p=json.loads((HERE/'attachment-arms.json').read_text());doc=App.newDocument('AttachmentArmConcept')
    doc.Label='ARM CONCEPT — face-aligned roots and contained collar ends'
    n=unit(p['socket_axis']);center=App.Vector(*p['socket_center_mm'])
    sd=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction/socket/01-socket-candidate.FCStd'))
    socket=doc.addObject('Part::Feature','SocketReference')
    socket.Shape=sd.UpperCollar.Shape.copy()
    socket.Placement=App.Placement(center,App.Rotation(App.Vector(0,0,1),n)).multiply(socket.Placement)
    traydoc=App.openDocument(str(ROOT/'generated/mouse-hats/model/tray-cleanup/cleaned-tray.FCStd'))
    tray=doc.addObject('Part::Feature','TrayReference');tray.Shape=traydoc.CleanedTrayAndMount.Shape.copy()
    report={}
    bore=Part.makeCylinder(1.45,10,center,n)
    ball=Part.makeSphere(2.1,center)
    for name in ['rear','top']:
        data={**p,'arm':p[name]};obj=doc.addObject('Part::FeaturePython',name.title()+'Arm')
        SmoothArm(obj,data);doc.recompute();obj.Shape.check(True)
        item=dict(volume_mm3=obj.Shape.Volume)
        _,rootcap,endcap,_,angle=geometry(data,obj.Width.Value,obj.Thickness.Value)
        item['root_endcap_outside_parent_mm2']=Part.Face(rootcap).cut(tray.Shape).Area
        item['socket_endcap_outside_parent_mm2']=Part.Face(endcap).cut(socket.Shape).Area
        assert item['root_endcap_outside_parent_mm2']<1e-7
        assert item['socket_endcap_outside_parent_mm2']<1e-7
        for key,shape in [('bore',bore),('ball_seat',ball),('socket',socket.Shape),('tray',tray.Shape)]:
            common=obj.Shape.common(shape,0.001)
            if common.Solids:common.check(True)
            item[key+'_overlap_mm3']=common.Volume
        assert item['bore_overlap_mm3']<1e-7 and item['ball_seat_overlap_mm3']<1e-7,item
        report[name]=item
    union=doc.RearArm.Shape.fuse(doc.TopArm.Shape).fuse(socket.Shape).fuse(tray.Shape)
    union.check(True);report['combined_solid_count']=len(union.Solids)
    assert len(union.Solids)==1
    final=doc.addObject('Part::MultiFuse','CompleteCarrier')
    final.Label='Complete tray + both arms + socket — fused solid'
    final.Shapes=[tray,doc.RearArm,doc.TopArm,socket];final.Refine=True
    doc.recompute();final.Shape.check(True)
    doc.saveAs(str(OUT/'attachment-arm-concept.FCStd'))
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report)
    return doc
if __name__=='__main__':main()
