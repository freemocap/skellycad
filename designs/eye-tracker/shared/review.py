"""One code-based entry point for opening a verified selected or review model."""
from pathlib import Path
from .model import load_manifest


def open_review(manifest_path):
    import FreeCAD as App
    import FreeCADGui as Gui
    record, path = load_manifest(manifest_path)
    doc = next((d for d in App.listDocuments().values()
                if d.FileName and Path(d.FileName).resolve() == path), None)
    if doc is None:
        doc = App.openDocument(str(path))
    App.setActiveDocument(doc.Name)
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    return record, doc
