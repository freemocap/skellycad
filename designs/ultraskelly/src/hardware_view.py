"""Exploded hardware and wiring view of UltraSkelly's electronics, laid flat for planning.

Every board, actuator, camera and supply lies on the table (XY plane, mm) and is joined by the
connections it uses on the robot. Positions form a diagram, not the robot's layout. Vendor STEP
models (references/vendor.json) are used where available; other parts are labelled stand-ins.
Connector positions on stand-ins and on the Motor HAT, whose model has no terminals, are
approximate. Channel and address assignments follow the robot software's current defaults.
Run live in the project FreeCAD window:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py hardware_view --run r001
"""
import argparse
import json

import FreeCAD as App
import Part

import cadkit
import vendor

V = App.Vector
PCB_GREEN, HAT_BLUE, PCA_BLUE = (0.1, 0.5, 0.25), (0.12, 0.2, 0.45), (0.1, 0.35, 0.75)
BLACK, GREY, SILVER, WHITE = (0.12, 0.12, 0.14), (0.45, 0.45, 0.48), (0.75, 0.76, 0.78), (0.92, 0.92, 0.9)
WIRE = {'usb3': (0.55, 0.2, 0.8), 'usb2': (0.4, 0.4, 0.4), 'pcie': (0.9, 0.55, 0.1), 'header': (0.55, 0.55, 0.55),
        '3v3': (0.9, 0.1, 0.1), 'gnd': (0.05, 0.05, 0.05), 'sda': (0.1, 0.45, 0.95), 'scl': (0.95, 0.8, 0.05),
        'servo': (0.95, 0.45, 0.05), 'motor': (0.1, 0.55, 0.2), 'power': (0.85, 0.1, 0.1)}


def box(x, y, z, origin=(0, 0, 0)):
    return Part.makeBox(x, y, z, V(*origin))


def ai_hat():
    """AI HAT+ stand-in from its drawing: 65 x 56.5 mm board, notch, Hailo can, header, ribbon socket."""
    board = box(65, 56.5, 1.6).cut(box(10, 16, 4, (47.5, -1, -1)))
    for x, y in ((3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)):
        board = board.cut(Part.makeCylinder(1.375, 4, V(x, y, -1)))
    parts = [board, box(17, 17, 1.8, (21, 20, 1.6)), box(50.8, 5.1, 8.5, (7.1, 50, 1.6)), box(4, 18, 2.5, (0.5, 21, 1.6))]
    return Part.makeCompound(parts)


def servo():
    """Standard hobby servo stand-in, about 41 x 20 x 36 mm; lead leaves the -X end."""
    return Part.makeCompound([box(40.7, 19.7, 36, (-20.35, -9.85, 0)), box(54.5, 19.7, 2.5, (-27.25, -9.85, 26.5)),
                              Part.makeCylinder(3, 4, V(10, 0, 36))])


def gearmotor(diameter, length):
    """DC gear motor stand-in lying along X; leads leave the -X end."""
    can = Part.makeCylinder(diameter / 2, length, V(-length / 2, 0, diameter / 2), V(1, 0, 0))
    gearbox = Part.makeCylinder(diameter / 2, length * 0.6, V(length / 2, 0, diameter / 2), V(1, 0, 0))
    return Part.makeCompound([can, gearbox])


def placed(shape, x, y, z=0, angle=0):
    shape = shape.copy()
    if angle:
        shape.rotate(V(0, 0, 0), V(0, 0, 1), angle)
    shape.translate(V(x, y, z))
    return shape


# id: (label lines, shape factory, placement (x, y, z, angle), color, source)
PARTS = {
    'pi5': (['Raspberry Pi 5', 'bottom of the stack'], lambda: vendor.shape('pi5-step'), (0, 0, 1.5, 0), PCB_GREEN, 'pi5-step'),
    'ai_hat': (['Hailo-8 AI HAT+ (26 TOPS)', 'middle: 16 mm spacers, PCIe ribbon'], ai_hat, (0, 100, 0, 0), PCB_GREEN, 'stand-in'),
    'motor_hat': (['Adafruit DC+Stepper Motor HAT', 'top: I2C 0x60, stacking header'], lambda: vendor.shape('motor-hat-step'),
                  (0, 200, 0, 0), HAT_BLUE, 'motor-hat-step'),
    'pca9685': (['PCA9685 16-ch servo board', 'I2C 0x40, separate, jumper-wired'], lambda: vendor.shape('pca9685-step'),
                (132, 212, 2, 0), PCA_BLUE, 'pca9685-step'),
    'zed': (['ZED Mini stereo camera', 'eye sockets, USB 3'], lambda: vendor.shape('zed-mini-step'), (372, 110, 14, 0), BLACK, 'zed-mini-step'),
    'oak': (['OAK-1 camera', 'nose hole, USB 3'], lambda: vendor.shape('oak1-enclosure-step'), (330, 40, 16, 0), BLACK, 'oak1-enclosure-step'),
    'pan_servo': (['Pan servo', 'PCA9685 ch 11'], servo, (335, 225, 0, 0), BLACK, 'stand-in'),
    'tilt_servo': (['Tilt servo', 'PCA9685 ch 3'], servo, (410, 225, 0, 0), BLACK, 'stand-in'),
    'jaw_motor': (['Jaw motor', 'Motor HAT M2, spring return'], lambda: gearmotor(24, 30), (340, 300, 0, 0), SILVER, 'stand-in'),
    'waist_motor': (['Waist motor', 'Motor HAT M1, turns the torso'], lambda: gearmotor(37, 50), (-150, 320, 0, 0), SILVER, 'stand-in'),
    'hub': (['USB 2 hub'], lambda: box(60, 25, 12), (150, 30, 0, 0), BLACK, 'stand-in'),
    'yeti': (['Yeti X microphone'], lambda: Part.makeCompound([Part.makeCylinder(45, 12), Part.makeCylinder(30, 110, V(0, 0, 12))]),
             (180, -110, 0, 0), BLACK, 'stand-in'),
    'pi_psu': (['Pi 5 supply', '5 V 5 A USB-C'], lambda: box(65, 45, 30), (-190, 0, 0, 0), WHITE, 'stand-in'),
    'motor_psu': (['Motor supply', 'voltage to confirm'], lambda: box(65, 45, 30), (-190, 190, 0, 0), WHITE, 'stand-in'),
    'servo_psu': (['Servo supply (V+)', 'voltage to confirm'], lambda: box(65, 45, 30), (170, 300, 0, 0), WHITE, 'stand-in'),
}

# Connection end points in layout coordinates (mm). PCA9685 pins follow the 815 breakout model.
PCA_X, PCA_Y = PARTS['pca9685'][2][:2]
PCA_PIN = {'gnd': 12.7, 'scl': 7.62, 'sda': 5.08, '3v3': 2.54}
P = {
    'pi_usb3_a': (88, 31), 'pi_usb3_b': (88, 27), 'pi_usb2': (88, 47), 'pi_usbc': (11, -2), 'pi_pcie': (0, 40),
    'pi_gpio': (32.5, 53), 'ai_ffc': (0.5, 130), 'ai_gpio': (32.5, 153), 'mh_gpio': (32.5, 253),
    'mh_m1': (0, 230), 'mh_m2': (0, 220), 'mh_power': (0, 205),
    'pca_v+': (PCA_X + 29.2, PCA_Y + 18.7), 'pca_ch11': (PCA_X + 40.64, PCA_Y - 5.1), 'pca_ch3': (PCA_X + 12.7, PCA_Y - 5.1),
    'zed_usb': (306, 125), 'oak_usb': (330, 15), 'hub_in': (150, 42), 'hub_out': (180, 30), 'yeti': (180, -65),
    'pan_lead': (308, 225), 'tilt_lead': (383, 225), 'jaw_lead': (325, 312), 'waist_lead': (-175, 338),
    'pi_psu': (-125, 22), 'motor_psu': (-125, 212), 'servo_psu': (202, 300),
}

# (kind, from, to, via points, label, label position)
WIRES = [
    ('usb3', 'pi_usb3_a', 'zed_usb', [(110, 31), (110, 90), (260, 90), (260, 125)], 'USB 3 to ZED Mini', (180, 94)),
    ('usb3', 'pi_usb3_b', 'oak_usb', [(240, 27), (240, -10), (330, -10)], 'USB 3 to OAK-1', (250, -6)),
    ('usb2', 'pi_usb2', 'hub_in', [(120, 47), (120, 42)], 'USB 2', (95, 50)),
    ('usb2', 'hub_out', 'yeti', [], '', None),
    ('power', 'pi_psu', 'pi_usbc', [(-60, 22), (-60, -20), (11, -20)], '5 V 5 A USB-C', (-58, -16)),
    ('pcie', 'pi_pcie', 'ai_ffc', [(-25, 40), (-25, 130)], 'PCIe ribbon', (-60, 85)),
    ('header', 'pi_gpio', 'ai_gpio', [], '40-pin header', (36, 75)),
    ('header', 'ai_gpio', 'mh_gpio', [], 'stacking header', (36, 175)),
    ('power', 'motor_psu', 'mh_power', [(-60, 212), (-60, 205)], 'motor V+', (-110, 200)),
    ('motor', 'mh_m1', 'waist_lead', [(-30, 230), (-30, 338)], 'M1 to waist', (-95, 342)),
    ('motor', 'mh_m2', 'jaw_lead', [(-15, 220), (-15, 360), (325, 360)], 'M2 to jaw', (120, 364)),
    ('power', 'servo_psu', 'pca_v+', [(202, 270), (PCA_X + 29.2, 270)], 'servo V+', (205, 262)),
    ('servo', 'pca_ch11', 'pan_lead', [(PCA_X + 40.64, 195), (290, 195), (290, 225)], 'ch 11 to pan', (240, 199)),
    ('servo', 'pca_ch3', 'tilt_lead', [(PCA_X + 12.7, 180), (370, 180), (370, 225)], 'ch 3 to tilt', (240, 184)),
]


def i2c_wires():
    """The four jumpers from the stack's I2C pins to the PCA9685 control header."""
    wires = []
    for k, name in enumerate(['3v3', 'gnd', 'sda', 'scl']):
        start = V(9 + 2.54 * k, 253, 3)
        lane_y, lane_x = 275 + 4 * k, 112 + 4 * k
        end = V(PCA_X, PCA_Y + PCA_PIN[name], 3)
        points = [start, V(start.x, lane_y, 3), V(lane_x, lane_y, 3), V(lane_x, end.y, 3), end]
        wires.append((name, Part.makePolygon(points)))
    return wires


def regions():
    """Dashed outlines grouping parts by where they live on the robot."""
    return [('Head (inside the skull)', (285, -20, 470, 340), (290, -36)),
            ('Electronics case on the spine tube (to design)', (-40, -40, 250, 295), (-35, -56))]


def label(doc, name, lines, x, y, size=6.0, color=(0.1, 0.1, 0.1)):
    if not App.GuiUp:
        return None
    import Draft
    text = Draft.make_text(lines, V(x, y, 25))
    text.Label = name
    text.ViewObject.FontSize = size
    text.ViewObject.TextColor = color
    return text


def build(doc):
    connections = []
    for part_id, (lines, factory, (x, y, z, angle), color, source) in PARTS.items():
        shape = placed(factory(), x, y, z, angle)
        cadkit.add(doc, part_id, shape, color, label=lines[0])
        box_ = shape.BoundBox
        label(doc, part_id + '_label', lines, box_.XMin, box_.YMax + 18, 10)
    for kind, start, end, via, text, at in WIRES:
        points = [V(*P[start], 3)] + [V(px, py, 3) for px, py in via] + [V(*P[end], 3)]
        cadkit.add(doc, f'wire_{start}_{end}', Part.makePolygon(points), WIRE[kind], label=f'{kind}: {start} to {end}', line_width=4)
        if text:
            label(doc, f'wire_{start}_{end}_label', [text], *at, size=8, color=WIRE[kind])
        connections.append({'kind': kind, 'from': start, 'to': end, 'label': text})
    for name, wire in i2c_wires():
        cadkit.add(doc, f'i2c_{name}', wire, WIRE[name], label=f'I2C jumper {name}', line_width=4)
        connections.append({'kind': 'i2c', 'from': f'stack_{name}', 'to': f'pca9685_{name}', 'label': name})
    label(doc, 'i2c_label', ['I2C jumpers: 3.3 V, GND, SDA, SCL', 'came loose 2026-11-02: secure these'], 110, 318, 8, WIRE['3v3'])
    for title, (x0, y0, x1, y1), (tx, ty) in regions():
        outline = Part.makePolygon([V(x0, y0, 0.5), V(x1, y0, 0.5), V(x1, y1, 0.5), V(x0, y1, 0.5), V(x0, y0, 0.5)])
        obj = cadkit.add(doc, 'region_' + title.split()[0].lower(), outline, GREY, label=title, line_width=2)
        if App.GuiUp:
            obj.ViewObject.DrawStyle = 'Dashed'
        label(doc, 'region_label_' + title.split()[0].lower(), [title], tx, ty, 11, GREY)
    label(doc, 'title', ['UltraSkelly electronics, laid flat', 'diagram positions; not the robot layout'], -200, 440, 18)
    return connections


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--run', required=True, help='new run name under generated/ultraskelly/hardware-view/')
    args = parser.parse_args(argv)
    folder = cadkit.run_folder('hardware-view', args.run)
    cadkit.close_saved_runs(folder.parent)
    doc = App.newDocument('UltraSkellyHardware')
    connections = build(doc)
    doc.recompute()
    native = folder / 'hardware-view.FCStd'
    native_sha = cadkit.save_verified(doc, native)
    cadkit.write_report(folder / 'build-report.json', {
        'part': 'hardware-view', 'run': args.run, 'units': 'mm', 'native': {'path': native.name, 'sha256': native_sha},
        'parts': {k: {'label': v[0], 'model': v[4]} for k, v in PARTS.items()}, 'connections': connections,
        'status': 'Planning diagram; positions are not the robot layout.'})
    if App.GuiUp:
        cadkit.present(doc, 'top')
    else:
        App.closeDocument(doc.Name)
    print(json.dumps({'saved': str(native), 'parts': len(PARTS), 'connections': len(connections)}))


if __name__ == '__main__':
    main()
