"""Prepare current review records and freeze a verified, explicitly unreleased snapshot."""
from pathlib import Path
import json,hashlib,shutil,zipfile,argparse,re,runpy
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'designs/eye-camera-ov9281';S=D/'electronics/r11';P=ROOT/'generated/ov9281-r11-electronics';M=ROOT/'generated/ov9281-r11-mechanics';C=D/'checkpoints/2026-10-29-r11-slimflex'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def documents():
    assert (C/'lineage/working-review.json').exists()
    (D/'WORKING-REVIEW.md').write_text('''# Resume at the R11 SLIM.flex review — 2026-10-29

R11 is the current offline engineering candidate. It combines the OV9281 head,
integrated flex and ESP32-P4 controller into one routed circuit with a matched
FreeCAD assembly. It is not a functional camera or a manufacturing release.

Open [the rendered R11 review](electronics/r11/index.html) in a browser. The
[approved session checklist](electronics/r11/CHECKLIST.md) records the nine-item
scope; [the roadmap](ROADMAP.md) retains the broader project trajectory.

## Current native files

Paths below are relative to the repository root.

- KiCad PCB: `generated/ov9281-r11-electronics/camera.kicad_pcb`.
- KiCad schematic/project and local libraries: `generated/ov9281-r11-electronics/`.
- Complete FreeCAD assembly: `generated/ov9281-r11-mechanics/OV9281-R11-MATCHED.FCStd`.
- Sensor/synthetic compiled firmware: `generated/camera-firmware-r11/`.
- Review records, BOM and material ledger: `designs/eye-camera-ov9281/electronics/r11/`.

The flat span is 74.85 mm: controller 28 × 14 mm, head 14 × 14 mm, and free flex
32.85 × 8 mm. The native FreeCAD tree contains flat, static-bend and preserved
Pupil comparison assemblies. Keep each complete assembly's matched parts together.
The finished component/flex thickness targets are 0.303/0.166 mm; fabrication
qualification remains separate [@wurthSlimFlex0302026; @wurthSlimRules2023].

## Verified scope

The saved schematic has zero ERC violations; 418 pin assignments and 343 retained
baseline nodes were checked. The PCB has zero errors/unconnected items, with 199
individually dispositioned stacked-laser-via warnings. Native geometry transfer,
support clearance, optical-envelope clearance, programming access and static-bend
geometry passed their recorded checks. Both firmware variants compile; 12 host
tests and three synthetic recordings pass. See [electrical](electronics/r11/ELECTRICAL-AUDIT.md),
[mechanical](electronics/r11/MECHANICAL-ASSEMBLY.md) and [firmware](firmware/README.md) records.

## Unresolved results

- Estimated complete-module mass is **1.34 g**, excluding only the external
  tether. The under-one-gram target is not met by the nominal estimate.
- The corrected sensor DVDD screen passes typical current but fails the selected
  twice-typical stress case. Actual load/transient requirements and delivery margin
  must be resolved before fabrication.
- All 104 fitted packages have purchasing observations, but the sensor has no
  qualified stocked source and several exact codes have supply/lifecycle risks.
- The M6-size lens, IR filter, focus, datum and retention remain provisional.
- Construction approval, complete-channel SI, USB power/throughput, thermal
  behavior and physical camera operation remain unqualified. The firmware is a
  snapshot bring-up path; continuous streaming and UVC are not implemented.

See [mass and purchasing](electronics/r11/MASS-AND-PURCHASING.md) and
[release gates and prototype tests](electronics/r11/PROTOTYPE-TESTS.md).

## Preservation and review

`working-review.json` selects the exact R11 files. The frozen review is
`checkpoints/2026-10-29-r11-slimflex/snapshot.json`. The R08 electrical baseline,
R09 routing selector, R10 review and complete Pupil checkpoint remain preserved.
The prior working selector and documentation are copied into this checkpoint's
`lineage/` directory before advancing the current review.

Use KiCad CLI/Python and FreeCAD CLI/macros. Do not use computer use. Save and
verify native work before closing task-owned documents; leave only the saved
current review open. Preserve unrelated desktop sessions and never inject a
macro through an unverified shared FreeCAD pipe.
''',encoding='utf8')
    old=(C/'lineage/README.md').read_text(encoding='utf8');cut=old.index('## Camera to build')
    (D/'README.md').write_text('''# OV9281 infrared eye camera

**Current working candidate: [R11 C SLIM.flex](WORKING-REVIEW.md).**
The approved nine-item offline session produced one routed circuit, matched
FreeCAD assembly, compiled bring-up firmware, mass ledger and purchasing BOM.
Open [the rendered review](electronics/r11/index.html) for actual native views.

The controller is 28 × 14 mm, the head 14 × 14 mm and the integrated free flex
32.85 × 8 mm. Nominal module mass is **1.34 g excluding the external tether**;
the under-one-gram target is not met. No functional camera has been demonstrated.

Native spacing/connectivity and offline assembly checks pass. Sensor DVDD stress
margin, supply-chain qualification, real close-focus IR optics, fabrication,
thermal behavior and hardware operation remain open. The [test plan](electronics/r11/PROTOTYPE-TESTS.md)
separates remaining design gates from eventual bench tests. The [global roadmap](ROADMAP.md)
is broader than this completed session.

R08 remains the selected historical electrical baseline. R10, the C packaging
study and the complete Pupil reference are preserved. `working-review.json`
identifies R11 as the latest checked working candidate, not an accepted release.

## Earlier design rationale

The following notes preserve earlier architecture decisions and research context.
Historical revision descriptions and preliminary dimensions below are superseded
by the current R11 records where they differ.

'''+old[cut:],encoding='utf8')
    old=(C/'lineage/STATUS.md').read_text(encoding='utf8')
    (D/'STATUS.md').write_text('''# Current camera status — 2026-10-29

R11 is the current offline engineering checkpoint. See [WORKING-REVIEW.md](WORKING-REVIEW.md)
and [the native-file review](electronics/r11/index.html). Connectivity, nominal
cross-section analysis, matched geometry and compiled snapshot software are
checked; physical operation is not demonstrated. Nominal mass is 1.34 g without
the external tether, so the target is not met. Supply risks, sensor DVDD stress
margin, fabrication, optics and hardware tests remain open.

The earlier status below is retained as history. Its R08/R10 defects and counts
are not the current R11 results; use the linked R11 reports to resume work.

---

'''+old,encoding='utf8')
    old=(C/'lineage/ROADMAP.md').read_text(encoding='utf8');cut=old.index('## Global roadmap')
    (D/'ROADMAP.md').write_text('''# Eye-camera roadmap

Updated 2026-10-29. The [approved R11 session](electronics/r11/CHECKLIST.md)
advances compact electronics, matching mechanics and offline bring-up software.
The resulting candidate is fully routed and reviewed, but the global qualification
items below remain open. Session completion is not product completion.

R11's immediate remaining gates are the 1.34 g mass estimate versus the under-one-gram
target, supplier/lifecycle gaps, sensor DVDD stress margin, actual IR optics,
fabrication qualification and physical operation. See [the current review](WORKING-REVIEW.md)
and [prototype gates](electronics/r11/PROTOTYPE-TESTS.md). Future work receives a
bounded checklist and approval before execution.

'''+old[cut:].replace('## Approved session: interconnect audit','## Earlier approved session: interconnect audit').replace('## Where this puts us','## Earlier R10 milestone'),encoding='utf8')
    files=[P/n for n in ['camera.kicad_pcb','camera.kicad_sch','camera.kicad_pro']]+[M/'OV9281-R11-MATCHED.FCStd']
    selector={'date':'2026-10-29','selected_electrical_baseline':'OV9281-P4-R08','working_pcb_trial':'OV9281-P4-R11-SLIM-flex','working_mechanics':'OV9281-R11-MATCHED','fabrication_ready':False,'physical_camera_demonstrated':False,'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in files],'previous_snapshot':'checkpoints/2026-10-28-r10-matched/snapshot.json','snapshot':'checkpoints/2026-10-29-r11-slimflex/snapshot.json','review':'electronics/r11/index.html','automation':'KiCad CLI/Python and FreeCAD CLI/macros only; no computer use.','external_tether_excluded':True,'estimated_nominal_mass_g':json.loads((S/'mass-budget.json').read_text())['totals']['nominal_g'],'under_one_gram_demonstrated':False}
    (D/'working-review.json').write_text(json.dumps(selector,indent=2)+'\n')
def freeze():
    assert not (C/'snapshot.json').exists(),'Frozen snapshot already exists; create a new revision instead'
    session=json.loads((S/'session.json').read_text());assert all(t['complete'] for t in session['tasks'][:8])
    verified=json.loads((S/'checkpoint-verification.json').read_text());assert verified['status']=='pass'
    paths=set()
    paths.update(p for p in S.iterdir() if p.is_file())
    names=['camera.kicad_pcb','camera.kicad_sch','camera.kicad_pro','Camera.kicad_sym','fp-lib-table','sym-lib-table','LICENSE-Antmicro','LICENSE-Espressif-library.md','camera.pdf','camera-preview.png','source-netlist.xml','expected-connections.json','native-geometry.json','audit-drc.json','erc.json','pdn-grid-0.025.json.gz','pdn-grid-0.04.json.gz','pdn-grid-0.05.json.gz']
    paths.update(P/n for n in names);paths.update((P/'Camera.pretty').glob('*'));paths.update((P/'schematic-svg').glob('*.svg'))
    paths.update(M/n for n in ['OV9281-R11-MATCHED.FCStd','validation.json','geometry-measurements.json','render-validation.json','flat-top.png','flat-bottom.png','flat-iso.png','bent-iso.png','pupil-comparison.png','review-desktop.png','review-open.json'])
    paths.update(p for p in (D/'firmware').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    for mode in ['sensor','synthetic']:
        base=ROOT/'generated/camera-firmware-r11'/mode;paths.update(base/n for n in ['build-report.json','sdkconfig','build.log','build/flasher_args.json','build/skelly_eye_camera.bin','build/skelly_eye_camera.elf','build/bootloader/bootloader.bin','build/partition_table/partition-table.bin'])
    paths.update((ROOT/'generated/camera-loopback-r11').glob('*'))
    paths.update(D.glob('*r11*.py'));paths.update(D/n for n in ['cross_section.py','routing_geometry.py','routing_spatial.py','interconnect_graph.py','extract_head.py','test_cross_section.py','test_interconnect_graph.py','test_routing_spatial.py','WORKING-REVIEW.md','README.md','STATUS.md','ROADMAP.md','working-review.json'])
    paths.update(ROOT/n for n in ['references.bib','CITATIONS.md','docs/development.md'])
    for p in paths:
        assert p.is_file(),p;dest=C/'files'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);assert sha(dest)==sha(p)
    # All required files now exist in the checkpoint and have passed byte
    # comparison; native windows and the rendered review were verified above.
    # Complete the administrative checklist before sealing the manifest.
    session['tasks'][8]['complete']=True;session['status']='complete';session['current_item']=None;session['completed_date']='2026-10-29'
    (S/'session.json').write_text(json.dumps(session,indent=2)+'\n')
    (S/'CHECKLIST.md').write_text('# Approved R11 work session\n\n'+'\n'.join('- [x] '+t['text'] for t in session['tasks'])+'\n',encoding='utf8')
    runpy.run_path(str(D/'build_r11_review.py'),run_name='__main__')
    for n in ['session.json','CHECKLIST.md','index.html']:shutil.copy2(S/n,C/'files'/(S/n).relative_to(ROOT))
    page=(S/'index.html').read_text(encoding='utf8').replace("'/generated/","'files/generated/").replace('src="/generated/','src="files/generated/')
    def href(m):
        u=m[1]
        if u.endswith('snapshot.json'):return 'href="snapshot.json"'
        if u.startswith('http'):return m[0]
        p=ROOT/u.lstrip('/') if u.startswith('/') else (S/u).resolve();return 'href="files/'+p.relative_to(ROOT).as_posix()+'"'
    page=re.sub(r'href="([^"]+)"',href,page);(C/'index.html').write_text(page,encoding='utf8')
    hashes={p.relative_to(C).as_posix():sha(p) for p in C.rglob('*') if p.is_file()}
    snap={'date':'2026-10-29','revision':'OV9281-P4-R11-SLIM-flex','status':'Frozen offline engineering review; not fabrication ready','lineage':'2026-10-28-r10-matched','checks':verified,'external_tether_excluded':True,'estimated_nominal_mass_g':json.loads((S/'mass-budget.json').read_text())['totals']['nominal_g'],'sha256':hashes}
    (C/'snapshot.json').write_text(json.dumps(snap,indent=2)+'\n');assert all(sha(C/p)==h for p,h in hashes.items());print('Frozen and verified',len(hashes),'files at',C)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--freeze',action='store_true');args=a.parse_args()
    if args.freeze:freeze()
    else:documents()
