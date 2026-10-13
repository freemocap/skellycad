# Selected revision: MH-T3-EYE-R10

The vertical ledge is shifted up 0.5 mm, projects 0.96 mm (40% less), and is 0.8 mm wide (double). R09 body-mounted arms and matched parts are retained. See [R10 notes](../side-ledge-r10/README.md). Exports: generated/mouse-hats/active/print-r10/.

## Historical notes

# Selected print-test revision: MH-T3-EYE-R09-STUDY

The user approved the socket-body attachment version for STL export. Current print files are in generated/mouse-hats/active/print-r09/. The unchanged study checkpoint is now selected by the manifest, retaining its STUDY ID. Native and watertight STL checks passed; physical fit and angular travel remain unverified. Matched cap, clip and baseplate are unchanged from R08.

## Historical notes

# Selected revision: MH-T3-EYE-R08

B2 now includes the requested small vertical side ledge at the far hole. See [R08 notes](../side-ledge-r08/README.md). Camera, loop, upper ledge and matched cap are retained. Print files: generated/mouse-hats/active/print-r08/.

## Previous revision notes

# Selected revision: MH-T3-EYE-R07 / B2

B was selected from the user's physical print test. R07 bows the inner curve toward the plug by up to 4.26 mm, with a 25-degree angled departure at the unchanged root. The flat PCB ledge, T3 cap/rail, camera position and matched parts are retained. See [R07 notes and replay](../b-flared-loop-r07/README.md). Current exports: generated/mouse-hats/active/print-r07/. Physical B2 fit is pending. The active manifest is authoritative; older notes below are history.

## Historical R06 notes

# Selected revision: MH-T3-EYE-R06

The PCB catch now has a flat ledge with its downward return removed. See [R06 notes](../flat-ledge-r06/README.md) and [validation](../flat-ledge-r06/validation.json). The matched cap and engagement rail are unchanged. A/B/C arm testing is still pending; R04's arm remains the reference. The manifest selects the R06 checkpoint and builder. Current exports are in generated/mouse-hats/active/print-r06/. The R05 comparison pack remains the historical pack currently being tested.

## Previous R04 reference notes

# Current mouse-hats model

**MH-T3-EYE-R04** is the current complete assembly: T3 PCB retention and matching cap, neutral eye alignment, and the requested compact rear arm attached directly below the adjacent circular tray hole.

The sole selector is [active-model.json](active-model.json).
The latest print comparison is [R05 A/B/C loop-space options](../loop-options-r05/PRINT-NOTES.md),
with old text removed and new A/B/C labels. No winner has been selected; R04 remains the reference.
Open [the native checkpoint](checkpoints/MH-T3-EYE-R04.FCStd).
The prior [R03 checkpoint](checkpoints/MH-T3-EYE-R03.FCStd) remains preserved.

## R04 change

The rear root moves 4.35 mm down and 4.67 mm toward the hole's center along the panel. Rearward projection drops from 19.96 to 11.20 mm (43.9%). Root section is 2.6 x 2 mm to fit below the hole. Camera and socket positions are unchanged.
See [R04 notes and replay](../compact-arm-r04/README.md) and [validation.json](validation.json).

One valid carrier solid; no holder, clip, PCB or baseplate overlap. Holder gap remains 0.333165 mm. Both tray holes, T3 catch and raised rail are retained. Cap contact is unchanged from the inherited baseline, 0.00221823 mm3. The optical guide is unobstructed. The tighter loop needs a physical ribbon and motion check; ribbon bend limits have not been supplied.

## Files and replay

The manifest points to `compact-arm-r04/build.py` for rebuilding. The older `current/build.py` reconstructs R03 only and is not the selected builder.
Run `current/export_print.py` in pinned FreeCAD to export the hash-verified selected revision. R04 print files are in `generated/mouse-hats/active/print-r04/`. Use the matching cap. Printing and physical fit remain unverified.

The separately exported skull/baseplate display print remains based on the same unchanged baseplate. It is not an export of the camera carrier.

[R03 baseline notes](../compact-arm-r04/source-r03-readme.md) | [T3 reconciliation](RECONCILIATION.md) | [Historical index](../INDEX.md)




Latest visual study: [R09 body-mounted arms](../socket-body-study-r09/README.md). R08 remains the selected print revision pending review.


