# Forward mount and cylindrical ribbon bends R39

R39 is a complete rat binocular review candidate derived from hash-verified R38.
The historical species selector remains R01; `review.json` selects this newer
complete assembly. R38 is preserved. The user's physical trial reported that
R38's ribbon twisting was not workable, despite its earlier static clearance pass.

The mount moves 9 mm forward and 0.7201 mm down to follow the sampled skull-roof
height at the baseplate center. Baseplate geometry and thickness are preserved;
seating and anatomical placement remain provisional. Central PCB support remains
1.8 mm thick.

Both ribbon routes use the existing piecewise cylindrical sheet map, with a
32.85 by 4 mm sheet and 0.25 mm thickness. The model does not impose axial twist
to reconcile endpoints. It permits oblique bend axes. Numerical surface metrics
check stretch and shear; finite-thickness solids are checked against the hardware.
Minimum inside bend radii are 3.5 mm, meeting the recorded 3.5 mm limit.
This geometry does not simulate material force, springback or fatigue. Physical
ribbon handling is still required before accepting the design for printing.

Lens positions and viewing axes are mirrored about skull Y=0. Camera frames
are mirrored with a half-turn orientation difference, keeping the accepted
upside-down alternative. The initial independent-roll candidate remains in
`generated/eye-tracker/rat/forward-mount-r39/initial-roll-study/` for traceability;
it is superseded by the symmetric-frame fit. Main board orientation is preserved.
Small rounded relief cuts in the printed carrier provide 0.25 mm clearance around
ribbon-exit interference regions. The PCB support retains its 1.8 mm nominal
thickness; the skull baseplate is unchanged.

The four arms use flared roots and socket ends with the R38 nominal section
sizes. Each route is fitted separately. The left socket-port assignments are
swapped to accommodate the camera half-turn without forcing crossed supports.
Six junctions have 0.4 mm fillets; the two right carrier roots have 0.3 mm chamfers.
Junction and final geometry results are
recorded in the generated reports. The label occupies the existing rail area;
functional geometry is not enlarged to accommodate text.

To reproduce the selected geometry, run scripts from the repository root with
pinned FreeCAD Python: `mount.py`, `prepare_selected.py`, `place.py`,
`validate_ribbons.py`, `arms.py`, `fillets.py`, `finish_missing.py`, and `label.py`. Preserve or move
existing generated output first: `arms.py` resumes its partial state when present.
`prepare_selected.py` reconstructs the frozen parameters in `selected-pose.json`;
it does not rerun the pose search. Run `check_label.py` with tooling Python, then
`validate.py` with FreeCAD Python and `check_eyes.py` with tooling Python.

The other search scripts preserve the exploration history, including the stricter
camera-frame search and the final finite-thickness radius correction. Their
candidates are not interchangeable with the selected complete assembly.

`open.FCMacro` requires the final validation reports and opens the complete saved
assembly in the existing FreeCAD session, saving and closing obsolete rat task
tabs. No R39 print pack is released by this work. Review the routing in FreeCAD
and physically form the ribbons before requesting an updated print export.
