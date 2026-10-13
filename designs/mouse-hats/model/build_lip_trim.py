"""Confirmed shoulder corner snips only; lip front remains unchanged."""
import runpy
from pathlib import Path
import FreeCAD as App
import Part

HERE=Path(__file__).resolve().parent
api=runpy.run_path(str(HERE/'build_mount.py'))
OUT=api['ROOT']/'generated/mouse-hats/model/lip-trim'


def main():
    doc=api['main'](save=False)
    tools=[]
    for name,z in [('UpperCornerTool',3.2544620596798137),
                   ('LowerCornerTool',-3.3315379403202114-20)]:
        tool=doc.addObject('Part::Box',name)
        tool.Length=40;tool.Width=40;tool.Height=20
        tool.Placement.Base=App.Vector(-10,-10,z)
        tools.append(tool)
    union=doc.addObject('Part::MultiFuse','CornerTools');union.Shapes=tools
    corners=doc.addObject('Part::Common','LipCorners')
    corners.Base=doc.MountSection02_0;corners.Tool=union
    final=doc.addObject('Part::Cut','TrimmedTrayAndMount')
    final.Label='PCB tray + stem — confirmed lip corner snips'
    final.Base=doc.PCBTrayAndMount;final.Tool=corners;final.Refine=True
    doc.recompute()
    final.Shape.check(True)
    assert len(final.Shape.Solids)==1
    assert len(corners.Shape.Solids)==2
    added=final.Shape.cut(doc.PCBTrayAndMount.Shape,0.001)
    if added.Solids: added.check(True)
    assert abs(added.Volume)<1e-7
    assert abs(doc.PCBTrayAndMount.Shape.Volume-final.Shape.Volume-corners.Shape.Volume)<1e-5
    assert final.Shape.common(doc.Baseplate.Shape,0.001).Volume<1e-7
    # Preserve the entire portion that enters the receiving baseplate (Y < 5).
    seat=Part.makeBox(40,14.999,40,App.Vector(-10,-10,-20))
    before=doc.PCBTrayAndMount.Shape.common(seat)
    after=final.Shape.common(seat)
    for difference in (before.cut(after,0.001),after.cut(before,0.001)):
        if difference.Solids:difference.check(True)
        assert difference.Volume<1e-7
    doc.Label='Lip: corner trims only — original front'
    OUT.mkdir(parents=True,exist_ok=True)
    doc.saveAs(str(OUT/'trimmed-mount.FCStd'))
    print('Removed:',corners.Shape.Volume,'mm3. No extension; one valid solid; seated stem unchanged.')
    return doc


if __name__=='__main__':main()


