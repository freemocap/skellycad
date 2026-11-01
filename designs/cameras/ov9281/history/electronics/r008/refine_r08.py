"""Keep only R08 routes that improve native connectivity; remove unused escapes."""
from pathlib import Path
import argparse, json, shutil, subprocess, sys
import pcbnew as p
from build_r07 import uid
from validate_r06 import key, v
ROOT=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--board',choices=['controller','head']);a=ap.parse_args()
    a.input=a.input.resolve();a.output=a.output.resolve()
    if not a.board:
        assert not a.output.exists()
        shutil.copytree(a.input,a.output,ignore=shutil.ignore_patterns('checks','*.svg','validation.json','*-assembly.kicad_pcb'))
        for name in ['controller','head']:
            subprocess.run([sys.executable,__file__,'--input',str(a.input),'--output',str(a.output),'--board',name],check=True)
        return
    report=json.loads((a.output/'routing-r08.json').read_text())
    # Rebuild from the immutable parent instead of removing SWIG-owned objects.
    # These nets improved in the trial's native connectivity inspection. The
    # saved result still has to pass validate_r06.py before selection.
    reviewed={'controller':{'/FLASH_CS','/FLASH_Q','/M1_CAM_SDA_1V8'},
              'head':{'/M1_AVDD','/M1_DOVDD','/M1_DVDD','/M1_PVDD','/M1_SID'}}
    for name in [a.board]:
        b=p.LoadBoard(str(ROOT/'electronics/r07'/f'{name}.kicad_pcb'))
        print(name,'loaded parent',flush=True)
        routes=report['boards'][name]['routes'];vias=report['boards'][name]['added_vias']
        improved=reviewed[name]
        branches=[r for r in routes if r['purpose']!='Surface escape' and r['net'] in improved]
        endpoints={r[x] for r in branches for x in ['from_uuid','to_uuid']}
        selected=branches+[r for r in routes if r['purpose']=='Surface escape' and r['to_uuid'] in endpoints]
        via_ids={x['uuid'] for x in vias if x['uuid'] in endpoints}
        remap={}
        selected_vias=[dict(item) for item in vias if item['uuid'] in via_ids]
        for item in selected_vias:
            if item['uuid'] not in via_ids:continue
            via=p.PCB_VIA(b);via.SetPosition(v(*item['xy_mm']))
            via.SetWidth(p.FromMM(item['diameter_mm']));via.SetDrill(p.FromMM(item['drill_mm']))
            via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu)
            via.SetNet(b.FindNet(item['net']));b.Add(via)
            remap[item['uuid']]=uid(via);item['uuid']=uid(via)
        for r in selected:
            for field in ['from_uuid','to_uuid']:r[field]=remap.get(r[field],r[field])
            for start,end in zip(r['points_mm'],r['points_mm'][1:]):
                if key(v(*start))==key(v(*end)):continue
                t=p.PCB_TRACK(b);t.SetStart(v(*start));t.SetEnd(v(*end))
                t.SetWidth(p.FromMM(r['width_mm']));t.SetLayer(b.GetLayerID(r['layer']))
                t.SetNet(b.FindNet(r['net']));b.Add(t)
        if name=='head':
            f=next(f for f in b.GetFootprints() if f.GetReference()=='R8')
            f.SetAttributes(f.GetAttributes() & ~p.FP_DNP & ~p.FP_EXCLUDE_FROM_BOM)
        b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(a.output/f'{name}.kicad_pcb'),b)
        report['boards'][name]={'routes':selected,'added_vias':selected_vias}
        print(name,'retained',len(selected),'routes',len(via_ids),'new vias')
    report['refinement']='Retain only branches that reduced native connectivity groups; discard unused escape vias. Native DRC required after refill.'
    (a.output/'routing-r08.json').write_text(json.dumps(report,indent=2)+'\n')
    interface=json.loads((a.output/'interface.json').read_text());interface.update(revision=report['revision'],parent_sha256=report['parent_sha256'],status='SID-low assembly selected; additional routing; incomplete camera')
    (a.output/'interface.json').write_text(json.dumps(interface,indent=2)+'\n')
if __name__=='__main__':main()
