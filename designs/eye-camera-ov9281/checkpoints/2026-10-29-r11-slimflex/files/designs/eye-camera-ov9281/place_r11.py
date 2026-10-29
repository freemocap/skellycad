"""Place the continuous C board with native package courtyards, in millimetres."""
from pathlib import Path
import json,math,re
import pcbnew as p
import build_r02 as schematic
from build_r11_schematic import OUT,SPEC,BASE

LAYERS=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In3_Cu,p.In4_Cu,p.B_Cu]
CTRL=28.;FLEX=32.85;HEAD=14.;WIDTH=14.;HX=CTRL+FLEX
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def xy(q):return p.ToMM(q.x),p.ToMM(q.y)
def overlap(a,b,g=.06):return a[0]<b[2]+g-1e-7 and b[0]<a[2]+g-1e-7 and a[1]<b[3]+g-1e-7 and b[1]<a[3]+g-1e-7
def courtyard(f):
    boxes=[g.GetBoundingBox() for g in f.GraphicalItems() if g.GetLayer() in (p.F_CrtYd,p.B_CrtYd)]
    if not boxes:
        boxes=[q.GetBoundingBox() for q in f.Pads()]
    bb=boxes[0]
    for z in boxes[1:]:bb.Merge(z)
    return [p.ToMM(q) for q in (bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom())]


def main():
    path=OUT/'camera.kicad_pcb'
    assert not path.exists(), 'Preserve routed work; use an explicit new placement revision'
    spec=json.loads((SPEC/'components.json').read_text())['parts']
    b=p.BOARD();b.SetCopperLayerCount(6);b.SetFileName(str(path))
    ds=b.GetDesignSettings();ds.SetBoardThickness(p.FromMM(.303))
    ds.m_MinClearance=p.FromMM(.075);ds.m_TrackMinWidth=p.FromMM(.075)
    ds.m_CopperEdgeClearance=p.FromMM(.3);ds.m_ViasMinSize=p.FromMM(.225)
    ds.m_ViasMinAnnularWidth=p.FromMM(.075);ds.m_MicroViasMinSize=p.FromMM(.225);ds.m_MicroViasMinDrill=p.FromMM(.07)
    ds.m_SolderMaskExpansion=p.FromMM(.04);ds.m_SolderMaskMinWidth=p.FromMM(.07)
    ds.m_FillVias=True;ds.m_CapVias=True
    nets={}
    for net in sorted({n for row in spec.values() for n in row['pin_nets'].values() if n}):
        q=p.NETINFO_ITEM(b,net);b.Add(q);nets[net]=q
    fps={}
    for ref,row in spec.items():
        f=p.FootprintLoad(str(OUT/'Camera.pretty'),row['footprint'].split(':')[1]);f.SetReference(ref);f.SetValue(row['value']);b.Add(f)
        f.SetFPID(p.LIB_ID('Camera',row['footprint'].split(':')[1]))
        link=p.KIID_PATH();link.push_back(p.KIID(schematic.uid('R11-root')));link.push_back(p.KIID(schematic.uid(ref)));f.SetPath(link)
        for pad in f.Pads():
            if row['pin_nets'].get(pad.GetNumber()):pad.SetNet(nets[row['pin_nets'][pad.GetNumber()]])
        f.SetDNP(not row['populated']);f.Reference().SetVisible(False);f.Value().SetVisible(False)
        for g in f.GraphicalItems():
            if isinstance(g,p.PCB_TEXT):g.SetVisible(False)
        fps[ref]=f
    polygon=[(0,0),(27,0),(28,3),(HX,3),(HX+1,0),(HX+14,0),(HX+14,14),(HX+1,14),(HX,11),(28,11),(27,14),(0,14)]
    for a,z in zip(polygon,polygon[1:]+polygon[:1]):
        e=p.PCB_SHAPE();e.SetShape(p.SHAPE_T_SEGMENT);e.SetStart(v(*a));e.SetEnd(v(*z));e.SetWidth(p.FromMM(.05));e.SetLayer(p.Edge_Cuts);b.Add(e)
    occupied={('controller','F'):[('CSI corridor',[19.7,3.8,27.3,6.7]),('USB right corridor',[20.9,.35,22.0,3.8])],('controller','B'):[('P4 stiffener west',[9,2,12,12]),('P4 stiffener east',[16,2,19,12]),('P4 stiffener north',[12,2,16,4]),('P4 stiffener middle',[12,6.5,16,7.5]),('P4 stiffener south',[12,10,16,12]),('programming access',[.5,11.45,8.3,13.7])],
              ('head','F'):[('optics',[HX+3,3,HX+11,11]),('CSI lower corridor',[HX+.8,11.2,HX+12,13.5]),('CSI left corridor',[HX+.8,3,HX+3.1,11.2])],
              ('head','B'):[('stiffener north',[HX+3,3,HX+11,3.75]),('stiffener south',[HX+3,10.25,HX+11,11]),('stiffener west',[HX+3,3.75,HX+3.75,10.25]),('stiffener east',[HX+10.25,3.75,HX+11,10.25])]}
    placed={}
    def pad(ref,num):return next(q for q in fps[ref].Pads() if q.GetNumber()==str(num))
    def put(ref,side,target,angles=(0,90,180,270),exact=False,pin=None,ignore=()):
        f=fps[ref];region=spec[ref]['region'];left=0 if region=='controller' else HX;right=28 if region=='controller' else HX+14
        if f.IsFlipped()!=(side=='B'):f.Flip(f.GetPosition(),False)
        candidates=[]
        for angle in angles:
            f.SetOrientationDegrees(angle);f.SetPosition(v(0,0));box=courtyard(f);offset=xy(pad(ref,pin).GetPosition()) if pin else (0,0)
            points=[target] if exact else ((left+ix*.1,iy*.1) for ix in range(2,round((right-left)*10)) for iy in range(2,138))
            for x,y in points:
                r=[box[0]+x,box[1]+y,box[2]+x,box[3]+y]
                if r[0]<left+.25 or r[1]<.25 or r[2]>right-.25 or r[3]>13.75:continue
                if region=='head' and r[0]<HX+1.3 and (r[1]<3.3 or r[3]>10.7):continue
                if region=='controller' and r[2]>27:
                    inset=3*(r[2]-27)+.32
                    if r[1]<inset or r[3]>14-inset:continue
                if any(overlap(r,q,.1 if 'stiffener' in name else .06) for name,q in occupied[region,side] if name not in ignore):continue
                # Hold the front USB lane above the processor clear.
                if region=='controller' and side=='F' and ref not in ('U101','J101','U105','R109','R110') and overlap(r,[7.8,.35,21.8,1.3]):continue
                score=(x+offset[0]-target[0])**2+(y+offset[1]-target[1])**2
                candidates.append((score,angle,x,y,r))
        if not candidates:
            (OUT/'placement-debug.json').write_text(json.dumps({'failed':ref,'placed':placed,'occupied':{str(k):v for k,v in occupied.items()}},indent=2)+'\n')
            raise RuntimeError(('No placement',ref,region,side,target))
        score,angle,x,y,r=min(candidates);f.SetOrientationDegrees(angle);f.SetPosition(v(x,y))
        occupied[region,side].append((ref,r));placed[ref]={'region':region,'side':side,'xy_mm':[x,y],'rotation_deg':angle,'courtyard_mm':r,'target_mm':list(target),'target_pin':pin,'target_distance_mm':math.sqrt(score)}
        return f
    put('U101','F',(14,7),(90,),True)
    put('J101','F',(3.65,7),(270,),True)
    put('U1','F',(HX+7,7),(0,),True,ignore=('optics',))
    put('Y101','F',(6.9,12.25),(0,),True)
    put('U105','F',(5,1.9),(0,180))
    put('R109','F',(7.55,2.0),(90,),True)
    put('R110','F',(7.55,4.2),(90,),True)
    # Joint power clusters precede the individual decouplers. The two bulk
    # capacitors occupy deliberate windows in the controller support.
    fixed=[('C123','B',14,5.3,0),('C124','B',14,8.7,0),
      ('U103','F',24.7,11,270),('L101','F',22,11,90),('C105','F',25.4,8.7,0),('C106','F',22,8.2,0),
      ('R105','F',25,13.2,0),('R106','F',26.7,11.2,90),('C107','F',22.9,13.225,0),
      ('U104','B',5.3,6.5,180),('L102','B',2.1,6.5,180),('C108','B',5.4,9,180),('C109','B',2.1,9,0),
      ('R107','B',5.4,4.5,0),('R108','B',5.4,3.3,0),
      ('U5','B',1.3,1.5,0),('C1','B',4,1.1,0),('C5','B',1.8,3.5,0),
      ('U6','B',23.5,5,0),('C2','B',26,5,90),('C6','B',21.5,5,90),
      ('U7','B',23.5,2,0),('C3','B',26,1.9,90),('C4','B',21.5,1.9,90)]
    for ref,side,x,y,angle in fixed:put(ref,side,(x,y),(angle,),True)
    put('U102','B',(23,10),(90,),True)
    put('C103','B',xy(pad('U102',8).GetPosition()),pin='1')
    put('R101','B',xy(pad('U102',1).GetPosition()),pin='2')
    # Decoupling has priority over convenient packing of slower circuitry.
    baseline=p.LoadBoard(str(BASE/'controller.kicad_pcb'))
    original={f.GetReference():f for f in baseline.GetFootprints()}
    decaps={r:re.search(r'U101\.(\d+)',f.GetValue())[1] for r,f in original.items() if re.search(r'U101\.(\d+)',f.GetValue())}
    for ref,n in decaps.items():
        if ref in placed:continue
        target=xy(pad('U101',n).GetPosition())
        try:put(ref,'B',target,pin='1')
        except RuntimeError:put(ref,'F',target,pin='1')
    for ref,n in [('C125','71'),('C126','72'),('C127','74'),('C131','41'),('C132','41'),('C133','73'),('C134','51'),('C135','51'),('C136','77')]:
        if ref not in placed:
            target=xy(pad('U101',n).GetPosition())
            try:put(ref,'B',target,pin='1')
            except RuntimeError:put(ref,'F',target,pin='1')
    put('C101','F',xy(pad('Y101','1').GetPosition()),pin='1')
    put('C102','F',xy(pad('Y101','3').GetPosition()),pin='1')
    # Programming lands retain an unobstructed fixture approach from below.
    put('J103','B',(1.2,12.6),(0,),True,ignore=('programming access',))
    for ref,t in [('D201',(HX+3,1.4)),('D202',(HX+11,1.4))]:put(ref,'F',t)
    put('Q201','B',(HX+7,8.6))
    put('Y1','B',(HX+7,5.3))
    for q,target in [('Q101',(23,3)),('Q102',(23,5)),('Q103',(23,7))]:
        try:put(q,'B',target)
        except RuntimeError:put(q,'F',target)
    targets={'R105':('U103',1),'R106':('U103',1),'C107':('U103',1),'R107':('U104',1),'R108':('U104',1),
             'R111':('U101',48),'C104':('U101',103),'R102':('U101',103),'R103':('U101',66),'R104':('U101',68),'C123':('U101',9),'C124':('U101',76),
             'R112':('Q101',3),'R113':('Q101',2),'R114':('Q102',3),'R115':('Q102',2),'R116':('Q103',1),'R117':('Q103',3),
             'R201':('D201',2),'R202':('D202',2),'R203':('Q201',1),'R204':('Q201',1)}
    remaining=sorted(set(fps)-set(placed),key=lambda r: -math.prod([courtyard(fps[r])[i+2]-courtyard(fps[r])[i] for i in range(2)]))
    for ref in remaining:
        region=spec[ref]['region'];target=xy(pad(*targets[ref]).GetPosition()) if ref in targets else (HX+7,7) if region=='head' else (23,7)
        # Sensor bias parts gravitate to the sensor pad carrying their private net.
        if region=='head' and ref not in targets:
            own={n for n in spec[ref]['pin_nets'].values() if n and n not in ('GND','+1V2','+1V8','+2V8','+3V3')}
            pins=[q for q in fps['U1'].Pads() if q.GetNetname() in own]
            if pins:target=xy(pins[0].GetPosition())
        try:put(ref,'B',target)
        except RuntimeError:put(ref,'F',target)
    for x,label in [(28,'6L to 2L'),(HX,'2L to 6L')]:
        line=p.PCB_SHAPE();line.SetShape(p.SHAPE_T_SEGMENT);line.SetStart(v(x,3));line.SetEnd(v(x,11));line.SetWidth(p.FromMM(.1));line.SetLayer(p.Dwgs_User);b.Add(line)
    p.SaveBoard(str(path),b)
    report={'units':'mm','controller_mm':[28,14],'head_mm':[14,14],'free_flex_mm':[32.85,8],'head_origin_mm':[HX,0],'outline_mm':polygon,
      'reason_for_growth':'Physical decoupling, support exclusions and transition space require more room than the packing-only C study. Dimensions remain within the approved ceilings.',
      'stiffeners':{'controller':[9,2,19,12],'controller_windows':[[12,4,16,6.5],[12,7.5,16,10]],'head_outer':[HX+3,3,HX+11,11],'head_inner':[HX+3.75,3.75,HX+10.25,10.25]},
      'optical_datum_mm':[HX+7,7],'placements':placed,'reservations':{f'{region}_{side}':[{'name':n,'bounds_mm':q} for n,q in rows if n not in spec] for (region,side),rows in occupied.items()},'mass_excludes_external_tether':True}
    (SPEC/'placement.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Placed',len(placed),'components;',path)


if __name__=='__main__':main()
