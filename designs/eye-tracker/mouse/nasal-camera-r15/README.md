# Mouse nasal camera placement — R15

R15 moves the camera and ball/socket assembly toward the nose and refits both supports and the ribbon to the accepted R04 eye placement. It preserves the R14 eye and skull geometry, main PCB, connector, cap and baseplate. The selected checkpoint remains unchanged; this is a complete review assembly.

## Result

The lens moves 2.985 mm nasally in the accepted skull frame. Its assembly-coordinate shift is approximately (2.921, 0.805, -0.402) mm. The camera ray misses the eye center by 0.000011 mm at a forward distance of 14.694 mm. This numerical alignment is much more precise than the anatomical estimate. Camera and outward eye axes oppose one another with a remaining angular difference of 12.724 degrees.

The socket, holder, clip and sensor receive the same rigid transform. Their mating relationship is unchanged; the new pose is the central joint pose, not extra articulation within the joint. Both rectangular arms are rebuilt between fixed tray roots and transformed socket terminals. Root engagement volumes are 2.135 and 2.446 mm3; each socket terminal engages by 4.657 mm3. The previous label-clearance cut is retained on the finished carrier.

## Pose exploration and tradeoff

Exact coaxial alignment at the original projected stand-off was reachable by the ribbon solver but collided with the fixed tray and lower arm. Increasing stand-off by 3 mm still collided. A 2.5 mm purely nasal shift cleared the holder but left 15.67 degrees of axis mismatch. A scan toward the exact coaxial pose showed decreasing tray clearance: approximately 0.65 mm at 20% interpolation and 0.30 mm at 30%, with interference by 40%. These scan values use minimum-rotation orientation; final validation uses the solved orientation.

The chosen lens position uses 20% interpolation between that nasal-shift pose and the coaxial pose. This is a practical local compromise, not a proof of global optimality. `pose_scan.py`, `search.py`, `refine_ribbon.py` and `solution.json` record the method. Further coaxial improvement may need a different tray layout or mounting arrangement.

## Validation

Full-solid checks find zero ribbon interference with the tested fixtures and camera components. Static clearance is 0.600 mm at the lower guard, 0.710 mm at the upper support and 1.462 mm at the socket. Ribbon contact at board/holder boundaries remains zero-gap without detected overlapping volume. The ribbon is 32.85 x 4 x 0.25 mm; radius parameters are at least 3.75 mm, conservatively leaving 3.5 mm through the thickness. Endpoint frames are constrained during refinement.

The finished carrier is one valid solid. Its mesh is closed with no detected self-intersections. Surface checks find no changed-hardware crossings with either eye or the skull; 2,500 sampled hardware surface points also yield zero containment hits. These geometric checks do not demonstrate physical fit, fatigue resistance or full joint motion clearance.

Inherited carrier overlaps are unchanged: 0.002218 mm3 with the cap and 0.059028 mm3 with the connector. Holder, clip, PCB and lens show no carrier overlap. `interface-validation.json` verifies fixed poses and the common rigid transform of moving parts. Other reports separate solid checks, anatomy, containment and mesh validation.

## Rebuild and review

Read `docs/development.md` and `docs/eye-tracker-targeting.md` first. From the repository root, run `build.py` with the pinned FreeCAD Python runtime. It verifies R14 and selected checkpoint hashes and uses the saved `solution.json`; optimization scripts are exploratory and overwrite that solution if rerun. Run `check_anatomy.py` and `check_interfaces.py` with the same runtime after rebuilding. Preserve the frozen checkpoint identified by `review.json`.

Open `open.FCMacro` through `tools/cad/open_in_running.py` with a freshly verified desktop PID. It opens the generated review without replacing other documents. Do not export for printing unless solid, mesh, interface and anatomy checks pass; physical testing remains separate.
