# Mouse complete assembly with landmark-based eyes — R14

R14 integrates the [R04 anatomical placement](../landmark-eyes-r04/README.md) into the complete R13 assembly. Both eye optical frames move; their adult shapes and visible axes remain attached. The camera, plug, lens, ribbon, support, matched mounting parts and skull retain their previous geometry and poses.

`recipe.json` records the input checkpoint hash and targeting recipe. `validation.json` confirms every non-eye shape and pose is unchanged and finds zero eye surface crossings with the existing skull, detailed reference atlas or tessellated hardware. Surface-intersection checks are not proof of physical fit or anatomical accuracy.

The fixed camera axis misses the new Eye1 globe center by 2.465 mm, at 14.982 mm forward distance. Camera aim is therefore a separate follow-up; this revision does not claim that the camera is centered on the newly placed eye. Fixed interfaces, ribbon routing and arm seating inherit R13 unchanged.

`review.json` identifies the frozen complete assembly. `open.FCMacro` opens and styles the generated review in the existing FreeCAD desktop session. `../landmark-eyes-r04/integrate.py` verifies the selected checkpoint and R13 source hashes before rebuilding. Follow `docs/development.md` for the pinned runtime and desktop workflow. The selected `active-model.json` remains unchanged; R14 is a review checkpoint alongside its baseline.
