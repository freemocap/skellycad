# R10 side ledge refinement

Based on the hash-pinned complete R09 body-mounted-arm assembly. User requested moving the vertical ledge upward a bit, reducing its height above the board by 40%, and doubling thickness. Chosen upward shift: 0.5 mm (Y 15.5–17.5). Exposed projection: 1.6 to 0.96 mm. Width: 0.4 to 0.8 mm, centered at unchanged Z -14.903379 mm. Vertical length remains 2 mm. Embed depth remains 0.08 mm; only the old exposed ledge is removed, preserving the plate underneath.

Native carrier is one valid solid. Changes are confined to the old/new ledge volumes. All matched parts and their inherited contacts are unchanged; holder clearance remains 0.333165 mm. New ledge clears the approximate PCB by 0.5034 mm and cap by 1.0924 mm. Exported STLs passed watertight shell checks. Physical fit and full joint travel remain unverified.

Replay build.py in pinned FreeCAD. settings.json stores units and lineage. Export selected checkpoint through current/export_print.py. show.FCMacro adds the revision to the running desktop session without removing prior documents. Latest STL: generated/mouse-hats/active/print-r10/MH-T3-EYE-R10-carrier-and-holder.stl. Existing B2 label is retained.
