"""Export the checked R06 boards and prepare a macro for the existing FreeCAD GUI.

Run with ordinary Python from any directory. This does not launch or close CAD.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parent
CLI='C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,default=ROOT/'electronics/r06')
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--revision',choices=['R06','R07','R08','R09'],default='R06');a=ap.parse_args()
    source=a.directory.resolve();out=a.output.resolve()
    if out.exists():raise SystemExit('Choose a new review directory to preserve prior exports.')
    record=json.loads((source/'validation.json').read_text())
    for name,digest in record['sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest,name
    out.mkdir(parents=True)
    for name in ['controller','head','flex-study']:
        subprocess.run([CLI,'pcb','export','step','--no-components','--include-tracks','--include-pads','--include-zones',
                        '--include-inner-copper','--cut-vias-in-body','--output',str(out/(name+'.step')),str(source/(name+'.kicad_pcb'))],check=True)
    template=(ROOT/'review_r06.FCMacro.in').read_text().replace('R06',a.revision)
    if a.revision!='R06':template=template.replace('power copper and ground planes','additional board connections')
    (out/'open-review.FCMacro').write_text(template.replace('__REVIEW_DIRECTORY__',out.as_posix()))
    (out/'source-record.json').write_text(json.dumps({'native_directory':str(source),'native_sha256':record['sha256'],
        'limits':'PCB substrates and copper only. No component bodies or optics. Review transforms do not establish mating heights.'},indent=2)+'\n')
    print(out/'open-review.FCMacro')

if __name__=='__main__':main()
