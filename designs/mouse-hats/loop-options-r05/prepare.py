from pathlib import Path
import json,shutil
p=Path(__file__).resolve().parent
old=p.parent/'compact-arm-r04'
s=json.loads((old/'settings.json').read_text())
m=json.loads((p.parent/'current/active-model.json').read_text())
s['source_checkpoint']=m['native_checkpoint'];s['source_sha256']=m['native_sha256']
s['variants']={'A':{'description':'Compact','handle_mm':13},'B':{'description':'Medium','handle_mm':18},'C':{'description':'Roomy','handle_mm':23}}
(p/'settings.json').write_text(json.dumps(s,indent=2))
shutil.copyfile(old/'socket-source.brep',p/'socket-source.brep')
code=(old/'build.py').read_text()
body=code[code.index('shift=App.Vector'):code.index('doc=App.newDocument')]
body=body.replace("str(HERE/'socket-source.brep')",'str(socket_path)')
header='import FreeCAD as App, Part\nfrom attachment_arm_features import geometry,unit\nfrom options_root_edges import tray_edges\n\ndef build_geometry(s,src,socket_path):\n'
(p/'geometry.py').write_text(header+'\n'.join(' '+line for line in body.splitlines())+'\n return carrier,arm,path\n')
