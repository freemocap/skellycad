# Two supports for the world camera

R05 adds a second support to the hash-verified R04 complete assembly. It runs
back from the world-camera socket and down into the top of the PCB holder.
Its terminal tangent is exactly 90 degrees to the existing arm's terminal
tangent. The centerline lies in a vertical fore-aft plane. Camera, ribbon,
holder, clip, ball/socket relationship, anatomy and baseplate poses are unchanged.

The new beam is 2.8 mm wide, with thickness increasing from 1.5 mm at its embedded
root to 2.6 mm along the arm. Its root and socket engagement volumes are 4.746
and 1.743 mm³. Concave fillets of 0.4 mm at the root and 0.8 mm at the socket
finish the joins. The complete carrier remains one valid solid.

The finished carrier clears the camera, tray, clip, ribbon, existing viewing
regions and fixed board hardware. The axial socket-bore check passes. Its mesh
is closed and has no self-intersections in mount coordinates. These checks do
not establish printed strength, joint fit or a measured adjustment range.
Inherited lens/holder and clip/holder overlaps from R04 remain unchanged.
No print pack is released by this revision.

`source.json` and `review.json` record lineage and native hashes. Generated
`support-validation.json` records the terminal angle, seating, blends and mesh
checks; `final-validation.json` records the assembly checks. The historical
species selector and the separate binocular branch remain unchanged.

Use `open.FCMacro` through the verified existing-session IPC bridge. It saves
and closes only obsolete eye/world review tabs and opens the complete assembly
in top view. Run `build-isolated.FCMacro` only in a separate native FreeCAD build
process; it closes its documents after verified saves.
