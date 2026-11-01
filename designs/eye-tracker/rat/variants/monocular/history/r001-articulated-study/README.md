# Rat articulated arm concepts

Open `build.FCMacro` through the existing FreeCAD listener, then run
`present.FCMacro` for the uncluttered side-by-side comparison (A on the left,
B on the right). The build reuses an existing
study tab. Units are millimetres; R21 is hash-verified and preserved.

- **A: shoulder hinge, elbow hinge, camera ball joint.** Two blue links and
  parallel single-axis pivots show a simpler adjustment strategy.
- **B: shoulder hinge, elbow ball joint, camera ball joint.** The elbow reuses
  the R21 camera socket shape, with a schematic ball and a stem to the existing
  camera joint. It adds directional freedom at the elbow.

Both have the same chosen shoulder, elbow and camera centers. The actual R21
tray, camera parts and camera socket are reused. Hinges, links, pivot screws and
guide rings are illustrative geometry, not fitted mechanisms. In particular,
fork/tongue details, ball capture and stem exits, clamp force, screw access and
motion clearance remain unresolved. Yellow is the inherited R21 ribbon route;
the guide silhouettes do not establish cable capture or a feasible moving route.
No skull or baseplate is displayed, to keep the mechanism comparison legible.

Noga's articulated holders establish the prior-art combination of links,
swivel clamps and ball ends [@nogaArticulatedHolders]. SmallRig's double-ball
arm provides another clampable camera-support precedent [@smallrig3874DualBall].
These are mechanism references, not downloaded CAD or scaleable product designs.
No manufacturer load rating, patent clearance or miniature fit is claimed.
The concepts use separate clamp placeholders, not Noga's centralized locking.

This study is not a complete working assembly, a kinematic simulation, or a
print release. Choose the joint strategy before solving motion, ribbon guidance,
mounting tabs and M2 hardware. No active species selection is changed.
