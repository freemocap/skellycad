"""Isolated runner: relocate executable path literals in memory, never evidence files."""
from pathlib import Path
import importlib.abc
import importlib.machinery
import os
import re
import runpy
import sys

original=Path(sys.argv[1]).resolve()
runtime=sys.argv[2]
target=Path(sys.argv[3]).resolve()
workspace=Path.cwd().resolve()
sys.argv=sys.argv[3:]
sys.path.insert(0,str(target.parent))


def transform(raw):
    text=raw.decode('utf-8-sig')
    replacements={}
    for source in [Path(os.environ.get('SKELLY_REPLAY_ORIGINAL_ROOT',str(original))),original]:
        replacements[str(source).replace('\\','\\\\')]=str(workspace).replace('\\','\\\\')
        replacements[source.as_posix()]=workspace.as_posix()
        replacements[str(source)]=str(workspace)
    pattern='|'.join(re.escape(k) for k in sorted(replacements,key=len,reverse=True))
    text=re.sub(pattern,lambda m:replacements[m[0]],text)
    return re.sub(r'''(['"])(\.cad-tools[^'"]*|tools/cad/\.venv[^'"]*|tools/electronics/\.venv[^'"]*)\1''',
                  lambda m:repr((original/m[2]).as_posix()),text)


class ReplayLoader(importlib.machinery.SourceFileLoader):
    def get_code(self,fullname):
        return compile(transform(Path(self.path).read_bytes()),self.path,'exec')


class ReplayFinder(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        spec=importlib.machinery.PathFinder.find_spec(fullname,path)
        if spec and spec.origin and spec.origin.endswith('.py'):
            source=Path(spec.origin).resolve()
            if source.is_relative_to(workspace):
                spec.loader=ReplayLoader(fullname,str(source))
        return spec


sys.meta_path.insert(0,ReplayFinder())
original_get_code=runpy._get_code_from_file


def relocated_code(*args,**kwargs):
    name=args[-1] if args else kwargs['fname']
    path=Path(name).resolve()
    if path.is_relative_to(workspace) and path.suffix in ['.py','.FCMacro']:
        code=compile(transform(path.read_bytes()),str(path),'exec')
        return (code,str(path)) if len(args)>1 else code
    return original_get_code(*args,**kwargs)


runpy._get_code_from_file=relocated_code
if runtime=='freecad':
    sys.path.insert(0,str(original/'tools/cad'))
    from process_lifecycle import finish_isolated
    import FreeCAD as App
    import FreeCADGui as Gui
    from PySide import QtWidgets
    Gui.showMainWindow();Gui.getMainWindow().hide()
    QtWidgets.QApplication.instance().setQuitOnLastWindowClosed(False)
    sys.stdout=sys.__stdout__;sys.stderr=sys.__stderr__
    def save_close_documents():
        import zipfile
        out=workspace/'generated/replay-saves'/target.stem
        out.mkdir(parents=True,exist_ok=True)
        saved_files=[]
        for name in list(App.listDocuments()):
            doc=App.getDocument(name);saved=out/(name+'.FCStd')
            doc.recompute();doc.saveAs(str(saved))
            with zipfile.ZipFile(saved) as archive:
                assert archive.testzip() is None and 'Document.xml' in archive.namelist()
            App.closeDocument(name)
            saved_files.append(str(saved.relative_to(workspace)))
        import json
        (out/'session-finalization.json').write_text(json.dumps({'saved':saved_files,'remaining_documents':len(App.listDocuments())},indent=2))
    def request_exit(code):
        # A legacy hard exit must save and close task-owned documents first.
        # Do this before stopping Qt to avoid unsaved-document dialogs.
        save_close_documents()
        finish_isolated(code)
    os._exit=request_exit

code=0
try:
    globals_for_script={'App':App,'Gui':Gui,'FreeCAD':App,'FreeCADGui':Gui} if runtime=='freecad' else None
    runpy.run_path(str(target),run_name='__main__',init_globals=globals_for_script)
except SystemExit as error:
    code=error.code if isinstance(error.code,int) else (0 if error.code is None else 1)
except BaseException:
    import traceback
    traceback.print_exc();code=1
finally:
    if runtime=='freecad':save_close_documents()
    sys.stdout.flush();sys.stderr.flush()
if runtime=='freecad':finish_isolated(code)
sys.exit(code)
