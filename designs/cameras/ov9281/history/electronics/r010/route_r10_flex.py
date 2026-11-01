"""Create paired R10 flex routes, retaining the original contacts and pin map."""
import json, math, shutil, subprocess, sys
from pathlib import Path
import pcbnew as p
from route_r10_head import offset
from route_head_dovdd import v, xy
from extract_head import children

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'generated/ov9281-r10-controller-16'
OUT=ROOT/'generated/ov9281-r10-flex-03'

def center(y, amplitude):
    if amplitude<1e-12:return [(2.75,y),(32.55,y)]
    points=[(2.75,y),(3,y)]
    points += [(3+i*.025,y-amplitude*(1-math.cos(math.pi*i/60))/4) for i in range(1,61)]
    points += [(4.5+i*.025,y-amplitude*math.cos(2*math.pi*i/104)/2) for i in range(1,1041)]
    points += [(30.5+i*.025,y-amplitude*(1+math.cos(math.pi*i/60))/4) for i in range(1,61)]
    return points+[(32.55,y)]

def conductor(y, amplitude, polarity):
    sign=1 if polarity=='N' else -1
    q=offset(center(y,amplitude),sign*.175)
    py=y-sign*.25
    return [(.75,py),(1.5,py)]+q+[(33.8,py),(34.55,py)]

def length(points):return sum(math.dist(a,b) for a,b in zip(points,points[1:]))

def stackup():
    return '''(stackup
      (layer "F.Mask" (type "Top Solder Mask") (thickness 0.0275) (material "PI and adhesive coverlay") (epsilon_r 3.4))
      (layer "F.Cu" (type "copper") (thickness 0.024))
      (layer "dielectric 1" (type "core") (thickness 0.065) (material "PI 25um plus adhesive 2x20um") (epsilon_r 3.4) (loss_tangent 0.02))
      (layer "B.Cu" (type "copper") (thickness 0.024))
      (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.0275) (material "PI and adhesive coverlay") (epsilon_r 3.4))
      (copper_finish "ENIG") (dielectric_constraints yes))'''

def main():
    assert not OUT.exists();shutil.copytree(SRC,OUT)
    # Apply the approved R10 0.10 mm construction rules instead of R09's
    # provisional 0.15 mm rules; retain the existing hole and via minima.
    project=OUT/'flex-study.kicad_pro';settings=json.loads(project.read_text())
    rules=settings['board']['design_settings']['rules'];rules['min_clearance']=.1;rules['min_track_width']=.1
    for cls in settings['net_settings']['classes']:cls['clearance']=.1;cls['track_width']=.1
    project.write_text(json.dumps(settings,indent=2)+'\n')
    b=p.LoadBoard(str(OUT/'flex-study.kicad_pcb'));held=[]
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA):continue
        if t.GetNetname().startswith('/CAM_L_') or (t.GetNetname()=='GND' and any(abs(xy(t.GetStart())[1]-y)<1e-5 for y in [.5,2,3.5])):
            held.append(t);b.Remove(t)
    def route(net,points,width=.1):
        code=next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()==net)
        for a,z in zip(points,points[1:]):
            if math.dist(a,z)<1e-7:continue
            t=p.PCB_TRACK(b);t.SetNetCode(code);t.SetLayer(p.B_Cu);t.SetWidth(p.FromMM(width));t.SetStart(v(*a));t.SetEnd(v(*z));t.SetLocked(True);b.Add(t)
    rigid={key:0 for key in ['D0','CLK','D1']}
    for board in ['head','controller']:
        r=json.loads((SRC/(board+'-routing-validation.json')).read_text())
        for pair in r['pairs']:rigid[pair['pair']]+=(pair['p_mm']+pair['n_mm'])/2
    target=rigid['D1']+length(conductor(4.25,0,'P'));rows=[]
    for pair,y in [('D0',1.25),('CLK',2.75),('D1',4.25)]:
        low,high=0.,.9
        for _ in range(45):
            a=(low+high)/2
            if rigid[pair]+sum(length(conductor(y,a,s)) for s in ['P','N'])/2<target:low=a
            else:high=a
        a=(low+high)/2 if pair!='D1' else 0
        for s in ['P','N']:route('/CAM_L_'+pair+'_'+s,conductor(y,a,s))
        rows.append({'pair':pair,'amplitude_mm':a,'period_mm':2.6,'cycles':10,'flex_mean_mm':sum(length(conductor(y,a,s)) for s in ['P','N'])/2,'rigid_mean_mm':rigid[pair],'target_full_planar_mean_mm':target})
        if pair=='CLK':
            for sign,gy in [(1,2),(-1,3.5)]:
                guard=offset(center(y,a),sign*.376)
                route('GND',[(.75,gy),(2,gy)]+guard+[(33.3,gy),(34.55,gy)])
    route('GND',[(.75,.5),(2,.5),(2.75,.325),(32.55,.325),(33.3,.5),(34.55,.5)],.15)
    for z in b.Zones():held.append(z);b.Remove(z)
    z=p.ZONE(b);z.SetLayer(p.F_Cu);z.SetNetCode(next(q.GetNetCode() for q in b.GetPads() if q.GetNetname()=='GND'));z.SetLocalClearance(p.FromMM(.15));z.SetMinThickness(p.FromMM(.1));z.SetPadConnection(p.ZONE_CONNECTION_FULL)
    poly=z.Outline();poly.NewOutline()
    for xx,yy in [(.25,.25),(35.05,.25),(35.05,12.25),(.25,12.25)]:poly.Append(p.FromMM(xx),p.FromMM(yy))
    b.Add(z);b.GetDesignSettings().SetBoardThickness(p.FromMM(.168));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());path=OUT/'flex-study.kicad_pcb';p.SaveBoard(str(path),b)
    text=path.read_text();setup=next(s for s in children(text) if s.startswith('(setup'));old=next(s for s in children(setup) if s.startswith('(stackup'));path.write_text(text.replace(old,stackup(),1))
    (OUT/'flex-route-construction.json').write_text(json.dumps({'pairs':rows,'body_thickness_mm':.168,'contact_side':'B.Cu','stiffened_end_regions_x_mm':[[0,2.5],[32.8,35.3]],'ground_plane_inset_mm':.25,'scope':'Planar matching; connector/package delay and assembled flex remain unqualified'},indent=2)+'\n')
    cli=Path(sys.executable).with_name('kicad-cli.exe');report=OUT/'checks/flex-study-drc.json';subprocess.run([str(cli),'pcb','drc','--format','json','--output',str(report),str(path)],capture_output=True,check=True)
    d=json.loads(report.read_text());print(json.dumps({'pairs':rows,'violations':len(d['violations']),'unconnected':len(d['unconnected_items'])},indent=2))

if __name__=='__main__':main()
