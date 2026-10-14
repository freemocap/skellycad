from pathlib import Path
import json,hashlib,shutil,zipfile
r=Path.cwd();out=r/'generated/eye-tracker/mouse/seated-tip-r07';src=r/'designs/eye-tracker/mouse/seated-tip-r07';native=out/'mouse-seated-tip-r07.FCStd'
p=json.loads((r/'designs/eye-tracker/mouse/joined-arms-r06/print-test.json').read_text());v=json.loads((out/'validation.json').read_text());v['native_sha256']=hashlib.sha256(native.read_bytes()).hexdigest();v['tip_correction']=json.loads((out/'tip-correction.json').read_text());v['junction_finishing_note']='Inherited R06 fillets and chamfer; upper terminal top locally tapered in R07.'
(out/'validation.json').write_text(json.dumps(v,indent=2));(out/'print/manifest.json').write_text(json.dumps(v,indent=2))
(src/'checkpoints').mkdir(exist_ok=True);dest=src/'checkpoints/ET-MOUSE-MONO-STEM-R07.FCStd';shutil.copy2(native,dest)
p.update(revision='ET-MOUSE-MONO-STEM-R07',native_checkpoint=dest.relative_to(r).as_posix(),native_sha256=v['native_sha256'],validation=v)
(src/'print-test.json').write_text(json.dumps(p,indent=2))
(out/'print/README.txt').write_text('Mouse R07 print-test candidate. Units: mm. Supersedes R06 upper-arm terminal.\nUse carrier-and-holder.stl together with matching-cap.stl, camera-clip.stl and baseplate.stl from this package. Preserve the carrier/holder relative placement. Physical fit and strength require a print test.\n')
with zipfile.ZipFile(out/'mouse-R07-print-test.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted((out/'print').iterdir()):z.write(f,f.name)
print(v['native_sha256'])
