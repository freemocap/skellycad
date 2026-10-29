"""Regional, adjacent-microvia-only routing helpers for the C construction."""
import collections,heapq,itertools,math
from functools import lru_cache
import pcbnew as p
from place_r11 import LAYERS,CTRL,HX,v,xy
from routing_spatial import NearestPoints

SIGNAL=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.In4_Cu,p.B_Cu]
POLYGON=[(0,0),(27,0),(28,3),(HX,3),(HX+1,0),(HX+14,0),(HX+14,14),(HX+1,14),(HX,11),(28,11),(27,14),(0,14)]


def uid(q):return q.m_Uuid.AsString()
def dist_segment(q,a,z):
    dx,dy=z[0]-a[0],z[1]-a[1];d=dx*dx+dy*dy
    t=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/d)) if d else 0
    return math.hypot(q[0]-a[0]-t*dx,q[1]-a[1]-t*dy)


@lru_cache(maxsize=500000)
def inside(x,y,margin):
    if not (margin<=x<=HX+14-margin and margin<=y<=14-margin):return False
    if 28<x<HX and not 3+margin<=y<=11-margin:return False
    # Four sloping transition boundaries; conservative normal clearance.
    for a,z in [(POLYGON[1],POLYGON[2]),(POLYGON[3],POLYGON[4]),(POLYGON[7],POLYGON[8]),(POLYGON[9],POLYGON[10])]:
        if dist_segment((x,y),a,z)<margin-1e-8:return False
    if 27<x<28 and not 3*(x-27)<=y<=14-3*(x-27):return False
    if HX<x<HX+1 and not 3-3*(x-HX)<=y<=11+3*(x-HX):return False
    return True


def legal_layer(x,layer):return not 28<x<HX or layer in (p.In2_Cu,p.In3_Cu)
def launch(x,y):return (18.1<x<20.1 and 2.7<y<6.9) or (HX+3.5<x<HX+10.5 and 4.5<y<10.1) or (3<x<8.3 and .5<y<8.8)


def track(b,points,layer,net,width=.075,locked=False):
    code=b.FindNet(net).GetNetCode() if isinstance(net,str) else net
    result=[]
    for a,z in zip(points,points[1:]):
        if math.dist(a,z)<1e-7:continue
        t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetLayer(layer);t.SetWidth(p.FromMM(width));t.SetNetCode(code);t.SetLocked(locked);b.Add(t);result.append(t)
    return result


def via_stack(b,point,start,end,net,locked=False):
    code=b.FindNet(net).GetNetCode() if isinstance(net,str) else net
    lo,hi=sorted((LAYERS.index(start),LAYERS.index(end)));added=[]
    for i in range(lo,hi):
        if any(isinstance(t,p.PCB_VIA) and t.GetNetCode()==code and xy(t.GetPosition())==tuple(point) and set((t.TopLayer(),t.BottomLayer()))==set(LAYERS[i:i+2]) for t in b.GetTracks()):continue
        t=p.PCB_VIA(b);t.SetPosition(v(*point));t.SetWidth(p.FromMM(.25));t.SetDrill(p.FromMM(.07))
        t.SetViaType(p.VIATYPE_MICROVIA if i in (0,4) else p.VIATYPE_BURIED);t.SetLayerPair(LAYERS[i],LAYERS[i+1]);t.SetNetCode(code);t.SetLocked(locked);b.Add(t);added.append(t)
    return added


def groups(b,net):
    b.BuildConnectivity();c=b.GetConnectivity();items={uid(q):q for q in list(b.GetPads())+list(b.GetTracks()) if q.GetNetname()==net}
    pending=set(items);result=[]
    while pending:
        key=min(pending);q=items[key]
        connected=[items.get(uid(x),x) for x in c.GetConnectedItems(q)]+[q]
        ids={uid(x) for x in connected};pending-=ids;result.append(connected)
    return sorted(result,key=len)


def ends(items,layer):
    points={}
    for q in items:
        if not isinstance(q,(p.PAD,p.PCB_TRACK)) or not q.IsOnLayer(layer):continue
        for point in [q.GetPosition()] if isinstance(q,(p.PAD,p.PCB_VIA)) else [q.GetStart(),q.GetEnd()]:points[point.x,point.y]=point
    return list(points.values())


class Clearance:
    def __init__(self,b,net,width=.075,protect=True):
        self.b=b;self.net=net;self.width=width;self.bins=collections.defaultdict(list);self.protected=collections.defaultdict(list)
        for item in list(b.GetPads())+list(b.GetTracks()):
            if item.GetNetname()==net:continue
            for layer in LAYERS:
                if not item.IsOnLayer(layer):continue
                shape=item.GetEffectiveShape(layer);bb=shape.BBox();a,z=xy(bb.GetOrigin()),xy(bb.GetEnd())
                for i in range(math.floor(a[0]-.5),math.floor(z[0]+.5)+1):
                    for j in range(math.floor(a[1]-.5),math.floor(z[1]+.5)+1):self.bins[layer,i,j].append(shape)
            if protect and isinstance(item,p.PCB_TRACK) and not isinstance(item,p.PCB_VIA) and item.IsLocked():
                targets=([p.F_Cu,p.In1_Cu,p.In2_Cu] if item.GetNetname().startswith('/CAM_L_') else
                         [p.F_Cu,p.In1_Cu,p.In2_Cu] if item.GetNetname() in ('/USB_DP_CHIP','/USB_DM_CHIP') else [])
                shape=item.GetEffectiveShape(item.GetLayer());bb=shape.BBox();a,z=xy(bb.GetOrigin()),xy(bb.GetEnd())
                for layer in targets:
                    for i in range(math.floor(a[0]-.6),math.floor(z[0]+.6)+1):
                        for j in range(math.floor(a[1]-.6),math.floor(z[1]+.6)+1):self.protected[layer,i,j].append(shape)

    def segment(self,a,z,layer):
        aa,zz=xy(a),xy(z)
        if not inside(*aa,.301+self.width/2) or not inside(*zz,.301+self.width/2):return False
        if not legal_layer(aa[0],layer) or not legal_layer(zz[0],layer):return False
        # A long line must also remain inside the narrow neck and transition.
        for k in range(1,math.ceil(math.dist(aa,zz)/.2)):
            t=k/math.ceil(math.dist(aa,zz)/.2);q=(aa[0]+t*(zz[0]-aa[0]),aa[1]+t*(zz[1]-aa[1]))
            if not inside(*q,.301+self.width/2) or not legal_layer(q[0],layer):return False
        shape=p.SHAPE_SEGMENT(a,z,p.FromMM(self.width));seen=set();protected=set()
        for i in range(math.floor(min(aa[0],zz[0])),math.floor(max(aa[0],zz[0]))+1):
            for j in range(math.floor(min(aa[1],zz[1])),math.floor(max(aa[1],zz[1]))+1):
                for s in self.bins[layer,i,j]:
                    if id(s) not in seen:
                        seen.add(id(s))
                        if s.Collide(shape,76000):return False
                if launch(*aa) and launch(*zz):continue
                for s in self.protected[layer,i,j]:
                    if id(s) not in protected:
                        protected.add(id(s))
                        if s.Collide(shape,300000):return False
        return True

    @lru_cache(maxsize=200000)
    def via(self,x,y,start,end):
        if not inside(x,y,.427) or (27<x<HX+1):return False
        lo,hi=sorted((LAYERS.index(start),LAYERS.index(end)))
        circle=p.SHAPE_CIRCLE(v(x,y),125000)
        for layer in LAYERS[lo:hi+1]:
            if any(s.Collide(circle,76000) for s in self.bins[layer,math.floor(x),math.floor(y)]):return False
            if not launch(x,y) and any(s.Collide(circle,300000) for s in self.protected[layer,math.floor(x),math.floor(y)]):return False
        return True


def join(b,net,width=.075,max_nodes=200000,protect=True):
    gs=groups(b,net)
    if len(gs)<2:return None
    # Start from the smallest island; orphan flex tracks are valid islands.
    start=gs[0];targets={l:ends([q for group in gs[1:] for q in group],l) for l in SIGNAL}
    if not any(targets.values()):return {'result':'no accessible targets'}
    nearest=NearestPoints([xy(q) for rows in targets.values() for q in rows]);target_bins=collections.defaultdict(list)
    for l,points in targets.items():
        for q in points:
            x,y=xy(q);target_bins[l,math.floor(x),math.floor(y)].append(q)
    clear=Clearance(b,net,width,protect);step=.05
    def point(node):return v(node[0]*step,node[1]*step)
    @lru_cache(maxsize=300000)
    def h(node):return nearest.distance(node[0]*step,node[1]*step)
    roots={};cost={};parent={};counter=itertools.count();queue=[]
    for layer in SIGNAL:
        for q in ends(start,layer):
            x,y=xy(q);ix,iy=round(x/step),round(y/step)
            for dx,dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]:
                node=(ix+dx,iy+dy,layer)
                if clear.segment(q,point(node),layer):
                    d=math.dist(xy(q),xy(point(node)))
                    if d<cost.get(node,float('inf')):cost[node]=d;roots[node]=q
    for n,c in cost.items():heapq.heappush(queue,(c+1.08*h(n),next(counter),n))
    seen=set();finish=None;goal=None
    while queue and len(seen)<max_nodes:
        _,_,node=heapq.heappop(queue)
        if node in seen:continue
        seen.add(node);pt=point(node);x,y=xy(pt);layer=node[2];cx,cy=math.floor(x),math.floor(y)
        for target in (q for i in [-1,0,1] for j in [-1,0,1] for q in target_bins[layer,cx+i,cy+j]):
            if math.dist((x,y),xy(target))<.4 and clear.segment(pt,target,layer):finish=node;goal=target;break
        if finish is not None:break
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
            other=(node[0]+dx,node[1]+dy,layer);value=cost[node]+step*math.hypot(dx,dy)
            if other not in seen and value<cost.get(other,float('inf')) and clear.segment(pt,point(other),layer):
                cost[other]=value;parent[other]=node;heapq.heappush(queue,(value+1.08*h(other),next(counter),other))
        for nextlayer in SIGNAL:
            if nextlayer==layer:continue
            other=(node[0],node[1],nextlayer);span=abs(LAYERS.index(nextlayer)-LAYERS.index(layer));value=cost[node]+.6+.15*span
            if other not in seen and value<cost.get(other,float('inf')) and clear.via(x,y,layer,nextlayer):
                cost[other]=value;parent[other]=node;heapq.heappush(queue,(value+1.08*h(other),next(counter),other))
    if finish is None:return {'result':'no path','visited':len(seen),'islands':len(gs),'width_mm':width}
    nodes=[finish]
    while nodes[-1] in parent:nodes.append(parent[nodes[-1]])
    nodes.reverse();layer=nodes[0][2];current=[roots[nodes[0]],point(nodes[0])];runs=[];vias=[]
    for node in nodes[1:]:
        if node[2]!=layer:
            runs.append((layer,current));pos=xy(point(node));via_stack(b,pos,layer,node[2],net);vias.append({'xy_mm':pos,'from':b.GetLayerName(layer),'to':b.GetLayerName(node[2])});layer=node[2];current=[point(node)]
        else:current.append(point(node))
    current.append(goal);runs.append((layer,current));paths=[]
    for layer,points in runs:
        simple=[points[0]];i=0
        while i<len(points)-1:
            # Bounded lookahead avoids quadratic work on a long neck trace.
            j=next(j for j in range(min(len(points)-1,i+80),i,-1) if clear.segment(points[i],points[j],layer));simple.append(points[j]);i=j
        coords=[xy(q) for q in simple];track(b,coords,layer,net,width);paths.append({'layer':b.GetLayerName(layer),'points_mm':coords})
    return {'result':'routed','visited':len(seen),'width_mm':width,'vias':vias,'paths':paths}
