"""Shared FreeCAD helpers for UltraSkelly builders: run folders, verified saves and STL export."""
import hashlib
import json
import zipfile
from pathlib import Path

import FreeCAD as App

ROOT = Path(__file__).resolve().parents[3]
GENERATED = ROOT / 'generated' / 'ultraskelly'


def run_folder(part, run):
    """Return a new working folder generated/ultraskelly/<part>/<run>/; never reuse a used one."""
    folder = GENERATED / part / run
    if folder.exists() and any(folder.iterdir()):
        raise FileExistsError(f'{folder} already contains files; choose a new run name')
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_verified(doc, path):
    """Save a native document, then check it is an intact ZIP that contains Document.xml."""
    doc.saveAs(str(path))
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None or 'Document.xml' not in archive.namelist():
            raise RuntimeError(f'{path} failed the FCStd integrity check')
    if App.GuiUp and not doc.isTouched():
        import FreeCADGui as Gui
        Gui.getDocument(doc.Name).Modified = False  # a Python save leaves the window's flag set in FreeCAD 1.1.4
    return sha256(path)


def export_stl(shape, path, linear_deflection=0.01, angular_deflection=0.1):
    """Tessellate one solid in mm and write a binary STL; reject open or non-manifold meshes."""
    import MeshPart
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=linear_deflection,
                                  AngularDeflection=angular_deflection, Relative=False)
    if mesh.CountFacets == 0 or not mesh.isSolid() or mesh.hasNonManifolds():
        raise RuntimeError(f'{path}: tessellation is not a closed manifold solid')
    mesh.write(str(path))
    return {'sha256': sha256(path), 'facets': mesh.CountFacets,
            'linear_deflection_mm': linear_deflection, 'angular_deflection_rad': angular_deflection}


def write_report(path, report):
    report = {'freecad': App.Version()[:4], **report}
    Path(path).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


def add(doc, name, shape, color=None, transparency=0, label=None, line_width=None):
    """Add a shape as a Part::Feature; style it when the GUI is up."""
    obj = doc.addObject('Part::Feature', name)
    obj.Shape = shape
    obj.Label = label or name
    if App.GuiUp and color is not None:
        view = obj.ViewObject
        view.ShapeColor = view.LineColor = view.PointColor = tuple(color)
        view.Transparency = transparency
        if line_width:
            view.LineWidth = line_width
    return obj


def close_saved_runs(folder):
    """Close earlier runs saved under a working folder, so each review has one open run.

    These documents are builder-owned; any later change (view styling marks them modified)
    is saved to their own run file before closing, so nothing is discarded.
    """
    folder = Path(folder).resolve()
    for doc in list(App.listDocuments().values()):
        if doc.FileName and folder in Path(doc.FileName).resolve().parents:
            if App.GuiUp:
                import FreeCADGui as Gui
                if Gui.getDocument(doc.Name).Modified:
                    save_verified(doc, doc.FileName)
            App.closeDocument(doc.Name)


def present(doc, view='isometric'):
    """Show a document in the live window: Blender navigation, chosen view, fit all."""
    if not App.GuiUp:
        return
    import FreeCADGui as Gui
    App.setActiveDocument(doc.Name)
    Gui.ActiveDocument = Gui.getDocument(doc.Name)
    active = Gui.ActiveDocument.ActiveView
    active.setNavigationType('Gui::BlenderNavigationStyle')
    getattr(active, 'view' + view.capitalize())()
    active.fitAll()
