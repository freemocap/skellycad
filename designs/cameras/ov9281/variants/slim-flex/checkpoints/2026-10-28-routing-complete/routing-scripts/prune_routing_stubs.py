"""Remove native-DRC dangling tracks on explicitly named nets in a working trial.

This changes no pads or nets. Re-run the full validator and regression checks.
"""
from pathlib import Path
import argparse,json,hashlib,subprocess,sys
import pcbnew as p
from route_head_dovdd import xy

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True);ap.add_argument('--nets',nargs='+',required=True);a=ap.parse_args();out=a.directory.resolve();assert 'generated' in out.parts
    path=out/'head.kicad_pcb';before=hashlib.sha256(path.read_bytes()).hexdigest();b=p.LoadBoard(str(path));held=[];removed=[]
    for iteration in range(20):
        drc_path=out/'checks'/f'stub-cleanup-{iteration}.json'
        subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--output',str(drc_path),str(path)],capture_output=True,check=True)
        drc=json.loads(drc_path.read_text());ids={i['uuid'] for violation in drc['violations'] if violation['type']=='track_dangling' for i in violation['items']}
        matches=[t for t in b.GetTracks() if t.m_Uuid.AsString() in ids and t.GetNetname() in a.nets and not isinstance(t,p.PCB_VIA)]
        if not matches:break
        held.extend(matches)
        for t in matches:removed.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'start':xy(t.GetStart()),'end':xy(t.GetEnd())});b.Remove(t)
        b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
    else:raise AssertionError('Cleanup did not converge')
    (out/'stub-cleanup.json').write_text(json.dumps({'before_sha256':before,'after_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'removed':removed},indent=2)+'\n')
    print(json.dumps({'removed':len(removed),'unconnected':len(drc['unconnected_items']),'violations':[v['type'] for v in drc['violations']]}))
if __name__=='__main__':main()
