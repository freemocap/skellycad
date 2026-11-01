"""Planar centerline graph measurements, in mm; no electrical-delay model."""
import heapq
import itertools
import math

EPS = 0.000002

def project(q, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    den = dx*dx+dy*dy
    t = max(0., min(1., ((q[0]-a[0])*dx+(q[1]-a[1])*dy)/den)) if den else 0.
    p = (a[0]+t*dx, a[1]+t*dy)
    return t, p, math.dist(q, p)

def measure(segments, vias, ports):
    """Shortest centerline path between two exact port centers.

    Split T junctions, collinear overlaps and crossings. Zero-cost via edges
    connect layers; their barrel length and all package delays are excluded.
    Refuse disconnected graphs instead of substituting total copper length.
    """
    cuts = [[(0., tuple(s['a'])), (1., tuple(s['b']))] for s in segments]
    for i, s in enumerate(segments):
        points = [p['xy'] for p in ports if p['layer'] == s['layer']]
        points += [v['xy'] for v in vias if s['layer'] in v['layers']]
        for j, t in enumerate(segments):
            if i == j or s['layer'] != t['layer']:continue
            points += [t['a'], t['b']]
            ax, ay = s['a']; bx, by = s['b']; cx, cy = t['a']; dx, dy = t['b']
            rx, ry = bx-ax, by-ay; sx, sy = dx-cx, dy-cy
            den = rx*sy-ry*sx
            if abs(den)>1e-14:
                u=((cx-ax)*sy-(cy-ay)*sx)/den
                w=((cx-ax)*ry-(cy-ay)*rx)/den
                if 0<=u<=1 and 0<=w<=1:points.append((ax+u*rx,ay+u*ry))
        for q in points:
            u, p, distance = project(q,s['a'],s['b'])
            if distance<=EPS:cuts[i].append((u,p))
    graph={}
    def node(layer,xy):return (layer,round(xy[0],6),round(xy[1],6))
    def edge(a,b,length,meta):
        if a==b:return
        graph.setdefault(a,[]).append((b,length,meta));graph.setdefault(b,[]).append((a,length,meta))
    for s, points in zip(segments,cuts):
        points=sorted({round(u,12):q for u,q in points}.items())
        for (_,a),(_,b) in zip(points,points[1:]):
            edge(node(s['layer'],a),node(s['layer'],b),math.dist(a,b),{'kind':'trace','uuid':s['uuid'],'layer':s['layer'],'a':a,'b':b})
    for via in vias:
        for l1,l2 in itertools.combinations(via['layers'],2):
            edge(node(l1,via['xy']),node(l2,via['xy']),0.,{'kind':'via','uuid':via['uuid'],'xy':via['xy']})
    start,end=[node(q['layer'],q['xy']) for q in ports]
    queue=[(0.,start)];cost={start:0.};parents={}
    while queue:
        d,n=heapq.heappop(queue)
        if d!=cost[n]:continue
        if n==end:break
        for other,length,meta in graph.get(n,[]):
            nd=d+length
            if nd+1e-12<cost.get(other,float('inf')):
                cost[other]=nd;parents[other]=(n,meta);heapq.heappush(queue,(nd,other))
    if end not in cost:raise ValueError(f'Centerline graph disconnected: {ports}')
    path=[];n=end
    while n!=start:
        prior,meta=parents[n];path.append({**meta,'from':prior,'to':n});n=prior
    path.reverse();by_layer={}
    for item in path:
        if item['kind']=='trace':by_layer[item['layer']]=by_layer.get(item['layer'],0)+math.dist(item['from'][1:],item['to'][1:])
    return {'path_length_mm':cost[end],'length_by_layer_mm':by_layer,'path':path,'path_via_uuids':sorted({x['uuid'] for x in path if x['kind']=='via'}),'inventory_length_mm':sum(math.dist(s['a'],s['b']) for s in segments)}
