"""Baseplate taper candidate with protected upper mount and print R02 export."""
from pathlib import Path
import sys,json,runpy
import FreeCAD as App
import Part,MeshPart
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/'reconstruction/baseplate'))
import baseplate_features
from baseplate_taper_features import TaperedBaseplate
OUT=ROOT/'generated/mouse-hats/baseplate-taper';OUT.mkdir(parents=True,exist_ok=True)


def validate(doc):
    old=doc.Baseplate.Shape;new=doc.TaperedBaseplate.Shape
    # Protect the complete solid region at and above the pocket floor. This is
    # stronger than merely checking that the inserted stem still has no overlap.
    protected=Part.makeBox(100,50,100,App.Vector(-50,1.5,-50))
    removed=old.cut(new,.0001);added=new.cut(old,.0001)
    protected_loss=removed.common(protected,.0001).Volume
    carrier=App.openDocument(str(ROOT/'generated/mouse-hats/print-test/r01/print-in-place-review.FCStd'))
    interference=new.common(carrier.Carrier.Shape,.0001).Volume
    bottom=Part.makePlane(100,100,App.Vector(-50,-5,-50),App.Vector(0,1,0))
    # Plane origin/orientation is unnecessary for area: identify the planar face.
    areas=lambda shape:sum(f.Area for f in shape.Faces if abs(f.CenterOfMass.y+5)<1e-6
                          and abs(abs(f.normalAt(0,0).y)-1)<1e-6)
    report={'valid':new.isValid(),'solid_count':len(new.Solids),'bottom_scale':doc.TaperedBaseplate.BottomScale,
        'original_bottom_area_mm2':areas(old),'tapered_bottom_area_mm2':areas(new),
        'removed_mm3':removed.Volume,'added_mm3':added.Volume,
        'protected_mount_region_removed_mm3':protected_loss,'seated_carrier_overlap_mm3':interference}
    assert report['valid'] and report['solid_count']==1
    assert added.Volume<1e-6 and protected_loss<1e-6 and interference<1e-6
    assert abs(report['tapered_bottom_area_mm2']/report['original_bottom_area_mm2']-doc.TaperedBaseplate.BottomScale**2)<1e-6
    App.closeDocument(carrier.Name)
    return report


def main():
    settings=json.loads((HERE/'settings.json').read_text())
    p=json.loads((HERE.parent/'reconstruction/baseplate/parameters.json').read_text())
    doc=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction/baseplate/01-baseplate-candidate.FCStd'))
    final=doc.addObject('Part::FeaturePython','TaperedBaseplate')
    final.Label='Baseplate — smaller footprint, protected mount'
    TaperedBaseplate(final,doc.Baseplate,p['outer_profile_mm'],settings)
    doc.recompute();report=validate(doc)
    doc.Label='BASEPLATE — tapered lower stock'
    doc.saveAs(str(OUT/'tapered-baseplate.FCStd'))
    mesh=MeshPart.meshFromShape(Shape=final.Shape,LinearDeflection=.03,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid();mesh.write(str(OUT/'baseplate.stl'))
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    App.closeDocument(doc.Name);doc=App.openDocument(str(OUT/'tapered-baseplate.FCStd'))
    volume=doc.TaperedBaseplate.Shape.Volume
    for scale in [1,.65,settings['bottom_scale']]:
        doc.TaperedBaseplate.BottomScale=scale;doc.recompute();validate(doc)
    assert abs(doc.TaperedBaseplate.Shape.Volume-volume)<1e-6
    print(json.dumps(report,indent=2));print('Fresh reopen / scale edits / restore passed.')


if __name__=='__main__':main()

