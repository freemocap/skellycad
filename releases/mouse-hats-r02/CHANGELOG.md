# Changes and decisions

## R02

Baseplate exterior tapers inward below Y=1.5 mm; bottom stays at Y=-5 mm.
Bottom width/depth scale 0.57004 matches the measured legacy tapered mesh.
Upper seating and interior mounting geometry preserved. No skull boolean.
Other print files are unchanged from R01. This sharing package adds part IDs,
assembly organization, documentation and validation; it changes no design geometry.

## R01 inherited in R02

Clean two-arm carrier aligned to tray/socket; arm-root and socket blends;
R3 tangent stem/tray blend. PCB retainers +1.5 mm at two arm-end locations and
+0.7 mm at the lower stop. Holder walls +0.5 mm outward each side; clip span
+1 mm with retaining-arm geometry preserved. Ball/neck dimensions unchanged.
Carrier lip side corners trimmed, no front extension; vestigial tray notch removed.

## Earlier reconstruction

58 STEP selected as source baseline, then reconstructed into controlled native
parts. Historical candidate files and rejected trials remain in the playground.
Source snapshot includes older scripts for dependency/context; they are not all
accepted design variants. Current entry points are identified in source/README.md.

## Deferred

Larger coupled ball/neck/socket, extra ventilation/weight openings, and physical
print-test findings. Do not silently change functional mating geometry.
