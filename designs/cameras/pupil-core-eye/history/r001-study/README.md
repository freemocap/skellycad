# Pupil Core camera geometry and ribbon study R01

Open `open.FCMacro` in the existing FreeCAD session. It imports the reusable
`camera_study` module and builds three camera instances: straight, 90 degrees,
and 180 degrees. Expand an instance, select **Ribbon - edit BendDegrees**, and
change **Data > Routing > BendDegrees** between 0 and 180. The rigid camera head
moves with the ribbon endpoint. Move the containing camera App::Part to place
the whole camera. The module must remain importable for parametric recomputation;
opening the macro establishes that path for this FreeCAD session.

Outputs are rebuilt under `generated/eye-tracker/shared/camera-study-r01/`:
`camera-flex-study-r01.FCStd`, a static STEP snapshot, and `validation.json`.
The native file preserves named, colored parts and editable bending. STEP carries
static solids, not the Python behavior. STL is suitable for a mesh snapshot but
would discard the assembly and bending controls.

## Source and scale

The supplied Blender file and photograph remain unchanged. `blender-scene.json`
preserves evaluated world-space vertices, triangles, names and the Blender hash.
To refresh it after editing the source, run from the repository root:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup designs/eye-tracker/shared/cameras/pupil-core-eye/pupil-core-eye-camera.blend --python designs/eye-tracker/shared/cameras/pupil-core-eye/study-r01/export_blender.py
```

Blender declares metric units with scale 1.0. This study explicitly interprets
one coordinate unit as **1 mm**, provisionally, based on the photograph and
plausible component dimensions. It does not multiply the coordinates by 1000.

| Part | Supplied geometry interpreted in mm | Treatment |
| --- | --- | --- |
| PCB | 8.381 x 28.257; zero thickness | Original outline extruded 0.25 mm below its surface |
| ribbon | 3.940 x 31.302; zero thickness | Analytic cylindrical strip, assumed 0.15 mm thickness |
| camera-pcb | 5.471 x 14.191; zero thickness | Original notched outline extruded 0.25 mm |
| M4-lens | 5.488 x 5.488 x 0.988 | Supplied box, not a threaded or optically calibrated lens |
| JST-4pin | 6.199 x 4.411 x 1.773 | Supplied solid envelope |
| IR-LED / IR-LED.001 | Each 0.975 x 2.098 x 0.988 | Supplied solid envelopes |

The thickness assumptions are display/clearance placeholders, not measurements.
The source leaves a 0.222 mm gap between ribbon and camera PCB; it is preserved
rather than silently extending the ribbon. No hidden components, mounting holes,
connector internals, copper layers or optical prescription are invented.

The four closed mesh envelopes convert to valid CAD solids; planar board
boundaries become extruded solids with the original notch preserved. This is a
small enough mesh conversion to retain the supplied geometry directly. General
mesh conversion produces topology, not an editable sketch history
[@freecadMeshToPart]. These solids are useful for placement and Boolean clearance
checks, but their fidelity still depends on the source measurements.

## Reference frames and bending

The main attachment frame is at the center of the ribbon's lower edge.
Local +X spans ribbon width, +Y runs along the straight ribbon toward the sensor,
and +Z is the board surface normal. The head attachment frame starts at the
ribbon's upper edge. All supplied head geometry is expressed relative to it.
The blue optical guide uses head +Z provisionally; the source contains no measured
optical axis or focal datum. All frames are right handed.

For bend angle theta in radians and free length L, the neutral radius is R=L/theta.
The ribbon endpoint is (0, R sin(theta), R[1-cos(theta)]); the head rotates theta
about +X. The straight limit is (0,L,0). Width is constant and every longitudinal
line on the neutral mid-surface retains length L. The cylindrical surface can be
unrolled without stretching. Finite-thickness inner and outer fibers necessarily
have different lengths: the model's no-stretch constraint is on the neutral
surface, not every fiber in the laminate.

At 90 degrees R=19.927 mm; at 180 degrees R=9.964 mm. These are examples derived
from free length, **not minimum safe bend radii**. The prototype allows easy-axis
bending only; it does not model sideways bending, twist, contact, gravity, stress,
fatigue, strain relief or the laminate's actual neutral-axis location. Flex
construction and thickness affect bend limits; general design guidance cannot
certify this particular camera [@allFlexBendRadiusPartI].

## Route toward independently placed boards

1. Confirm physical scale, free flexible length, thickness and attachment edges.
   Keep the connector and populated board regions rigid for layout purposes.
2. Register the main PCB and camera-head frames to the existing mouse carrier and
   lens holder. Check source dimensions against the accepted fit envelope before
   choosing a new compatible mount profile. Repeat the same interfaces for rat.
3. Add a planar route solver using straight spans and smooth bends, fixed arc
   length, endpoint positions and tangents, with obstacle and radius constraints.
   Reject infeasible configurations instead of stretching the ribbon. A simple
   check is that endpoint distance cannot exceed the available length; endpoint
   orientations, bends and obstacles impose additional constraints.
4. If needed, extend to a spatial rod/strip solver with different easy/hard bending
   stiffnesses and torsional stiffness. Minimize a bending/twisting energy subject
   to length, pose and contact constraints. Different initial routes may settle
   into different solutions; offer candidates for review.
5. Calibrate stiffness and allowable curvature using manufacturer information or
   measurements. Reserve detailed laminate/contact finite-element analysis for
   questions about stress or reliability that the layout model cannot answer.

Steps 3-5 are proposed work, not implemented physics. A visually smooth curve is
not evidence of a natural resting shape. FreeCAD holds the solids and placement
frames; a numerical routing solver can return the ribbon centerline and frame
along its length, from which we generate the CAD surface and clearance envelope.

## Integration and checks

The accepted mouse and rat complete assemblies retain their selections. The
`pupil-core-eye-inherited` profile remains the original R10 fit envelope; its
small files were restored after the folder rename so existing recipes resolve.
The new `pupil-core-eye` profile is a study and has no released mount compatibility.
`create_camera(doc, name, degrees, offset)` is the shared entry point for future
species-specific registration; the core camera geometry has no species dependency.

The build checks valid single solids, ribbon volume L*w*t, constant neutral length
and head endpoint placement. `validate_study.py` additionally checks recomputation
at other angles, rigid relative geometry, saved-file restoration, and STEP solids.
These are geometry checks, not demonstrated physical fit.

To rerun the geometry checks after opening the study, run from the repository root:

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/shared/cameras/pupil-core-eye/study-r01/validate_study.py
```

Success writes `verification.json` with `passed: true` and 21 STEP solids. The
validator uses a separate process and does not change the desktop study. Source
Blender/photo hashes and provisional assumptions are recorded in `provenance.json`.
