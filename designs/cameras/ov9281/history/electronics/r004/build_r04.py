"""Functional controller placement and partial copper study, preserving R03.

Run using KiCad's bundled Python with --output NEW_DIRECTORY.
Layout basis: [@esp32P4PcbLayout; @tiTlv62569]. Geometry is not SI qualification.
"""
from pathlib import Path
import argparse, collections, heapq, itertools, json, math, shutil, hashlib
import pcbnew as p

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'electronics/r03'
ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True)
OUT=ap.parse_args().output.resolve()
if OUT.exists(): raise SystemExit('Output must be new; preserve revisions and open files.')
OUT.mkdir(parents=True)
for name in ['Camera.pretty','Camera.kicad_sym','fp-lib-table','sym-lib-table','camera.kicad_sch','camera.kicad_pro','source-netlist.xml','head.kicad_pcb','head.kicad_pro','LICENSE-Antmicro','LICENSE-Espressif-library.md']:
    source=SRC/name
    if source.is_dir(): shutil.copytree(source,OUT/name)
    else: shutil.copy2(source,OUT/name)
mm=p.FromMM
def v(x,y): return p.VECTOR2I(mm(x),mm(y))
def xy(q): return (p.ToMM(q.x),p.ToMM(q.y))
def rect(fp):
    bb=fp.GetBoundingBox(False,False)
    return [p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())]
def overlap(a,b,gap=.15):
    return not(a[2]+gap<=b[0] or b[2]+gap<=a[0] or a[3]+gap<=b[1] or b[3]+gap<=a[1])
baseline=p.LoadBoard(str(SRC/'controller.kicad_pcb'))
b=p.BOARD();b.SetCopperLayerCount(4);b.GetDesignSettings().SetBoardThickness(mm(.6))
nets={}
for f in baseline.GetFootprints():
    for q in f.Pads():
        name=q.GetNetname()
        if name and name not in nets:
            item=p.NETINFO_ITEM(b,name);b.Add(item);nets[name]=item
for original in baseline.GetFootprints():
    f=p.FOOTPRINT(original);b.Add(f)
    for q in f.Pads():
        if q.GetNetname():q.SetNet(nets[q.GetNetname()])
for a,z in [((0,0),(32,0)),((32,0),(32,20)),((32,20),(0,20)),((0,20),(0,0))]:
    edge=p.PCB_SHAPE();edge.SetShape(p.SHAPE_T_SEGMENT);edge.SetStart(v(*a));edge.SetEnd(v(*z));edge.SetWidth(mm(.05));edge.SetLayer(p.Edge_Cuts);b.Add(edge)
fps={f.GetReference():f for f in b.GetFootprints()}
old={r:{'xy':xy(f.GetPosition()),'side':'back' if f.IsFlipped() else 'front'} for r,f in fps.items()}
oldpads={(r,q.GetNumber()):xy(q.GetPosition()) for r,f in fps.items() for q in f.Pads()}
placed={}; occupied={'front':[],'back':[]}
# Right-edge reservation is the former 12 x 4 mm flex budget rotated 90 degrees.
reservations=[('flex interface budget',[27,3,31,15]),('CSI route corridor',[14,0.75,26.5,3.6])]
occupied['front'].extend(reservations)
def pad(r,n): return next(q for q in fps[r].Pads() if q.GetNumber()==str(n))
def put(r,side,target,angles=(0,90,180,270),exact=False,pin=None):
    f=fps[r]
    if f.IsFlipped()!=(side=='back'): f.Flip(f.GetPosition(),False)
    candidates=[]
    for angle in angles:
        f.SetOrientationDegrees(angle);f.SetPosition(v(0,0));bounds=rect(f)
        off=xy(pad(r,pin).GetPosition()) if pin else (0,0)
        if exact: points=[target]
        else:
            points=((ix*.25,iy*.25) for ix in range(3,125) for iy in range(3,77))
        for x,y in points:
            box=[bounds[0]+x,bounds[1]+y,bounds[2]+x,bounds[3]+y]
            if box[0]<.75 or box[1]<.75 or box[2]>31.25 or box[3]>19.25: continue
            if any(overlap(box,o) for _,o in occupied[side]): continue
            score=(x+off[0]-target[0])**2+(y+off[1]-target[1])**2
            candidates.append((score,angle,x,y,box))
    if not candidates: raise RuntimeError(('No space',r,side,target))
    _,angle,x,y,box=min(candidates)
    f.SetOrientationDegrees(angle);f.SetPosition(v(x,y))
    f.Reference().SetVisible(False);f.Value().SetVisible(False)
    for graphic in f.GraphicalItems():
        if isinstance(graphic,p.PCB_TEXT):
            if 'Author:' in graphic.GetText() or 'License:' in graphic.GetText():
                graphic.SetLayer(p.Cmts_User)
            elif graphic.GetText() in ('${REFERENCE}','%R'):
                graphic.SetPosition(f.GetPosition())
    occupied[side].append((r,box));placed[r]={'side':side,'xy':[x,y],'angle':angle,'bounds':box}
    return f

# Camera exits north toward the right-hand flex. USB exits north toward the left.
put('U101','front',(16.5,10),(180,),True)
put('J101','front',(4,4.5),(270,))
put('U105','front',(8.5,3),(0,))
put('R109','front',(12.25,2),(0,),True)
put('R110','front',(12.25,3.5),(0,),True)
# Crystal region separated from switching components, same copper side as P4.
put('Y101','front',(25,17),(180,),True)
put('C101','front',xy(pad('Y101','1').GetPosition()),pin='1')
put('C102','front',xy(pad('Y101','3').GetPosition()),pin='1')
# Core buck on the side nearest P4 feedback/enable pins after rotation.
put('U103','front',(5.5,12.5),(0,),True)
put('L101','front',(3,16),(0,180))
put('C105','front',(8,14),(0,90,180,270),pin='1')
put('C106','front',(4,18),(0,180),pin='1')
for r,t in [('R105',(8.5,10)),('R106',(8.5,11.5)),('C107',(6,10))]: put(r,'front',t)
# System buck is grouped on the back beneath the connector area.
put('U104','back',(4,11),(180,),True)
put('L102','back',(7,13),(180,0))
put('C108','back',(1.5,12),(0,90,180,270),pin='1')
put('C109','back',(7,16),(180,0),pin='1')
put('R107','back',(2,8));put('R108','back',(4,8))

# Each named P4 decoupler is placed by its own pad, not by the rail centroid.
decaps={}
for r,f in fps.items():
    import re
    match=re.search(r'U101\.(\d+)',f.GetValue())
    if match: decaps[r]=match[1]
for r,n in sorted(decaps.items(),key=lambda t:int(t[1])):
    target=xy(pad('U101',n).GetPosition())
    put(r,'back',target,pin='1')
# Flash near the P4 flash-pin bank; supply/filter and level-shifter groups follow.
put('U102','back',(20,5),(90,270))
put('C103','back',xy(pad('U102','8').GetPosition()),pin='1')
put('R101','back',xy(pad('U102','1').GetPosition()),pin='2')
for u,c_in,c_out,target in [('U5','C1','C5',(27,4)),('U6','C2','C6',(27,9)),('U7','C3','C4',(27,14))]:
    put(u,'back',target)
    put(c_in,'back',xy(pad(u,1).GetPosition()),pin='1')
    put(c_out,'back',xy(pad(u,5).GetPosition()),pin='1')
put('J103','back',(15,18),(0,180))
for q,rs,t in [('Q101',['R112','R113'],(20,10)),('Q102',['R114','R115'],(20,14)),('Q103',['R116','R117'],(25,17))]:
    put(q,'back',t)
    for r in rs: put(r,'back',xy(fps[q].GetPosition()))
targets={'R111':('U101','48'),'C125':('U101','71'),'C126':('U101','72'),'C127':('U101','74'),
         'C131':('U101','41'),'C132':('U101','41'),'C133':('U101','73'),'C134':('U101','51'),
         'C135':('U101','51'),'C136':('U101','77'),'C104':('U101','103'),
         'R102':('U101','103'),'R103':('U101','66'),'R104':('U101','68'),
         'C123':('U101','9'),'C124':('U101','76')}
for r in sorted(set(fps)-set(placed)):
    target=xy(pad(*targets[r]).GetPosition()) if r in targets else (23,16)
    try: put(r,'back',target)
    except RuntimeError: put(r,'front',target)

tracks=[];routes=[]
def track(points,net,layer,width,label):
    length=0
    for a,z in zip(points,points[1:]):
        if math.dist(a,z)<.00001: continue
        t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetWidth(mm(width));t.SetLayer(layer);t.SetNetCode(net);b.Add(t)
        tracks.append((a,z,width,net,layer));length+=math.dist(a,z)
    routes.append({'label':label,'net':b.FindNet(net).GetNetname(),'layer':b.GetLayerName(layer),'width_mm':width,'length_mm':round(length,4),'points_mm':points})

def route(a,z,width=.15):
    """Obstacle-aware local copper path; no impedance/length-matching claim."""
    pa,pz=pad(*a),pad(*z)
    assert pa.GetNetCode()==pz.GetNetCode(),(a,z)
    assert fps[a[0]].GetLayer()==fps[z[0]].GetLayer(),(a,z,'cross-layer')
    layer=fps[a[0]].GetLayer();net=pa.GetNetCode();start=xy(pa.GetPosition());end=xy(pz.GetPosition())
    step=.025;nx,ny=1281,801;blocked=bytearray(nx*ny);clear=.15+width/2+.005
    def markbox(x0,y0,x1,y1,test=None):
        for iy in range(max(0,math.floor(y0/step)),min(ny,math.ceil(y1/step)+1)):
            for ix in range(max(0,math.floor(x0/step)),min(nx,math.ceil(x1/step)+1)):
                px,py=ix*step,iy*step
                if x0<=px<=x1 and y0<=py<=y1 and (test is None or test(px,py)):blocked[iy*nx+ix]=1
    for f in b.GetFootprints():
        for q in f.Pads():
            if q.GetNetCode()==net or not q.IsOnLayer(layer):continue
            bb=q.GetBoundingBox();x,y=xy(bb.GetPosition());X,Y=p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())
            markbox(x-clear,y-clear,X+clear,Y+clear)
    def distance(x,y,a,z):
        dx,dy=z[0]-a[0],z[1]-a[1];den=dx*dx+dy*dy
        t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/den)) if den else 0
        return math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)
    for aa,zz,w,n,l in tracks:
        if n==net or l!=layer:continue
        margin=clear+w/2
        markbox(min(aa[0],zz[0])-margin,min(aa[1],zz[1])-margin,max(aa[0],zz[0])+margin,max(aa[1],zz[1])+margin,
                lambda x,y:distance(x,y,aa,zz)<margin)
    s=tuple(round(c/step) for c in start);g=tuple(round(c/step) for c in end)
    for pos in (s,g):
        if blocked[pos[1]*nx+pos[0]]:raise RuntimeError(('Endpoint blocked',a,z,pos))
    queue=[(0,0,s)];cost={s:0};parent={};moves=[(x,y) for x in [-1,0,1] for y in [-1,0,1] if x or y]
    while queue:
        _,gc,node=heapq.heappop(queue)
        if gc>cost[node]+1e-8:continue
        if node==g:break
        for dx,dy in moves:
            x,y=node[0]+dx,node[1]+dy
            if x<20 or y<20 or x>=nx-20 or y>=ny-20 or blocked[y*nx+x]:continue
            if dx and dy and (blocked[node[1]*nx+x] or blocked[y*nx+node[0]]):continue
            nxt=(x,y);new=gc+math.hypot(dx,dy)
            if new<cost.get(nxt,1e20):
                cost[nxt]=new;parent[nxt]=node
                heapq.heappush(queue,(new+math.hypot(x-g[0],y-g[1]),new,nxt))
    else:raise RuntimeError(('No route',a,z))
    nodes=[g]
    while nodes[-1]!=s:nodes.append(parent[nodes[-1]])
    nodes.reverse();simple=[nodes[0]]
    for i in range(1,len(nodes)-1):
        if (nodes[i][0]-nodes[i-1][0],nodes[i][1]-nodes[i-1][1])!=(nodes[i+1][0]-nodes[i][0],nodes[i+1][1]-nodes[i][1]):simple.append(nodes[i])
    simple.append(nodes[-1])
    # Remove grid stair-steps where a direct, obstacle-checked segment is clear.
    def visible(a,z):
        count=max(1,math.ceil(math.dist(a,z)*2))
        return all(not blocked[round(a[1]+(z[1]-a[1])*i/count)*nx+round(a[0]+(z[0]-a[0])*i/count)] for i in range(count+1))
    smooth=[simple[0]];i=0
    while i<len(simple)-1:
        j=len(simple)-1
        while j>i+1 and not visible(simple[i],simple[j]):j-=1
        smooth.append(simple[j]);i=j
    points=[start]+[(x*step,y*step) for x,y in smooth]+[end]
    track(points,net,layer,width,f'{a[0]}.{a[1]} to {z[0]}.{z[1]}')

# Real short copper escapes for the camera signals, intentionally unterminated.
for n in range(42,48):
    q=pad('U101',n);x,y=xy(q.GetPosition());track([(x,y),(x,y-1.0)],q.GetNetCode(),p.F_Cu,.15,f'CSI pin {n} escape only')
# Route complete USB signal chains; geometry only, lengths are reported for tuning.
requests=[(('U105','1'),('U105','6'),.15),(('U105','3'),('U105','4'),.15),
          (('U101','49'),('R109','2'),.15),(('U101','50'),('R110','2'),.15),
          (('R109','1'),('U105','6'),.15),(('R110','1'),('U105','4'),.15),
          (('U105','1'),('J101','2'),.15),(('U105','3'),('J101','3'),.15)]
# Compact switch-to-inductor and capacitor connections on each buck.
for u,l,ci,co,rt,rb in [('U103','L101','C105','C106','R105','R106'),('U104','L102','C108','C109','R107','R108')]:
    requests.extend([((u,'3'),(l,'1'),.4),((u,'4'),(ci,'1'),.3),((l,'2'),(co,'1'),.4),
                     ((u,'5'),(rt,'2'),.15),((u,'5'),(rb,'1'),.15)])
requests.extend([(('U101','100'),('Y101','1'),.15),(('U101','99'),('Y101','3'),.15),
                 (('Y101','1'),('C101','1'),.15),(('Y101','3'),('C102','1'),.15)])
failed=[]
for a,z,width in requests:
    try:route(a,z,width)
    except RuntimeError as e:failed.append(str(e))

def line(board,a,z,layer=p.Dwgs_User,width=.06):
    t=p.PCB_SHAPE();t.SetShape(p.SHAPE_T_SEGMENT);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetWidth(mm(width));t.SetLayer(layer);board.Add(t)
for label,(x,y,X,Y) in reservations:
    for a,z in [((x,y),(X,y)),((X,y),(X,Y)),((X,Y),(x,Y)),((x,Y),(x,y))]:line(b,a,z)
b.BuildConnectivity();p.SaveBoard(str(OUT/'controller.kicad_pcb'),b)
# Candidate process rules, deliberately explicit and not a fabrication approval.
project={'meta':{'filename':'controller.kicad_pro','version':1},'net_settings':{'classes':[{'name':'Default','clearance':.15,'track_width':.15,'via_diameter':.45,'via_drill':.2}]},
 'board':{'design_settings':{'rules':{'min_clearance':.15,'min_track_width':.15,'min_via_diameter':.45,'min_through_hole_diameter':.2}}}}
(OUT/'controller.kicad_pro').write_text(json.dumps(project,indent=2)+'\n')
distances=[]
for r,n in decaps.items():
    distances.append({'capacitor':r,'p4_pin':n,'before_xy_mm':round(math.dist(oldpads[(r,'1')],oldpads[('U101',n)]),3),
                      'after_xy_mm':round(math.dist(xy(pad(r,'1').GetPosition()),xy(pad('U101',n).GetPosition())),3),
                      'side':placed[r]['side'],'note':'XY pad-centre distance; a ground/power via path is still required'})
record={'revision':'OV9281-P4-R04','status':'Functional placement and partial copper study; not for fabrication',
        'units':'mm','controller_size_mm':[32,20],'head_size_mm':[14,14],'board_thickness_mm':.6,
        'parent_sha256':{n:hashlib.sha256((SRC/n).read_bytes()).hexdigest() for n in ['controller.kicad_pcb','head.kicad_pcb','camera.kicad_sch']},
        'placements':placed,'decoupler_distances':distances,'routes':routes,'unrouted_requests':failed,
        'reservations':reservations,'sources':['esp32P4PcbLayout','tiTlv62569','jlcThinPcbCapabilities'],
        'limits':['Partial copper only','USB paths not impedance or length qualified','CSI escapes end without a selected connector','No power/ground planes or decoupling vias yet','Optics, LEDs and flex remain unselected','No physical imaging test']}
(OUT/'routing-study.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'placed':len(placed),'routes':len(routes),'failed':failed,'decouplers':distances},indent=2))
