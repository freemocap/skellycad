"""Link editable retained parts in their measured 58 STEP assembly frames."""
from pathlib import Path
import json
import sys
import FreeCAD as App

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT = ROOT/'generated/mouse-hats/reconstruction/assembly'
FILE = OUT/'02-linked-assembly.FCStd'


def load_modules():
    for folder in ('baseplate', 'main_carrier'):
        sys.path.insert(0, str(HERE.parent/folder))
    import baseplate_features
    import carrier_features


def placement(data):
    return App.Placement(App.Vector(*data['translation_mm']),
                         App.Rotation(*data['quaternion_xyzw']))


def main():
    load_modules()
    manifest = json.loads((HERE/'parts.json').read_text())
    doc = App.newDocument('MouseHatsLinkedAssembly58')
    doc.Label = '58 rebuilt assembly — old arm omitted'
    OUT.mkdir(parents=True, exist_ok=True)
    # Cross-document links require the owner to have a file location first.
    doc.saveAs(str(FILE))
    groups = {}
    for name in ('MountAndElectronics', 'CameraHead'):
        groups[name] = doc.addObject('App::DocumentObjectGroup', name)
    for entry in manifest['parts']:
        path = (ROOT/entry['file']).resolve()
        source_doc = next((d for d in App.listDocuments().values()
                           if d.FileName and Path(d.FileName).resolve() == path), None)
        if source_doc is None:
            source_doc = App.openDocument(str(path))
        source = source_doc.getObject(entry['object'])
        if source is None:
            raise ValueError(f"Missing final feature: {entry}")
        if entry['name'] == 'Baseplate' and str(source.DisplayStage) != 'Finished':
            raise ValueError('Baseplate must be in Finished stage')
        link = doc.addObject('App::Link', entry['name'])
        link.setLink(source)
        link.LinkTransform = True
        link.LinkPlacement = placement(entry['local_to_assembly'])
        groups[entry['group']].addObject(link)
        link.Label = entry['label']
        link.addProperty('App::PropertyString', 'FrameSource', 'Provenance')
        link.FrameSource = entry['frame_source']
        if App.GuiUp:
            link.Visibility = True
    doc.recompute()
    OUT.mkdir(parents=True, exist_ok=True)
    if App.GuiUp:
        import FreeCADGui as Gui
        App.setActiveDocument(doc.Name)
        Gui.activeDocument().activeView().viewIsometric()
        Gui.activeDocument().activeView().fitAll()
    doc.saveAs(str(FILE))
    return doc


if __name__ == '__main__':
    main()
