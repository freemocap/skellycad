"""Require a verified connection improvement without changing native rules."""
from pathlib import Path
import argparse,hashlib,json

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--before',type=Path,required=True);ap.add_argument('--after',type=Path,required=True);ap.add_argument('--net',required=True);a=ap.parse_args()
    old=a.before.resolve();new=a.after.resolve();before=json.loads((old/'validation.json').read_text());after=json.loads((new/'validation.json').read_text())
    for folder,record in [(old,before),(new,after)]:
        for name,digest in record['sha256'].items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest,(folder,name)
    for name,oldboard in before['boards'].items():
        current=after['boards'][name]
        assert (old/(name+'.kicad_pro')).read_bytes()==(new/(name+'.kicad_pro')).read_bytes(),name+' rules changed'
        for net,previous in oldboard['net_connectivity'].items():
            now=current['net_connectivity'][net]
            assert now['pads']==previous['pads'] and len(now['connected_pad_groups'])<=len(previous['connected_pad_groups']),(name,net)
        olddrc=json.loads((old/'checks'/(name+'-drc.json')).read_text());newdrc=json.loads((new/'checks'/(name+'-drc.json')).read_text())
        def issues(drc):return {(v['type'],tuple(sorted(i['uuid'] for i in v['items']))) for v in drc['violations']}
        assert issues(newdrc)<=issues(olddrc),(name,'New DRC issues',issues(newdrc)-issues(olddrc))
    assert after['boards']['head']['net_connectivity'][a.net]['complete_on_this_board'],a.net
    assert after['boards']['head']['unconnected_items']<before['boards']['head']['unconnected_items']
    report={'before':str(old),'after':str(new),'completed_net':a.net,'unconnected_before':before['boards']['head']['unconnected_items'],'unconnected_after':after['boards']['head']['unconnected_items'],'new_drc_issues':[],'per_net_connectivity_regressions':[],'native_rules_unchanged':True,'native_hashes_verified':True,'scope':'Connectivity and native design rules, not signal integrity or hardware operation.'}
    (new/'routing-progress.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
