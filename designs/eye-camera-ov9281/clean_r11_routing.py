"""Remove unused escape stubs and align sequential laser stacks."""
from pathlib import Path
import json,shutil,subprocess,sys
import pcbnew as p
from routing_r11 import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'generated/ov9281-r11-electronics';CLI=Path(sys.executable).with_name('kicad-cli.exe')

def main():
    path=OUT/'camera.kicad_pcb';backup=OUT/'trials/before-audit-cleanup.kicad_pcb';assert not backup.exists();shutil.copy2(path,backup)
    b=p.LoadBoard(str(path));changes=[]
    for net,old,new in [('/P4_VDD_HP',(22.42,13.424999),(22.4,13.3)),('/M1_MCLK',(66.05,7.25),(66.0025,7.214))]:
        for t in list(b.GetTracks()):
            if t.GetNetname()!=net:continue
            if isinstance(t,p.PCB_VIA):
                if math.dist(xy(t.GetPosition()),old)<.00001:t.SetPosition(v(*new));changes.append(['align via',uid(t),old,new])
            else:
                if math.dist(xy(t.GetStart()),old)<.00001:t.SetStart(v(*new))
                if math.dist(xy(t.GetEnd()),old)<.00001:t.SetEnd(v(*new))
                if t.GetStart()==t.GetEnd():b.Delete(t)
    # Remove exactly the two silkscreen graphics identified in native DRC;
    # assembly outlines and pin numbering remain in the fabrication layers.
    for f in b.GetFootprints():
        for q in list(f.GraphicalItems()):
            if uid(q) in ['f37b5014-8339-4fc4-9fae-23336462498a','50614dc9-c330-4b9f-b2ac-c311c0c29413']:
                changes.append(['remove clipped silk',uid(q)]);f.Delete(q)
    for iteration in range(6):
        p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
        subprocess.run([str(CLI),'pcb','drc','--format','json','--output',str(OUT/'audit-drc.json'),str(path)],capture_output=True,check=True)
        report=json.loads((OUT/'audit-drc.json').read_text());assert not report['unconnected_items']
        dangling={i['uuid'] for x in report['violations'] if x['type'] in ['via_dangling','track_dangling'] for i in x['items']}
        if not dangling:break
        for t in list(b.GetTracks()):
            if uid(t) in dangling:changes.append(['remove unused stub',uid(t),t.GetNetname()]);b.Delete(t)
    (OUT/'routing-cleanup.json').write_text(json.dumps(changes,indent=2)+'\n')
    print('Corrections',len(changes),'remaining warnings',len(report['violations']))
    for x in report['violations']:
        if x['type']!='holes_co_located':print(x)

if __name__=='__main__':main()
