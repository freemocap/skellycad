"""Show verified geometry snapshots together; this is not a linked assembly."""
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/assembly'

def main():
    doc=App.newDocument('TrayCapAssemblyReview58')
    for name,file,label,color,transparency in [
        ('Baseplate','baseplate','Base plate — verified snapshot',(0.65,0.45,0.9),55),
        ('Tray','tray-stem','PCB tray + stem — verified snapshot',(0.2,0.8,0.9),0),
        ('Cap','pcb-cap','PCB cap — verified snapshot',(0.35,0.85,0.45),65)]:
        obj=doc.addObject('PartDesign::Feature',name)
        obj.Label=label;obj.Shape=Part.read(str(OUT/(file+'.brep')))
        obj.addProperty('App::PropertyString','Provenance','Review')
        obj.Provenance='Fixed snapshot from pcb_cap/verify.py; re-run verification and review after design changes.'
        obj.ViewObject.ShapeColor=color;obj.ViewObject.Transparency=transparency
        obj.ViewObject.LineColor=(0.15,0.2,0.2)
    section=doc.addObject('PartDesign::Feature','StemSection')
    section.Label='Virtual section of tray/stem for inspection — not a separate part'
    section.Shape=doc.Tray.Shape.common(Part.makeBox(30,35,10.2,App.Vector(-10,-10,-5.1)))
    section.ViewObject.ShapeColor=(0.2,0.8,0.9)
    # First inspect the seat without the tall tray hiding the receiving pocket.
    doc.Tray.Visibility=False;doc.Cap.Visibility=False;section.Visibility=True
    doc.recompute()
    view=Gui.activeDocument().activeView()
    view.setCameraOrientation(App.Rotation(App.Vector(0,0,1),160).multiply(App.Rotation(App.Vector(1,0,0),70)).Q)
    view.fitAll()
    view.saveImage(str(OUT/'mount-interface.png'),1000,750,'Current')
    # Leave the complete three-part review visible in the saved file.
    section.Visibility=False;doc.Tray.Visibility=True;doc.Cap.Visibility=True
    view.viewIsometric();view.fitAll()
    view.saveImage(str(OUT/'tray-cap-baseplate.png'),1000,750,'Current')
    doc.recompute();doc.saveAs(str(OUT/'01-tray-cap-baseplate-review.FCStd'))
    return doc

if __name__=='__main__':main()
