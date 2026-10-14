"""Rebuild the registered reference in generated/ using FreeCAD Python."""
from pathlib import Path
import json
import sys
import FreeCAD as App
import Mesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
from shared.assembly import _asset


def prepare_reference():
    provenance = json.loads((HERE / 'references/skull/provenance.json').read_text())
    source = _asset(provenance['selected_mesh'])
    registration = provenance['registration']
    doc = App.newDocument('RatAnatomyReference')
    doc.Label = 'Rat skull and mandible — provisional registration R01'
    doc.CreatedBy = 'scienceminer (source scan); SkellyCAD (rigid registration)'
    doc.License = provenance['license_as_supplied']
    doc.LicenseURL = provenance['source_url']
    doc.Comment = 'Unmodified source mesh with rigid placement only; original README and LICENSE retained beside this reference.'
    obj = doc.addObject('Mesh::Feature', 'RatSkullAndMandible')
    obj.Label = 'Rat skull + mandible — scienceminer; scale unverified'
    obj.Mesh = Mesh.Mesh(str(source))
    obj.Placement = App.Placement(App.Vector(*registration['translation_mm']),
                                  App.Rotation(App.Vector(1, 0, 0), registration['rotation_degrees']))
    obj.ViewObject.ShapeColor = (.88, .86, .73)
    obj.addProperty('App::PropertyString', 'SourceAttribution').SourceAttribution = 'scienceminer — Thingiverse 469391 — CC BY-SA (version unspecified)'
    obj.addProperty('App::PropertyString', 'UnitsStatus').UnitsStatus = provenance['units']
    doc.recompute()
    out = ROOT / 'generated/eye-tracker/rat/reference'
    out.mkdir(parents=True, exist_ok=True)
    doc.saveAs(str(out / 'anatomy-r01.FCStd'))
    return doc


if __name__ == '__main__':
    prepare_reference()
