"""Exploded, labelled views and assembly steps for the UltraSkelly neck clamp and enclosure.

Every part is its own named object: printed parts, screws and nuts, the bought boards and the
spine tube. A pose moves parts along the direction they assemble by changing only their
placements; each pose is rendered in its own call so the window settles between views. A
second document shows the actual STL files to print. Run live in the project FreeCAD window:

    live.py explain build --run r003          # both documents, exploded pose, captions.json
    live.py explain pose --name step4-slide-down
    live.py explain prints-image
    live.py explain finish                    # back to the exploded view, saved, in front

(`live.py` is tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py.)
"""
import argparse
import json
import math
from pathlib import Path

import FreeCAD as App
import Mesh
import Part

import cadkit
import case_view
import enclosure
import hardware_view
import mount
import vendor

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
STATE = cadkit.GENERATED / 'explain' / 'current.json'
V = App.Vector
NOW, LATER = (0.95, 0.55, 0.15), (0.3, 0.6, 0.85)
STEEL, BRASS, METAL = (0.55, 0.57, 0.6), (0.8, 0.65, 0.3), (0.3, 0.3, 0.33)
DOC, PRINTS_DOC = 'UltraSkellyExploded', 'UltraSkellyWhatYouPrint'


def screw(diameter, length, head_d, head_h, head_top, axis):
    """Socket-head screw whose head's outer face is at head_top, shaft running along axis."""
    axis = V(*axis).normalize()
    top = V(*head_top)
    return Part.makeCylinder(head_d / 2, head_h, top, axis).fuse(
        Part.makeCylinder(diameter / 2, length, top + axis * head_h, axis))


def hex_prism(flats, length, start, axis, bore=0.0):
    """Hexagonal prism (nut or standoff) starting at `start` and extending along `axis`."""
    r = flats / math.sqrt(3)
    points = [V(r * math.cos(math.radians(60 * k)), r * math.sin(math.radians(60 * k)), 0) for k in range(6)]
    body = Part.Face(Part.makePolygon(points + [points[0]])).extrude(V(0, 0, length))
    if bore:
        body = body.cut(Part.makeCylinder(bore / 2, length + 2, V(0, 0, -1)))
    body.transformShape(App.Placement(V(*start), App.Rotation(V(0, 0, 1), V(*axis))).toMatrix())
    return body


def parts(p):
    """All parts at their assembled positions in the clamp frame: name -> (shape, color, label, group)."""
    g = enclosure.geometry(p)
    c = p['clamp']
    m = enclosure.case_matrix(p, g)
    case_shape = mount.moved(mount.cut_case(p['case']['cut_height']), m)
    back, wing_outer = enclosure.enclosure_back(p, g, case_shape.BoundBox)
    z = case_view.stack_heights()
    out = {
        'SpineTube': (mount.box(-12.7, 12.7, -12.7, 12.7, -70, 150), STEEL, 'Spine tube (robot)', 'tube'),
        'ClampU': (enclosure.clamp_u(p, g), NOW, '1 Clamp U - PRINT NOW', 'clamp'),
        'ClampBar': (enclosure.clamp_bar(p, g), NOW, '2 Clamp bar - PRINT NOW', 'clamp'),
        'EnclosureBack': (back, LATER, '3 Enclosure back - print later', 'enclosure'),
        'CaseCut': (case_shape, (0.88, 0.88, 0.9), '4 Pi case, cut down - print later', 'enclosure'),
    }
    screws = [screw(3, 25, 5.5, 3, (g['x_bar'][1], s * c['bolt_y'], h), (-1, 0, 0)) for s in (1, -1) for h in c['bolt_heights']]
    out['ClampScrews'] = (Part.makeCompound(screws), METAL, 'M3x25 screws (4)', 'clamp')
    k = 0
    for s in (1, -1):
        for h in c['bolt_heights']:
            k += 1
            nut = hex_prism(5.5, 2.4, (c['nut_slot_x'] + 0.3, s * c['bolt_y'], h), (1, 0, 0), 3)
            out[f'ClampNut{k}'] = (nut, METAL, 'M3 nuts (4)' if k == 1 else '', 'clamp')
    pin_x, pin_z = g['pin']
    half_w = g['block_w'] / 2
    pin = screw(3, 35, 5.5, 3, (pin_x, -half_w - 3, pin_z), (0, 1, 0)).fuse(
        hex_prism(5.5, 2.4, (pin_x, half_w + 0.2, pin_z), (0, 1, 0), 3))
    out['LockPin'] = (pin, METAL, 'M3 lock pin + nut', 'enclosure')
    for name, shape, height, color, label in (
            ('Pi5', vendor.shape('pi5-step'), z['pi_z'], hardware_view.PCB_GREEN, 'Raspberry Pi 5'),
            ('AIHat', hardware_view.ai_hat(), z['ai_hat_bottom'], hardware_view.PCB_GREEN, 'AI HAT+ (Hailo-8)'),
            ('MotorHat', vendor.shape('motor-hat-step'), z['motor_hat_bottom'], hardware_view.HAT_BLUE, 'Motor HAT')):
        out[name] = (mount.moved(hardware_view.placed(shape, 0, 0, height), m), color, label, 'enclosure')
    holes = case_view.HOLES
    ai_spacers = [hex_prism(5, 16, (x, y, z['pi_top']), (0, 0, 1), 2.5) for x, y in holes]
    mh_spacers = [hex_prism(5, case_view.MOTOR_GAP, (x, y, z['ai_hat_bottom'] + 1.6), (0, 0, 1), 2.5) for x, y in holes]
    out['AISpacers'] = (mount.moved(Part.makeCompound(ai_spacers), m), BRASS, '16 mm spacers (4)', 'enclosure')
    out['MotorSpacers'] = (mount.moved(Part.makeCompound(mh_spacers), m), BRASS, 'spacers (4)', 'enclosure')
    case_screws = [screw(2.5, 16, 4.5, 2.5, (g['x_plate_front'], y, zz), (-1, 0, 0)) for y, zz in enclosure.pi_holes(p)]
    out['CaseScrews'] = (Part.makeCompound(case_screws), METAL, 'M2.5x16 screws (4)', 'enclosure')
    pca_m = enclosure.pca_matrix(p, g, wing_outer)
    out['PCA9685'] = (mount.moved(vendor.shape('pca9685-step'), pca_m), hardware_view.PCA_BLUE, 'PCA9685 servo board', 'enclosure')
    board_top = wing_outer + p['pca9685']['boss_length'] + 1.6
    pca_screws = [screw(2.5, 6, 4.5, 2.5, (x, board_top + 2.5, zz), (0, -1, 0)) for x, zz in enclosure.pca_holes(p)]
    out['PCAScrews'] = (Part.makeCompound(pca_screws), METAL, 'M2.5x6 screws (4)', 'enclosure')
    # I2C jumpers from the stack's header pins (top of the Motor HAT) to the PCA9685 control header.
    hat_z = z['motor_hat_bottom'] + 7.6
    hat_pins = {'Vcc': (8.37, 50.92), 'Sda': (10.91, 50.92), 'Scl': (13.45, 50.92), 'Gnd': (13.45, 53.46)}
    pca_pins = {'Vcc': 2.54, 'Sda': 5.08, 'Scl': 7.62, 'Gnd': 12.7}
    wire = hardware_view.WIRE
    colors = {'Vcc': wire['3v3'], 'Sda': wire['sda'], 'Scl': wire['scl'], 'Gnd': wire['gnd']}
    for k, (key, (px, py)) in enumerate(hat_pins.items()):
        start, end = m.multVec(V(px, py, hat_z)), pca_m.multVec(V(0, pca_pins[key], 8.5))
        lane = 54 + 1.5 * k
        points = [start, V(start.x - 5, start.y, start.z), V(start.x - 5, lane, start.z), V(end.x, lane, end.z), end]
        out['Jumper' + key] = (Part.makePolygon(points), colors[key], 'I2C jumpers (4)' if key == 'Vcc' else '', 'wires')
    # Thin horizontal slices through the clamp joint, for the cut-through view of the dovetail.
    slab = mount.box(-70, 40, -60, 60, 29, 31)
    for name, source, color, label in (('SectionTube', 'SpineTube', STEEL, 'Spine tube (cut)'),
                                       ('SectionU', 'ClampU', NOW, '1 Clamp U (cut): dovetail tongue at its back'),
                                       ('SectionBar', 'ClampBar', NOW, '2 Clamp bar (cut)'),
                                       ('SectionBack', 'EnclosureBack', LATER, '3 Enclosure back (cut): dovetail channel')):
        out[name] = (out[source][0].common(slab), color, label, 'section')
    top = case_shape.BoundBox.ZMax
    out['Bundle'] = (Part.makePolygon([V(-50, 0, top + 2), V(-50, 0, top + 60), V(-20, 0, top + 120)]), (0.2, 0.2, 0.2),
                     'cables up to the head', 'wires')
    return out


NUTS = ['ClampNut1', 'ClampNut2', 'ClampNut3', 'ClampNut4']
CLAMP = ['SpineTube', 'ClampU', 'ClampBar', 'ClampScrews'] + NUTS
ENCLOSURE = ['EnclosureBack', 'CaseCut', 'Pi5', 'AISpacers', 'AIHat', 'MotorSpacers', 'MotorHat', 'PCA9685', 'PCAScrews', 'CaseScrews']
WIRES = ['JumperVcc', 'JumperSda', 'JumperScl', 'JumperGnd', 'Bundle']
SIDE = (-0.5, 1.0, 0.45)
UP = 170.0


def nuts(dx, out):
    """Nut offsets: move with the U along X and slide out of their side slots by `out`."""
    return {name: ('side', dx, out) for name in NUTS}


def assembled(*names):
    return {name: (0, 0, 0) for name in names}


EXPLODED = dict({'SpineTube': (0, 0, 0), 'ClampU': (-45, 0, 0), 'ClampBar': (40, 0, 0), 'ClampScrews': (80, 0, 0),
                 'EnclosureBack': (-45, 0, UP), 'LockPin': (-45, -40, UP), 'CaseScrews': (-10, 0, UP),
                 'CaseCut': (-95, 0, UP), 'Pi5': (-140, 0, UP), 'AISpacers': (-165, 0, UP), 'AIHat': (-190, 0, UP),
                 'MotorSpacers': (-215, 0, UP), 'MotorHat': (-240, 0, UP), 'PCA9685': (-45, 45, UP + 70),
                 'PCAScrews': (-45, 75, UP + 70)}, **nuts(-45, 22))

POSES = {  # name: (caption, pose, camera direction from the model, parts to fit or None, parts to label or None)
    'exploded': ('Exploded view: every part pulled apart along the direction it assembles. Orange = print now, blue and grey = print later, dark grey = screws and nuts, boards = bought parts.',
                 EXPLODED, SIDE, None, None),
    'step1-u-onto-tube': ("Step 1. The neck clamp U goes around the spine tube from behind. Its dovetail tongue faces the skeleton's back.",
                          {'SpineTube': (0, 0, 0), 'ClampU': (-45, 0, 0)}, (-0.9, -1.0, 0.8), None, None),
    'step2-nuts-bar-screws': ('Step 2. Push an M3 nut into each of the four side slots in the U. Put the bar in front of the tube, then four M3 screws go through the bar into the nuts.',
                              dict({'SpineTube': (0, 0, 0), 'ClampU': (0, 0, 0), 'ClampBar': (22, 0, 0), 'ClampScrews': (50, 0, 0)}, **nuts(0, 14)),
                              (1.0, -1.0, 0.7), None, ['ClampU', 'ClampBar', 'ClampScrews', 'ClampNut1']),
    'step3-clamp-grips': ('Step 3. Tightening the screws pulls the bar toward the U. The tube is squeezed between the bar (front) and the U (back): that squeeze is the grip. Loosen the screws to move or remove the clamp.',
                          assembled(*CLAMP), (0.6, -0.7, 1.0), None, ['ClampU', 'ClampBar', 'ClampScrews', 'SpineTube']),
    'step4-slide-down': ('Step 4. The enclosure, with the Pi stack and PCA9685 already inside, slides straight down onto the clamp. A dovetail tongue on the back of the U fits a matching channel on the front of the enclosure back, so the enclosure can only move up and down.',
                         dict(assembled(*CLAMP), **{name: (0, 0, 110) for name in ENCLOSURE}), (-0.75, 1.0, 0.12), None,
                         ['ClampU', 'EnclosureBack', 'CaseCut', 'PCA9685']),
    'step4b-dovetail-section': ("Step 4, cut through the joint and seen from above (front of the skeleton at the top). The tube sits in the U, and the bar is screwed across its front. The U's dovetail tongue sits inside the enclosure's channel, which is wider inside than at its mouth: the enclosure cannot pull away from the tube or slide sideways, only up and down. The channel is closed at its top, so the enclosure hangs on the top of the tongue.",
                                {'SectionTube': (0, 0, 0), 'SectionU': (0, 0, 0), 'SectionBar': (0, 0, 0), 'SectionBack': (0, 0, 0)},
                                (-0.02, 0.0, 1.0), None, None),
    'step5-lock-pin': ('Step 5. Seated: the enclosure rests on top of the tongue. An M3 screw (the lock pin) goes sideways through the channel just below the tongue, so the enclosure cannot lift off. Remove that one screw and lift to take the electronics off.',
                       dict(assembled(*CLAMP, *ENCLOSURE), LockPin=(0, -35, 0)), (-0.8, -1.0, 0.25), ['ClampU', 'EnclosureBack', 'LockPin'],
                       ['LockPin', 'EnclosureBack']),
    'step6-inside-enclosure': ('Step 6. Inside the enclosure: the Pi sits on the case stand-offs. Four M2.5 x 16 screws go from the enclosure back, through the case and the Pi, into the AI HAT+ spacers, so one set of screws holds all of it. The Motor HAT sits on the next spacers. The PCA9685 screws onto the side wing.',
                               {'EnclosureBack': (0, 0, 0), 'CaseScrews': (40, 0, 0), 'CaseCut': (-40, 0, 0), 'Pi5': (-85, 0, 0),
                                'AISpacers': (-105, 0, 0), 'AIHat': (-125, 0, 0), 'MotorSpacers': (-145, 0, 0), 'MotorHat': (-165, 0, 0),
                                'PCA9685': (0, 40, 60), 'PCAScrews': (0, 70, 60)}, SIDE, None, None),
    'step7-wiring': ("Step 7. Wiring: four short I2C jumpers (3.3 V, GND, SDA, SCL) run from the stack's header to the PCA9685 on the side wing. Both ends ride on the enclosure, so they stay connected when it lifts off. USB, servo and motor cables leave from the top, toward the head; tie them to the two slots in the top tab.",
                     assembled(*CLAMP, *ENCLOSURE, 'LockPin', *WIRES), (-1.0, 0.75, 0.5), None,
                     ['JumperVcc', 'Bundle', 'PCA9685', 'MotorHat']),
}


LABEL_BELOW = {'SpineTube', 'ClampScrews', 'CaseScrews', 'MotorSpacers', 'EnclosureBack', 'ClampNut1'}


def apply_pose(doc, pose, toward=(0, 0, 1), label_names=None):
    for obj in doc.Objects:
        if obj.TypeId == 'Part::Feature':
            spec = pose.get(obj.Name)
            obj.Visibility = spec is not None
            if spec is None:
                continue
            offset = V(spec[1], math.copysign(spec[2], obj.Side), 0) if spec[0] == 'side' else V(*spec)
            # Shapes carry their assembled rotation in their placement; offsets go on top of it.
            obj.Placement = App.Placement(offset, App.Rotation()).multiply(obj.BasePlacement)
    doc.recompute()
    for obj in doc.Objects:
        if obj.Label.startswith('label_'):  # Draft text keeps its own Name; the label holds the target
            target = doc.getObject(obj.Label[len('label_'):])
            shown = target.Name in pose and (label_names is None or target.Name in label_names)
            obj.ViewObject.Visibility = shown
            if shown:
                # In front of the part (toward the camera), above it or below it, so geometry does not hide it.
                b = target.Shape.BoundBox  # includes the target's placement
                front = V(*toward).normalize() * (b.DiagonalLength / 2 + 30)  # in front of its part in the live window
                lift = -(b.ZLength / 2 + 12) if target.Name in LABEL_BELOW else b.ZLength / 2 + 6
                obj.Placement = App.Placement(b.Center + front + V(0, 0, lift), App.Rotation())


def camera(view, look_from, fit_names, doc):
    import FreeCADGui as Gui
    back = V(*look_from).normalize()
    up = (V(0, 0, 1) - back * back.z).normalize()
    right = up.cross(back)
    axes = App.Matrix(right.x, up.x, back.x, 0, right.y, up.y, back.y, 0, right.z, up.z, back.z, 0, 0, 0, 0, 1)
    # Camera changes animate by default; an image saved mid-animation shows a rolled, half-turned view.
    App.ParamGet('User parameter:BaseApp/Preferences/View').SetBool('UseNavigationAnimations', False)
    view.setCameraType('Orthographic')  # parallel edges; perspective distorts the exploded spacing
    view.setCameraOrientation(App.Placement(axes).Rotation)
    # Fit by hiding everything else for a moment: fit-to-selection animates and would be captured
    # half-way, and selecting the case mesh takes minutes. fitAll ignores hidden objects.
    others = [o for o in doc.Objects if fit_names and o.TypeId == 'Part::Feature' and o.Visibility and o.Name not in fit_names]
    for obj in others:
        obj.Visibility = False
    view.fitAll()
    camera_node = view.getCameraNode()
    camera_node.height.setValue(camera_node.height.getValue() * 0.9)  # fitAll leaves wide margins
    for obj in others:
        obj.Visibility = True


def bound_box(obj):
    return obj.Mesh.BoundBox if obj.TypeId == 'Mesh::Feature' else obj.Shape.BoundBox


def save_with_marks(view, doc, path, width):
    """Save the view at the window's aspect ratio and record where each visible label points.

    The 3D labels are hidden for the image; caption.py draws them from <image>.labels.json so
    they are never clipped or hidden behind parts.
    """
    vw, vh = view.getSize()
    k = width / vw
    marks, hidden = [], []
    for text in doc.Objects:
        if text.Label.startswith('label_') and text.ViewObject.Visibility:
            target = doc.getObject(text.Label[len('label_'):])
            b = bound_box(target)
            below = target.Name in LABEL_BELOW
            x, y = view.getPointOnScreen(V(b.Center.x, b.Center.y, b.ZMin if below else b.ZMax))
            marks.append({'text': list(text.Text), 'x': round(x * k), 'y': round((vh - y) * k), 'below': below})
            text.ViewObject.Visibility = False
            hidden.append(text)
    view.saveImage(str(path), round(vw * k), round(vh * k), 'Current')
    for text in hidden:
        text.ViewObject.Visibility = True
    path.with_suffix('.labels.json').write_text(json.dumps(marks, indent=1), encoding='utf-8')


def activate(name):
    import FreeCADGui as Gui
    view = Gui.getDocument(name).mdiViewsOfType('Gui::View3DInventor')[0]
    Gui.getMainWindow().setActiveWindow(view)
    App.setActiveDocument(name)
    Gui.ActiveDocument = Gui.getDocument(name)
    return view


def build_prints(folder):
    """The exact STL files, print-now versus later."""
    doc = App.newDocument(PRINTS_DOC)
    clamp = PROJECT / 'checkpoints' / 'r001-neck-clamp'
    manifest = json.loads((clamp / 'manifest.json').read_text(encoding='utf-8'))
    later = cadkit.GENERATED / 'enclosure' / 'r005'
    files = [(clamp / 'clamp-u.stl', NOW, '1 clamp-u.stl', 'PRINT NOW'), (clamp / 'clamp-bar.stl', NOW, '2 clamp-bar.stl', 'PRINT NOW'),
             (later / 'enclosure-back.stl', LATER, '3 enclosure-back.stl', 'LATER'),
             (later / 'omt-case-cut.stl', (0.88, 0.88, 0.9), '4 omt-case-cut.stl', 'LATER')]
    x, sources = 0.0, {}
    for path, color, title, when in files:
        if path.parent == clamp and cadkit.sha256(path) != manifest['parts'][path.name]['sha256']:
            raise ValueError(f'{path} differs from its manifest')
        mesh = Mesh.Mesh(str(path))
        b = mesh.BoundBox
        mesh.translate(x - b.XMin, -b.YMin, -b.ZMin)
        obj = doc.addObject('Mesh::Feature', path.stem.replace('-', '_'))
        obj.Mesh = mesh
        obj.Label = f'{title} - {when}'
        obj.ViewObject.ShapeColor = color
        label = hardware_view.label(doc, 'label_' + obj.Name, [title, when], x, -20, 22)
        label.ViewObject.DisplayMode = 'Screen'
        label.Placement = App.Placement(V(x, -20, 0), App.Rotation())
        sources[path.name] = {'path': path.relative_to(cadkit.ROOT).as_posix(), 'sha256': cadkit.sha256(path), 'when': when}
        x += b.XLength + 50
    doc.recompute()
    sha = cadkit.save_verified(doc, folder / 'what-you-print.FCStd')
    return {'native': {'path': 'what-you-print.FCStd', 'sha256': sha}, 'stl_files': sources}


def build(args):
    params = json.loads((HERE / 'enclosure.json').read_text(encoding='utf-8'))
    for name in (DOC, PRINTS_DOC):
        if name in App.listDocuments():
            raise RuntimeError(f'{name} is already open; close it before a new build')
    folder = cadkit.run_folder('explain', args.run)
    prints = build_prints(folder)
    doc = App.newDocument(DOC)
    for name, (shape, color, text, group) in parts(params).items():
        obj = cadkit.add(doc, name, shape, color, label=text or name, line_width=6 if group == 'wires' else None)
        obj.addProperty('App::PropertyPlacement', 'BasePlacement', 'Explain', 'assembled placement')
        obj.BasePlacement = obj.Placement
        if name in NUTS:
            obj.addProperty('App::PropertyInteger', 'Side', 'Explain', 'which arm the nut sits in')
            obj.Side = 1 if shape.BoundBox.Center.y > 0 else -1
        if text:
            label = hardware_view.label(doc, 'label_' + name, [text], 0, 0, args.label_px)
            label.ViewObject.DisplayMode = 'Screen'  # always faces the camera; size in pixels
    apply_pose(doc, EXPLODED, SIDE)
    native = folder / 'exploded.FCStd'
    sha = cadkit.save_verified(doc, native)
    captions = {f'{name}.png': entry[0] for name, entry in POSES.items()}
    captions['what-you-print.png'] = 'What you print: 1 and 2 (orange) print now for the clamp test; 3 and 4 (blue, grey) print later, after the clamp test. These are the exact STL files.'
    (folder / 'captions.json').write_text(json.dumps(captions, indent=2) + '\n', encoding='utf-8')
    cadkit.write_report(folder / 'build-report.json', {
        'part': 'explain', 'run': args.run, 'units': 'mm', 'native': {'path': native.name, 'sha256': sha},
        'what_you_print': prints, 'images': list(captions),
        'status': 'Explanation views of the approved concept; hardware drawn as simple stand-ins, wires schematic.'})
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({'folder': str(folder)}), encoding='utf-8')
    print(json.dumps({'folder': str(folder), 'poses': list(POSES)}))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--size', type=int, nargs=2, default=[1800, 1200])
    sub = parser.add_subparsers(dest='command', required=True)
    b = sub.add_parser('build')
    b.add_argument('--run', required=True)
    b.add_argument('--label-px', type=float, default=22.0)
    pz = sub.add_parser('pose')
    pz.add_argument('--name', required=True, choices=list(POSES))
    sub.add_parser('prints-image')
    sub.add_parser('finish')
    args = parser.parse_args(argv)
    if not App.GuiUp:
        raise SystemExit('explain needs the live FreeCAD window')
    if args.command == 'build':
        build(args)
        return
    folder = Path(json.loads(STATE.read_text(encoding='utf-8'))['folder'])
    if args.command == 'prints-image':
        view = activate(PRINTS_DOC)
        camera(view, (1.0, -1.2, 0.9), None, App.getDocument(PRINTS_DOC))
        save_with_marks(view, App.getDocument(PRINTS_DOC), folder / 'what-you-print.png', args.size[0])
        print(folder / 'what-you-print.png')
        return
    doc = App.getDocument(DOC)
    view = activate(DOC)
    name = 'exploded' if args.command == 'finish' else args.name
    _text, pose, look, fit, label_names = POSES[name]
    apply_pose(doc, pose, look, label_names)
    camera(view, look, fit, doc)
    if args.command == 'finish':
        print('exploded view saved', cadkit.save_verified(doc, doc.FileName)[:12])
        return
    save_with_marks(view, doc, folder / f'{name}.png', args.size[0])
    captions_path = folder / 'captions.json'
    captions = json.loads(captions_path.read_text(encoding='utf-8'))
    captions[f'{name}.png'] = POSES[name][0]
    captions_path.write_text(json.dumps(captions, indent=2) + chr(10), encoding='utf-8')
    print(folder / f'{name}.png')


if __name__ == '__main__':
    main()
