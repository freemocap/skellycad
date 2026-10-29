"""Build R02: a routed teaching coupon, not a validated MIPI product.

Use KiCad's bundled Python. Footprint: [@molex200528Series; @kicadFootprintsSource].
R01 remains immutable. Trace dimensions are teaching choices, not impedance rules.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import pcbnew as p
from build import uid

HERE = Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
OUT=parser.parse_args().output.resolve()
if OUT.exists():
    raise SystemExit('Use a new output directory; preserve reviewed revisions.')
OUT.mkdir(parents=True)
KICAD = Path(r'C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/share/kicad')
NAME = 'Molex_200528-0150_1x15-1MP_P1.00mm_Horizontal'
LIB = KICAD / 'footprints/Connector_FFC-FPC.pretty'
PINS = json.loads((HERE/'electronics/r01/interface.json').read_text())['pins']
mm = p.FromMM
def point(x, y): return p.VECTOR2I(mm(x), mm(y))

board = p.BOARD()
board.GetDesignSettings().SetBoardThickness(mm(1.6))
nets = {}
for name in sorted(set(PINS.values())):
    net = p.NETINFO_ITEM(board, '/'+name)
    board.Add(net)
    nets[name] = net

# Same orientation makes the logical one-to-one routing easy to inspect.
# Cable routing/contact orientation still requires a physical continuity check.
fps = []
for ref, y in [('J1', 56), ('J2', 76)]:
    fp = p.FootprintLoad(str(LIB), NAME)
    fp.SetReference(ref)
    fp.SetValue('200528-0150')
    fp.SetPosition(point(65, y))
    fp.SetFPID(p.LIB_ID('CameraStudy', NAME))
    fp.SetPath(p.KIID_PATH('/'+uid('sheet')+'/'+uid(ref)))
    fp.Reference().SetVisible(False)
    board.Add(fp)
    for pad in fp.Pads():
        if pad.GetNumber() in PINS:
            pad.SetNet(nets[PINS[pad.GetNumber()]])
    fps.append(fp)

for num, netname in PINS.items():
    a, b = [next(pad.GetPosition() for pad in fp.Pads() if pad.GetNumber()==num) for fp in fps]
    tr = p.PCB_TRACK(board)
    tr.SetStart(a); tr.SetEnd(b); tr.SetWidth(mm(.25)); tr.SetLayer(p.F_Cu)
    tr.SetNet(nets[netname]); board.Add(tr)
    if netname == 'GND':
        for y in (p.ToMM(a.y)+1, p.ToMM(b.y)-1):
            via = p.PCB_VIA(board)
            via.SetPosition(point(p.ToMM(a.x), y))
            via.SetWidth(mm(.6)); via.SetDrill(mm(.3)); via.SetLayerPair(p.F_Cu,p.B_Cu)
            via.SetNet(nets['GND']); board.Add(via)

for a,b in [((50,50),(80,50)),((80,50),(80,84)),((80,84),(50,84)),((50,84),(50,50))]:
    edge=p.PCB_SHAPE(); edge.SetShape(p.SHAPE_T_SEGMENT); edge.SetStart(point(*a)); edge.SetEnd(point(*b))
    edge.SetLayer(p.Edge_Cuts); edge.SetWidth(mm(.05)); board.Add(edge)
for x,y in [(52.5,52.5),(77.5,52.5),(52.5,81.5),(77.5,81.5)]:
    fp=p.FOOTPRINT(board); fp.SetReference('H'+str(len(list(board.GetFootprints()))-1)); fp.SetPosition(point(x,y))
    fp.SetAttributes(p.FP_EXCLUDE_FROM_BOM | p.FP_EXCLUDE_FROM_POS_FILES | p.FP_BOARD_ONLY)
    pad=p.PAD(fp); pad.SetAttribute(p.PAD_ATTRIB_NPTH); pad.SetShape(p.PAD_SHAPE_CIRCLE)
    pad.SetSize(point(2.2,2.2)); pad.SetDrillSize(point(2.2,2.2)); pad.SetLayerSet(p.LSET.AllCuMask())
    pad.SetPosition(point(x,y)); fp.Add(pad); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); board.Add(fp)

zone=p.ZONE(board); zone.SetLayer(p.B_Cu); zone.SetNet(nets['GND'])
zone.SetLocalClearance(mm(.25)); zone.SetThermalReliefGap(mm(.25)); zone.SetThermalReliefSpokeWidth(mm(.3))
outline=zone.Outline(); outline.NewOutline()
for x,y in [(50.5,50.5),(79.5,50.5),(79.5,83.5),(50.5,83.5)]: outline.Append(mm(x),mm(y))
board.Add(zone)
for text,x,y in [('CSI STUDY R02',65,51.8),('J1',54,55),('J2',54,75),('NOT FOR FAB',65,82.5)]:
    txt=p.PCB_TEXT(board); txt.SetText(text); txt.SetPosition(point(x,y)); txt.SetTextSize(point(.8,.8))
    txt.SetTextThickness(mm(.12)); txt.SetLayer(p.F_SilkS); board.Add(txt)
board.BuildConnectivity()
p.ZONE_FILLER(board).Fill(board.Zones())
p.SaveBoard(str(OUT/'camera-interface.kicad_pcb'),board)

# Vendor the exact installed footprint for reproducibility; attribution below.
local=OUT/'CameraStudy.pretty'; local.mkdir(exist_ok=True)
shutil.copyfile(LIB/(NAME+'.kicad_mod'),local/(NAME+'.kicad_mod'))
(OUT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "CameraStudy")(type "KiCad")(uri "${KIPRJMOD}/CameraStudy.pretty")(options "")(descr "Pinned KiCad library footprint")))\n')
for name in ['SkellyCAD.kicad_sym','sym-lib-table','camera-interface.kicad_pro']:
    shutil.copyfile(HERE/'electronics/r01'/name,OUT/name)
sch=(HERE/'electronics/r01/camera-interface.kicad_sch').read_text()
sch=sch.replace('(property "Footprint" ""',f'(property "Footprint" "CameraStudy:{NAME}"')
sch=sch.replace('"HOST SIDE / PI 4"','"200528-0150"').replace('"CAMERA PATH / VIA CABLE"','"200528-0150"')
sch=sch.replace('R01 / logical connection study','R02 / routed teaching coupon')
sch=sch.replace('Pending: exact module, cable contact mapping, connector footprints and routing.',
                'Molex 200528-0150 footprints assigned; physical cable mapping and MIPI performance pending.')
sch=sch.replace('OV9281 module candidate','B0224 bench reference')
(OUT/'camera-interface.kicad_sch').write_text(sch)
(OUT/'lineage.json').write_text(json.dumps({
    'revision':'R02-teaching-coupon','parent':'R01-logical-interface','units':'mm',
    'parent_schematic_sha256':hashlib.sha256((HERE/'electronics/r01/camera-interface.kicad_sch').read_bytes()).hexdigest(),
    'board_dimensions_mm':[30,34,1.6], 'trace_width_mm':.25, 'route_length_mm':20,
    'footprint_source':'KiCad 10.0.7 installed library',
    'footprint_sha256':hashlib.sha256((local/(NAME+'.kicad_mod')).read_bytes()).hexdigest(),
    'status':'Digital teaching artifact; not fabrication released; no impedance or cable validation',
},indent=2)+'\n')
print(OUT)
