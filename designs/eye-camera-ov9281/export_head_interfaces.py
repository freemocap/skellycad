"""Extract native head courtyard reservations for mechanical screening, in mm."""
from pathlib import Path
import argparse, hashlib, json
import pcbnew as p

ap=argparse.ArgumentParser()
ap.add_argument('--board',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args(); path=a.board.resolve(); b=p.LoadBoard(str(path)); records=[]
for f in b.GetFootprints():
    if f.GetLayer()!=p.F_Cu: continue
    points=[]
    for item in f.GraphicalItems():
        if isinstance(item,p.PCB_SHAPE) and item.GetLayer()==p.F_CrtYd:
            points.extend([item.GetStart(),item.GetEnd()])
    if not points: continue
    xs=[p.ToMM(q.x) for q in points]; ys=[-p.ToMM(q.y) for q in points]
    records.append({'reference':f.GetReference(),'value':f.GetValue(),
                    'bounds_xy_mm':[min(xs),min(ys),max(xs),max(ys)]})
u=next(f for f in b.GetFootprints() if f.GetReference()=='U1')
assert u.GetOrientationDegrees()==0,'This extraction assumes the checked R09 sensor orientation'
result={'source_board':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'frame':'FreeCAD board frame: native KiCad X, negated Y, mm',
        'optical_xy_mm':[p.ToMM(u.GetPosition().x),-p.ToMM(u.GetPosition().y)],
        'front_courtyard_rectangles':records,
        'limit':'Conservative XY reservations, not measured component bodies or qualified heights'}
assert not a.output.exists(),'Preserve prior interface extraction'
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(a.output)
