# Current working set — start here

Open `generated/mouse-hats/current/CURRENT.FCStd` using `model/open_current.py`
in FreeCAD so all custom feature modules load. Recreate the presentation with
`model/show_current.py` when necessary. `current-parts.json` is the authoritative
mapping of six part numbers to full editable final features and assembly frames.

Select **VIEW — choose numbered parts or assembled** and change **Layout**:
- **Numbered parts** shows six whole parts spread out with matching labels.
- **Assembled** shows those exact same six source features at assembly positions.

Both presentations use App::Links, not independent geometry copies. Layout moves
only the presentation. Open the linked source to edit construction; save that
source document to persist changes. Source FCStd files must remain available.
The arrangement is fixed and has no joint solver; overview spacing is a static
presentation and may need refreshing after major dimensional changes.

| Number | Current part | State |
| --- | --- | --- |
| 01 | Skull baseplate | Accepted reconstructed baseline; original fit |
| 02 | PCB tray + mounting stem | Full part with lip corner trims and filled end notch |
| 03 | PCB cap | Accepted reconstructed baseline |
| 04 | Socket | Accepted reconstructed baseline; old arm omitted |
| 05 | Camera holder + ball | Accepted reconstructed baseline |
| 06 | Camera retaining clip | Accepted reconstructed baseline |

There is NO front extension and NO added pocket clearance. Part 02 links to
CleanedTrayAndMount in model/tray-cleanup/cleaned-tray.FCStd, not its inspection slice.
The five other parts remain the prior reconstructed models. Visual acceptance
and geometric checks do not erase the recorded source-parity qualifications.

Old course files, imported references, cutaway reviews and the old linked assembly
are historical/reference documents. CURRENT is the working entry point. Existing
open historical documents were labeled REFERENCE in this session, not deleted or
closed; linked source documents were labeled SOURCE. Those session labels are
navigation aids, not changes to their geometry or a replacement for this manifest.

Fresh-process reopening of CURRENT verified six valid solids, the correct trimmed
tray target and zero overlap for all 15 seated pairs at 0.001 mm tolerance. The
view switch was exercised in the GUI. Results: generated/mouse-hats/current/validation.json.
No physical-fit or insertion-motion claim. Camera head is unsupported because the
old arm is intentionally absent; later two-arm work remains deferred.

Latest tray cleanup: build_notch_cleanup.py fills the three-vertex recess in
TrayBacking to join its end-edge endpoints. Adds 7.142446 mm3, removes no material;
one valid solid and zero cap overlap. Prior lip trim and all stem fit remain.
