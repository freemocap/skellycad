"""Run with pinned FreeCAD Python in a separate process; never alter input geometry."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import argparse
import FreeCAD as App
import Part

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = next(p for p in PROJECT.parents if (p/'tools/cad/toolchain.json').is_file())
OUT = WORKSPACE/'generated/mouse-hats/inspection'


def bounds(shape):
    b = shape.BoundBox
    return dict(min=[b.XMin,b.YMin,b.ZMin], max=[b.XMax,b.YMax,b.ZMax],
                extents=[b.XLength,b.YLength,b.ZLength])


def describe(shape):
    return dict(valid=shape.isValid(), solids=len(shape.Solids), faces=len(shape.Faces),
                volume_mm3=shape.Volume, area_mm2=shape.Area, bounds_mm=bounds(shape),
                surfaces=dict(Counter(type(f.Surface).__name__ for f in shape.Faces)))


def main(generations=(52,53)):
    OUT.mkdir(parents=True, exist_ok=True)
    results=[]
    for number in generations:
        path=PROJECT/f'old/df-hardware/camera-assembly/cad/{number}nassembly/{number}nassembly.step'
        print('Reading',path.name,flush=True)
        shape=Part.read(str(path))
        report=dict(source=path.relative_to(PROJECT).as_posix(),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    freecad_version=App.Version(),units='mm from STEP import',
                    summary=describe(shape), components=[])
        for index,solid in enumerate(shape.Solids,1):
            component=describe(solid)
            component['id']=f'{number}-solid-{index:02d}'
            target=OUT/f'{component["id"]}.brep'
            solid.exportBrep(str(target))
            component['inspection_brep']=target.relative_to(WORKSPACE).as_posix()
            report['components'].append(component)
        (OUT/f'assembly-{number}.json').write_text(json.dumps(report,indent=2)+'\n')
        results.append(report)
        print(number,report['summary'],flush=True)
    (OUT/'step-comparison.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generations',nargs='+',type=int,choices=(50,52,53),default=[52,53])
    main(parser.parse_args().generations)
