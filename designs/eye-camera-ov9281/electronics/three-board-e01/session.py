"""Approved linear checklist and preservation ledger for THREE-BOARD-E01."""
from pathlib import Path
import json, hashlib, sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
ITEMS=[
'**1. Update the design requirements and mass budgets**, retaining the complete head-mounted assembly’s under-one-gram target and making base-station footprint, thickness, connector size and complete backpack mass explicit optimization objectives.',
'**2. Verify the component and documentation basis**, checking exact sensor, serializer, receiver, processor and power-component packages, public design information and availability, with unresolved dependencies clearly identified.',
'**3. Design the camera-head and interface-board circuits**, creating pin-connected KiCad schematics for the sensor, serializer, clocks, power rails, illumination control, protection and tether interface.',
'**4. Design the compact base-station circuits**, creating pin-connected KiCad schematics for the receiver, ESP32-P4, memory, power, USB and programming/debug access while minimizing unnecessary components and bulky connectors.',
'**5. Audit the complete electrical chain**, checking pin mappings, voltage compatibility, clocks, reset and startup behavior, remote control, illumination defaults and connector assignments, and correcting every resolvable issue found.',
'**6. Build compact placement studies from the actual footprints**, checking component and routing space on all three boards, updating matched FreeCAD assemblies and recalculating head, tether and complete base-station mass estimates.',
'**7. Publish the reviewed electrical-design package**, including schematics, BOM, placement files, electrical-rule-check results, cited evidence and all remaining blockers, with a clear handoff to detailed routing.']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if not (HERE/'preservation.json').exists():
    files=json.loads((ROOT/'designs/eye-camera-ov9281/architecture/three-board-r01/r11-preservation.json').read_text())['files']
    assert all(sha(ROOT/p)==h for p,h in files.items()),'R11 mismatch before work'
    for folder in ['designs/eye-camera-ov9281/architecture/three-board-r01','generated/three-board-a01']:
        for p in (ROOT/folder).rglob('*'):
            if p.is_file() and p.suffix.lower() not in ('.lck','.pyc','.fcbak') and '__pycache__' not in str(p):files[str(p.relative_to(ROOT))]=sha(p)
    (HERE/'preservation.json').write_text(json.dumps({'files':files},indent=2)+'\n')
path=HERE/'session.json'
s=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'id':'THREE-BOARD-E01','approved':True,'date':'2026-10-29','items':[{'text':t,'complete':False} for t in ITEMS]}
assert [i['text'] for i in s['items']]==ITEMS
if len(sys.argv)>1:
    n=int(sys.argv[1])-1;assert all(i['complete'] for i in s['items'][:n]);s['items'][n]['complete']=True
path.write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
checklist='\n'.join('- ['+('x' if i['complete'] else ' ')+'] '+i['text'] for i in s['items'])
(HERE/'CHECKLIST.md').write_text('# Approved E01 electrical-design phase\n\n'+checklist+'\n',encoding='utf-8')
print('Checklist saved; completed',sum(i['complete'] for i in s['items']))
