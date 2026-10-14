# Arm-free mouse camera layout R02

**Superseded for this task:** R02 incorrectly freed the sensor pose and removed
the cradle/socket. Use [fixed-cradle R03](../ribbon-fixed-r03/README.md), which
removes only the two arms and preserves the seated camera pose.

This exploratory layout removes the accepted carrier's support/socket region,
sensor holder and clip. It retains the extracted PCB tray, matching cap and
baseplate. It does not select a new checkpoint or define printable replacement
arms. The selected complete assembly remains ET-MOUSE-MONO-R01.

## Inputs and choices

The user reported a 32.85 mm free ribbon length, 4 mm width, a backward S bend,
a comfortable 7 mm rod diameter, a preferred 10 mm rod diameter, a gentle
reverse bend, and a nearly flat sensor entry. Sideways motion is possible but
stiffer; stretching is not allowed. Roughly 10 mm downward displacement and
90 degrees of sensor rotation describe the physical route, not exact measured
attachment constraints.

The model uses two cylindrical bend zones with independently angled bend axes.
Each zone maps the flat sheet onto a cylinder without changing its intrinsic
length or width. Angled axes redirect the sheet in space without stretching it.
Straight regions connect the bends and the rigid boards. This is a geometric
construction, not a material-energy or force simulation. It excludes many other
possible ribbon shapes; failure would not establish physical incompatibility.

The seven search parameters are first radius, signed first angle, first axis
angle in the flat sheet, second radius, signed second angle, second axis angle,
and separation between bend-zone envelopes. `solve.py` contains their bounds
and objective weights. The main PCB pose stays fixed. Sensor pose follows the
ribbon endpoint; eye aim is the main objective, with weaker preferences for
height, standoff and the preferred first radius. The 90-degree observation is
not yet an independent objective. The solver searches 35 deterministic starts.

Thickness is assumed to be 0.15 mm. Neutral-surface radii are 0.075 mm larger
than the corresponding inside bend radius. Minimum inside radii are 3.5 mm for
the first bend and 5 mm for the second. These are empirical routing choices,
not manufacturer limits. The source dimensions and provisional component
identities remain those of the shared camera R03 study.

## First candidate

- First inside radius: 3.5 mm; bend angle: approximately -158.86 degrees.
- Second inside radius: 5 mm; bend angle: approximately +154.70 degrees.
- Straight entry across the full width: approximately 1 mm.
- Sensor attachment: (-15.473, 9.529, 10.216) mm in the inherited assembly frame.
- Drop from the main ribbon attachment: approximately 6.284 mm, short of the
  rough 10 mm preference. The sensor is substantially behind the old holder.
- Aim error: approximately 0.461 degrees from the inherited eye-surface proxy.
  This target is not a verified pupil location or an optical calibration.

The native finite-thickness tessellated solid is valid and closed, with no
mesh self-intersection detected. Boolean checks report zero ribbon overlap with
the retained tray, cap, baseplate, both PCBs, lens envelope, LEDs and provisional
JST connector. Ribbon/anatomy bounding boxes are disjoint. Numerical local
length and shear errors of the analytic neutral surface are below 5e-10.
These checks concern the ribbon and do not certify the entire retained rigid
assembly, physical bend stresses, optical visibility through anatomy, or grip.
The aim line has zero intersection length with the retained printed hardware.

## Rebuild and review

Use the pinned FreeCAD bundled Python from the repository root. First run
`designs/eye-tracker/mouse/camera-fit-r01/build.py` to regenerate the rigid camera
fit input. Then run this directory's `solve.py`, followed by `build.py`.
The builder verifies the selected checkpoint and extracted tray hashes.

Outputs are under `generated/eye-tracker/mouse/ribbon-layout-r02/`:
`candidates.json`, `validation.json`, `mouse-arm-free-r02.FCStd`, and
`ribbon-candidate.stl`. The STL is a schematic ribbon, not a part to print.
The native file retains the rigid camera parts and review aim line.

Open this directory's `open.FCMacro` through the existing FreeCAD listener, as
specified in `docs/development.md`. It refuses to show the ribbon if the recorded
ribbon validation fails. Review the rearward sensor position with the anatomy
visible before designing replacement arms. The accepted matched parts remain
available at their unchanged checkpoint paths.
