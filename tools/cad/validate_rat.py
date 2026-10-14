"""Build and validate Monocular rat in an isolated hidden FreeCAD GUI."""
from pathlib import Path
import hashlib
import json
import sys
import traceback
import zipfile
import xml.etree.ElementTree as ET
import FreeCAD as App
import FreeCADGui as Gui
import Mesh
from PySide import QtCore, QtWidgets

ROOT = Path(__file__).resolve().parents[2]
EYE = ROOT / 'designs/eye-tracker'
sys.path.insert(0, str(EYE))
from shared.assembly import build_assembly, _asset
from shared.model import open_selected
from shared.validation import validate_selected

OUT = ROOT / 'generated/eye-tracker/rat/monocular-r01'
OUT.mkdir(parents=True, exist_ok=True)
Gui.showMainWindow()
Gui.getMainWindow().hide()
app = QtWidgets.QApplication.instance()
app.setQuitOnLastWindowClosed(False)
exit_code = 1


def verify():
    global exit_code
    report = {'passed': False, 'physical_fit_verified': False}
    try:
        provenance = json.loads((EYE / 'rat/references/skull/provenance.json').read_text())
        for record in provenance['unmodified_files']:
            _asset(record)
        rat = build_assembly(EYE / 'rat/assembly.json', OUT)
        doc = rat.document
        validate_selected(doc, rat.manifest)
        mouse_manifest, mouse = open_selected(EYE / 'mouse/active-model.json')
        report['mouse_reference_sha256'] = mouse_manifest['native_sha256']
        report['parts'] = {}
        assert len(rat.manifest['camera_instances']) == 1
        for role, name in rat.manifest['parts'].items():
            a = doc.getObject(name).Shape
            b = mouse.getObject(mouse_manifest['parts'][role]).Shape
            delta = a.cut(b).Volume + b.cut(a).Volume
            assert a.isValid() and len(a.Solids) == 1 and delta < 1e-6, role
            report['parts'][role] = {'valid_single_solid': True, 'difference_from_mouse_mm3': delta}
        assert doc.getObject('Skull') is None and doc.getObject('Eye1') is None and doc.getObject('Eye2') is None
        skull = doc.RatSkullAndMandible
        expected = Mesh.Mesh(str(_asset(provenance['selected_mesh'])))
        actual = skull.Mesh.copy()
        actual.transform(skull.Placement.inverse().toMatrix())
        # FreeCAD meshes include object placement in their exposed point coordinates.
        assert len(actual.Topology[0]) == len(expected.Topology[0])
        assert actual.Topology[1] == expected.Topology[1]
        deviation = max((a-b).Length for a,b in zip(actual.Topology[0], expected.Topology[0]))
        assert deviation < 1e-4, deviation
        report['anatomy'] = {'source_facets': expected.CountFacets, 'assembly_facets': skull.Mesh.CountFacets,
                             'unscaled_source_deviation_mm': deviation, 'mouse_anatomy_absent': True,
                             'units': provenance['units'], 'registration': provenance['registration']}
        station = rat.manifest['camera_instances'][0]
        lens = doc.getObject(station['objects']['LensDatum']).Shape.CenterOfMass
        guide = doc.getObject(station['objects']['OpticalAxis']).Shape
        target = doc.EyeTarget.Shape.CenterOfMass
        direction = guide.Vertexes[-1].Point - guide.Vertexes[0].Point
        direction.normalize()
        offset = target-lens
        report['provisional_aim'] = {'lens_mm': list(lens), 'target_mm': list(target),
            'target_distance_mm': offset.Length, 'distance_from_sightline_mm': offset.cross(direction).Length,
            'status': 'Diagnostic only: target estimated visually; arms and internal aim unchanged'}
        # Reopen the generated native file to verify the saved complete assembly.
        saved = Path(doc.FileName)
        App.closeDocument(doc.Name)
        reopened = App.openDocument(str(saved))
        validate_selected(reopened, rat.manifest)
        assert reopened.RatSkullAndMandible.Mesh.CountFacets == expected.CountFacets
        # FreeCAD may display the filename on open even when XML preserves Label.
        with zipfile.ZipFile(saved) as archive:
            xml = ET.fromstring(archive.read('Document.xml'))
            assert xml.find("./Properties/Property[@name='Label']/String").attrib['value'] == 'Monocular rat'
        reopened.Label = rat.manifest['label']
        App.setActiveDocument(reopened.Name)
        Gui.activeDocument().activeView().viewAxonometric()
        Gui.activeDocument().activeView().fitAll()
        Gui.activeDocument().activeView().saveImage(str(OUT / 'monocular-rat.png'), 1400, 1100, 'White')
        report.update(passed=True, saved_native_reopened=True, supplied_assets_unchanged=True,
                      native_sha256=hashlib.sha256(saved.read_bytes()).hexdigest())
        exit_code = 0
    except Exception:
        report['error'] = traceback.format_exc()
        print(report['error'], flush=True)
    finally:
        (OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
        for name in list(App.listDocuments()):
            App.closeDocument(name)
        print('MONOCULAR_RAT_OK' if report['passed'] else 'MONOCULAR_RAT_FAILED', flush=True)
        app.quit()


QtCore.QTimer.singleShot(0, verify)
app.exec()
sys.exit(exit_code)
