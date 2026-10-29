"""Finite-difference copper sheets with filled-via resistors; DC only."""
from pathlib import Path
import gzip,json,math,sys
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import spsolve
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'generated/ov9281-r11-electronics';SPEC=ROOT/'designs/eye-camera-ov9281/electronics/r11'
def main():
    step=float(sys.argv[1]) if len(sys.argv)>1 else .05
    with gzip.open(OUT/f'pdn-grid-{step}.json.gz','rt') as f:data=json.load(f)
    ny=data['ny'];stride=data['nx']*ny;rho=1.72e-8;thickness=np.array([.025,.018,.018,.018,.018,.025])*1e-3;gap=np.array([.02,.02,.05,.02,.02])*1e-3;results={}
    for net,row in data['nets'].items():
        ids={n:i for i,n in enumerate(row['nodes'])};edges=[]
        for n,i in ids.items():
            layer=n//stride
            for d in [1,ny]:
                z=n+d
                if z in ids and z//stride==layer and (d!=1 or z//ny==n//ny):edges.append((i,ids[z],thickness[layer]/rho))
        for a,z,lo,hi in row['vias']:
            assert a in ids and z in ids
            length=gap[lo]+(thickness[lo]+thickness[hi])/2
            edges.append((ids[a],ids[z],math.pi*(.000035)**2/(rho*length)))
        ii=[];jj=[];vv=[]
        for a,z,g in edges:ii.extend([a,z,a,z]);jj.extend([a,z,z,a]);vv.extend([g,g,-g,-g])
        matrix=coo_matrix((vv,(ii,jj)),shape=(len(ids),len(ids))).tocsr()
        _,labels=connected_components(matrix,directed=False);sources=[ids[n] for n in row['source']['nodes']];label=labels[sources[0]]
        assert all(labels[s]==label for s in sources)
        rhs=np.zeros(len(ids));load_ids=[]
        for load in row['loads']:
            nodes=[ids[n] for n in load['nodes']];assert nodes and all(labels[n]==label for n in nodes),(net,load['reference'],'grid disconnected')
            rhs[nodes]+=load['current_A']/len(nodes);load_ids.append(nodes)
        free=np.where((labels==label)&~np.isin(np.arange(len(ids)),sources))[0]
        voltage=np.zeros(len(ids));voltage[free]=spsolve(matrix[free][:,free],rhs[free]);residual=np.max(np.abs((matrix@voltage-rhs)[free]));source_current=-sum((matrix@voltage)[sources]);total=sum(q['current_A'] for q in row['loads'])
        assert residual<1e-6 and abs(source_current-total)<1e-6
        results[net]={'copper_cells':len(ids),'connected_cells':int(sum(labels==label)),'total_load_A':total,'source_current_A':float(source_current),'matrix_residual_A':float(residual),'maximum_load_drop_V':max(float(max(voltage[n])) for n in load_ids),'loads':[{'reference':q['reference'],'current_A':q['current_A'],'max_drop_V':float(max(voltage[n]))} for q,n in zip(row['loads'],load_ids)]}
        print(net,results[net]['maximum_load_drop_V'],'V drop',flush=True)
    report={'step_mm':step,'rho_ohm_m_assumed':rho,'results':results,'scope':'DC conductor screening from saved native copper. Controller only; 1 A stress loading per rail, not a claim about actual consumption or USB bus-power compliance. Uniform copper thickness, filled solid copper vias and room-temperature resistivity assumed. Excludes return-path drop, device/package resistance, solder, regulator dynamics, heating and decoupling parasitics.'}
    (SPEC/f'pdn-validation-{step}.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
