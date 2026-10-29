"""Validate physical endpoint mapping and equal route lengths, without SI claims."""
import sys
import json
import hashlib
from pathlib import Path
import pcbnew as p

path=Path(sys.argv[1])
board=p.LoadBoard(str(path))
mapping=json.loads((Path(__file__).parent/'electronics/r01/interface.json').read_text())['pins']
connectors={fp.GetReference():fp for fp in board.GetFootprints() if fp.GetReference() in ['J1','J2']}
assert set(connectors)=={'J1','J2'}
for fp in connectors.values():
    pads={pad.GetNumber():pad for pad in fp.Pads() if pad.GetNumber() in mapping}
    assert set(pads)==set(mapping)
    assert all(pads[num].GetNetname()=='/'+net for num,net in mapping.items())
tracks=[t for t in board.GetTracks() if type(t)==p.PCB_TRACK]
assert len(tracks)==15
for num in mapping:
    ends=[next(pad.GetPosition() for pad in connectors[ref].Pads() if pad.GetNumber()==num) for ref in ['J1','J2']]
    matches=[t for t in tracks if t.GetStart()==ends[0] and t.GetEnd()==ends[1]]
    assert len(matches)==1, num
    assert abs(p.ToMM(matches[0].GetLength())-20)<1e-6
report={'board_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'mapped_pins':30,'routed_connections':15,'each_route_mm':20,
        'impedance_validated':False,'physical_cable_mapping_validated':False}
print(json.dumps(report,indent=2))
