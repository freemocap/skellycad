"""Prepare inspection solids from a source-hash-verified saved STEP reference.

This is a cached import, not an independent fresh STEP validation.
Only the STEP object's BREP is read from the supplied archive.
"""
from pathlib import Path
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET
import FreeCAD
import Part

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = next(p for p in PROJECT.parents if (p/'tools/cad/toolchain.json').is_file())
OUT = WORKSPACE/'generated/mouse-hats/inspection/cached-53'


def main():
    source = PROJECT/'old/df-hardware/camera-assembly/cad/53nassembly/53nassembly.step'
    archive = PROJECT/'old/df-hardware/rebuild/generated/reference-study.FCStd'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        root = ET.fromstring(z.read('Document.xml'))
        obj = root.find("./ObjectData/Object[@name='Assembly53Reference']")
        recorded = obj.find("./Properties/Property[@name='SourceSHA256']/String").get('value')
        assert recorded == digest, 'Cached reference source does not match STEP.'
        brep = OUT/'source.brep'
        brep.write_bytes(z.read('Assembly53Reference.Shape.brp'))
    shape = Part.read(str(brep))
    assert len(shape.Solids) == 3
    report = dict(source=source.relative_to(PROJECT).as_posix(), sha256=digest,
                  provenance='Cached STEP import; source hash verified against saved metadata',
                  cache_archive=archive.relative_to(PROJECT).as_posix(), components=[])
    for i, solid in enumerate(shape.Solids, 1):
        target = OUT/f'53-solid-{i:02d}.brep'
        solid.exportBrep(str(target))
        report['components'].append(dict(faces=len(solid.Faces),
            inspection_brep=target.relative_to(WORKSPACE).as_posix()))
    (OUT/'assembly-53.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report, flush=True)


if __name__ == '__main__':
    main()
