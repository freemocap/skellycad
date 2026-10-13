# Mouse-hats active scope

Rebuild old/df-hardware/camera-assembly/cad/53nassembly/53nassembly.step into
clean parametric FreeCAD parts and an assembly. The STEP is authoritative for
this phase. Do not perform STL comparisons, mesh registration, two-arm studies,
or later-variation work until the user explicitly resumes that scope.
Preserve all supplied files. Prior mesh exploration is inactive, not a baseline.

User authorized inspecting older supplied STEP/F3D sources to recover the cap,
ball/lens holder and clip missing from 53. Inspect 52 STEP first. Keep source
generation explicit; do not silently substitute its carrier for 53's carrier.

User subsequently supplied old/58nassembly.step and old/58nassembly.f3d as newer
sources and authorized inspection. 58 STEP contains cap, clip, holder, main,
two baseplate alternatives and Body44. User confirmed 58 is the correct assembled
design and authorized it as the reconstruction baseline, superseding 53.
Resolve baseplate alternatives before manufacturing output. See docs/source-58.json
and functional-map.md. Start bounded reconstruction with the camera clip.

User confirms the current design fits together nicely. Preserve its geometry and
fit during code/parameter refactoring. Do not introduce geometry changes merely
to demonstrate controls. Require an explicit functional reason for any geometry
change; discuss the intended change before adopting it. Added pocket clearance
defaults to zero, including visible review files. Nonzero test probes are isolated
verification experiments, not approved design changes or fit recommendations.

User has now explicitly resumed the mesh phase: use V5 STL to recover the camera
head pose and two arm paths (top bent arm and rear U-shaped arm). Preserve ribbon
space and work toward parameterized printable variants. Prioritize arms first;
PCB groove thickening/deepening and other strengthening details are later work.
Registration and mesh comparison are authorized within these supplied local files.
