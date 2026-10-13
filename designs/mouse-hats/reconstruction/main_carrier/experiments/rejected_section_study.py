"""Evaluate a sectional reconstruction of the planar carrier; no GUI writes."""
from pathlib import Path
import json
import FreeCAD as App
import Part
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'generated/mouse-hats/reconstruction/main-carrier'
OUT.mkdir(parents=True,exist_ok=True)
s=Part.read(str(ROOT/'generated/mouse-hats/inspection/carrier-source.brep'))
holes=[Part.makeCylinder(2,s.Faces[13].CenterOfMass.x-s.Faces[14].CenterOfMass.x,App.Vector(3.70677424482635,11.9423591269588,z),App.Vector(1,0,0)) for z in [-12.9033786820894,12.0966213179106]]
s=s.multiFuse(holes).removeSplitter()
print('Filled',s.isValid(),len(s.Faces),flush=True)
def plane(f):
    n=f.normalAt(0,0);return n,n.dot(f.CenterOfMass)
planes=[plane(f) for f in s.Faces if isinstance(f.Surface,Part.Plane)]
def intersect(a,b,z):
    n,d=a;m,e=b;k=App.Vector(0,0,1)
    return (m.cross(k)*d+k.cross(n)*e+n.cross(m)*z)/n.dot(m.cross(k))
levels=[]
for z in sorted(v.Point.z for v in s.Vertexes):
    if not levels or z-levels[-1]>1e-4:levels.append(z)
items=[];shapes=[]
for number,(lo,hi) in enumerate(zip(levels,levels[1:])):
    mid=(lo+hi)/2
    sec=s.section(Part.makePlane(100,100,App.Vector(-30,-30,mid)))
    remaining=[e for e in sec.Edges if e.Length>1e-4]
    loops=[]
    while remaining:
        e=remaining.pop(0);pts=[e.Vertexes[0].Point,e.Vertexes[-1].Point]
        while pts[-1].distanceToPoint(pts[0])>0.001:
            candidates=[(pts[-1].distanceToPoint(v.Point),i,j) for i,e in enumerate(remaining) for j,v in enumerate(e.Vertexes)]
            distance,ii,jj=min(candidates)
            assert distance<0.001,(number,distance)
            e=remaining.pop(ii)
            pts.append(e.Vertexes[1-jj].Point)
        loops.append(pts[:-1])
    for j,pts in enumerate(loops):
        sides=[]
        for p,q in zip(pts,pts[1:]+pts[:1]):
            candidates=sorted([pl for pl in planes if abs(pl[0].z)<1-1e-9 and abs(pl[0].dot(p)-pl[1])<0.001 and abs(pl[0].dot(q)-pl[1])<0.001],key=lambda pl:abs(pl[0].dot(p)-pl[1])+abs(pl[0].dot(q)-pl[1]))
            assert candidates,(number,list(p),list(q))
            sides.append(candidates[0])
        sides=[pl for i,pl in enumerate(sides) if abs(sides[i-1][0].cross(pl[0]).z)>1e-9]
        profiles=[]
        inset=min(0.001,(hi-lo)*0.1)
        for z in [lo+inset,hi-inset]:
            pp=[intersect(sides[i-1],sides[i],z) for i in range(len(sides))]
            clean=[]
            for p in pp:
                if not clean or p.distanceToPoint(clean[-1])>1e-6:clean.append(p)
            if clean[0].distanceToPoint(clean[-1])<1e-6:clean.pop()
            profiles.append(clean)
        try:
            wires=[Part.makePolygon(p+[p[0]]) for p in profiles]
            sh=Part.makeLoft(wires,True,True)
            sh.check(True)
            cap0=Part.Face(wires[0]).extrude(App.Vector(0,0,-inset-0.00001))
            cap1=Part.Face(wires[1]).extrude(App.Vector(0,0,inset+0.00001))
            shapes.append(sh.fuse(cap0).fuse(cap1).removeSplitter())
            items.append(dict(name=f'Section{number:02d}_{j}',profiles_mm=[[list(v) for v in p] for p in profiles],end_extension_mm=inset+0.00001))
        except Exception as e:
            print('FAIL',number,lo,hi,[len(p) for p in profiles],str(e),flush=True)
            raise
print('LOFTS',len(shapes),flush=True)
r=shapes[0].multiFuse(shapes[1:]).removeSplitter()
r=r.cut(Part.makeCompound(holes)).removeSplitter()
r.exportBrep(str(OUT/'section-candidate.brep'))
print('RESULT',r.isValid(),len(r.Solids),r.Volume,flush=True)
original=Part.read(str(ROOT/'generated/mouse-hats/inspection/carrier-source.brep'))
print('DIFF',original.cut(r).Volume,r.cut(original).Volume,flush=True)
(HERE/'section_profiles.json').write_text(json.dumps(dict(units='mm',features=items),indent=2)+'\n')
