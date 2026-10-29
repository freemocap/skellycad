from pathlib import Path
import sys,json,hashlib,shutil,zipfile
import FreeCAD as App
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'designs/eye-camera-ov9281'));from verify_r11_native import measurements
out=root/'generated/ov9281-r11-mechanics';native=out/'OV9281-R11-MATCHED.FCStd';diagnostic=out/'render-diagnostic.FCStd'
a=App.openDocument(str(native));expected=measurements(a);App.closeDocument(a.Name)
b=App.openDocument(str(diagnostic));actual=measurements(b);App.closeDocument(b.Name)
assert actual==expected,'Exact geometry changed';backup=out/'before-verified-render.FCStd';assert not backup.exists();shutil.copy2(native,backup);shutil.copy2(diagnostic,native)
with zipfile.ZipFile(native) as z:assert z.testzip() is None
(out/'geometry-measurements.json').write_text(json.dumps(actual,indent=2)+'\n');sha=hashlib.sha256(native.read_bytes()).hexdigest()
p=out/'validation.json';r=json.loads(p.read_text());r.update(native_sha256=sha,rendered_geometry_measurements_unchanged=True,geometry_measurements_count=len(actual));p.write_text(json.dumps(r,indent=2)+'\n')
r={'pid':23304,'native_sha256':sha,'geometry_measurements_unchanged':True,'exact_bounds_without_triangulation':True,'images':['flat-top.png','flat-bottom.png','flat-iso.png','bent-iso.png','pupil-comparison.png'],'native_saved_and_closed':True,'computer_use':False,'note':'Native render saved separately on conservative check failure; exact analytic bounds verified identical before promotion. The initial check used viewport triangulation bounds.'}
(out/'render-validation.json').write_text(json.dumps(r,indent=2)+'\n');print('Verified and saved',len(actual),'feature measurements',flush=True)
