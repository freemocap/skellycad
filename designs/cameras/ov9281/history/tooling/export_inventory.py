"""Export a review BOM and placement inventory from checked native boards.

No part availability, electrical compatibility or assembly qualification implied.
Run with KiCad Python. Does not modify board files.
"""
from pathlib import Path
import argparse, hashlib, json, xml.etree.ElementTree as ET
import pcbnew as p

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True);a=ap.parse_args()
    folder=a.directory.resolve();validation=json.loads((folder/'validation.json').read_text())
    for name,digest in validation['sha256'].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest,name
    xml=ET.parse(folder/'source-netlist.xml')
    components={c.get('ref'):c for c in xml.findall('.//components/comp')}
    items=[]
    for board in ['controller','head','flex-study']:
        b=p.LoadBoard(str(folder/(board+'.kicad_pcb')))
        for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
            c=components.get(f.GetReference()) if board!='flex-study' else None
            fields={v.get('name'):v.text for v in c.findall('./fields/field')} if c is not None else {}
            items.append({'board':board,'reference':f.GetReference(),'value':f.GetValue(),
                'footprint':str(f.GetFPID().GetLibItemName()),'mpn_field':fields.get('MPN'),
                'manufacturer_field':fields.get('Manufacturer'),'dnp':bool(f.GetAttributes() & p.FP_DNP),
                'excluded_from_bom':bool(f.GetAttributes() & p.FP_EXCLUDE_FROM_BOM),
                'position_mm':[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)],
                'rotation_deg':f.GetOrientationDegrees(),'side':b.GetLayerName(f.GetLayer())})
    (folder/'inventory.json').write_text(json.dumps({'revision':validation['revision'],
        'status':'Native review inventory; not an approved procurement BOM',
        'missing_mpn_field_count':sum(not x['mpn_field'] for x in items),
        'note':'Some values contain candidate part numbers without structured MPN fields. Flex contacts and solder lands are board geometry, not separately purchased parts.',
        'items':items},indent=2)+'\n')
    print('Exported',len(items),'native footprint records')

if __name__=='__main__':main()
