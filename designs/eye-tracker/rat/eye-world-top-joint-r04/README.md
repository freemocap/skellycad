# Level world camera with a top ball joint

R04 levels the world-camera tray's long edge with the PCB holder and moves the
lens 2 mm forward from R03. The fixed-length ribbon solution also lowers it
1.635 mm and moves it 0.050 mm laterally. The optical axis remains skull-world
+X; the tray long edge is world -Y. All dimensions are in millimetres.

The actual R43 ball stem is extracted below the tray back and rotated upward
onto the tray's top edge. Its matching socket receives the same rigid transform,
preserving the ball/socket relationship. A continuous arched support connects
the socket wall to the PCB holder's top edge. The bore remains open. Concave
0.8 mm fillets finish the support root and socket junction; a 0.4 mm fillet
finishes the new stem attachment.

The central holder, retained right-eye arms and right socket are rebuilt from
their source solids. This removes the old left-arm remnants without clipping
the holder. The retained eye-arm junctions are finished again. The right-eye
camera, ribbon, skull and baseplate remain fixed. The binocular branch remains
unchanged.

## Validation

The 32.85 × 4 × 0.25 mm ribbon uses cylindrical bends, with a minimum modeled
inside radius of 3.881 mm. The solved endpoint meets the forward position and
level orientation constraints. Length/shear mapping errors are below 1e-5.
This is geometric validation, not a strain or fatigue simulation.

Finished solids, full ribbon/fixture collisions, right-eye viewing clearance,
provisional world viewing clearance, socket bore access, and new-part skull
crossings pass. The carrier and world-holder meshes are closed and free from
self-intersections in their mount/head coordinate frames. An eventual print
export must validate its actual orientation and mesh.

The inherited lens-envelope/holder overlap of 1.91318 mm³ and clip/holder
overlap of 0.00794 mm³ remain unchanged. Optical focus, calibrated field of view,
physical ribbon handling, adjustment range and printed joint fit are unverified.
This is a review candidate, not a released print pack.

## Records and review

`review.json` identifies the complete native assembly, hash and R03 lineage.
`selected-pose.json` records the ribbon parameters and camera frame. Reports
under `generated/eye-tracker/rat/eye-world-top-joint-r04/` separate pose,
support, finishing, fixture and final assembly checks. The species selector
remains historical R01; this fork uses its explicitly identified, hash-verified
R03/R43 sources.

Use `open.FCMacro` through the verified existing-session IPC bridge. It saves
and closes only obsolete reviews of this eye/world fork. Run
`build-isolated.FCMacro` only in a separate native FreeCAD process; it closes
its build documents after verified saves.
