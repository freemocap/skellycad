"""Validate preserved courses, R10 reconstruction and the selected mouse separately."""
from pathlib import Path
import hashlib,json,os,runpy,sys,traceback,zipfile
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore,QtWidgets
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'generated/verification';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'designs/eye-tracker'))
from shared.assembly import build_assembly
from shared.validation import compare_mouse_baseline,validate_selected
from shared.model import load_manifest,open_selected,export_selected
os.environ['CAD_PLAYGROUND_ROOT']=str(ROOT)
Gui.showMainWindow();Gui.getMainWindow().hide()
app=QtWidgets.QApplication.instance();app.setQuitOnLastWindowClosed(False)
sys.stdout=sys.__stdout__;sys.stderr=sys.__stderr__
exit_code=1

def verify():
    global exit_code
    report={'passed':False,'course':[]}
    try:
        course=runpy.run_path(str(ROOT/'designs/cad-foundations/replay.py'))
        for lesson in course['STAGES']:
            doc=course['main'](lesson)
            with zipfile.ZipFile(doc.FileName) as z:
                assert z.testzip() is None and 'Document.xml' in z.namelist()
            report['course'].append({'lesson':lesson,'file':Path(doc.FileName).relative_to(ROOT).as_posix()})
            App.closeDocument(doc.Name)
        rebuilt=build_assembly(ROOT/'designs/eye-tracker/mouse/assembly.json',OUT/'mouse-r10-rebuild')
        report['r10_reconstruction']=compare_mouse_baseline(rebuilt)
        App.closeDocument(rebuilt.document.Name)
        selected=ROOT/'designs/eye-tracker/mouse/active-model.json'
        manifest,checkpoint=load_manifest(selected)
        before=hashlib.sha256(checkpoint.read_bytes()).hexdigest()
        # The selected R19 is a different design from the historical R10 reconstruction.
        # Check its exact matched parts and export its own explicit groups.
        manifest,doc=open_selected(selected)
        report['selected_revision']=manifest['revision']
        report['selected_parts']={role:{'object':name,'valid':doc.getObject(name).Shape.isValid()} for role,name in manifest['parts'].items()}
        export_manifest=dict(manifest);export_manifest['print_directory']='generated/verification/mouse-selected'
        export_path=OUT/'mouse-export-selection.json';export_path.write_text(json.dumps(export_manifest,indent=2))
        export_selected(export_path,lambda current: validate_selected(current,manifest))
        assert hashlib.sha256(checkpoint.read_bytes()).hexdigest()==before
        report['selected_checkpoint_unchanged']=True
        report['passed']=True;exit_code=0
    except Exception:
        report['error']=traceback.format_exc();print(report['error'],flush=True)
    finally:
        (OUT/'cad.json').write_text(json.dumps(report,indent=2))
        for name in list(App.listDocuments()):
            print('CLOSING',name,flush=True)
            App.closeDocument(name)
            print('CLOSED',name,flush=True)
        print('CAD_WORKSPACE_OK' if report['passed'] else 'CAD_WORKSPACE_FAILED',flush=True)
        from process_lifecycle import finish_isolated
        finish_isolated(exit_code)
QtCore.QTimer.singleShot(0,verify);app.exec();sys.exit(exit_code)
