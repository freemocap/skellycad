"""Inspect a hash-verified model; export only explicitly recorded matched groups.

Run with the pinned FreeCAD Python. This uses an isolated hidden GUI and closes
its own documents. It never controls an existing desktop session.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'designs/eye-tracker'))
from shared.model import load_manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--export',type=Path)
    args=parser.parse_args()
    report=args.report.resolve()
    if not report.is_relative_to(ROOT/'generated'):
        raise ValueError('Reports must be below generated/')
    manifest,native=load_manifest(args.manifest)
    before=hashlib.sha256(native.read_bytes()).hexdigest()
    with zipfile.ZipFile(native) as z:
        assert z.testzip() is None and 'Document.xml' in z.namelist()
    import FreeCAD as App
    import FreeCADGui as Gui
    from PySide import QtWidgets
    Gui.showMainWindow();Gui.getMainWindow().hide()
    app=QtWidgets.QApplication.instance();app.setQuitOnLastWindowClosed(False)
    doc=App.openDocument(str(native))
    try:
        roles=manifest.get('parts',{})
        matched={}
        for role,name in roles.items():
            if not isinstance(name,str):continue  # Camera asset records are checked by camera.selected_model.
            obj=doc.getObject(name)
            assert obj is not None and hasattr(obj,'Shape'),name
            assert obj.Shape.isValid() and len(obj.Shape.Solids)>0,name
            matched[role]={'object':name,'solids':len(obj.Shape.Solids),'volume_mm3':obj.Shape.Volume}
        result={'passed':True,'revision':manifest['revision'],'native_sha256':before,
            'objects':len(doc.Objects),'matched_parts':matched,'zip_integrity':True,
            'physical_fit_demonstrated':False,'exports':{}}
        if args.export:
            target=args.export.resolve()
            if not target.is_relative_to(ROOT/'generated'):raise ValueError('Export below generated/')
            if target.exists():raise ValueError('Use a fresh export directory')
            groups=manifest.get('print_groups')
            if not groups:raise ValueError('No explicit matched print groups; use the design-specific exporter')
            import Part,MeshPart
            target.mkdir(parents=True)
            for label,group in groups.items():
                if Path(label).name!=label:raise ValueError('Invalid print group name')
                shapes=[]
                for role in group:
                    obj=doc.getObject(roles[role]);shape=obj.Shape.copy()
                    shape.Placement=obj.getGlobalPlacement();shapes.append(shape)
                shape=Part.makeCompound(shapes) if len(shapes)>1 else shapes[0]
                mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.03,AngularDeflection=.15,Relative=False)
                path=target/(label+'.stl');mesh.write(str(path))
                result['exports'][path.name]={'expected_shells':len(shapes),'source_roles':group}
            (target/'export.json').write_text(json.dumps(result,indent=2))
        assert hashlib.sha256(native.read_bytes()).hexdigest()==before
        report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2))
        print(json.dumps(result),flush=True)
    finally:
        App.closeDocument(doc.Name)


if __name__=='__main__':
    from process_lifecycle import finish_isolated
    code=0
    try:main()
    except Exception:
        import traceback
        traceback.print_exc();code=1
    finish_isolated(code)

