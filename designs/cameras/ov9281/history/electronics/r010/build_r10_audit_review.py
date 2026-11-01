"""Record a disposition for every original interconnect finding."""
from pathlib import Path
import hashlib,html,json,shutil
ROOT=Path(__file__).resolve().parents[2];DESIGN=Path(__file__).resolve().parent
PCB=ROOT/'generated/ov9281-r10-review-02';CAD=ROOT/'generated/ov9281-r10-mechanics-02'
OUT=DESIGN/'audits/2026-10-28-corrective-routing'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    OUT.mkdir(exist_ok=True)
    source=DESIGN/'audits/2026-10-28-interconnect/findings.json';old=json.loads(source.read_text())
    v=json.loads((PCB/'validation.json').read_text());f=json.loads((PCB/'flex-routing-validation.json').read_text());u=json.loads((PCB/'usb-routing-validation.json').read_text());m=json.loads((CAD/'validation.json').read_text())
    assert m['pcb_native_sha256']==v['sha256']
    for n,h in v['sha256'].items():assert sha(PCB/n)==h,n
    assert sha(Path(m['native_document']))==m['native_sha256']
    for name in ['head','controller','usb']:
        a=json.loads((PCB/(name+'-routing-validation.json')).read_text());board='controller' if name=='usb' else name;assert a['sha256']==v['sha256'][board+'.kicad_pcb']
    assert f['head_sha256']==v['sha256']['head.kicad_pcb'] and f['controller_sha256']==v['sha256']['controller.kicad_pcb']
    details={
      'M-CLK':('Planar matching repaired','Complete-link P/N difference 0.000001591 mm; budget 0.254 mm.','flex-routing-validation.json'),
      'M-D0':('Planar matching repaired','Complete-link P/N difference 0.000343493 mm; budget 0.254 mm.','flex-routing-validation.json'),
      'M-D1':('Planar matching repaired','Complete-link P/N difference 0.000000440 mm; budget 0.254 mm.','flex-routing-validation.json'),
      'M-SPREAD':('Planar matching repaired','Pair-mean spread 0.000000800 mm; budget 0.762 mm. Barrel/contact/package delay is excluded; electrical delay is not matched or qualified.','flex-routing-validation.json'),
      'L-head-D0':('Layer symmetry repaired','Both members use F.Cu with no signal vias.','head-routing-validation.json'),
      'L-head-D1':('Layer symmetry repaired','Both members use F/B with two matching through transitions each.','head-routing-validation.json'),
      'L-controller-D0':('Layer symmetry repaired','Both members use F/B with two matching through transitions each.','controller-routing-validation.json'),
      'R-head':('Reference routing repaired','Signal and power routes removed from In1/In4; reference gaps limited to the signal transitions themselves.','head-routing-validation.json'),
      'R-controller':('Reference routing repaired','Signal and power routes removed from In1/In4; reference gaps limited to the signal transitions themselves.','controller-routing-validation.json'),
      'R-flex-study':('Reference routing repaired','F.Cu ground backs all measured MIPI paths; the outer 0.25 mm finger tips remain an explicit termination discontinuity.','flex-routing-validation.json'),
      'V-head':('Return transitions repaired','Paired signal transitions have nearby ground-return stitches; native clearance checks pass.','head-routing-validation.json'),
      'V-controller':('Return transitions repaired','Paired signal transitions have nearby ground-return stitches; native clearance checks pass.','controller-routing-validation.json'),
      'Z-head':('Nominal impedance design recorded','Six-layer catalog construction, explicit outer pair geometry and finite clock guards; tolerance corners and nonuniform launches remain unqualified.','../../electronics/r10/STACKUP.md'),
      'Z-controller':('Nominal impedance design recorded','Six-layer catalog construction and MIPI/USB cross-section models; manufacturing compensation and channel qualification remain pending.','../../electronics/r10/STACKUP.md'),
      'Z-flex-study':('Nominal impedance design recorded','Two-layer PI construction, 0.100/0.250 mm pair geometry and a separate clock-guard model; bend and termination qualification remain pending.','../../electronics/r10/FLEX-ROUTING.md'),
      'G-head':('Clock guard geometry repaired','Finite 0.100 mm ground guards and 0.101 mm edge clearance, with grounded connections.','head-routing-validation.json'),
      'G-controller':('Clock guard geometry repaired','Finite 0.100 mm ground guards and 0.101 mm edge clearance, with grounded connections.','controller-routing-validation.json'),
      'U-LENGTH':('Planar matching repaired','Complete U101-to-J101 P/N difference 0.000000509 mm; project target 0.050 mm.','usb-routing-validation.json'),
      'U-REF':('Reference routing repaired','The sampled 0.450 mm reference corridor has no uncovered points.','usb-routing-validation.json'),
      'U-PAIR':('Pair routing repaired','Front-only paired routing, zero signal vias, all four ESD pads on the through paths, and 26 passing ground-guard probes; package launches remain nonuniform.','usb-routing-validation.json'),
      'U-CABLE':('Prototype cable specified','50 mm shielded 90-ohm data pair; pin 1 VBUS, 2 Dâˆ’, 3 D+, 4 GND; explicit shield/drain splice and matching targets. No USB or Pupil compatibility certification.','../../electronics/r10/USB-ROUTING.md')}
    assert set(details)=={r['id'] for r in old}
    findings=[{'id':r['id'],'original_title':r['title'],'original_detail':r['detail'],'disposition':details[r['id']][0],'result':details[r['id']][1],'evidence':details[r['id']][2]} for r in old]
    for n in ['validation.json','head-routing-validation.json','controller-routing-validation.json','flex-routing-validation.json','usb-routing-validation.json','copper-balance.json']:
        shutil.copy2(PCB/n,OUT/n)
    shutil.copy2(CAD/'validation.json',OUT/'mechanical-validation.json')
    for n in ['assembly.png','head-detail.png']:shutil.copy2(CAD/n,OUT/n)
    shutil.copy2(PCB/'OV9281-P4-R10-assembly.svg',OUT/'assembly.svg')
    record={'date':'2026-10-28','scope':'Approved corrective routing phase; all 21 original findings reviewed. Geometry repairs and documented nominal models, not hardware qualification.','source_findings_sha256':sha(source),'native_sha256':v['sha256'],'mechanical_sha256':m['native_sha256'],'findings':findings,'fabrication_ready':False}
    (OUT/'findings.json').write_text(json.dumps(record,indent=2)+'\n')
    table='\n'.join('| '+r['id']+' | '+r['disposition']+' | '+r['result']+' |' for r in findings)
    report='''# R10 corrective routing review

The approved routing corrections are saved as a matched KiCad and FreeCAD review.
All 21 original audit findings have an explicit disposition below. This is an
offline engineering checkpoint, not a functional or fabrication-ready camera.

Native checks pass: **471 schematic-to-pad comparisons, 24 flex paths, 24 XY
interface alignments, zero schematic ERC findings, and zero DRC violations or
unconnected items on all three boards**. Every inner rigid layer exceeds 60%
conservative copper-area retention; the lowest are head In2 at 63.28% and In3
at 65.46%. A local +1V8 fill and four ground stitches achieved this without
changing the verified signal routes.

The six-layer construction and compression assumptions come from the selected
catalog stackup [@pcbwayRigidStackups2026]. Nominal cross-section calculations,
tolerance corners, guard models and project matching budgets are in
[STACKUP.md](../../electronics/r10/STACKUP.md). A passing nominal section does
not qualify connectors, vias, meanders, packages or manufacturing variation.

| Finding | Disposition | Evidence/result |
| --- | --- | --- |
'''+table+'''

## Matched mechanical review

The model uses these exact board hashes and native STEP copper. It includes 106
component reservations: head 8 front/22 back, controller 17 front/59 back.
Courtyard XY and side come from KiCad; heights remain assumptions. The compact
CH2021A envelope remains 6 mm diameter by 2.65 mm long [@chuanganCh2021a]. The
8 mm holder clears the modeled head components after the retained LED/transistor
reliefs. Lens travel at 0, 0.5 and 1 mm clears the holder and filter reservation;
these checks do not establish focus or adequate thread engagement.

Separate coverlay/stiffener envelopes represent the proposed 0.168 mm flex span
and 0.300 mm tips. Native STEP mask thickness differs from that construction.
Flat assembly placement checks XY correspondence; contact heights, solder
thickness, connector engagement and physical fit remain unqualified.

## Remaining qualification

Manufacturing tolerances, complete channel timing and signal integrity, power
and illumination design, verified component bodies, final optics/mounting, and
hardware capture remain outside this routing phase. Planar lengths deliberately
exclude barrel, contact and package paths. The recorded illustrative clock and
data delays differ; this review does not claim electrical delay matching.

The proposed cable and shield termination are recorded in
[USB-ROUTING.md](../../electronics/r10/USB-ROUTING.md); its 50 mm length, untwist
limit and matching budget are project targets. The JST SH wire range and contact
family are manufacturer data [@jstShCatalog]. No USB compliance or compatibility
with an existing Pupil cable is claimed.
'''
    (OUT/'REPORT.md').write_text(report,encoding='utf-8')
    rows=''.join('<tr><td>'+html.escape(r['id'])+'</td><td>'+html.escape(r['disposition'])+'</td><td>'+html.escape(r['result'])+'</td></tr>' for r in findings)
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OV9281 R10 â€” matched routing review</title><style>body{font:17px/1.5 system-ui;margin:0;background:#101720;color:#e7eef5}main{max-width:1160px;margin:auto;padding:36px}h1{font-size:34px}h2{margin-top:38px}.note{background:#213346;padding:18px;border-radius:10px}img{width:100%;background:white;border-radius:8px}a{color:#91d8ff}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:11px;border-bottom:1px solid #3c4a58;text-align:left;vertical-align:top}.links{display:flex;gap:20px;flex-wrap:wrap}.small{color:#b4c4d1}</style><main><h1>R10: corrected routes, matched native models</h1><p>The controller, flex and camera head below are the saved KiCad geometry. FreeCAD uses copper exported from those same files.</p><div class="note"><b>Offline routing checkpoint.</b> Zero ERC/DRC findings; 471 pad/net comparisons and 24 interface alignments pass. The camera is not yet functional or ready to fabricate.</div><h2>The complete assembly</h2><img src="assembly.png" alt="Matched native FreeCAD assembly"><p>Controller 32 Ã— 20 mm Â· flex 35.3 Ã— 12.5 mm Â· head 14 Ã— 14 mm. The flat review spans 76 mm. Component blocks reserve native courtyard space with assumed heights.</p><h2>The compact camera head</h2><img src="head-detail.png" alt="Current head copper and compact optics envelope"><p>The dark cylinder is the 6 mm lens envelope. The transparent holder and filter are design reservations. Their clearance is checked; focus, threads and mounting remain unfinished.</p><h2>The actual routed boards</h2><img src="assembly.svg" alt="Native KiCad copper overview"><p class="small">Composite inspection view. Edit the separate native boards; each retains its own stackup and rules.</p><div class="links"><a href="/generated/ov9281-r10-review-02/head.kicad_pcb">Head KiCad file</a><a href="/generated/ov9281-r10-review-02/controller.kicad_pcb">Controller KiCad file</a><a href="/generated/ov9281-r10-review-02/flex-study.kicad_pcb">Flex KiCad file</a><a href="/generated/ov9281-r10-mechanics-02/OV9281-R10-MATCHED-REVIEW.FCStd">Matched FreeCAD file</a></div><h2>Every original audit finding</h2><p>Nominal impedance models and planar matching are documented separately from manufacturing and electrical qualification.</p><table><tr><th>ID</th><th>Disposition</th><th>Result and limit</th></tr>'''+rows+'''</table><p><a href="REPORT.md">Detailed report</a> Â· <a href="findings.json">Machine-readable evidence</a></p></main></html>'''
    (OUT/'index.html').write_text(page,encoding='utf-8')
    (OUT/'package-manifest.json').write_text(json.dumps({'sha256':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='package-manifest.json'}},indent=2)+'\n')
    print(json.dumps({'findings_reviewed':len(findings),'output':str(OUT)}))
if __name__=='__main__':main()
