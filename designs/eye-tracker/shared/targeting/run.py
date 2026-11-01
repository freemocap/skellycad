"""Rebuild a target-driven complete assembly from an explicit species recipe."""
import argparse
from pathlib import Path
import sys
import zipfile
import FreeCAD as App
from prepare import prepare
from solve import solve
from build import build
from finish import finish
from assemble import assemble
from validate import validate

ROOT=Path(__file__).resolve().parents[4]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipe',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(ROOT/'generated') or out.exists():
        raise ValueError('Use a new output directory below generated/')
    try:
        for stage in [prepare,solve]:
            print(stage.__name__,flush=True);stage(args.recipe,out)
        print('build',flush=True);build(out)
        for stage in [finish,assemble,validate]:
            print(stage.__name__,flush=True);stage(args.recipe,out)
    finally:
        for name in list(App.listDocuments()):
            doc=App.getDocument(name)
            path=Path(doc.FileName).resolve() if doc.FileName else None
            if path and path.is_relative_to(out):
                doc.save()
            else:
                recovery=out/'session-saves';recovery.mkdir(parents=True,exist_ok=True)
                doc.saveAs(str(recovery/(name+'.FCStd')))
            with zipfile.ZipFile(doc.FileName) as archive:
                assert archive.testzip() is None and 'Document.xml' in archive.namelist()
            App.closeDocument(name)


if __name__=='__main__':
    sys.path.insert(0,str(ROOT/'tools/cad'))
    from process_lifecycle import finish_isolated
    code=0
    try:main()
    except Exception:
        import traceback
        traceback.print_exc();code=1
    finish_isolated(code)
