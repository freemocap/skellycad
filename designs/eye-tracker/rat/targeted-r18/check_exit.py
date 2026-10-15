from pathlib import Path
import sys,json
import FreeCAD as A
R=Path.cwd();S=R/'designs/eye-tracker/rat/targeted-r18';sys.path.insert(0,str(R/'designs/eye-tracker/shared/targeting'));from detailed_ribbon import ribbon_solid
b=json.loads((S/'baseline.json').read_text());d=A.openDocument(str(R/b['source']['native_checkpoint']));r,_,_=ribbon_solid(json.loads((S/'solution.json').read_text())['parameters']);sh=d.RetainedPCBTray.Shape;print('tray',r.common(sh).Volume,r.distToShape(sh)[0],flush=True)

