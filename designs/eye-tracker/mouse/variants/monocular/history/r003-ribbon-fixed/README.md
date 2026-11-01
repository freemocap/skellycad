# Fixed-cradle ribbon study R03

R03 corrects the scope of R02: keep the sensor cradle, ball, socket and clip at
the accepted assembly placements; remove only the two connecting arms. The
measured sensor PCB stays seated in its R01 notch-aligned pose. Neither PCB
position nor orientation is an optimization variable.

## Fixture preservation

`fixture.py` verifies the selected ET-MOUSE-MONO-R01 checkpoint hash. It retains
the holder (including its ball), clip, cap and baseplate without geometric
change. Boolean symmetric differences against the checkpoint are zero.

The socket belongs to the fused carrier. A hash-verified historical socket
shape plus its collar defines an extraction mask; intersecting this mask with
the accepted carrier retains the actual accepted surfaces. Small lower-body
markings excluded by the historical tray helper are also retained. Subtracting
the retained carrier regions leaves exactly two solids: the two arms, with
volumes approximately 57.859 and 206.439 mm3. Nothing is translated or mirrored.
`fixture-validation.json` records the extraction, lineage and pose checks.

## Ribbon model and result

The neutral surface is a 32.85 x 4 mm unstretched rectangular sheet mapped through
three cylindrical bend zones and straight regions. Each zone has a radius,
signed bend angle, bend-axis angle in the original flat sheet, and preceding
gap: twelve search parameters. Angled bend axes permit spatial turning while
preserving the sheet metric. Curvature may change abruptly at zone boundaries;
this is a geometric route, not a prediction of the ribbon's relaxed shape.

The first neutral radius is bounded between 3.575 and 5.075 mm; the other two
between 3.575 and 12 mm. With assumed thickness 0.15 mm, this corresponds to a
minimum inside radius of 3.5 mm, based on the user's comfortable 7 mm rod.
The solver matches both the endpoint position and complete endpoint frame.
The builder rejects an endpoint position or matrix error above 1e-5. It never
moves the sensor to compensate. Collision checks are performed after solving;
they are not part of the current least-squares objective.

The first passing candidate has inside bend radii of approximately 3.774,
8.797 and 3.923 mm, with 0.451 mm of straight entry across the full width.
Its endpoint position error is below 1e-8 mm. The mathematical surface preserves
length and width; sampled differential length/shear errors are below 6e-10.
The solution is a three-dimensional loop and is not asserted to reproduce the
user's physical S curve exactly.

The 0.15 mm thick tessellated solid is valid and closed, with no detected mesh
self-intersection. Full-solid Boolean checks find zero ribbon overlap with the
socket, cradle, clip, retained tray, cap, baseplate and measured camera components.
The ribbon and anatomy bounding boxes are disjoint. These checks validate this
modeled route at its tessellation resolution; they do not establish material
stress, physical assembly procedure, or the accuracy of assumed thickness.

## Reproduce and open

From the repository root, use the pinned FreeCAD bundled Python to run:

1. `designs/eye-tracker/mouse/camera-fit-r01/build.py` to generate the measured,
   seated rigid camera input if it is absent.
2. This directory's `fixture.py` to extract the fixed fixture.
3. `solve.py` to find the endpoint-constrained route with a deterministic seed.
4. `build.py` to generate and validate the finite-thickness ribbon.

Outputs are under `generated/eye-tracker/mouse/ribbon-fixed-r03/`. Open
`open.FCMacro` through the existing FreeCAD listener, following
`docs/development.md`. It checks `validation.json` before showing the ribbon in
`mouse-fixed-cradle-r03-verified.FCStd`. The accepted checkpoint and its matched
print parts remain unchanged. No new arms are defined or selected for printing.
