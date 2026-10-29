"""Check real KiCad netlist, critical interface mapping and inherited topology."""
from pathlib import Path
import subprocess
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
OUT = ROOT/'electronics/r02'
GEN = REPO/'generated/ov9281-r02-validation'
CLI = Path('C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe')
GEN.mkdir(exist_ok=True)
for name,path in [('current',OUT/'camera.kicad_sch'),('source',ROOT/'reference/antmicro/ov9281-dual-camera-board.kicad_sch')]:
    subprocess.run([str(CLI),'sch','export','netlist','--format','kicadxml','--output',str(GEN/f'{name}.xml'),str(path)],check=True)
current=ET.parse(GEN/'current.xml');source=ET.parse(GEN/'source.xml')
nets={}
for net in current.findall('.//nets/net'):
    for node in net.findall('node'):
        nets[(node.get('ref'),node.get('pin'))]=net.get('name')
def same(*pins):
    found=[nets[p] for p in pins]
    assert len(set(found))==1,(pins,found)
# Independently specified physical pin mapping, not generated expected labels.
for sensor,p4 in [('H3','42'),('G3','43'),('G4','44'),('H4','45'),('F5','46'),('G5','47')]:
    same(('U1',sensor),('U101',p4))
assert len({nets[('U101',n)] for n in ['42','43','44','45','46','47']})==6
same(('U101','26'),('U101','54'),('U101','76'),('U101','91'),('L101','2'))
same(('U101','73'),('U101','41'))
same(('U101','69'),('J103','2'));same(('U101','70'),('J103','3'))
same(('U1','A4'),('Q102','2'));same(('U1','E4'),('Q101','2'))
same(('Q101','1'),('U5','5'));same(('Q102','1'),('U5','5'))
same(('U1','A5'),('Q103','3'))
assert nets[('U101','7')]!=nets[('U1','E4')]
assert nets[('U101','8')]!=nets[('U1','A4')]
assert len({nets[('J101','1')],nets[('J101','4')],nets[('U101','21')],nets[('U101','26')],nets[('U101','41')]})==5
original_refs={c.get('ref') for c in source.findall('.//components/comp')}
refs={c.get('ref') for c in current.findall('.//components/comp')}&original_refs
def groups(tree):
    return {frozenset((n.get('ref'),n.get('pin')) for n in net.findall('node') if n.get('ref') in refs)
            for net in tree.findall('.//nets/net')}-{frozenset()}
assert groups(source)==groups(current),'Inherited component connectivity changed'
expected=json.loads((OUT/'expected-connections.json').read_text())
expected={k:v for k,v in expected.items() if not k.startswith('#')}
for pin,name in expected.items():
    ref,num=pin.split('.')
    assert nets[(ref,num)].lstrip('/')==name,(pin,name,nets[(ref,num)])
subprocess.run([str(CLI),'sch','erc','--exit-code-violations','--output',str(GEN/'erc.rpt'),str(OUT/'camera.kicad_sch')],check=True)
report={'status':'Schematic checks passed; not hardware qualification','components':len(current.findall('.//components/comp')),
        'controller_and_support_pins_checked':len(expected),'retained_reference_components':len(refs),
        'reference_topology_match':True,'critical_mipi_and_power_checks':True,'erc_errors':0,'erc_warnings':0,
        'limits':['No PCB routing or DRC','No power/thermal or signal-integrity simulation','No firmware or physical image test',
                  'Crystal, inductors, flex connector and LED drive not release-qualified',
                  'KiCad default disabled ERC checks retained; see erc.rpt']}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
