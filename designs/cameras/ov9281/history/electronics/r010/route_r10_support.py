"""Route ordinary support nets with protected camera pairs and ground planes.

Uses the installed Freerouting tool [@freerouting250]. Native verification is
mandatory after import; an autorouter result is not signal-integrity evidence.
"""
from pathlib import Path
import argparse,json,re,shutil,subprocess,sys
import pcbnew as p
from extract_head import children

ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','import']);ap.add_argument('directory',type=Path);ap.add_argument('--source',type=Path);a=ap.parse_args();out=a.directory.resolve()
def protected(t):return t.GetNetname()=='GND' or t.GetNetname().startswith('/CAM_L_')
if a.action=='prepare':
    assert a.source and not out.exists();shutil.copytree(a.source,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl'))
    b=p.LoadBoard(str(out/'head.kicad_pcb'))
    for t in b.GetTracks():
        near_sensor=not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.F_Cu and all(4.5e6<=q.x<=9.7e6 and 4e6<=q.y<=8e6 for q in [t.GetStart(),t.GetEnd()])
        t.SetLocked(protected(t) or isinstance(t,p.PCB_VIA) or near_sensor)
    p.SaveBoard(str(out/'support-input.kicad_pcb'),b)
    # The interchange format omits KiCad's 0.5 mm copper-edge rule. A 0.4 mm
    # border plus the unchanged 0.1 mm clearance imposes it on the router.
    for layer in [p.F_Cu,p.In2_Cu,p.In3_Cu,p.B_Cu]:
        for x0,y0,x1,y1 in [(0,0,.4,14),(13.6,0,14,14),(0,0,14,.4),(0,13.6,14,14)]:
            z=p.ZONE(b);z.SetLayer(layer);z.SetIsRuleArea(True);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);poly=z.Outline();poly.NewOutline()
            for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]:poly.Append(p.FromMM(x),p.FromMM(y))
            b.Add(z)
    dsn=out/'support.dsn';assert p.ExportSpecctraDSN(b,str(dsn))
    text=dsn.read_text()
    text='\n'.join(line for line in text.splitlines() if not ('(plane ' in line and not any('(polygon '+l+' ' in line for l in ['In1.Cu','In4.Cu'])))+'\n'
    text=re.sub(r'(\(layer (?:In1\.Cu|In4\.Cu)\s+)\(type signal\)',r'\1(type power)',text)
    text=text.replace('(clearance 25 (type smd_smd))','(clearance 100 (type smd_smd))');dsn.write_text(text)
    (out/'support-routing-source.json').write_text(json.dumps({'source':str(a.source.resolve()),'protected':'All camera pairs, ground copper, existing vias and sensor fanouts','reference_layers':['In1.Cu','In4.Cu']},indent=2)+'\n')
else:
    path=out/'head.kicad_pcb';b=p.LoadBoard(str(out/'support-input.kicad_pcb'));original=p.LoadBoard(str(out/'support-input.kicad_pcb'))
    assert p.ImportSpecctraSES(b,str(out/'support.ses'));held=[]
    # Preserve the exact native pair and guard coordinates, including sub-DSN precision.
    for t in list(b.GetTracks()):
        if protected(t):held.append(t);b.Remove(t)
        else:t.SetLocked(False)
    for t in original.GetTracks():
        if protected(t):b.Add(t.Duplicate())
    assert not any(not isinstance(t,p.PCB_VIA) and t.GetNetname()!='GND' and t.GetLayer() in [p.In1_Cu,p.In4_Cu] for t in b.GetTracks())
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
    cli=Path(sys.executable).with_name('kicad-cli.exe');subprocess.run([str(cli),'pcb','drc','--format','json','--output',str(out/'checks/head-drc.json'),str(path)],check=True,capture_output=True)
    d=json.loads((out/'checks/head-drc.json').read_text());print('violations',len(d['violations']),'unconnected',len(d['unconnected_items']))
