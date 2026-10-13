# 58 socket reconstruction candidate

Source is Body44 in 58nassembly.step. parameters.json records source hash, units
and local-to-assembly placement. Original ball-seat radius is 2.1 mm; holder ball
radius is 2 mm. This dimensional difference is not a physical-fit validation.

build.py takes the source in local coordinates, sections it on its axis and
revolves the lower measured profile. Source section polylines are approximated
with cubic splines (201 input samples, requested fit tolerance 1e-5 mm); a
0.000065 mm open section gap is explicitly connected. Revolving also replaces
slight source bore-axis skew with rotational symmetry. The saved native sketch
holds its own curves, with no imported-solid modeling dependency. Profile curves
are fixed baseline geometry; further nominal parameterization is not complete.

UpperCollar is a separate native pad. Live Dimensions controls:
- CollarHeight: 3 mm.
- CollarRadius: 2.70163704523684 mm.
- BoreRadius: 1.45 mm, applies to the upper collar only, not the lower ball seat.

Source passes basic validity but fails deeper BOP checking (C0/curve-on-surface
errors). Rebuilt shape passes the deeper check. Saved model reopens and all three
controls passed independent edit/restore tests in the pinned runtime. There are
12 rebuilt faces versus 11 source faces. Net volume difference is +0.0282873 mm3;
this is not symmetric-difference volume and exact Boolean parity is not claimed.

Bounded surface sampling: 240 points per direction, maximum sampled distances
0.0000173223 mm source-to-rebuild and 0.0000230596 mm rebuild-to-source. These are
sampling results, not certified global deviation bounds. One source edge failed
discretization and fell back to endpoints. The source's own tolerances limit
interpretation of very small distances. No fit or printed hardware acceptance.

Output: generated/mouse-hats/reconstruction/socket/01-socket-candidate.FCStd.
Cyan is the rebuild; gold is source with a display-only 10 mm X offset. Source
local BREP and validation.json are alongside it. verify.py runs outside the GUI
and repeats native-file geometry checks, sampling and parameter edits.
