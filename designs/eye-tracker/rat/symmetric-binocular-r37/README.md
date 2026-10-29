# Symmetric binocular rat R37

R37 makes both printed holders, clips, sockets and support pairs exact reflections
across skull Y=0. The R32 lens positions and optical axes were already symmetric;
its printed mounting geometry was not. R37 preserves those optical poses and the
physical camera geometry. Both lenses remain 19.768 mm from their eye centers.

The mirrored holders receive identical PCB clearance pockets. Both support roots
receive the same mirrored PCB relief. The left ribbon is refitted at its original
32.85 mm centerline length. A 180-degree camera-roll alternative was rejected
because the tested ribbon model could not satisfy that length and bend constraint.

The full-size rounded windows, engraving and shortened central carrier from R36
are preserved. The inherited engraving reads RAT R36; it identifies the retained
print-detail source, not this complete assembly revision. The anatomy and lowered
baseplate are unchanged. Historical checkpoints and the species R01 selector are
preserved; `review.json` identifies this complete assembly for review.

`validation.json` records zero reflected-shape difference for both printed head
assemblies and support pairs, zero lens/axis reflection error, positive support
engagement, no new solid interference, and closed meshes without self-intersections.
All 19 non-baseplate hardware parts have zero skull surface crossings and zero
sampled eye containment. Inherited lens/holder and holder/clip overlaps remain
documented. Geometry checks do not demonstrate physical fit or adjustment travel.

Run `prepare.py`, `ribbons.py`, and `validate.py` sequentially with the pinned
FreeCAD Python. Then run `check_eyes.py` with the CAD tooling Python. Only after
both validation reports pass, submit `open.FCMacro` through `open_in_running.py`
with the verified desktop PID. It saves recovery copies and closes obsolete rat
tabs, preserves unrelated documents, and opens one complete skull-frame review.
The generated R37 review is not a replacement print release for the R36 STL.
