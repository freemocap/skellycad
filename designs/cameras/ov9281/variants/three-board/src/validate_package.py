"""Validate E01 evidence and preserved predecessor hashes before handoff."""
from pathlib import Path
import json,hashlib,zipfile,sys
from check_native import check
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'generated/three-board-e01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
preserved=json.loads((HERE/'preservation.json').read_text())['files']
bad=[p for p,h in preserved.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
assert not bad,bad
cad=json.loads((OUT/'cad-validation.json').read_text());manifest=json.loads((HERE/'review-manifest.json').read_text());placement=json.loads((HERE/'placement.json').read_text())
assert cad['status']=='pass' and cad['task_documents_closed'] and not cad['body_intersections']
assert cad['sha256']==sha(OUT/cad['native'])==manifest['assembly_sha256']
assert cad['placement_sha256']==sha(HERE/'placement.json')==manifest['source_placement_sha256']
with zipfile.ZipFile(OUT/cad['native']) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
native=[check('head-interface'),check('base')]
assert sum(x['connected_pins_checked'] for x in native)==595
assert all(x['erc_violations']==0 for x in native)
assert len(placement['parts'])==len({p['ref'] for p in placement['parts']})==196
assert sum(x['footprints'] for x in manifest['pcbs'])==196
for board in manifest['pcbs']:
    assert sha(ROOT/board['file'])==board['sha256']
    assert not board['drc']['violations'] and board['tracks']==0
for folder in ['head-interface','base']:
    for name in ['camera.kicad_sch','camera.kicad_pcb','camera.pdf','placement.svg','Camera.kicad_sym','fp-lib-table','sym-lib-table','erc.json','drc.json','LICENSE-Antmicro','LICENSE-Espressif-library.md']:
        assert (OUT/folder/name).is_file(),(folder,name)
for name in ['assembly.png','assembly-top.png','head-top.png','base-top.png','THREE-BOARD-E01.step']:
    assert (OUT/name).stat().st_size>1000,name
mass=json.loads((HERE/'mass-budget.json').read_text());assert mass['cases']['nominal']['head_complete_g']>1 and manifest['head_target_met'] is False
report={'status':'pass','preserved_files':len(preserved),'preservation_changes':bad,'schematic_components':196,'checked_pin_connections':595,'electrical_contract_checks':len(json.loads((HERE/'electrical-audit.json').read_text())['checks']),'erc_violations':0,'placement_drc_violations':0,'unrouted_connections':488,'cad_saved_reloaded_verified':True,'head_target_met':False,'manufacture_ready':False,'hardware_demonstrated':False}
(HERE/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
