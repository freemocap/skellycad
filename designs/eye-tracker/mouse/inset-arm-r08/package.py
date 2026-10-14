from pathlib import Path
import json,hashlib,shutil,zipfile
r=Path.cwd();out=r/'generated/eye-tracker/mouse/inset-arm-r08';src=r/'designs/eye-tracker/mouse/inset-arm-r08';native=out/'mouse-inset-arm-r08.FCStd'
p=json.loads((r/'designs/eye-tracker/mouse/joined-arms-r06/print-test.json').read_text());v=json.loads((out/'validation.json').read_text());v['native_sha256']=hashlib.sha256(native.read_bytes()).hexdigest();v['ribbon_validation']=json.loads((out/'ribbon-validation.json').read_text());assert v['ribbon_validation']['ribbon_checks_pass'];v['upper_arm_change']={'source':'R06 complete assembly','axial_shift_mm':-1.1,'terminal_width_mm':3.0,'terminal_thickness_mm':2.2,'terminal_center_height_mm':4.2,'taper_cut':False};v['source_checkpoint']=p['native_checkpoint'];v['source_sha256']=p['native_sha256']
(out/'validation.json').write_text(json.dumps(v,indent=2));(out/'print/manifest.json').write_text(json.dumps(v,indent=2))
(src/'checkpoints').mkdir(exist_ok=True);dest=src/'checkpoints/ET-MOUSE-MONO-STEM-R08.FCStd';shutil.copy2(native,dest)
p.update(revision='ET-MOUSE-MONO-STEM-R08',native_checkpoint=dest.relative_to(r).as_posix(),native_sha256=v['native_sha256'],validation=v)
(src/'print-test.json').write_text(json.dumps(p,indent=2))
(out/'print/README.txt').write_text('Mouse R08 print-test candidate. Units: mm. Full-thickness upper arm moved inward 1.1 mm; ribbon re-solved. Replaces rejected R07.\nUse carrier-and-holder.stl with matching-cap.stl, camera-clip.stl and baseplate.stl from this package. Preserve the carrier/holder relative placement. Physical fit and strength require a print test.\n')
with zipfile.ZipFile(out/'mouse-R08-print-test.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted((out/'print').iterdir()):z.write(f,f.name)
print(v['native_sha256'])
