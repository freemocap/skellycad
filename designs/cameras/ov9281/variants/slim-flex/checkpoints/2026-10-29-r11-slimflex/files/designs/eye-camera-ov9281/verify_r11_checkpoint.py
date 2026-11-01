"""Check identity and coverage of the complete saved review, not hardware function."""
from pathlib import Path
import hashlib,json,zipfile,urllib.request,re,subprocess,sys
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'designs/eye-camera-ov9281';S=D/'electronics/r11';P=ROOT/'generated/ov9281-r11-electronics';M=ROOT/'generated/ov9281-r11-mechanics';C=D/'checkpoints/2026-10-29-r11-slimflex'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
    selector=read(D/'working-review.json');assert all(sha(ROOT/e['path'])==e['sha256'] for e in selector['files'])
    baseline=read(S/'source-hashes.json')
    for p,h in baseline.items():
        path=C/'lineage/working-review.json' if p.endswith('eye-camera-ov9281/working-review.json') else ROOT/p
        assert sha(path)==h,p
    board=read(S/'board-validation.json');assert board['status']=='pass' and board['board_sha256']==sha(P/'camera.kicad_pcb');assert board['native_errors']==board['native_unconnected']==0;assert len(board['reviewed_stack_warnings'])==board['native_warnings']==199
    sch=read(S/'schematic-validation.json');assert sch['status']=='pass' and all(sha(P/n)==h for n,h in sch['sha256'].items())
    comp=read(S/'component-validation.json');assert comp['status']=='pass' and all(sha(S/n)==h for n,h in comp['sha256'].items())
    cad=read(M/'validation.json');assert cad['board_sha256']==board['board_sha256'];assert cad['native_sha256']==sha(M/'OV9281-R11-MATCHED.FCStd');assert cad['geometry_transfer_sha256']==sha(P/'native-geometry.json');assert cad['rendered_geometry_measurements_unchanged']
    with zipfile.ZipFile(M/'OV9281-R11-MATCHED.FCStd') as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
    mass=read(S/'mass-budget.json');assert mass['external_tether_excluded'] and not mass['nominal_target_met'];assert all(sha(ROOT/p)==h for p,h in mass['source_sha256'].items())
    parts=read(S/'components.json')['parts'];bom=read(S/'purchasing-bom.json');refs=[r for x in bom['rows'] for r in x['refs']];assert len(refs)==len(set(refs))==104;assert set(refs)=={r for r,p in parts.items() if p['populated'] and r!='J103'};assert bom['component_source_sha256']==sha(S/'components.json')
    for row in bom['rows']:
        assert row['all_observations'];assert all(parts[r]['mpn']==row['mpn'] for r in row['refs'])
    power=read(S/'sensor-power-validation.json');assert not power['results']['DVDD']['twice_typical_passes_DC_screen'];assert all(parts[r]['dcr_max_ohm']==.247 for r in ['L1','L2','L3'])
    fw=read(S/'firmware-validation.json');assert fw['status']=='pass' and not fw['physical_camera_demonstrated'];assert fw['synthetic_frames_verified']==3
    for mode,check in fw['builds'].items():
        b=ROOT/'generated/camera-firmware-r11'/mode;assert check['compiled'] and not check['executed_on_hardware'];assert sha(b/'build-report.json')==check['build_report_sha256'];assert all(sha(b/'build'/p)==h for p,h in check['flash_file_sha256'].items())
    opened=read(M/'review-open.json');assert opened['opened'] and not opened['source_file_modified'] and opened['native_sha256']==cad['native_sha256']
    desktop=read(S/'desktop-open.json');assert len(desktop)==3 and all(x['MainWindowHandle'] for x in desktop)
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.links=[]
        def handle_starttag(self,tag,attrs):
            for k,v in attrs:
                if k in ['src','href'] and v:self.links.append(v)
    parser=Links();parser.feed((S/'index.html').read_text(encoding='utf8'));checked=[]
    for u in parser.links:
        if u.endswith('snapshot.json'):continue # Manifest is written after this check.
        p=ROOT/u.lstrip('/') if u.startswith('/') else (S/u).resolve();assert p.is_file(),u;checked.append(u)
    response=urllib.request.urlopen('http://127.0.0.1:8787/designs/eye-camera-ov9281/electronics/r11/index.html',timeout=10);assert response.status==200
    assert (M/'review-desktop.png').stat().st_size>10000
    bibliography=subprocess.run([sys.executable,'-B','tools/check_references.py'],cwd=ROOT,capture_output=True,text=True);assert bibliography.returncode==0,bibliography.stdout+bibliography.stderr
    tests=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tools','-p','test_references.py','-v'],cwd=ROOT,capture_output=True,text=True);assert tests.returncode==0
    report={'status':'pass','scope':'Saved-file identity, baseline preservation, evidence consistency, complete BOM coverage and review opening; not physical qualification','baseline_inputs_verified':len(baseline),'baseline_selector_archived_before_update':True,'pcb_sha256':board['board_sha256'],'cad_sha256':cad['native_sha256'],'schematic_pins_checked':sch['pin_assignments_checked'],'pcb_pad_instances_checked':board['pad_instances_checked'],'native_errors':0,'native_unconnected':0,'stack_warnings_individually_dispositioned':199,'fitted_packages_covered':104,'purchasing_lines':31,'mass_nominal_g':mass['totals']['nominal_g'],'external_tether_excluded':True,'under_one_gram_target_met':False,'dvdd_twice_typical_stress_passes':False,'firmware_variants_compiled':2,'physical_camera_demonstrated':False,'fabrication_ready':False,'native_review_opened':desktop,'freecad_review_opened':opened,'rendered_review_http_status':200,'local_html_links_checked':len(checked),'render_image_visually_reviewed':True,'bibliography':bibliography.stdout.strip(),'bibliography_tests':tests.stderr,'computer_use':False}
    (S/'checkpoint-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['native_review_opened','freecad_review_opened','bibliography_tests']},indent=2))
if __name__=='__main__':main()
