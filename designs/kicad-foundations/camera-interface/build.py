"""Create a new logical CSI interface study, not a fabrication-ready adapter.

Pin assignment: [@raspberryPiCameraPinout]. Format: [@kicadSchematicFormat].
Run with standard Python and --output pointing to a NEW directory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import uuid

PINS = ['GND','CAM_D0_N','CAM_D0_P','GND','CAM_D1_N','CAM_D1_P','GND',
        'CAM_CLK_N','CAM_CLK_P','GND','CAM_IO0','CAM_IO1','CAM_SCL','CAM_SDA','CAM_3V3']

def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'skellycad/csi-interface/r01/'+name))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():
        raise SystemExit('Use a fresh directory; existing revisions are preserved.')
    sheet=uid('sheet')
    symbol='''(symbol "SkellyCAD:CSI_15_Logical"
      (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 5.08 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "CSI_15_Logical" (at 5.08 2.54 0) (effects (font (size 1.27 1.27))))
      (symbol "CSI_15_Logical_0_1" (rectangle (start 0 2.54) (end 30.48 -38.1)
        (stroke (width 0.254) (type default)) (fill (type background))))
      (symbol "CSI_15_Logical_1_1"'''
    for i, net in enumerate(PINS):
        symbol+=f'''(pin passive line (at -5.08 {-i*2.54:.2f} 0) (length 5.08)
        (name "{net}" (effects (font (size 1.0 1.0))))
        (number "{i+1}" (effects (font (size 1.0 1.0)))))'''
    symbol+='))'
    parts=[f'(kicad_sch (version 20250114) (generator "skellycad_csi_study") (uuid {sheet}) (paper "A4")',
           '(lib_symbols '+symbol+')']
    for ref,x,value in [('J1',81.28,'HOST SIDE / PI 4'),('J2',195.58,'CAMERA PATH / VIA CABLE')]:
        parts.append(f'''(symbol (lib_id "SkellyCAD:CSI_15_Logical") (at {x} 76.2 0) (unit 1)
        (in_bom yes) (on_board yes) (dnp no) (uuid {uid(ref)})
        (property "Reference" "{ref}" (at {x+15.24} 66.04 0) (effects (font (size 1.27 1.27))))
        (property "Value" "{value}" (at {x+15.24} 69.85 0) (effects (font (size 1.27 1.27))))
        (property "Footprint" "" (at {x} 76.2 0) (effects (font (size 1.27 1.27)) (hide yes)))
        (instances (project "camera-interface" (path "/{sheet}" (reference "{ref}") (unit 1)))))''')
        for i,net in enumerate(PINS):
            y=76.2+i*2.54
            parts.append(f'(wire (pts (xy {x-30.48} {y:.2f}) (xy {x-5.08} {y:.2f})) (stroke (width 0) (type default)) (uuid {uid(ref+str(i))}))')
            parts.append(f'(label "{net}" (at {x-30.48} {y:.2f} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid {uid(ref+net+str(i))}))')
    for i,(text,x,y) in enumerate([
        ('CAMERA INTERFACE / R01 / logical connection study',35.56,40.64),
        ('Pi 4 CSI receiver <-> interface board <-> vendor cable <-> OV9281 module candidate',35.56,48.26),
        ('Equal labels are connected nets. This is MIPI CSI-2, NOT USB.',35.56,132.08),
        ('Data + clock: camera to host. I2C: configuration. 3V3: host supply to module.',35.56,139.7),
        ('CAM_IO0 / CAM_IO1 functions depend on the module; no trigger function assumed.',35.56,147.32),
        ('J2 uses the documented HOST pin convention, not an unverified module connector.',35.56,154.94),
        ('Pending: exact module, cable contact mapping, connector footprints and routing.',35.56,162.56),
        ('No USB bridge, sensor power redesign, IR LED driver or camera merger is implemented.',35.56,170.18),
    ]):
        parts.append(f'(text "{text}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid {uid("note"+str(i))}))')
    parts.extend(['(sheet_instances (path "/" (page "1")))',')'])
    args.output.mkdir(parents=True)
    (args.output/'SkellyCAD.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "skellycad_csi_study") '+symbol.replace('"SkellyCAD:CSI_15_Logical"','"CSI_15_Logical"',1)+')\n')
    (args.output/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "SkellyCAD")(type "KiCad")(uri "${KIPRJMOD}/SkellyCAD.kicad_sym")(options "")(descr "Original logical teaching connector")))\n')
    sch=args.output/'camera-interface.kicad_sch'
    sch.write_text('\n'.join(parts)+'\n',encoding='utf-8')
    (args.output/'camera-interface.kicad_pro').write_text('{"meta":{"filename":"camera-interface.kicad_pro","version":1}}\n')
    (args.output/'interface.json').write_text(json.dumps({
        'revision':'R01-logical-interface','units':'mm','source':'raspberryPiCameraPinout',
        'host_reference':'Raspberry Pi 4, 15-pin CSI',
        'camera_candidate':'Arducam OV9281 module; exact SKU and cable pending',
        'pins':{str(i+1):name for i,name in enumerate(PINS)},
        'schematic_sha256':hashlib.sha256(sch.read_bytes()).hexdigest(),
        'status':'Logical teaching study only; no physical connector or video validation',
    },indent=2)+'\n')
    print(sch.resolve())

if __name__=='__main__':
    main()
