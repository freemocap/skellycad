"""Rasterize saved native copper for a resistive DC screening model."""
from pathlib import Path
import argparse,gzip,json,math
import pcbnew as p
from routing_r11 import LAYERS,xy,v
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'generated/ov9281-r11-electronics'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--step',type=float,default=.05);args=ap.parse_args();step=args.step;nx=round(28/step)+1;ny=round(14/step)+1;stride=nx*ny
    b=p.LoadBoard(str(OUT/'camera.kicad_pcb'));pads={(q.GetParentFootprint().GetReference(),q.GetNumber()):q for q in b.GetPads()};result={}
    def key(l,x,y):return l*stride+x*ny+y
    def raster(shape):
        bb=shape.BBox();x0,y0=xy(bb.GetOrigin());x1,y1=xy(bb.GetEnd())
        return [(i,j) for i in range(max(0,math.floor(x0/step)),min(nx-1,math.ceil(x1/step))+1) for j in range(max(0,math.floor(y0/step)),min(ny-1,math.ceil(y1/step))+1) if shape.Collide(v(i*step,j*step),0)]
    for net,source,loads in [('/P4_VDD_HP',('L101','2'),[(('U101',n),.25) for n in ['26','54','76','91']]),('+3V3',('L102','2'),[(('U103','3'),.5),(('U5','4'),.05),(('U6','4'),.15),(('U7','4'),.05)]+[(('U101',q.GetNumber()),.25/sum(t.GetNetname()=='+3V3' for t in pads[('U101','9')].GetParentFootprint().Pads())) for q in pads[('U101','9')].GetParentFootprint().Pads() if q.GetNetname()=='+3V3'])]:
        occupied=set();vias=[]
        for q in list(b.GetPads())+list(b.GetTracks()):
            if q.GetNetname()!=net or xy(q.GetPosition())[0]>28:continue
            for l,layer in enumerate(LAYERS):
                if q.IsOnLayer(layer):occupied.update(key(l,i,j) for i,j in raster(q.GetEffectiveShape(layer)))
            if isinstance(q,p.PCB_VIA):
                x,y=xy(q.GetPosition());a,z=sorted([LAYERS.index(q.TopLayer()),LAYERS.index(q.BottomLayer())]);vias.append([key(a,round(x/step),round(y/step)),key(z,round(x/step),round(y/step)),a,z])
        for z in b.Zones():
            if z.GetNetname()!=net:continue
            l=LAYERS.index(z.GetLayer());poly=z.GetFilledPolysList(z.GetLayer())
            for i in range(nx):
                for j in range(ny):
                    if poly.Contains(v(i*step,j*step)):occupied.add(key(l,i,j))
        def cells(ref):
            pad=pads[ref];l=next(i for i,layer in enumerate(LAYERS) if pad.IsOnLayer(layer));return [key(l,i,j) for i,j in raster(pad.GetEffectiveShape(LAYERS[l]))]
        result[net]={'nodes':sorted(occupied),'vias':vias,'source':{'reference':source,'nodes':cells(source)},'loads':[{'reference':ref,'current_A':amp,'nodes':cells(ref)} for ref,amp in loads]}
        print(net,len(occupied),'cells',flush=True)
    with gzip.open(OUT/f'pdn-grid-{step}.json.gz','wt',encoding='utf-8') as f:json.dump({'step_mm':step,'nx':nx,'ny':ny,'layers':LAYERS,'nets':result},f)
if __name__=='__main__':main()
