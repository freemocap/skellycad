# R08 vertical side ledge

Adds the short vertical ledge requested at the red mark, on the PCB side of the panel above the far hole. Centerline Z = -14.903379 mm aligns with that hole's outer edge. Height 2 mm (Y 15–17), width 0.4 mm, exposed projection 1.6 mm from the seating face; 0.08 mm embedded into the plate. Plain rectangular profile with no hooked return, matching the upper ledge's projection and thickness.

Complete baseline is hash-pinned R07/B2, with all matched parts retained. No previous carrier material removed. Added volume approximately 1.28 mm3. New ledge clears the approximate PCB by 0.7034 mm and cap by 1.5924 mm. All inherited part intersections and holder gap unchanged. Carrier is one valid solid. Physical fit still needs testing.

Replay build.py in pinned FreeCAD, validate and update active-model.json, then use current/export_print.py. settings.json stores dimensions and lineage; validation.json records native checks. show.FCMacro adds the new revision to the running desktop session, retaining all open documents and its viewing direction. Send through tools/cad/open_in_running.py outside the sandbox; do not launch another FreeCAD.

Exports: generated/mouse-hats/active/print-r08/. The carrier retains the B2 arm label; filename R08 identifies the added side ledge. Carrier/holder STL preserves their print-in-place relationship. Use existing slicing/support settings; no printer job submitted.
