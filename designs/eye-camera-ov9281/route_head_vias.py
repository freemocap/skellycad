"""Search alternative through-via escapes without relaxing native clearance rules.

Uses F.Cu escape and B.Cu/In2.Cu continuation; no new In1 ground-layer tracks.
This is a connectivity trial, not controlled-impedance routing.
"""
from pathlib import Path
import argparse, hashlib, json, math, shutil
import pcbnew as p
from route_head_dovdd import v,xy
from route_isolated_head_pads import route

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    src=a.source.resolve();out=a.output.resolve();assert not out.exists()
    b=p.LoadBoard(str(src/'head.kicad_pcb'));report={};layers=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]
    def add_path(points,layer,code):
        for aa,bb in zip(points,points[1:]):
            t=p.PCB_TRACK(b);t.SetStart(v(*aa));t.SetEnd(v(*bb));t.SetWidth(p.FromMM(.1));t.SetLayer(layer);t.SetNetCode(code);b.Add(t)
    def add_via(point,code):
        t=p.PCB_VIA(b);t.SetPosition(point);t.SetWidth(p.FromMM(.4));t.SetDrill(p.FromMM(.2));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNetCode(code);b.Add(t)
    for number in ['B7','E4','E8','F7','G4','G5']:
        pad=next(q for q in b.GetPads() if q.GetParentFootprint().GetReference()=='U1' and q.GetNumber()==number)
        net=pad.GetNetname();items=list(b.GetPads())+list(b.GetTracks())
        obstacles=[i.GetEffectiveShape(layer) for layer in layers for i in items if i.GetNetname()!=net and i.IsOnLayer(layer)]
        vias=[xy(t.GetPosition()) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
        pad_shapes=[q.GetEffectiveShape(layer) for q in b.GetPads() for layer in [p.F_Cu,p.B_Cu] if q.IsOnLayer(layer)]
        def via_clear(point):
            x,y=xy(point)
            if min(x,y)<.7 or max(x,y)>13.3:return False
            if any(math.dist((x,y),q)<.4-1e-8 for q in vias):return False
            shape=p.SHAPE_CIRCLE(point,p.FromMM(.2))
            if any(s.Collide(shape,p.FromMM(.1)) for s in obstacles):return False
            # Keep holes out of solder pads, including same-net pads.
            return not any(s.Collide(shape,0) for s in pad_shapes)
        sx,sy=xy(pad.GetPosition());candidates={}
        for x in range(4,66):
            for y in range(4,66):
                point=v(x*.2,y*.2)
                if via_clear(point):candidates[(point.x,point.y)]=point
        for dx in range(-12,13):
            for dy in range(-12,13):
                point=v(sx+.32+dx*.64,sy+.25+dy*.5)
                if via_clear(point):candidates[(point.x,point.y)]=point
        # Existing dangling front-layer tails can receive a destination via.
        ends=[]
        for t in b.GetTracks():
            if t.GetNetname()==net and t.IsOnLayer(p.F_Cu) and not isinstance(t,p.PCB_VIA):
                ends.extend(q for q in [t.GetStart(),t.GetEnd()] if via_clear(q))
        result={'net':net,'legal_escape_candidates':len(candidates),'attempts':[]};success=False
        for attempt in range(5):
            if not candidates:break
            front=route(b,pad,targets=list(candidates.values()),commit=False,max_nodes=12000)
            if front['result']!='routed':result['front_search']=front;break
            escape=v(*front['path_xy_mm'][-1]);candidates.pop((escape.x,escape.y),None)
            for layer in [p.B_Cu,p.In2_Cu]:
                continuation=route(b,pad,layer=layer,start=escape,commit=False,max_nodes=20000)
                end_via=None
                if continuation['result']!='routed' and ends:
                    continuation=route(b,pad,layer=layer,start=escape,targets=ends,commit=False,max_nodes=20000)
                    if continuation['result']=='routed':end_via=v(*continuation['path_xy_mm'][-1])
                result['attempts'].append({'escape_mm':xy(escape),'layer':b.GetLayerName(layer),'result':continuation['result']})
                if continuation['result']=='routed':
                    add_path(front['path_xy_mm'],p.F_Cu,pad.GetNetCode());add_via(escape,pad.GetNetCode())
                    add_path(continuation['path_xy_mm'],layer,pad.GetNetCode())
                    if end_via is not None:add_via(end_via,pad.GetNetCode())
                    result.update(result='routed',front=front,continuation=continuation,continuation_layer=b.GetLayerName(layer),destination_via_mm=xy(end_via) if end_via is not None else None)
                    success=True;break
            if success:break
        if not success:result['result']='unresolved'
        report[number]=result;print(number,json.dumps({k:val for k,val in result.items() if k not in ['front','continuation']}),flush=True)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
    shutil.copytree(src,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl'))
    if (out/'validation.json').exists():(out/'validation.json').rename(out/'source-validation-via-search.json')
    p.SaveBoard(str(out/'head.kicad_pcb'),b)
    (out/'via-routing.json').write_text(json.dumps({'source_head_sha256':hashlib.sha256((src/'head.kicad_pcb').read_bytes()).hexdigest(),'results':report,'requires_native_drc':True},indent=2)+'\n')
if __name__=='__main__':main()
