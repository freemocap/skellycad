"""Inventory saved part controls and file hashes without saving any CAD document."""
import hashlib
import json
from pathlib import Path
import runpy
import FreeCAD as App

HERE = Path(__file__).resolve().parent
api = runpy.run_path(str(HERE/'build.py'))
api['load_modules']()
ROOT = api['ROOT']


def main():
    manifest = json.loads((HERE/'parts.json').read_text())
    report = {'units': 'mm', 'scope': 'Saved files, not unsaved GUI state', 'parts': {}}
    for entry in manifest['parts']:
        path = ROOT/entry['file']
        doc = App.openDocument(str(path))
        final = doc.getObject(entry['object'])
        controls = []
        # These are the user-facing control owners in this reconstruction.
        owner = doc.getObject('Dimensions') or final
        for name in owner.PropertiesList:
            if owner.getTypeIdOfProperty(name) != 'App::PropertyLength':
                continue
            controls.append({'object': owner.Name, 'property': name,
                             'value_mm': getattr(owner, name).Value,
                             'supported_range': 'Not established; individual edit probes only'})
        report['parts'][entry['name']] = {
            'file': entry['file'], 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'final_object': final.Name, 'volume_mm3': final.Shape.Volume,
            'face_count': len(final.Shape.Faces), 'live_length_controls': controls}
        App.closeDocument(doc.Name)
    out = api['OUT']/'control-inventory.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    main()
