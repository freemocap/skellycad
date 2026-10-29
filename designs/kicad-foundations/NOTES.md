# Teaching preferences and session state

The user wants the code-assisted, inspectable workflow used for FreeCAD, without
mouse/keyboard takeover. Use Python generation and CLI validation. Live PCB IPC
is optional and remains untested; do not make it a prerequisite for lessons.

Open HTML lessons as rendered pages, either inside Codex's browser or in the
desktop browser, never as source files in an editor. Launch desktop applications outside the sandbox so their
windows appear on the user's desktop. A background process alone does not prove
that the user can see the document. Opening requested documents is authorized;
mouse/keyboard automation remains outside this workflow.

The user explicitly rejects quizzes and prediction prompts. Keep explanations
short, practical and tied to actual artifacts. The introductory LED discussion
is complete as a walkthrough; do not require a demonstration of understanding.

The target is a camera module with a four-pin JST connection carrying USB, not
an extended LED course. The canonical guide is lessons/walkthrough.html. Use its
four broad stages, one at a time, and reproduce the FULL checkbox list whenever
mentioning curriculum progress in chat. The user chose to reuse an existing USB
camera board first, then examine its electronics. Exact board and electrical
pinout still need identification; the existing Pupil Core mechanical reference
is a candidate, not evidence of its electrical connections.

Stage 02 of the LED reference has assigned footprints and passed ERC. It is a
supporting example, not a reason to delay the camera architecture discussion.

The isolated official Python client was installed at
`tools/electronics/.venv` (kicad-python 0.8.0). The first lesson does not require it.
The user may open the project themselves; no desktop automation is authorized
for this workflow.

## Camera route update — 2026-10-27

The later discussion supersedes the USB-board-only starting point above. Start
with a documented MIPI camera module and supported receiver; keep USB conversion
as a separate system decision. R01 studies the Pi 4 15-pin host interface.
Exact Arducam OV9281 SKU, cable and image mode remain unverified. The canonical
four-stage checklist is in the rendered walkthrough; all outcomes remain open.
Do not treat R01 ERC success as a functioning camera or a fabrication approval.

The documentary bench reference is now B0224, its supplied 150 mm 15-to-22-pin
cable, and Pi 4B. See camera-interface/README.md for evidence and limits.
Physical validation remains pending. Keep the lesson moving through design
concepts without representing advertised modes as measured performance.

## Completed digital course artifacts

R02 completes the digital walkthrough: architecture, routed KiCad board,
FreeCAD mounting study, manufacturing-output demonstration and multi-head
payload explainer. The canonical checked list tracks those deliverables.
Do not put the completed lessons back behind purchasing or hardware testing.
Keep physical validation separately pending; never call the coupon a validated
MIPI adapter or the multi-head study an implemented product.
