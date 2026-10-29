"""Add ground returns and power distribution to a new R06, preserving R05.

Four-layer plane strategy: [@esp32P4PcbLayout]. Candidate geometry, not SI proof.
"""
from pathlib import Path
import argparse, collections, hashlib, heapq, json, math, shutil
import pcbnew as p

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'electronics/r05'
mm=p.FromMM
def v(x,y):return p.VECTOR2I(mm(x),mm(y))
def xy(q):return (p.ToMM(q.x),p.ToMM(q.y))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dist_point_segment(q,a,z):
    dx,dy=z[0]-a[0],z[1]-a[1];den=dx*dx+dy*dy
    t=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/den)) if den else 0
    return math.hypot(q[0]-a[0]-t*dx,q[1]-a[1]-t*dy)
def segment_box(a,z,box):
    lo,hi=0.,1.
    for axis in range(2):
        d=z[axis]-a[axis]
        if abs(d)<1e-12:
            if a[axis]<box[axis] or a[axis]>box[axis+2]:return False
        else:
            u,w=(box[axis]-a[axis])/d,(box[axis+2]-a[axis])/d
            lo=max(lo,min(u,w));hi=min(hi,max(u,w))
            if lo>hi:return False
    return True
def segment_distance(a,z,c,d):
    def cross(u,w):return u[0]*w[1]-u[1]*w[0]
    r=(z[0]-a[0],z[1]-a[1]);s=(d[0]-c[0],d[1]-c[1]);den=cross(r,s)
    if abs(den)>1e-12:
        ca=(c[0]-a[0],c[1]-a[1]);u=cross(ca,s)/den;t=cross(ca,r)/den
        if 0<=u<=1 and 0<=t<=1:return 0
    return min(dist_point_segment(q,x,y) for q,x,y in [(a,c,d),(z,c,d),(c,a,z),(d,a,z)])

class Router:
    def __init__(self,b,size):
        self.b=b;self.size=size;self.pads=[];self.copper=[];self.vias=[];self.links=[]
        for f in b.GetFootprints():
            for q in f.Pads():
                bb=q.GetBoundingBox();bounds=[p.ToMM(x) for x in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()]]
                self.pads.append((q,f.GetReference(),bounds,f.GetLayer(),q.GetNetname()))
        self.layerpads={layer:[x for x in self.pads if x[0].IsOnLayer(layer)] for layer in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]}
        for t in b.GetTracks():
            assert not isinstance(t,p.PCB_VIA),'R05 unexpectedly contains vias'
            self.copper.append((xy(t.GetStart()),xy(t.GetEnd()),p.ToMM(t.GetWidth()),t.GetLayer(),t.GetNetname()))
    def inboard(self,q,r=.225):
        return all(.5+r<=q[i]<=self.size[i]-.5-r for i in range(2))
    def free_via(self,point,net):
        # Reserve the eventual inner power-track width at edge-adjacent vias.
        radius=.3225 if net=='/USB_VBUS' else .259 if net=='/P4_VDD_HP' else .225
        if not self.inboard(point,radius):return False
        for q,ref,box,layer,n in self.pads:
            # No via-in-pad. Keep the annulus clear of same-net solder lands too.
            margin=.225+(.05 if n==net else .155)
            dx=max(box[0]-point[0],0,point[0]-box[2]);dy=max(box[1]-point[1],0,point[1]-box[3])
            if math.hypot(dx,dy)<margin:return False
        for a,z,w,l,n in self.copper:
            if n!=net and dist_point_segment(point,a,z)<.225+w/2+.155:return False
        return all(math.dist(point,pt)>.45+.155 for pt,n in self.vias)
    def free_segment(self,a,z,net,layer,width=.15):
        margin=.155+width/2
        bx0,bx1=min(a[0],z[0]),max(a[0],z[0]);by0,by1=min(a[1],z[1]),max(a[1],z[1])
        for q,ref,box,l,n in self.layerpads[layer]:
            if n==net:continue
            if segment_box(a,z,[box[0]-margin,box[1]-margin,box[2]+margin,box[3]+margin]):return False
        for c,d,w,l,n in self.copper:
            if n==net or l!=layer:continue
            sep=margin+w/2
            if max(c[0],d[0])+sep<bx0 or min(c[0],d[0])-sep>bx1 or max(c[1],d[1])+sep<by0 or min(c[1],d[1])-sep>by1:continue
            if segment_distance(a,z,c,d)<sep:return False
        for pt,n in self.vias:
            if n==net:continue
            sep=margin+.225
            if pt[0]+sep<bx0 or pt[0]-sep>bx1 or pt[1]+sep<by0 or pt[1]-sep>by1:continue
            if dist_point_segment(pt,a,z)<sep:return False
        return True
    def via(self,point,net):
        t=p.PCB_VIA(self.b);t.SetPosition(v(*point));t.SetWidth(mm(.45));t.SetDrill(mm(.2))
        t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(self.b.FindNet(net));self.b.Add(t)
        self.vias.append((point,net));return t
    def track(self,points,net,layer,width=.15):
        for a,z in zip(points,points[1:]):
            if math.dist(a,z)<1e-6:continue
            t=p.PCB_TRACK(self.b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetWidth(mm(width));t.SetLayer(layer);t.SetNet(self.b.FindNet(net));self.b.Add(t)
            self.copper.append((a,z,width,layer,net))
    def attach(self,pad,ref,layer,net):
        start=xy(pad.GetPosition());candidates=[]
        for pt,n in self.vias:
            if n==net and math.dist(start,pt)<=2.5:candidates.append((math.dist(start,pt),pt,True))
        for ix in range(-20,21):
            for iy in range(-20,21):
                distance=math.hypot(ix,iy)*.125
                if not .25<=distance<=2.5:continue
                pt=(round(start[0]+ix*.125,6),round(start[1]+iy*.125,6))
                candidates.append((distance+.08,pt,False))
        # Exact pad-edge candidates also cover tight edge pads missed by the grid.
        bb=pad.GetBoundingBox();box=[p.ToMM(x) for x in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()]]
        for point in [(box[0]-.275,start[1]),(box[2]+.275,start[1]),(start[0],box[1]-.275),(start[0],box[3]+.275)]:
            candidates.append((math.dist(start,point)+.08,point,False))
        free=[(distance,point,reused) for distance,point,reused in sorted(candidates) if reused or self.free_via(point,net)]
        selected=None
        for distance,point,reused in free:
            if self.free_segment(start,point,net,layer):selected=(point,reused,[start,point]);break
        if selected is None:
            # Try a single bend before declaring a pad blocked. Every segment is
            # checked against copper on its actual surface and all through vias.
            for distance,point,reused in free:
                for corner in [(start[0],point[1]),(point[0],start[1])]:
                    if self.free_segment(start,corner,net,layer) and self.free_segment(corner,point,net,layer):
                        selected=(point,reused,[start,corner,point]);break
                if selected:break
        if selected:
            point,reused,path=selected
            if not reused:self.via(point,net)
            self.track(path,net,layer)
            self.links.append({'reference':ref,'pad':pad.GetNumber(),'pad_xy_mm':start,'net':net,
                               'via_xy_mm':point,'layer':self.b.GetLayerName(layer),'reused_via':reused,
                               'surface_path_mm':path,'surface_length_mm':round(sum(math.dist(a,z) for a,z in zip(path,path[1:])),4)})
            return True
        return False
    def inner_path(self,start,end,net,width,layer=p.In2_Cu):
        if self.free_segment(start,end,net,layer,width):return [start,end]
        step=.125;s=tuple(round(x/step) for x in start);g=tuple(round(x/step) for x in end)
        # Grid connections are checked against the same actual via/track obstacles.
        def point(q):return (q[0]*step,q[1]*step)
        if not self.free_segment(start,point(s),net,layer,width) or not self.free_segment(point(g),end,net,layer,width):return None
        costs={s:0};parents={};queue=[(0,0,s)];visited=0
        while queue:
            _,cost,node=heapq.heappop(queue)
            if cost>costs[node]+1e-9:continue
            if node==g:break
            visited+=1
            if visited>25000:return None
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                nxt=(node[0]+dx,node[1]+dy);a,z=point(node),point(nxt)
                if not self.inboard(z,width/2) or not self.free_segment(a,z,net,layer,width):continue
                nc=cost+math.hypot(dx,dy)
                if nc<costs.get(nxt,1e99):
                    costs[nxt]=nc;parents[nxt]=node;heapq.heappush(queue,(nc+math.dist(nxt,g),nc,nxt))
        else:return None
        nodes=[g]
        while nodes[-1]!=s:nodes.append(parents[nodes[-1]])
        points=[start]+[point(q) for q in reversed(nodes)]+[end]
        smooth=[points[0]];i=0
        while i<len(points)-1:
            j=len(points)-1
            while j>i+1 and not self.free_segment(points[i],points[j],net,layer,width):j-=1
            smooth.append(points[j]);i=j
        return smooth

def zone(b,net,layer,size,inset=.5):
    z=p.ZONE(b);z.SetLayer(layer);z.SetNet(b.FindNet(net));z.SetLocalClearance(mm(.15))
    z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(mm(.15))
    outline=z.Outline();outline.NewOutline()
    for x,y in [(inset,inset),(size[0]-inset,inset),(size[0]-inset,size[1]-inset),(inset,size[1]-inset)]:outline.Append(mm(x),mm(y))
    b.Add(z);return z

def explicit_stackup(path,flex=False):
    # Design-assumption geometry, not a supplier stackup. Copper+dielectric totals
    # equal the intended substrate thickness; mask/coverlay is additional.
    if flex:
        layers=[('F.Cu','copper',.018),('dielectric 1','core',.064),('B.Cu','copper',.018)]
    else:
        layers=[('F.Cu','copper',.035),('dielectric 1','prepreg',.1),('In1.Cu','copper',.035),
                ('dielectric 2','core',.26),('In2.Cu','copper',.035),('dielectric 3','prepreg',.1),('B.Cu','copper',.035)]
    text='(stackup\n'
    for name,kind,t in layers:
        text+=f'(layer "{name}" (type "{kind}") (thickness {t})'
        if kind!='copper':text+=f' (material "{"Polyimide - provisional" if flex else "FR4 - provisional"}") (epsilon_r {3.4 if flex else 4.2}) (loss_tangent 0.02)'
        text+=')\n'
    text+='(copper_finish "ENIG - provisional") (dielectric_constraints no))\n'
    s=path.read_text();assert '(stackup' not in s;s=s.replace('(setup','(setup\n'+text,1);path.write_text(s)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--skip-power-routing',action='store_true')
    args=ap.parse_args();out=args.output.resolve()
    if out.exists():raise SystemExit('Use a new output directory.')
    parent=json.loads((SRC/'validation.json').read_text())['sha256']
    for n,h in parent.items():assert sha(SRC/n)==h,n
    out.mkdir(parents=True)
    for name in ['Camera.pretty','Camera.kicad_sym','fp-lib-table','sym-lib-table','camera.kicad_sch','camera.kicad_pro',
                 'source-netlist.xml','controller.kicad_pro','head.kicad_pro','flex-study.kicad_pro','flex-study.kicad_dru',
                 'LICENSE-Antmicro','LICENSE-Espressif-library.md','interface.json']:
        if (SRC/name).is_dir():shutil.copytree(SRC/name,out/name)
        else:shutil.copy2(SRC/name,out/name)
    result={'revision':'OV9281-P4-R06','parent_sha256':parent,'units':'mm','boards':{},'status':'Power and return-path draft; not for fabrication'}
    controller_rails=['+3V3','/P4_VDD_HP','/P4_FLASH_VDD','/P4_PSRAM_VDD','/P4_MIPI_2V5','/P4_LDO4_UNUSED','/USB_VBUS','+1V2','+1V8','+2V8']
    head_rails=['+1V2','+1V8','+2V8','/M1_DVDD','/M1_DOVDD','/M1_AVDD']
    for name,size,rails in [('controller',(32,20),controller_rails),('head',(14,14),head_rails)]:
        b=p.LoadBoard(str(SRC/f'{name}.kicad_pcb'));r=Router(b,size);missed=[]
        # Ground returns first; positive supplies then get physical access to layer 3.
        for net in ['GND']+rails:
            targets=[x for x in r.pads if x[4]==net]
            # Small/fine-pitch pads first; larger lands tolerate more attachment options.
            targets.sort(key=lambda x:(x[2][2]-x[2][0])*(x[2][3]-x[2][1]))
            for q,ref,box,layer,n in targets:
                if not r.attach(q,ref,layer,n):missed.append({'reference':ref,'pad':q.GetNumber(),'xy_mm':xy(q.GetPosition()),'net':n,'reason':'No collision-free straight or one-bend escape to a through via in the searched neighborhood'})
        print(name,'vias',len(r.vias),'links',len(r.links),'blocked',len(missed),flush=True)
        zone(b,'GND',p.In1_Cu,size)
        if name=='controller':zone(b,'+3V3',p.In2_Cu,size)
        routed=[];failed=[]
        if not args.skip_power_routing:
            for net in rails:
                if name=='controller' and net=='+3V3':continue
                points=sorted(set(pt for pt,n in r.vias if n==net))
                if len(points)<2:continue
                print(name,'routing',net,len(points),'vias',flush=True)
                reached=[points.pop(0)]
                while points:
                    _,a,z=min((math.dist(a,z),a,z) for a in reached for z in points)
                    width=.508 if net=='/P4_VDD_HP' else .635 if net=='/USB_VBUS' else .254
                    path=r.inner_path(a,z,net,width)
                    layer=p.In2_Cu
                    if not path:
                        layer=p.B_Cu;path=r.inner_path(a,z,net,width,layer)
                    if path:
                        r.track(path,net,layer,width);routed.append({'net':net,'layer':b.GetLayerName(layer),'width_mm':width,'points_mm':path})
                    else:failed.append({'net':net,'from_mm':a,'to_mm':z,'width_mm':width})
                    reached.append(z);points.remove(z)
        b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
        # The +3V3 fill can split around other layer-3 supplies. Bridge distinct
        # physical islands on the back, recomputing connectivity after each route.
        if name=='controller' and not args.skip_power_routing:
            attempted=set()
            for iteration in range(24):
                b.BuildConnectivity();c=b.GetConnectivity()
                vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()=='+3V3']
                groups=[];pending={t.m_Uuid.AsString():t for t in vias}
                while pending:
                    first=next(iter(pending.values()));ids={x.m_Uuid.AsString() for x in c.GetConnectedItems(first)}|{first.m_Uuid.AsString()}
                    group=[pending.pop(i) for i in list(pending) if i in ids];groups.append(group)
                if len(groups)<2:break
                pairs=sorted((math.dist(xy(a.GetPosition()),xy(z.GetPosition())),xy(a.GetPosition()),xy(z.GetPosition())) for i,g in enumerate(groups) for h in groups[i+1:] for a in g for z in h)
                found=False
                for _,a,z in pairs:
                    edge=tuple(sorted((a,z)))
                    if edge in attempted:continue
                    attempted.add(edge)
                    path=r.inner_path(a,z,'+3V3',.254,p.B_Cu)
                    if path:
                        r.track(path,'+3V3',p.B_Cu,.254);routed.append({'net':'+3V3','layer':'B.Cu','width_mm':.254,'points_mm':path,'purpose':'Bridge separate filled regions'})
                        found=True;break
                    # Bound each pass; untouched choices remain for a later revision.
                    if len(attempted)>=24:break
                if not found:break
        b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/f'{name}.kicad_pcb'),b)
        project=json.loads((out/'controller.kicad_pro').read_text());project['meta']['filename']=name+'.kicad_pro'
        (out/f'{name}.kicad_pro').write_text(json.dumps(project,indent=2)+'\n')
        explicit_stackup(out/f'{name}.kicad_pcb')
        result['boards'][name]={'via_count':len(r.vias),'pad_attachments':r.links,'blocked_pad_attachments':missed,
                               'power_routes':routed,'blocked_power_routes':failed,'via_diameter_mm':.45,'via_drill_mm':.2}
    b=p.LoadBoard(str(SRC/'flex-study.kicad_pcb'));r=Router(b,(35.3,12.5))
    pins=json.loads((SRC/'interface.json').read_text())['pins'];stitches=[]
    for n in range(1,25):
        if pins[str(n)]!='GND':continue
        for x in [2,33.3]:
            pos=(x,.5+(n-1)*.5)
            # These vias sit on existing ground conductors, outside exposed contacts.
            r.via(pos,'GND');stitches.append(pos)
    z=zone(b,'GND',p.F_Cu,(35.3,12.5),.25)
    outline=z.Outline();outline.RemoveAllContours();outline.NewOutline()
    for x,y in [(1.5,.25),(33.8,.25),(33.8,12.25),(1.5,12.25)]:outline.Append(mm(x),mm(y))
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/'flex-study.kicad_pcb'),b)
    explicit_stackup(out/'flex-study.kicad_pcb',True)
    result['boards']['flex-study']={'ground_vias':stitches,'via_diameter_mm':.45,'via_drill_mm':.2,'plane':'F.Cu; excludes exposed ends; bend and impedance qualification pending'}
    result['limits']=['Rigid-board routing incomplete','Surface power necks still 0.15 mm and require current/impedance review',
                      'No via-in-pad; blocked dense-pad escapes remain reported','Stackups are explicit assumptions, not fabrication-approved',
                      'Flex solid plane changes stiffness and impedance; bending and loss unqualified','No fabricated or powered hardware']
    (out/'power-routing.json').write_text(json.dumps(result,indent=2)+'\n')
    interface=json.loads((out/'interface.json').read_text())
    interface.update(revision=result['revision'],parent_sha256=parent,status=result['status'])
    interface['flex_body_thickness_note']='Explicit 0.10 mm copper/dielectric assumption; coverlay, adhesive and supplier stackup pending'
    interface['limits']=[x for x in interface['limits'] if 'ground contacts not yet' not in x]+result['limits'][1:]
    (out/'interface.json').write_text(json.dumps(interface,indent=2)+'\n')
    print(out,flush=True)

if __name__=='__main__':main()
