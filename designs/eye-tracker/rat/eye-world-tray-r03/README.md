# Restored PCB holder and stemless world-camera tray

R03 restores the complete PCB-holder region from the frozen R43 carrier. R02's
coincident Boolean union had returned four disconnected solids and failed to
restore the other half of the holder. R03 starts with the intact carrier and
cuts only left support material outside the central holder's bounding region,
with a 0.02 mm protective margin. The result is one valid solid. All 209 sampled
surface points from the original central holder remain in the result.

`WorldCameraStemlessTray` is a new object copied from the existing R43 left
camera holder. The rear ball, stem and projecting root blend are cut flush with
the tray back, at head-frame Z = -1.24998 mm. The retained tray back is about
0.85 mm thick beneath its existing seating surface. The camera cavity, side
walls and catches retain their existing geometry. The original holder remains
hidden as a reference; it is not overwritten.

The world camera and finite-width ribbon retain the R02 pose. The new tray uses
the original camera-to-holder registration. It clears the carrier, ribbon,
sensor PCB and LEDs. Its 1.91318 mm³ lens-envelope overlap is inherited unchanged
from R43 and remains a physical-fit limitation. No new checked interference was
introduced. The right-eye camera and skull remain unchanged.

The saved native document is a placement review, not a print release. World
camera support design is intentionally deferred until this tray arrangement is
reviewed. `review.json` identifies the frozen native document and lineage;
`generated/eye-tracker/rat/eye-world-tray-r03/repair-validation.json` records the
checks. The binocular branch and historical species selection remain unchanged.

Use `open.FCMacro` through the verified existing-session IPC bridge. It saves
and closes obsolete eye/world review tabs, preserves unrelated documents, and
opens the saved current review. Do not send `build-isolated.FCMacro` to the
desktop session; that macro is for a separate build process.
