"""Repair R09 trial copper while preserving footprints, nets and design rules.

Run with KiCad Python. Endpoint changes propagate to all tracks on the same net.
Native DRC and connectivity must be rerun after every revision.
"""
from pathlib import Path
import argparse, hashlib, json, shutil
import pcbnew as p

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def key(point):return (point.x,point.y)
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    src=a.source.resolve();out=a.output.resolve();assert not out.exists()
    record=json.loads((src/'validation.json').read_text())
    for name,digest in record['sha256'].items():assert sha(src/name)==digest,name
    shutil.copytree(src,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl','*.FCStd*'))
    report={'parent':str(src),'parent_sha256':record['sha256'],'changes':{},'design_rules_changed':False}
    fixes={
        'controller':{
            '/CAM_L_D0_N':[((28.2335,2.2511),(28.2735,2.2511)),((28.2335,2.1509),(28.2735,2.1509)),((28.2824,2.3),(28.3224,2.3)),((28.3429,2.3),(28.3829,2.3))],
            '/P4_LDO4_UNUSED':[((13.4848,14.0567),(13.4848,14.05))],
            '+3V3':[((14.225,14.3998),(14.225,14.4)),((12.8748,14.3998),(12.8748,14.4))]},
        'head':{
            '/M1_VN1':[((8.7742,5.9962),(8.7742,6.007)),((10.4476,5.9962),(10.4476,6.007))],
            'GND':[((5.3779,5.0276),(5.3779,5.025)),((3.189,5.0276),(3.189,5.025)),((6.602,6.42),(6.585,6.44)),((6.6727,6.4907),(6.6677,6.5))],
            '/M1_AVDD':[((3.5726,4.8274),(3.5726,4.825)),((2.2302,4.8274),(2.2302,4.825)),((6.8204,12.9523),(6.8204,12.94)),((8.4877,12.9523),(8.4877,12.94))],
            '/M1_CAM_SDA_1V8':[((7.8072,13.5093),(7.25,13.3)),((7.4496,13.1517),(7.25,13.2))]}}
    for name in ['controller','head']:
        b=p.LoadBoard(str(out/(name+'.kicad_pcb')));changes=[]
        mappings={net:{key(v(*old)):key(v(*new)) for old,new in pairs} for net,pairs in fixes[name].items()}
        for t in b.GetTracks():
            net=t.GetNetname()
            for point in [t.GetStart(),t.GetEnd()]:
                k=key(point)
                if name=='controller' and net=='+1V8' and point.y<p.FromMM(.56):
                    mappings.setdefault(net,{})[k]=(point.x,p.FromMM(.56))
                if name=='head' and isinstance(t,p.PCB_VIA) and point.y>p.FromMM(13.3):
                    mappings.setdefault(net,{}).setdefault(k,(point.x,p.FromMM(13.3)))
        for t in b.GetTracks():
            net=t.GetNetname();mapping=mappings.get(net,{})
            old=(key(t.GetStart()),key(t.GetEnd()))
            if isinstance(t,p.PCB_VIA):
                if old[0] in mapping:t.SetPosition(p.VECTOR2I(*mapping[old[0]]))
            else:
                if old[0] in mapping:t.SetStart(p.VECTOR2I(*mapping[old[0]]))
                if old[1] in mapping:t.SetEnd(p.VECTOR2I(*mapping[old[1]]))
            new=(key(t.GetStart()),key(t.GetEnd()))
            if new!=old:changes.append({'uuid':t.m_Uuid.AsString(),'net':net,'before_nm':old,'after_nm':new})
        removed=[]
        if name=='head':
            original_drc=json.loads((src/'checks/head-drc.json').read_text())
            dangling={i['uuid'] for x in original_drc['violations'] if x['type']=='via_dangling' for i in x['items']}
            # Retain SWIG references during removal; native DRC checks connectivity afterward.
            discarded=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.m_Uuid.AsString() in dangling]
            for t in discarded:
                removed.append({'uuid':t.m_Uuid.AsString(),'net':t.GetNetname(),'position_nm':key(t.GetPosition())})
                b.Remove(t)
            report['removed_single_layer_vias']=removed
        b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/(name+'.kicad_pcb')),b)
        report['changes'][name]=changes
    (out/'clearance-repair.json').write_text(json.dumps(report,indent=2)+'\n')
    # Copied results describe the parent and must not masquerade as fresh validation.
    (out/'validation.json').rename(out/'parent-validation.json')
    print(json.dumps({n:len(x) for n,x in report['changes'].items()}))
if __name__=='__main__':main()
