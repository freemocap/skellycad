"""Create architecture-only KiCad drawings. No fabricated sensor pin map.
Sensor source [@omnivisionOc0tcBrief]; bridge [@infineonCx3Datasheet].
"""
from pathlib import Path
import json,uuid
import pcbnew as p
BASE=Path(__file__).resolve().parent
OUT=BASE/'electronics/r02'
if (OUT/'oc0tc-usb.kicad_sch').exists(): raise SystemExit('Preserve R02; create a new revision.')
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'skellycad/oc0tc-r02/'+s))
parts=[f'(kicad_sch (version 20250114) (generator "skellycad_architecture") (uuid {uid("sheet")}) (paper "A4") (lib_symbols)']
def text(s,x,y,size=1.5):
    parts.append(f'(text "{s}" (at {x} {y} 0) (effects (font (size {size} {size})) (justify left)) (uuid {uid(s)}))')
def box(title,sub,x,y,w=62,h=25):
    parts.append(f'(rectangle (start {x} {y}) (end {x+w} {y+h}) (stroke (width 0.3) (type default)) (fill (type none)) (uuid {uid(title+"box")}))')
    text(title,x+3,y+7);text(sub,x+3,y+15,1.1)
text('OC0TC -> MIPI -> USB / ARCHITECTURE ONLY',20,20,2)
text('Blocks are functions, NOT symbols with verified package pins. No ERC completeness claim.',20,28,1.2)
box('SENSOR HEAD','OC0TC / sensor + optics integrated',20,45)
box('MIPI RECEIVER + USB','CX3 candidate / 10 x 10 mm',110,45)
box('FOUR-WIRE USB','JST SH candidate -> external hub',200,45)
text('1-lane D-PHY',84,57,1.1);text('USB 2.0 HS',174,57,1.1)
box('INTEGRATED OPTICS','No separate threaded lens or holder',20,85)
box('POWER + DECOUPLING','5 V -> bridge rails + sensor rails',110,85)
box('BOOT / CLOCK / RESET','Flash, oscillator and sequencing',200,85)
text('Sensor nominal rails: 2.8 V analog, 1.1 V core in D-PHY mode; IO voltage TBD.',20,124,1.2)
text('Control/configuration, reference clock, reset and grounds also cross the flex as required.',20,132,1.2)
text('IR LEDs need a current driver and exposure/illumination timing; values not selected.',20,140,1.2)
text('Proposed local J1 pin convention: 1=5V, 2=D-, 3=D+, 4=GND. NOT Pupil cable pinout.',20,150,1.2)
text('Missing before schematic/layout: sensor land pattern, pinout, register data and power timing.',20,161,1.2)
text('58 mm flat length: 20 mm main + 30 mm flex + 8 mm head. Main width 14 mm (goal 10).',20,172,1.2)
parts.append(')')
(OUT/'oc0tc-usb.kicad_sch').write_text('\n'.join(parts))
(OUT/'oc0tc-usb.kicad_pro').write_text('{"meta":{"filename":"oc0tc-usb.kicad_pro","version":1}}')
board=p.BOARD();board.GetDesignSettings().SetBoardThickness(p.FromMM(.8))
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def rect(x,y,w,h,layer):
    sh=p.PCB_SHAPE();sh.SetShape(p.SHAPE_T_RECT);sh.SetStart(pt(x,y));sh.SetEnd(pt(x+w,y+h));sh.SetLayer(layer);sh.SetWidth(p.FromMM(.12));board.Add(sh)
def label(s,x,y,size=.7):
    t=p.PCB_TEXT(board);t.SetText(s);t.SetPosition(pt(x,y));t.SetTextSize(pt(size,size));t.SetTextThickness(p.FromMM(.1));t.SetLayer(p.Dwgs_User);board.Add(t)
rect(50,50,20,14,p.Edge_Cuts)
rect(70,55,30,4,p.Dwgs_User);label('30 mm FLEX / STACKUP TBD',85,53)
rect(100,53,8,8,p.Dwgs_User);rect(102.5,55.5,3,3,p.Dwgs_User)
label('HEAD',104,51);label('OC0TC / XY TBD',104,63)
rect(53,52,10,10,p.Dwgs_User);label('CX3',58,57,1)
rect(65,54.2,5,5.6,p.Dwgs_User);label('JST',67.5,57)
rect(50.3,52,2.4,10,p.Dwgs_User);label('POWER',51.5,65)
label('MAIN 20 x 14 mm / NO ROUTES OR SENSOR PADS',60,47)
label('FUNCTIONAL PLACEMENT STUDY / NOT FOR FAB',79,69,1)
label('Flash + decoupling may occupy underside; placement feasibility unverified.',79,72,.7)
p.SaveBoard(str(OUT/'oc0tc-usb.kicad_pcb'),board)
print(OUT)
