"""Read immutable R10 geometry; never save or alter a native board."""
from pathlib import Path
import sys,json,hashlib,collections
import pcbnew as p
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parents[1]));from copper_retention import retention
SRC=ROOT/'generated/ov9281-r10-review-02'
hashes=json.loads((HERE/'source-hashes.json').read_text(encoding="utf-8"))
rows=json.loads((SRC/'component-reservations.json').read_text(encoding="utf-8"))['boards']
result={'boards':{},'components':[]}
for name,area in [('controller',640),('head',196),('flex-study',441.25)]:
    path=SRC/(name+'.kicad_pcb');assert hashlib.sha256(path.read_bytes()).hexdigest()==hashes[path.relative_to(ROOT).as_posix()]
    b=p.LoadBoard(str(path));layers=[p.F_Cu,p.B_Cu] if name=='flex-study' else [p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
    counts=collections.Counter()
    for f in b.GetFootprints():
        ref=f.GetReference();fp=str(f.GetFPID().GetLibItemName());counts[fp]+=1
        row=next((r for r in rows[name] if r['reference']==ref),None)
        result['components'].append({'board':name,'reference':ref,'value':f.GetValue(),'footprint':fp,'courtyard':row,'pad_count':len(list(f.Pads()))})
    vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
    result['boards'][name]={'area_mm2':area,'layers':[retention(b,l,area) for l in layers],'vias':[{'drill_mm':p.ToMM(v.GetDrill())} for v in vias],'footprint_counts':dict(counts)}
(HERE/'native-geometry.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({n:d['footprint_counts'] for n,d in result['boards'].items()},indent=2))
