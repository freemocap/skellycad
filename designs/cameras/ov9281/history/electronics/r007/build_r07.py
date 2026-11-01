"""Continue R06 with collision-checked surface routes, preserving its copper.

No clearance reductions, new vias, component moves or MIPI pair routing.
Native connectivity and DRC, not the router's success count, assess the result.
"""
from pathlib import Path
import argparse, collections, heapq, hashlib, json, math, shutil
import pcbnew as p
from build_r06 import Router as BaseRouter, xy, v, segment_box, segment_distance, dist_point_segment
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'electronics/r06'

def uid(item):return item.m_Uuid.AsString()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class Router(BaseRouter):
    def __init__(self,b,size):
        self.b=b;self.size=size;self.pads=[];self.copper=[];self.vias=[];self.links=[];self.cache={}
        for f in b.GetFootprints():
            for q in f.Pads():
                bb=q.GetBoundingBox();bounds=[p.ToMM(x) for x in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()]]
                self.pads.append((q,f.GetReference(),bounds,f.GetLayer(),q.GetNetname()))
        self.layerpads={layer:[x for x in self.pads if x[0].IsOnLayer(layer)] for layer in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]}
        for t in b.GetTracks():
            if isinstance(t,p.PCB_VIA):self.vias.append((xy(t.GetPosition()),t.GetNetname()))
            else:self.copper.append((xy(t.GetStart()),xy(t.GetEnd()),p.ToMM(t.GetWidth()),t.GetLayer(),t.GetNetname()))
    def free_segment(self,a,z,net,layer,width=.15):
        # Spatial bins avoid checking every unrelated pad for every search step.
        cachekey=(net,layer,width,len(self.copper))
        if cachekey not in self.cache:
            self.cache.clear();items=[];bins=collections.defaultdict(set);margin=.155+width/2
            def add(item,bb):
                i=len(items);items.append(item)
                for ix in range(math.floor(bb[0]),math.floor(bb[2])+1):
                    for iy in range(math.floor(bb[1]),math.floor(bb[3])+1):bins[(ix,iy)].add(i)
            for q,ref,box,l,n in self.layerpads[layer]:
                if n==net:continue
                bb=[box[0]-margin,box[1]-margin,box[2]+margin,box[3]+margin];add(('box',bb),bb)
            for c,d,w,l,n in self.copper:
                if n==net or l!=layer:continue
                sep=margin+w/2;add(('track',c,d,sep),[min(c[0],d[0])-sep,min(c[1],d[1])-sep,max(c[0],d[0])+sep,max(c[1],d[1])+sep])
            for pt,n in self.vias:
                if n==net:continue
                sep=margin+.225;add(('via',pt,sep),[pt[0]-sep,pt[1]-sep,pt[0]+sep,pt[1]+sep])
            self.cache[cachekey]=(items,bins)
        items,bins=self.cache[cachekey];indices=set()
        for ix in range(math.floor(min(a[0],z[0])),math.floor(max(a[0],z[0]))+1):
            for iy in range(math.floor(min(a[1],z[1])),math.floor(max(a[1],z[1]))+1):indices.update(bins.get((ix,iy),()))
        for i in indices:
            item=items[i]
            if item[0]=='box' and segment_box(a,z,item[1]):return False
            if item[0]=='track' and segment_distance(a,z,item[1],item[2])<item[3]:return False
            if item[0]=='via' and dist_point_segment(item[1],a,z)<item[2]:return False
        return True
    def path(self,start,end,net,layer,width=.15,step=.05,region=None):
        if self.free_segment(start,end,net,layer,width):return [start,end]
        for corner in [(start[0],end[1]),(end[0],start[1])]:
            if self.free_segment(start,corner,net,layer,width) and self.free_segment(corner,end,net,layer,width):return [start,corner,end]
        s=tuple(round(x/step) for x in start);g=tuple(round(x/step) for x in end)
        def point(q):return (q[0]*step,q[1]*step)
        if not self.free_segment(start,point(s),net,layer,width) or not self.free_segment(point(g),end,net,layer,width):return None
        costs={s:0};parents={};queue=[(0,0,s)];visited=0
        while queue:
            _,cost,node=heapq.heappop(queue)
            if cost>costs[node]+1e-9:continue
            if node==g:break
            visited+=1
            if visited>16000:return None
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                nxt=(node[0]+dx,node[1]+dy);a,z=point(node),point(nxt)
                if region and not (region[0]<=z[0]<=region[2] and region[1]<=z[1]<=region[3]):continue
                if not self.inboard(z,width/2) or not self.free_segment(a,z,net,layer,width):continue
                nc=cost+math.hypot(dx,dy)
                if nc<costs.get(nxt,1e99):
                    costs[nxt]=nc;parents[nxt]=node;heapq.heappush(queue,(nc+math.dist(nxt,g),nc,nxt))
        else:return None
        nodes=[g]
        while nodes[-1]!=s:nodes.append(parents[nodes[-1]])
        points=[start]+[point(q) for q in reversed(nodes)]+[end];smooth=[points[0]];i=0
        while i<len(points)-1:
            j=len(points)-1
            while j>i+1 and not self.free_segment(points[i],points[j],net,layer,width):j-=1
            smooth.append(points[j]);i=j
        return smooth

def groups(b,net):
    b.BuildConnectivity();c=b.GetConnectivity()
    anchors=[q for f in b.GetFootprints() for q in f.Pads() if q.GetNetname()==net]
    anchors += [t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==net]
    pending={uid(q):q for q in anchors};result=[]
    while pending:
        first=next(iter(pending.values()));connected={uid(x) for x in c.GetConnectedItems(first)}|{uid(first)}
        result.append([pending.pop(i) for i in list(pending) if i in connected])
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();out=args.output.resolve()
    assert not out.exists(),'Choose a new output directory'
    parent=json.loads((SRC/'validation.json').read_text())['sha256']
    for name,h in parent.items():assert sha(SRC/name)==h,name
    shutil.copytree(SRC,out,ignore=shutil.ignore_patterns('*.kicad_prl','*.lck','checks','*.svg','overview.html','README.md','validation.json','assembly-interconnect-study.kicad_pcb'))
    report={'revision':'OV9281-P4-R07','parent_sha256':parent,'units':'mm','boards':{},
            'limits':['Partial routing only; not for fabrication','No MIPI or USB pair routing added','Surface power necks and flash/clock timing remain unqualified','No component moves, new vias or reduced clearances']}
    report['fine_sensor_escape_rule']={'width_mm':.1,'clearance_mm':.15,'max_path_length_mm':4,'region_mm':[3.3,2.75,10.8,9.25],
                                      'status':'Candidate trace process; land pattern and complete stackup require fabrication review','sources':['jlcThinPcbCapabilities']}
    for name,size in [('controller',(32,20)),('head',(14,14))]:
        b=p.LoadBoard(str(SRC/f'{name}.kicad_pcb'));r=Router(b,size);added=[];failed=[]
        nets=sorted({q.GetNetname() for f in b.GetFootprints() for q in f.Pads() if q.GetNetname()})
        nets=[n for n in nets if not any(s in n for s in ['CAM_L_','USB_D','XTAL','P4_SW','SYS_SW'])]
        # First join short local networks; longer external control runs follow.
        def span(net):
            positions=[xy(q.GetPosition()) for f in b.GetFootprints() for q in f.Pads() if q.GetNetname()==net]
            return max((math.dist(a,z) for a in positions for z in positions),default=0)
        nets.sort(key=lambda n:(span(n),n))
        for net in nets:
            attempted=set();count=0
            for iteration in range(24):
                parts=groups(b,net)
                if len(parts)<2:break
                candidates=[]
                for i,g in enumerate(parts):
                    for h in parts[i+1:]:
                        for a in g:
                            for z in h:
                                for layer in [p.F_Cu,p.B_Cu]:
                                    if a.IsOnLayer(layer) and z.IsOnLayer(layer):
                                        candidates.append((math.dist(xy(a.GetPosition()),xy(z.GetPosition())),uid(a),uid(z),layer,a,z))
                found=False
                for distance,aid,zid,layer,a,z in sorted(candidates,key=lambda x:x[:4]):
                    edge=(tuple(sorted((aid,zid))),layer)
                    if edge in attempted:continue
                    attempted.add(edge)
                    start,end=xy(a.GetPosition()),xy(z.GetPosition())
                    # Preserve the inherited power-width targets [@esp32P4PcbLayout].
                    # Narrow escapes are allowed only as short local necks.
                    power=net.startswith('+') or 'VDD' in net or net in ['/USB_VBUS','/M1_AVDD']
                    width=.635 if net=='/USB_VBUS' else .508 if net=='/P4_VDD_HP' else .254 if power else .15
                    path=r.path(start,end,net,layer,width)
                    if not path and power and distance<=1.5:
                        narrow=r.path(start,end,net,layer,.15)
                        if narrow and sum(math.dist(a,z) for a,z in zip(narrow,narrow[1:]))<=1.5:
                            path=narrow;width=.15
                    if path:
                        length=sum(math.dist(a,z) for a,z in zip(path,path[1:]))
                        if power and length>max(distance*2,distance+1):continue
                        if '/FLASH_' in net or net in ['/M1_MCLK','/P4_FB','/SYS_FB']:
                            if length>max(distance*1.6,distance+1):continue
                        r.track(path,net,layer,width);added.append({'net':net,'layer':b.GetLayerName(layer),'width_mm':width,'points_mm':path,'length_mm':round(length,4),'from_uuid':aid,'to_uuid':zid})
                        found=True;count+=1;break
                    if len(attempted)>=12:break
                if not found:break
            remaining=groups(b,net)
            if len(remaining)>1:failed.append({'net':net,'remaining_anchor_groups':len(remaining),'attempted_pairs':len(attempted)})
            if count:print(name,net,'added',count,'groups',len(remaining),flush=True)
        if name=='head':
            # Local candidate fan-out [@jlcThinPcbCapabilities]: 0.10 mm traces,
            # unchanged 0.15 mm clearance. No claim of process/land approval.
            region=[3.3,2.75,10.8,9.25]
            sensor=next(f for f in b.GetFootprints() if f.GetReference()=='U1')
            targets=sorted(sensor.Pads(),key=lambda q:(q.GetNetname(),q.GetNumber()))
            for q in targets:
                net=q.GetNetname()
                if net not in ['GND','/M1_DVDD','/M1_DOVDD','/M1_AVDD']:continue
                b.BuildConnectivity();c=b.GetConnectivity();joined={uid(x) for x in c.GetConnectedItems(q)}|{uid(q)}
                vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==net]
                if any(uid(t) in joined for t in vias):continue
                candidates=sorted(vias,key=lambda t:math.dist(xy(q.GetPosition()),xy(t.GetPosition())))
                for target in candidates[:4]:
                    start,end=xy(q.GetPosition()),xy(target.GetPosition())
                    if not(region[0]<=end[0]<=region[2] and region[1]<=end[1]<=region[3]):continue
                    path=r.path(start,end,net,p.F_Cu,.1,.025,region)
                    if not path:continue
                    length=sum(math.dist(a,z) for a,z in zip(path,path[1:]))
                    if length>4:continue
                    r.track(path,net,p.F_Cu,.1);added.append({'net':net,'layer':'F.Cu','width_mm':.1,'points_mm':path,'length_mm':round(length,4),'from_uuid':uid(q),'to_uuid':uid(target),'purpose':'Local sensor fan-out','region_mm':region})
                    print(name,'fine escape',q.GetNumber(),net,round(length,3),flush=True);break
            project=json.loads((out/'head.kicad_pro').read_text())
            project['board']['design_settings']['rules']['min_track_width']=.1
            (out/'head.kicad_pro').write_text(json.dumps(project,indent=2)+'\n')
        b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out/f'{name}.kicad_pcb'),b)
        report['boards'][name]={'routes':added,'unresolved_searched_nets':failed};print(name,'routes',len(added),flush=True)
    interface=json.loads((out/'interface.json').read_text());interface.update(revision=report['revision'],parent_sha256=parent,status='Additional surface connections; incomplete camera, not for fabrication')
    (out/'interface.json').write_text(json.dumps(interface,indent=2)+'\n')
    (out/'surface-routing.json').write_text(json.dumps(report,indent=2)+'\n')
    print(out,flush=True)

if __name__=='__main__':main()
