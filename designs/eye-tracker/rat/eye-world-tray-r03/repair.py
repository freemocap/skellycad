from pathlib import Path
import FreeCAD as A,Part
O=Path('generated/eye-tracker/rat/eye-world-tray-r03')
def read(n):
 s=Part.Shape();s.read(str(O/(n+'.brep')));return s
central=read('CentralCarrier');full=read('FinishedCarrier');right=full.cut(Part.makeBox(150,100,150,A.Vector(-60,0,-60)))
print('vol',central.Volume,full.Volume,right.Volume,flush=True)
for tol in [0,1e-5,.0001]:
 new=right.fuse(central,tol).removeSplitter();print('FUSE',tol,new.Volume,new.isValid(),len(new.Solids),flush=True);new.exportBrep(str(O/('restored-'+str(tol)+'.brep')))
tray=read('source-holder-head');tray=tray.cut(Part.makeBox(100,100,30,A.Vector(-50,-50,-31.24998))).removeSplitter();print('TRAY',tray.Volume,tray.isValid(),len(tray.Solids),tray.BoundBox,flush=True);tray.exportBrep(str(O/'stemless-tray-head.brep'))
