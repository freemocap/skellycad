"""Create the scripted, editable 58 baseplate in the pinned FreeCAD runtime."""
from pathlib import Path
import json,sys
import FreeCAD as App
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/baseplate'
sys.path.insert(0,str(HERE))
from baseplate_features import BaseplateModel

def main(save=True):
    p=json.loads((HERE/'parameters.json').read_text())
    doc=App.newDocument('BaseplateRebuild58')
    result=doc.addObject('Part::FeaturePython','Baseplate')
    result.Label='Rebuilt skull base plate — uncut 58 reference'
    BaseplateModel(result,p)
    doc.recompute();result.Shape.check(True)
    assert len(result.Shape.Solids)==1
    if App.GuiUp:
        result.ViewObject.Proxy=0;result.Visibility=True
        result.ViewObject.ShapeColor=(0.2,0.8,0.9)
        result.ViewObject.LineColor=(0.12,0.18,0.2)
    OUT.mkdir(parents=True,exist_ok=True)
    if save:doc.saveAs(str(OUT/'01-baseplate-candidate.FCStd'))
    print('Built',result.Shape.Volume,'mm3;',len(result.Shape.Faces),'faces',flush=True)
    return doc

if __name__=='__main__':main()
