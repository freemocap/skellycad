"""Build an isolated mount candidate without overwriting baseline part files."""
from pathlib import Path
import json
import runpy
import sys
import FreeCAD as App

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
RECON = HERE.parent/'reconstruction'
OUT = ROOT/'generated/mouse-hats/model/mount'


def load_modules():
    for folder in (HERE, RECON/'baseplate', RECON/'main_carrier'):
        if str(folder) not in sys.path:
            sys.path.insert(0, str(folder))
    import mount_features
    import carrier_features


def main(save=True):
    load_modules()
    from mount_interface import stem_profiles
    from mount_features import MountPocket
    interface = json.loads((HERE/'mount-interface.json').read_text())
    measured = json.loads((RECON/'main_carrier/profiles.json').read_text())
    builder = runpy.run_path(str(RECON/'main_carrier/build.py'))
    doc = builder['main'](save=False, profiles_data=stem_profiles(measured, interface))
    doc.Label = 'Mount fit candidate — shared bearing planes'
    base = doc.addObject('Part::FeaturePython', 'Baseplate')
    base.Label = 'Baseplate — adjustable pocket clearance'
    MountPocket(base, json.loads((RECON/'baseplate/parameters.json').read_text()), interface)
    doc.recompute()
    base.Shape.check(True)
    OUT.mkdir(parents=True, exist_ok=True)
    if save:
        doc.saveAs(str(OUT/'mount-fit.FCStd'))
    return doc


if __name__ == '__main__': main()
