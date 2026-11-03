"""The community OMT Pi 5 case, open top, with UltraSkelly's Pi 5 and HAT stack placed in it.

Case frame: origin at the Pi 5 board's lower-left corner, +X toward its USB and Ethernet ports,
+Z up from the case's underside, millimetres. The case comes from references/vendor.json
(omt-case-3mf, MIT); its lid is left off so the HAT stack stays open and visible. The AI HAT+
sits on its 16 mm spacers; the Motor HAT gap is an estimate until the stack is measured.
Run live: tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py case_view --run r001
"""
import argparse
import json

import FreeCAD as App
import Part

import cadkit
import hardware_view
import vendor

V = App.Vector
CASE_TO_PI = V(-90.0, -45.97, 0)  # OMT stand-off (93.5, 49.47) is the Pi's (3.5, 3.5) hole
STANDOFF_TOP = 7.5                 # Pi board underside rests here (section of the case mesh)
PI_BOARD = (0.03, 1.306)           # board solid z range in the Pi 5 STEP model
AI_SPACER, MOTOR_GAP = 16.0, 11.0  # AI HAT+ spacers per its brief; Motor HAT header gap estimated
HOLES = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]
CASE_COLOR, BRASS = (0.85, 0.86, 0.88), (0.8, 0.65, 0.3)


def cut_case(height):
    """OMT case body in Pi-origin coordinates, cut at a wall height; cached as BREP."""
    source = vendor.path('omt-case-3mf')
    cached = vendor.CACHE / 'omt-case-3mf' / f'case-cut-{height:g}.{vendor.sha256(source)[:12]}.brep'
    if cached.exists():
        return Part.read(str(cached))
    mesh = vendor.mesh_3mf('omt-case-3mf')['Pi Case v11.step']
    mesh.translate(*CASE_TO_PI)
    shape = Part.Shape()
    shape.makeShapeFromMesh(mesh.Topology, 0.01)
    solid = Part.makeSolid(shape)  # one face per mesh triangle; refining took minutes for little gain
    b = solid.BoundBox
    result = solid.common(cadkit.box(b.XMin - 5, b.XMax + 5, b.YMin - 5, b.YMax + 5, b.ZMin - 1, height))
    assert result.isValid() and len(result.Solids) == 1, 'case cut is not one valid solid'
    cached.parent.mkdir(parents=True, exist_ok=True)
    result.exportBrep(str(cached))
    return result


def stack_heights():
    pi_z = STANDOFF_TOP - PI_BOARD[0]
    pi_top = pi_z + PI_BOARD[1]
    ai_z = pi_top + AI_SPACER
    motor_z = ai_z + 1.6 + MOTOR_GAP
    return {'pi_board_bottom': STANDOFF_TOP, 'pi_z': pi_z, 'pi_top': pi_top, 'ai_hat_bottom': ai_z,
            'motor_hat_bottom': motor_z}


def build(doc):
    case_mesh = vendor.mesh_3mf('omt-case-3mf')['Pi Case v11.step']
    case_mesh.translate(*CASE_TO_PI)
    case = doc.addObject('Mesh::Feature', 'OMTCase')
    case.Mesh = case_mesh
    case.Label = 'OMT Pi 5 case (community, MIT), lid left off'
    if App.GuiUp:
        case.ViewObject.ShapeColor = CASE_COLOR
        case.ViewObject.Transparency = 35
    z = stack_heights()
    cadkit.add(doc, 'Pi5', hardware_view.placed(vendor.shape('pi5-step'), 0, 0, z['pi_z']), hardware_view.PCB_GREEN,
               label='Raspberry Pi 5')
    spacers = [Part.makeCylinder(2.5, AI_SPACER, V(x, y, z['pi_top'])) for x, y in HOLES]
    spacers += [Part.makeCylinder(2.5, MOTOR_GAP, V(x, y, z['ai_hat_bottom'] + 1.6)) for x, y in HOLES]
    cadkit.add(doc, 'Spacers', Part.makeCompound(spacers), BRASS, label='M2.5 spacers: 16 mm, then Motor HAT gap')
    cadkit.add(doc, 'AIHat', hardware_view.placed(hardware_view.ai_hat(), 0, 0, z['ai_hat_bottom']), hardware_view.PCB_GREEN,
               label='Hailo-8 AI HAT+')
    cadkit.add(doc, 'MotorHat', hardware_view.placed(vendor.shape('motor-hat-step'), 0, 0, z['motor_hat_bottom']),
               hardware_view.HAT_BLUE, label='Adafruit DC+Stepper Motor HAT')
    box = case_mesh.BoundBox
    if App.GuiUp:
        hardware_view.label(doc, 'case_label', ['OMT Pi 5 case, lid off (open top)', f'{box.XLength:.0f} x {box.YLength:.0f} x {box.ZLength:.0f} mm'],
                            box.XMin, box.YMax + 30, 5)
        hardware_view.label(doc, 'stack_label', [f"AI HAT+ at z {z['ai_hat_bottom']:.1f}", f"Motor HAT at z {z['motor_hat_bottom']:.1f}",
                                                 f'case wall top z {box.ZMax:.1f}'], box.XMax + 10, box.YMax, 5)
    return {'case_bounds_mm': [[box.XMin, box.YMin, box.ZMin], [box.XMax, box.YMax, box.ZMax]],
            'stack_heights_mm': z}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--run', required=True, help='new run name under generated/ultraskelly/case-view/')
    args = parser.parse_args(argv)
    folder = cadkit.run_folder('case-view', args.run)
    cadkit.close_saved_runs(folder.parent)
    doc = App.newDocument('UltraSkellyCase')
    report = build(doc)
    doc.recompute()
    native = folder / 'case-view.FCStd'
    native_sha = cadkit.save_verified(doc, native)
    cadkit.write_report(folder / 'build-report.json', {'part': 'case-view', 'run': args.run, 'units': 'mm',
                                                      'native': {'path': native.name, 'sha256': native_sha}, **report})
    if App.GuiUp:
        cadkit.present(doc, 'isometric')
    else:
        App.closeDocument(doc.Name)
    print(json.dumps({'saved': str(native), **report}, default=float))


if __name__ == '__main__':
    main()
