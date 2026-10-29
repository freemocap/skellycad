"""Build a local review from measured native geometry; annotate copies only."""
from pathlib import Path
import hashlib, html, json, math, shutil
import pcbnew as p
from audit_interconnect import OUT, DESIGN, ROOT, checked_inputs, geometry, vec

def main():
    manifest,source=checked_inputs()
    m=json.loads((OUT/'mipi.json').read_text());u=json.loads((OUT/'usb.json').read_text());maps=json.loads((OUT/'board-geometry.json').read_text());findings=[]
    routes=m['routes']+u['routes']
    def add(identifier,title,detail,kind,locations,net_names=()):
        findings.append(dict(id=identifier,title=title,detail=detail,kind=kind,locations=locations,nets=list(net_names)))
    def endpoints(rs):return [{'board':r['board'],'xy':r['ports'][0]['xy'],'layer':r['ports'][0]['layer'],'uuid':r['ports'][0]['uuid']} for r in rs]
    for pair in m['whole_link']:
        rs=[r for r in m['routes'] if r['net'].startswith('/CAM_L_'+pair['pair']+'_')]
        add('M-'+pair['pair'],pair['pair']+' length mismatch',f"P {pair['p_mm']:.3f} mm; N {pair['n_mm']:.3f} mm; difference {pair['difference_mm']:.3f} mm versus 0.254 mm geometric budget.",'measured',endpoints(rs),[r['net'] for r in rs])
    add('M-SPREAD','Inter-pair length spread',f"Pair-mean spread {m['inter_pair_mean_spread_mm']:.3f} mm versus 0.762 mm screening budget. This is geometry, not delay.",'measured',endpoints(m['routes']),[r['net'] for r in m['routes']])
    for pair in m['board_pairs']:
        if not pair['layer_sets_match']:
            rs=[r for r in m['routes'] if r['board']==pair['board'] and r['net'].startswith('/CAM_L_'+pair['pair']+'_')]
            add('L-'+pair['board']+'-'+pair['pair'],'Asymmetric layers: '+pair['pair'],'P and N use different layer sets; rebuild them as a pair with a defined reference and transition geometry.','measured',endpoints(rs),[r['net'] for r in rs])
    for board in maps:
        rs=[r for r in m['routes'] if r['board']==board];locations=[]
        for r in rs:
            for segment in r['reference_screen']:
                for gap in segment['gaps']:
                    locations.append({'board':board,'xy':[(a+b)/2 for a,b in zip(gap['start'],gap['end'])],'layer':segment['layer'],'uuid':segment['uuid'],'net':r['net'],**gap})
        add('R-'+board,'MIPI reference-plane gaps','Orange overlays identify sampled gaps beneath the path; signal layers without an adjacent GND plane are included. Point coverage cannot certify a return-current corridor.','screening',locations,[r['net'] for r in rs])
        locations=[{'board':board,'xy':v['xy'],'uuid':v['uuid'],'layer':'F.Cu','nearby_ground_vias':len(v['ground_vias_within_1mm'])} for r in rs for v in r['via_return_screen'] if len(v['ground_vias_within_1mm'])<2]
        if locations:add('V-'+board,'Ground returns at MIPI vias','Each marked signal via has fewer than two ground vias within the 1 mm screening radius. The radius is a heuristic; actual return geometry needs review.','screening',locations)
        add('Z-'+board,'Impedance not established','Saved material/thickness values are provisional. Width, pair spacing, masks, coverlay and transitions need a manufacturable stackup and impedance calculation.','unqualified',[{'board':board,'xy':rs[0]['ports'][0]['xy'],'layer':rs[0]['ports'][0]['layer']}])
        if board!='flex-study':
            clk=[r for r in rs if '_CLK_' in r['net']]
            add('G-'+board,'Clock guarding and spacing','No continuous same-layer ground pour guards the clock routes. Pair separation varies; complete guarding and aggressor-spacing review are required.','review',endpoints(clk),[r['net'] for r in rs])
    add('U-LENGTH','USB length mismatch',f"DP 12.481 mm; DM 10.102 mm; difference {u['difference_mm']:.3f} mm. No numerical P4 USB skew limit was established.",'measured',endpoints(u['routes']),[r['net'] for r in u['routes']])
    locations=[{'board':'controller','xy':[(a+b)/2 for a,b in zip(gap['start'],gap['end'])],'layer':segment['layer'],'uuid':segment['uuid'],'net':r['net'],**gap} for r in u['routes'] for segment in r['reference_screen'] for gap in segment['gaps']]
    add('U-REF','USB reference-plane gaps','Both USB conductors cross gaps in the saved In1 ground fill. Restore a continuous reference below the complete route.','screening',locations,[r['net'] for r in u['routes']])
    add('U-PAIR','USB pair geometry','Connector-side nearest-mate spacing varies substantially; DP-to-DM median is 1.500 mm. Revisit R109/R110, U105 and J101 launch geometry together.','measured',endpoints(u['routes']),[r['net'] for r in u['routes']])
    j=[q for q in maps['controller']['pads'] if q['ref']=='J101' and q['number']=='4'][0]
    add('U-CABLE','Cable and shield boundary','J101 pin mapping is checked. The external cable, shield termination and channel performance remain unspecified; four contacts provide no dedicated shield connection.','unqualified',[{'board':'controller','xy':j['xy'],'layer':j['layer'],'uuid':j['uuid']}])
    (OUT/'findings.json').write_text(json.dumps(findings,indent=2)+'\n')
    # Native copies contain callouts and exact reference-gap overlays on Dwgs.User.
    native_dir=OUT/'native';native_dir.mkdir(exist_ok=True)
    native_manifest=[]
    for board,g in maps.items():
        b=p.LoadBoard(str(source/(board+'.kicad_pcb')))
        assert geometry(b)==g,'Source geometry changed after measurement'
        maxx=max(max(e['a'][0],e['b'][0]) for e in g['edges'])
        local=[f for f in findings if any(q['board']==board for q in f['locations'])]
        for i,f in enumerate(local):
            candidates=[q for q in f['locations'] if q['board']==board]
            location=max(candidates,key=lambda q:q.get('length_mm',0));point=location['xy']
            circle=p.PCB_SHAPE(b);circle.SetShape(p.SHAPE_T_CIRCLE);circle.SetCenter(vec(point));circle.SetEnd(vec([point[0]+.3,point[1]]));circle.SetLayer(p.Dwgs_User);circle.SetWidth(50000);b.Add(circle)
            marker=p.PCB_TEXT(b);marker.SetText(f['id']);marker.SetPosition(vec([point[0]+.4,point[1]+.4]));marker.SetTextSize(vec([.22,.22]));marker.SetTextThickness(40000);marker.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT);marker.SetLayer(p.Dwgs_User);b.Add(marker)
            label=p.PCB_TEXT(b);label.SetText(f['id']+'  '+f['title']);label.SetPosition(vec([maxx+2,1+i*.7]));label.SetTextSize(vec([.3,.3]));label.SetTextThickness(50000);label.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT);label.SetLayer(p.Dwgs_User);b.Add(label)
            for gap in candidates:
                if 'start' not in gap:continue
                line=p.PCB_SHAPE(b);line.SetShape(p.SHAPE_T_SEGMENT);line.SetStart(vec(gap['start']));line.SetEnd(vec(gap['end']));line.SetWidth(80000);line.SetLayer(p.Dwgs_User);b.Add(line)
        path=native_dir/('AUDIT-'+board+'.kicad_pcb');p.SaveBoard(str(path),b)
        shutil.copy2(source/(board+'.kicad_pro'),path.with_suffix('.kicad_pro'))
        if (source/(board+'.kicad_dru')).exists():shutil.copy2(source/(board+'.kicad_dru'),path.with_suffix('.kicad_dru'))
        reopened=p.LoadBoard(str(path));assert geometry(reopened)==g,'Annotation altered copper, pads, fills or outline'
        native_manifest.append({'path':path.relative_to(OUT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'copper_pads_zones_outline_unchanged':True})
    (OUT/'native-review.json').write_text(json.dumps(native_manifest,indent=2)+'\n')
    # Pre-render every board as SVG, with geometry taken from native coordinates.
    def esc(s):return html.escape(str(s),quote=True)
    svgs=[]
    for board,g in maps.items():
        maxx=max(max(e['a'][0],e['b'][0]) for e in g['edges']);maxy=max(max(e['a'][1],e['b'][1]) for e in g['edges'])
        parts=[f'<svg class="board" data-board="{board}" viewBox="-1 -1 {maxx+2} {maxy+2}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{board} native copper audit">']
        def line(a,z,color,width,extra=''):
            return f'<line x1="{a[0]}" y1="{a[1]}" x2="{z[0]}" y2="{z[1]}" stroke="{color}" stroke-width="{width}" {extra}/>'
        for zone in g['zones']:
            if zone['net']!='GND':continue
            for poly in zone['polygons']:
                d=' '.join('M '+' L '.join(f'{x},{y}' for x,y in contour)+' Z' for contour in [poly['outer']]+poly['holes'])
                parts.append(f'<path class="ground" d="{d}" fill="#17392d" fill-rule="evenodd"/>')
        for edge in g['edges']:parts.append(line(edge['a'],edge['b'],'#b4bbc8',.06))
        for s in g['segments']:
            is_signal=s['net'].startswith('/CAM_L_') or s['net'].startswith('/USB_D')
            color=('#65d6ff' if s['net'].endswith('_P') or '_DP' in s['net'] else '#e5a0ff') if is_signal else '#333f4d'
            attrs=f'class="trace {"signal" if is_signal else "other"}" data-net="{esc(s["net"])}" data-layer="{s["layer"]}"'
            parts.append(line(s['a'],s['b'],color,s['width_mm'],attrs))
        for q in g['pads']:
            x,y=q['xy'];w,h=q['size_mm'];parts.append(f'<rect class="pad" x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" transform="rotate({-q["rotation_deg"]} {x} {y})" fill="#7c785a" opacity=".6"><title>{esc(q["ref"]+"."+q["number"]+" "+q["net"])}</title></rect>')
        for v in g['vias']:parts.append(f'<circle cx="{v["xy"][0]}" cy="{v["xy"][1]}" r="{v["diameter_mm"]/2}" fill="none" stroke="#8d9cab" stroke-width=".035"><title>{esc(v["net"])}</title></circle>')
        for f in findings:
            locations=[q for q in f['locations'] if q['board']==board]
            for q in locations:
                if 'start' in q:parts.append(line(q['start'],q['end'],'#ff983c',.16,f'class="finding" data-issue="{f["id"]}"'))
                else:parts.append(f'<circle class="finding" data-issue="{f["id"]}" cx="{q["xy"][0]}" cy="{q["xy"][1]}" r=".33" fill="none" stroke="#ffcf6e" stroke-width=".07"/>')
        parts.append('</svg>');svg=''.join(parts);(OUT/(board+'-map.svg')).write_text(svg,encoding='utf-8');svgs.append(svg)
    rows=''.join(f'<tr><td>{x["pair"]}</td><td>{x["p_mm"]:.3f}</td><td>{x["n_mm"]:.3f}</td><td>{x["difference_mm"]:.3f}</td><td>0.254</td></tr>' for x in m['whole_link'])
    cards=''.join(f'<button class="issue" data-id="{f["id"]}"><b>{f["id"]} · {esc(f["title"])}</b><span>{esc(f["detail"])}</span></button>' for f in findings)
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Eye camera — interconnect audit</title>
<style>body{margin:0;background:#0c121a;color:#e5edf6;font:16px/1.5 system-ui}main{max-width:1280px;margin:auto;padding:28px}h1{font-size:30px;margin:0}p{max-width:950px;color:#bac8d7}.tag{color:#ffcf6e}.metrics{display:flex;gap:28px;flex-wrap:wrap}table{border-collapse:collapse}td,th{padding:7px 18px 7px 0;text-align:left;border-bottom:1px solid #334254}button,select{background:#202d3d;color:#e5edf6;border:1px solid #486078;border-radius:7px;padding:8px;cursor:pointer}button.active{border-color:#65d6ff;background:#173349}.review{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:18px;margin-top:20px}.canvas{background:#101b26;padding:12px;border-radius:12px;position:sticky;top:10px;align-self:start}.board{width:100%;height:64vh;display:none}.board.active{display:block}.issue{width:100%;text-align:left;margin-bottom:8px}.issue span{display:block;font-size:13px;color:#becbda}.finding{display:none}.finding.selected{display:block}.dim{opacity:.14}a{color:#65d6ff}.controls{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:8px}.note{font-size:13px}footer{margin-top:30px;border-top:1px solid #334254;padding-top:15px}@media(max-width:850px){.review{display:block}.canvas{position:static}.board{height:50vh}}</style>
<main><div class="tag">R09 · audit complete · repairs pending</div><h1>High-speed routing review.</h1><p>This is the measured copper from our saved KiCad boards. The paths are connected, but their lengths, layer choices and ground references need repair before high-speed qualification. Select an issue to locate it on the actual board geometry.</p>
<div class="metrics"><div><b>MIPI: complete head → flex → controller paths</b><table><tr><th>Pair</th><th>P mm</th><th>N mm</th><th>Difference</th><th>Budget</th></tr>ROWS</table></div><div><b>USB</b><p>DP 12.481 mm · DM 10.102 mm<br>Difference 2.379 mm<br>JST pin mapping verified; cable unqualified.</p></div></div>
<p class="note">Planar copper lengths only. Package/contact delay and via barrels excluded. MIPI budgets: 0.254 mm within a pair, 0.762 mm between pair means for this screen. No impedance or waveform simulation was performed. Pad outlines are simplified; the native KiCad copies retain their exact shapes.</p>
<div class="review"><div class="canvas"><div class="controls"><select id="board"><option value="head">Sensor head</option><option value="controller">Controller / USB</option><option value="flex-study">Flex</option></select><select id="layer"><option value="all">All signal layers</option><option>F.Cu</option><option>In1.Cu</option><option>In2.Cu</option><option>B.Cu</option></select><label><input id="ground" type="checkbox" checked>Ground fill</label><button id="reset">Show all signals</button></div>SVGS<p class="note" id="selection">Select an issue. Cyan and violet distinguish conductors; orange marks sampled reference gaps. All dimensions are native millimetres. Filled ground may belong to another layer.</p></div><div id="issues">CARDS</div></div>
<footer><p><a href="REPORT.md">Full report</a> · <a href="CORRECTIVE-CHECKLIST.md">Corrective worklist</a> · <a href="findings.json">Coordinates and IDs</a> · <a href="mipi.json">MIPI measurements</a> · <a href="usb.json">USB measurements</a></p><p class="note">Requirements: <a href="https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32p4/pcb-layout-design-esp32p4.html">Espressif PCB layout guide</a>. Reference-plane sampling and a 1 mm ground-via search are screens, not high-speed qualification. Source checkpoint copper is unchanged; the native review copies add drawing-layer callouts only.</p></footer></main>
<script>const findings=FINDINGS;let chosen=null;const board=document.querySelector('#board'),layer=document.querySelector('#layer');function update(){document.querySelectorAll('.board').forEach(s=>s.classList.toggle('active',s.dataset.board===board.value));document.querySelectorAll('.trace').forEach(s=>{s.style.display=layer.value==='all'||s.dataset.layer===layer.value?'':'none';s.classList.toggle('dim',!!chosen&&chosen.nets.length>0&&!chosen.nets.includes(s.dataset.net));});document.querySelectorAll('.finding').forEach(s=>s.classList.toggle('selected',!!chosen&&s.dataset.issue===chosen.id));document.querySelectorAll('.ground').forEach(s=>s.style.display=document.querySelector('#ground').checked?'':'none');document.querySelectorAll('.issue').forEach(s=>{const f=findings.find(f=>f.id===s.dataset.id);s.style.display=f.locations.some(l=>l.board===board.value)?'':'none';s.classList.toggle('active',chosen?.id===s.dataset.id);});document.querySelector('#selection').textContent=chosen?chosen.id+': '+chosen.detail:'Select an issue. Cyan/violet are conductors; orange marks sampled reference gaps. Ground fill is shown as context and may be on another layer.';}document.querySelectorAll('.issue').forEach(b=>b.onclick=()=>{chosen=findings.find(f=>f.id===b.dataset.id);update();});board.onchange=()=>{chosen=null;update();};layer.onchange=update;document.querySelector('#ground').onchange=update;document.querySelector('#reset').onclick=()=>{chosen=null;layer.value='all';update();};update();</script></html>'''
    page=page.replace('ROWS',rows).replace('SVGS',''.join(svgs)).replace('CARDS',cards).replace('FINDINGS',json.dumps(findings).replace('</','<\\/'))
    (OUT/'index.html').write_text(page,encoding='utf-8');checked_inputs()
    print(json.dumps({'findings':len(findings),'native_copies':native_manifest,'html':str(OUT/'index.html'),'source_native_hashes_unchanged':True},indent=2))

if __name__=='__main__':main()
