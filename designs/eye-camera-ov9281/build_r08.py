"""R08 candidate: select SID-low assembly and continue non-differential nets.

Preserve R07 and its placements. Refill planes, then validate native connectivity.
This is a routing experiment until its report has been reviewed.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, re, shutil
import pcbnew as p
from build_r07 import Router, groups, uid, xy, sha
from extract_head import children
ROOT = Path(__file__).resolve().parent
SRC = ROOT/'electronics/r07'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);out=ap.parse_args().output.resolve()
    assert not out.exists()
    parent=json.loads((SRC/'validation.json').read_text())['sha256']
    for name,h in parent.items():assert sha(SRC/name)==h,name
    shutil.copytree(SRC,out,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl','checks','*.svg','overview.html','README.md','validation.json','*-assembly.kicad_pcb'))
    # Both SID selection resistors were DNP in the inherited reference. Select
    # only the low-side jumper; keep the high-side jumper unpopulated.
    sch=(out/'camera.kicad_sch').read_text(encoding='utf-8')
    changed=False
    for block in children(sch):
        if re.match(r'\(symbol\s',block) and re.search(r'\(property\s+"Reference"\s+"R8"',block):
            assert '(dnp yes)' in block
            sch=sch.replace(block,block.replace('(dnp yes)','(dnp no)').replace('(in_bom no)','(in_bom yes)'))
            changed=True
    assert changed,'R8 assembly option not found'
    (out/'camera.kicad_sch').write_text(sch,encoding='utf-8')
    report={'revision':'OV9281-P4-R08','parent_sha256':parent,'units':'mm','boards':{},
            'assembly_variant':{'R7':'DNP','R8':'populate 0 ohm','sensor_sccb_address_7bit':'0x60'},
            'limits':['No differential pair or impedance qualification','Candidate routing; not for fabrication']}
    for name,size in [('controller',(32,20)),('head',(14,14))]:
        b=p.LoadBoard(str(out/f'{name}.kicad_pcb'));r=Router(b,size);routes=[];addedvias=[]
        if name=='head':
            f=next(f for f in b.GetFootprints() if f.GetReference()=='R8')
            f.SetAttributes(f.GetAttributes() & ~p.FP_DNP & ~p.FP_EXCLUDE_FROM_BOM)
        nets=sorted({q.GetNetname() for f in b.GetFootprints() for q in f.Pads() if q.GetNetname()})
        nets=[n for n in nets if not any(t in n for t in ('CAM_L_','USB_D','XTAL','P4_SW','SYS_SW')) and n!='GND']
        for net in nets:
            if len(groups(b,net))<2:continue
            fine=.1 if name=='head' else .15
            power=net.startswith('+') or 'VDD' in net or net=='/USB_VBUS'
            width=.635 if net=='/USB_VBUS' else .508 if net=='/P4_VDD_HP' else .254 if power else fine
            # Escape disconnected surface islands to through vias. Skip islands
            # that already contain a via; preserve all previous copper.
            for island in groups(b,net):
                if any(isinstance(a,p.PCB_VIA) for a in island):continue
                succeeded=False
                for pad in island:
                    if not isinstance(pad,p.PAD):continue
                    start=xy(pad.GetPosition());layer=pad.GetParentFootprint().GetLayer()
                    candidates=[]
                    for ix in range(-20,21):
                        for iy in range(-20,21):
                            pt=(round(start[0]+ix*.125,6),round(start[1]+iy*.125,6));distance=math.dist(start,pt)
                            if .4<=distance<=2.5 and r.free_via(pt,net):candidates.append((distance,pt))
                    for distance,pt in sorted(candidates)[:100]:
                        path=r.path(start,pt,net,layer,fine,step=.05)
                        if not path:continue
                        length=sum(math.dist(a,z) for a,z in zip(path,path[1:]))
                        if length>min(4,distance*1.7+.2):continue
                        via=r.via(pt,net);r.track(path,net,layer,fine)
                        addedvias.append({'net':net,'xy_mm':pt,'diameter_mm':.45,'drill_mm':.2,'uuid':uid(via)})
                        routes.append({'net':net,'layer':b.GetLayerName(layer),'width_mm':fine,'points_mm':path,'length_mm':length,'purpose':'Surface escape','from_uuid':uid(pad),'to_uuid':uid(via)})
                        succeeded=True;break
                    if succeeded:break
            # Finish branches through shared copper layers. Never cut layer-2 GND.
            for iteration in range(30):
                islands=groups(b,net)
                if len(islands)<2:break
                candidates=[]
                for i,g in enumerate(islands):
                    for h in islands[i+1:]:
                        for a in g:
                            for z in h:
                                for layer in [p.F_Cu,p.B_Cu,p.In2_Cu]:
                                    if a.IsOnLayer(layer) and z.IsOnLayer(layer):
                                        candidates.append((math.dist(xy(a.GetPosition()),xy(z.GetPosition())),uid(a),uid(z),layer,a,z))
                found=False
                for distance,aid,zid,layer,a,z in sorted(candidates,key=lambda x:x[:4])[:30]:
                    path=r.path(xy(a.GetPosition()),xy(z.GetPosition()),net,layer,width,step=.1)
                    if not path:continue
                    length=sum(math.dist(a,z) for a,z in zip(path,path[1:]))
                    if length>max(distance*1.8,distance+2):continue
                    r.track(path,net,layer,width)
                    routes.append({'net':net,'layer':b.GetLayerName(layer),'width_mm':width,'points_mm':path,'length_mm':length,'purpose':'Non-differential branch','from_uuid':aid,'to_uuid':zid})
                    found=True;break
                if not found:break
            print(name,net,'remaining islands',len(groups(b,net)),flush=True)
        b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/f'{name}.kicad_pcb'),b)
        report['boards'][name]={'routes':routes,'added_vias':addedvias}
    (out/'routing-r08.json').write_text(json.dumps(report,indent=2)+'\n')
    print(out,flush=True)
if __name__=='__main__':main()
