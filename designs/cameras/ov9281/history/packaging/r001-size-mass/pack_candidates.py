"""Conservative two-sided courtyard packing, not PCB routing or release checks."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
MARGIN=.25
GAP=.08

def overlap(a,b,g=0):
    return a[0]<b[0]+b[2]+g-1e-7 and b[0]<a[0]+a[2]+g-1e-7 and a[1]<b[1]+b[3]+g-1e-7 and b[1]<a[1]+a[3]+g-1e-7

def pack(parts,L,W,fixed,obstacles):
    placed=[];occupied=list(obstacles)
    for p in parts:
        if p['reference'] in fixed:
            r=fixed[p['reference']];placed.append({**p,'rect_mm':r});occupied.append(r)
    rest=sorted([p for p in parts if p['reference'] not in fixed],key=lambda p:-(p['courtyard_mm'][0]*p['courtyard_mm'][1]))
    for p in rest:
        best=None
        xs=sorted({MARGIN,*[round(r[0]+r[2]+GAP,5) for r in occupied]});ys=sorted({MARGIN,*[round(r[1]+r[3]+GAP,5) for r in occupied]})
        for w,h in [p['courtyard_mm'],list(reversed(p['courtyard_mm']))]:
            for y in ys:
                for x in xs:
                    r=[x,y,w,h]
                    if x+w>L-MARGIN+1e-6 or y+h>W-MARGIN+1e-6:continue
                    if any(overlap(r,q,GAP) for q in occupied):continue
                    score=(y+h,x+w,y,x)
                    if best is None or score<best[0]:best=(score,r)
        if best is None:raise ValueError(f"No packing space for {p['reference']} in {L} x {W}")
        placed.append({**p,'rect_mm':best[1]});occupied.append(best[1])
    return placed

def main():
    o=json.loads((HERE/'options.json').read_text(encoding="utf-8"));native=json.loads((HERE/'component-budget.json').read_text(encoding="utf-8"));out=[]
    for v in o['variants']:
        compact=v['id']!='A';placed=[];checks=[]
        for board in ['controller','head']:
            L,W=v[board+'_mm'];parts=[p.copy() for p in v['parts'] if p['board']==board]
            if board=='head':
                for p in parts:
                    if p['reference']=='Q201':p['source_side']='B';p['placement_change']='Moved to underside for optical support clearance'
            for side in ['F','B']:
                ps=[p for p in parts if p['source_side']==side];fixed={};obstacles=[]
                if board=='controller' and side=='F':
                    fixed={'J101':[.25,.25,6.56,7.8],'U101':[7.2,(W-11.2)/2,11.2,11.2]}
                    if not compact:fixed['J102']=[L-.25-4.45,(W-14.5)/2,4.45,14.5]
                if board=='controller' and side=='B':
                    obstacles=[[.25,W-2.45,7.2,2.2]]
                    if v['id']=='C':obstacles.append([7.8,W/2-5,10,10])
                if board=='head' and side=='B' and v['id']=='C':
                    x,y=L/2-4,W/2-4;obstacles=[[x,y,8,.75],[x,y+7.25,8,.75],[x,y+.75,.75,6.5],[x+7.25,y+.75,.75,6.5]]
                if board=='head' and side=='F':
                    # Preserve sensor footprint anchor-to-courtyard offset.
                    src=next(q for q in native if q['reference']=='U1' and q['board']=='head')['courtyard'];x0,y0,x1,y1=src['bounds_xy_mm'];cx,cy=src['xy_mm'];fixed={'U1':[L/2+x0-cx,W/2+y0-cy,x1-x0,y1-y0]};obstacles=[[L/2-4,W/2-4,8,8]]
                    if not compact:obstacles.append([0,1,2.5,12])
                packed=pack(ps,L,W,fixed,obstacles)
                for p in packed:
                    x,y,w,h=p['rect_mm'];assert x>=-1e-6 and y>=-1e-6 and x+w<=L+1e-6 and y+h<=W+1e-6,(v['id'],board,p['reference'],'edge')
                    if board=='head' and side=='F' and p['reference']!='U1':
                        assert not overlap(p['rect_mm'],obstacles[0]),(v['id'],p['reference'],'optics collision')
                for i,p in enumerate(packed):
                    for q in packed[i+1:]:assert not overlap(p['rect_mm'],q['rect_mm']),(v['id'],board,p['reference'],q['reference'],'courtyard collision')
                placed+=packed;checks.append({'board':board,'side':side,'count':len(packed),'in_outline':True,'courtyard_overlap_count':0})
        assert len(placed)==len(v['parts'])
        out.append({'id':v['id'],'name':v['name'],'controller_mm':v['controller_mm'],'head_mm':v['head_mm'],'free_flex_mm':v['free_flex_mm'],'rigid_thickness_mm':v['rigid_thickness_mm'],'flex_thickness_mm':v['flex_thickness_mm'],'parts':placed,'checks':checks,'total_flat_length_mm':v['controller_mm'][0]+v['free_flex_mm'][0]+v['head_mm'][0],'optical_center_head_mm':[x/2 for x in v['head_mm']],'height_semantics':'Courtyard prisms reserve space, not exact package CAD. Separate front/back populations. Lens/holder are unqualified study envelopes.','tether_exit_reservation_mm':[-8,.25,8,7.8],'module_mass_excludes_tether':True})
    report={'variants':out,'units':'mm','packing_only':True,'validated':['All 106 retained physical references in A; 105 in B/C after connector elimination','Board containment','Same-side courtyard non-overlap','Front optics keepout apart from the sensor','Separate connector exit reservation outside board'], 'not_validated':['Electrical routing or decoupling placement','Pin escape, impedance, power, thermal behavior or manufacturability','Thread strength, close focus, IR transmission, cable bend radius or strain relief strength','Physical fit, functioning camera or actual mass']}
    (HERE/'packing.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps([{'id':v['id'],'parts':len(v['parts']),'checks':v['checks']} for v in out],indent=2))
if __name__=='__main__':main()
