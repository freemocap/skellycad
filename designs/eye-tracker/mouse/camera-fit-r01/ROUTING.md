# Ribbon routing correction

The first mouse-fit curve is rejected. It intersected the carrier. The user
confirmed that the physical assembly fits and that the ribbon goes rearward,
then around the carrier. This demonstrated fit is the target to reproduce.
The failed curve is not evidence that the physical hardware cannot fit.

The initial implementation constrained only a cubic centerline's length and end
tangents. It omitted obstacle constraints, ribbon width and material metric.
It must not be reused as a fitted route or promoted under a different label.

## Chosen approach

Use a rear-path initial configuration and a constrained strip model:

- Pin attachment positions and orientations to the two PCBs.
- Preserve the measured 32.85 x 4 mm neutral surface. A triangulated strip can
  preserve its intrinsic geometry by constraining every material triangle edge.
- Model easy bending, harder sideways bending and twisting through explicit
  penalties; these are geometric preferences until calibrated with material data.
- Include hardware contact constraints across the strip surface, not only along
  its centerline. Check the eventual finite-thickness solid independently.
- Reject length/width changes, collisions, self-intersection, broken attachment
  constraints, or solver failure. Never show a rejected result as a fitted ribbon.

SciPy provides the constrained optimization machinery [@scipyConstrainedMinimize].
This requires custom geometry and constraints; it is not an installed ribbon
workbench. FreeCAD supplies the actual hardware solids and final Boolean checks.
For later force/stress questions, FreeCAD FEM/CalculiX has contact capabilities
[@freecad11FemContact], but using them would require a laminate/material model,
loads and appropriate nonlinear analysis. No FEM simulation has been run.

## Diagnostic results

Scratch experiments are under `generated/eye-tracker/mouse/routing-debug/`.
A collision-free swept candidate had approximately 38.7 and 38.5 mm longitudinal
edges despite a 32.85 mm centerline. It was rejected for stretching the strip.
A constrained triangulated candidate preserved all material edge lengths to
about 1.3e-11 mm, but independent solid checks found about 1.037 mm3 overlap
with the carrier and 0.055 mm3 with the holder. It was also rejected.
These examples demonstrate why both metric and solid-contact checks are needed.
No accepted replacement ribbon or new printable hardware is selected by this note.

## Subsequent arm-free study

The user authorized a separate layout with the arms removed.
[Arm-free R02](../ribbon-layout-r02/README.md) now has a two-bend cylindrical
sheet candidate that passes its documented ribbon geometry checks. It allows
the sensor pose to change and therefore does not solve the original fixed-arm
route. No replacement arms or new checkpoint are selected.

## Corrected fixed-cradle scope

R02 misunderstood the requested fixture. [R03](../ribbon-fixed-r03/README.md)
retains the cradle, ball, socket and clip at their original placements, removes
only the two arms, and has a ribbon candidate passing the documented endpoint
and finite-thickness geometry checks. The sensor pose is fixed.
