"""Validate A01 deliverable lineage and assumptions without touching R11."""
from pathlib import Path
import hashlib,json,math,re,zipfile
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'generated/three-board-a01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())

baseline=read(HERE/'r11-preservation.json')['files'];changed=[]
for path,digest in baseline.items():
    p=ROOT/path
    if not p.is_file() or sha(p)!=digest:changed.append(path)
assert not changed,changed
placement=read(HERE/'placement.json');cad=read(OUT/'cad-validation.json');kicad=read(OUT/'kicad-validation.json')
assert cad['status']=='pass' and len(cad['variants'])==2
for v in cad['variants']:
    p=OUT/v['native'];assert sha(p)==v['sha256']
    with zipfile.ZipFile(p) as z:assert 'Document.xml' in z.namelist() and z.testzip() is None
    assert v['placement_sha256']==sha(HERE/'placement.json')
    assert v['body_count']==len(placement['parts'])==99
    assert not v['intersections'] and v['saved_reloaded_volume_check'] and v['task_document_closed']
    assert not v['physical_fit_verified'] and not v['routing_verified']
assert kicad['native_sheets_exported']==4 and not kicad['electrical_connectivity_validated']
for s in kicad['sheets']:assert sha(OUT/s['path'])==s['sha256']
assert all(p['side']=='F' for p in placement['parts'])
for board in ['head','interface','base']:
    info=placement['boards'][board];w,h=info['size'];parts=[p for p in placement['parts'] if p['board']==board]
    for p in parts:
        x,y=p['center'];pw,ph,_=p['body'];assert x-pw/2>=0 and y-ph/2>=0 and x+pw/2<=w and y+ph/2<=h
    for i,p in enumerate(parts):
        for q in parts[i+1:]:
            assert abs(p['center'][0]-q['center'][0])>=(p['body'][0]+q['body'][0])/2 or abs(p['center'][1]-q['center'][1])>=(p['body'][1]+q['body'][1])/2
assert placement['boards']['head']['size']==[14,10] and placement['boards']['interface']['size']==[18,10]
assert placement['flex']['size']==[25,5.5]
# Explicitly couple the mass calculation's areas to the envelope geometry.
budget=read(HERE/'budgets.json')
for variant in budget['mass'].values():
    for case in variant.values():assert math.isclose(sum(case['parts_g'].values()),case['total_g'],abs_tol=1e-10)
nominal=budget['mass']['FR4_100um']['nominal']['parts_g']
assert math.isclose(nominal['head_copper'],14*10*.122*.6*.00891)
assert math.isclose(nominal['interface_copper'],18*10*.122*.6*.00891)
assert math.isclose(nominal['flex_copper'],25*5.5*.036*.6*.00891)
assert budget['mass']['FR4_100um']['nominal']['total_g']<1<budget['mass']['FR4_100um']['high']['total_g']
assert math.isclose(sum(budget['package_nominal_allowance_g'].values()),nominal['populated_packages'])
for c in budget['cable_cases']:
    assert math.isclose(c['current_A']*c['received_V'],c['load_W'])
    assert math.isclose(c['received_V']+c['current_A']*c['loop_ohm'],c['supply_V'])
assert budget['modes'][0]['payload_MB_s']==25.6 and not budget['modes'][2]['fits_USB480_absolute_ceiling']

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ('href','src') and v:self.links.append(v)
parser=Links();parser.feed((HERE/'index.html').read_text(encoding='utf-8'))
local=[]
for url in parser.links:
    u=urlsplit(url)
    if u.scheme or not u.path:continue
    p=(HERE/unquote(u.path)).resolve()
    if p==HERE/'review-validation.json':continue
    assert p.is_file(),str(p);local.append(str(p.relative_to(ROOT)))
# The view switcher also references these generated screenshots.
for f in ['head-top-FR4.png','head-bottom-FR4.png','assembly-FR4.png','head-bottom-steel.png']:
    assert (OUT/f).stat().st_size>3000
manifest={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.suffix.lower() in ['.fcstd','.step','.pdf','.kicad_sch','.png','.svg']}
report={'status':'pass','date':'2026-10-29','r11_files_verified_unchanged':len(baseline),
    'r11_changed':changed,'placement_bodies':99,'native_variants':2,'native_architecture_sheets':4,
    'local_review_links_checked':len(local),'shape_report_hashes_verified':True,'source_placement_hash_verified':True,
    'one_sided_placement_verified':True,'mass_arithmetic_and_geometry_verified':True,'DC_conservation_verified':True,
    'bibliography_review':'Run repository checker and tests separately; recorded in VALIDATION.md',
    'physical_fit_verified':False,'routing_verified':False,'continuous_capture_verified':False,
    'files':manifest,'scope':'Architecture package checks only; not hardware or fabrication qualification'}
html=read(OUT/'html-validation.json')
assert html['status']=='pass' and not html['script_errors'] and not html['mobile_overflow']
desktop=read(OUT/'desktop-review.json')
assert desktop['opened'] and desktop['native_sha256']==sha(OUT/'THREE-BOARD-A01.FCStd')
report['html_review_verified']=True
report['desktop_native_open_verified']=True
report['source_files']={p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='review-validation.json'}
(HERE/'review-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('files','source_files')},indent=2))
