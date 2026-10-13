# Learning route

This is a reusable course outline, not a list of prerequisites for the original
user's next project. They have completed enough to begin real-part work.

| Step | Exercise | Inspect / try | Original-session status |
| --- | --- | --- | --- |
| 1. Inputs and dependencies | workflow-cube | Change length; predict linked height; inspect Cut Base/Tool | Completed |
| 2. Export boundary | workflow-cube/export_mesh.py | Compare native solid, STEP and unitless STL | Export checked; printing skipped |
| 3. Sketch intent | practice-mount, sketch through pocket | Explain constraints, origin reference, degrees of freedom, Pad and ThroughAll | Completed |
| 4. Feature dependencies | practice-mount, two/four holes | Resize plate; holes retain equal size and edge margins | Completed |
| 5. Fabrication choices | chamfer/fillet alternatives and fit-coupon | Explain chamfer leg size vs diagonal; radial vs diametral clearance; text extrusion | Concepts completed; physical trials deferred |
| 6. Camera bracket | bracket envelope through interfaces | Follow named dimensions into cradle, slot, strap, optical/cable keep-outs | Fictional teaching model completed |
| 7. Assembly reasoning | support, motion, explosion, access | Separate shape edits from placements; identify permitted motion and tool space | Geometric study completed |
| 7b. Requirements and variation | stack_study.py | Compare nominal and worst-case stack; distinguish measured facts from assumptions | Hypothetical study completed |
| 8. Real-part reconstruction | User-supplied next project | Preserve baseline, map interfaces, rebuild one bounded part, compare | Not started |

## Teaching rhythm

State intent -> show a short actual code excerpt with verified line numbers ->
make a visible change -> inspect and explain -> validate -> preserve a checkpoint.
Use a pace appropriate to the learner. Do not build many unexplained features
before showing them. A code-oriented learner can inspect the GUI while the agent
operates through Python; using the GUI for every modeling action is not required.

For the original learner: FreeCAD Blender navigation and a G HUB application
profile are configured. Do not reset them or introduce custom mouse scripts.
Printer is Snapmaker U1, PLA, Snapmaker Orca; no automated print was requested.

## Useful distinctions

- Parameters change a manufactured shape; placements move an existing shape.
- Clearance is an intentional gap; tolerance is permitted variation.
- Geometric validity, assembly fit and mechanical strength are different checks.
- Animation prescribes motion; a joint solver maintains relationships; neither
  by itself proves strength, friction or actual assembly access.
- A reference or hidden object is not automatically excluded from an export.
- A snapshot result is not a live dependency. Read each chapter's refresh limits.

## Real-project transition

The original user will add new files in a new folder in the same playground and
discuss scope. Do not access the old client checkout or create another chat.
Preserve the supplied baseline, inventory its formats and components, identify
functional interfaces, choose one representative part, reconstruct cleanly,
compare critical geometry, and expand only with the resulting understanding.
