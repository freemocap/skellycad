"""Compare KiCad's exported connectivity with every intended component pin."""
from pathlib import Path
import json,xml.etree.ElementTree as E,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def check(name):
    folder=ROOT/'generated/three-board-e01'/name
    parts=json.loads((HERE/(name+'-components.json')).read_text(encoding='utf-8'))
    tree=E.parse(folder/'netlist.xml');nodes={}
    for net in tree.findall('.//nets/net'):
        for n in net.findall('node'):nodes[(n.attrib['ref'],n.attrib['pin'])]=net.attrib['name'].lstrip('/')
    errors=[];count=0
    actual={x.attrib['ref'] for x in tree.findall('.//components/comp')}
    for ref,p in parts.items():
        if ref not in actual:errors.append([ref,'missing component'])
        for pin,net in p['pin_nets'].items():
            if net is not None:
                count+=1
                if nodes.get((ref,pin))!=net:errors.append([ref,pin,net,nodes.get((ref,pin))])
    erc=json.loads((folder/'erc.json').read_text(encoding='utf-8'))
    violations=[v for s in erc['sheets'] for v in s['violations']]
    result={'components':len(parts),'connected_pins_checked':count,'connectivity_errors':errors,'erc_violations':len(violations),'scope':'Native schematic parsing and intended-pin net equivalence; not hardware validation.'}
    (folder/'native-check.json').write_text(json.dumps(result,indent=2)+'\n')
    assert not errors,errors
    print(name,result)
    return result
if __name__=='__main__':check(sys.argv[1])
