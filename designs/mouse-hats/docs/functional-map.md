# Functional map — user account, 2026-10-08

Source: user's spoken description in this chat. This records design intent and
recollection, not newly measured geometry or verified hardware specifications.
Current reconstruction authority remains 53nassembly.step. Descriptions of later
modifications are context only; do not introduce them into STEP parity silently.

## System

Mouse eye tracker using a tiny camera taken from a Pupil Labs Pupil Core unit.
A thin PCB connects through a thin ribbon to the camera sensor/lens and nearby
infrared emitters. User reports the whole assembly weighs less than four grams;
exact inclusion of hardware, cables and baseplate in that figure is not specified.
Record as context, not yet a formal mass acceptance requirement.

## Names and roles

| Working name | Function and relationships |
| --- | --- |
| Skull-mounted baseplate | Fixed attachment foundation. Receives the main body's mounting tab and a threaded-insert fastening arrangement. Its underside may have been adapted to the mounting surface in use. |
| Main carrier / camera assembly body | Combines the mating mounting tab, rim around the baseplate interface, PCB support tray and single arm. These are functional regions, not necessarily separate manufactured parts. |
| PCB support tray | Broad flat region with locating/retaining channels for the thin PCB. Openings exist; heat dissipation is the user's tentative interpretation, not confirmed purpose. |
| Single arm and socket | Arm extends from the carrier to the socket supporting the adjustable camera holder. Preserve the STEP arm exactly for this phase. |
| Ball / sensor holder | Ball mates with arm socket. Attached plate/channel locates lens/sensor and the ribbon neck; nearby IR emitters occupy the other side. Seating/orientation are functionally important. |
| Sensor retention clip | User calls this 52N assembly clip. Clips over the holder notch to retain the camera/ribbon assembly. Not the electrical connector. |
| PCB protective cap | User calls this 52N assembly cap. Attaches to the front of the tray, protects and retains PCB, and accommodates cable/connector exit. |
| Upper electrical connection | User recalls a four-pin JST connector leading toward an attachment above the enclosure. Exact connector family/pitch and routing are unconfirmed. |

The prior STEP report describes three solids. Do not force these functional
names into a one-to-one mapping: first inspect which features/parts are actually
represented. In particular, do not assume the clip/cap are included or import
their separate mesh files to fill gaps. If absent, record the gap and ask about
scope after the STEP is understood.

## Priority interfaces to annotate on the STEP

1. Baseplate-to-carrier mating tab, rim, seating surfaces and fastening axis.
   User identifies this as a principal source of geometric complexity and the
   main attachment interface. Treat geometry as critical until understood.
2. PCB edge channels, retention features, cap mating features and connector exit.
3. Socket/ball fit and clamp arrangement; arm-to-socket transition.
4. Sensor/lens seat, ribbon-neck path, IR-emitter space and retention-clip interface.

For each: record participating solids/features, intended contact versus clearance,
axes/datums, STEP measurements, and a proposed comparison method. No guessed
insert/connector/lens dimensions should replace measured STEP geometry.

## Uncertainties to retain explicitly

- Lens mount might be M4 or M2; neither size is confirmed.
- Socket insert is recalled as M2, possibly about 2 mm in one dimension; exact
  thread, insert outside diameter, length and installation pocket are unknown.
- User describes replacing earlier plastic threads with insert pockets. Whether
  each replacement appears in the selected STEP must be inspected, not assumed.
- Baseplate insert specification and screw details are not established.
- Vent openings may also serve other purposes; avoid naming them HeatVents yet.
- One phrase about the cap permitting the "clip" to exit may refer to a cable
  or connector. Preserve this ambiguity until the relevant geometry is shown.

These uncertainties do not prevent geometric STEP reconstruction. They matter
when inferring design intent, defining independent parameters or changing hardware.

## Deferred context

Later two-arm replacements, reinforced junctions, skull meshes (hollow, manually
solidified and eyeball-augmented), and a skull-subtracted baseplate were described.
Do not inspect or compare those sources during this phase. No surgical procedure
or in-vivo suitability is being designed or evaluated here.

## Immediate next action

Show a numbered, component-separated view of the selected STEP. Use this map to
identify functional regions and ask only about ambiguous features visible there.
Then propose a bounded first component and a source-versus-rebuild acceptance
check. The user has supplied enough context to proceed; no hardware-size quiz is
needed before inspecting the actual STEP.

## Numbered STEP inspection — 2026-10-08

Opened generated/mouse-hats/inspection/53-numbered-reference.FCStd with three
colored solids and display-only X offsets of 0, 55 and 110 mm. The source
coordinates remain in the component BREP files; show_step53.set_layout(doc,
False) restores the original arrangement.

User-confirmed identities:
- 1 (amber, 93 faces): main carrier, single arm, and socket side. This is
  incomplete as a camera assembly: the mating ball/sensor-lens holder is absent.
- 2 (blue, 4,086 faces): skull-mounted baseplate with its underside Boolean-cut
  against the skull. User cautions this is not the best first reconstruction target.
- 3 (green, 39,780 faces): skull-shaped reference embedded in this STEP.
  No separate skull mesh was imported or compared.

User confirms three missing components: PCB protective cap, mating ball with
sensor/lens holder, and the clip retaining the camera on that holder. Rebuilding
the three imported solids does not constitute a complete camera assembly.
First reconstruction candidate is now the main carrier; preserve the cut
baseplate as an interface reference. Missing component sources remain to be
established, without silently expanding into mesh comparisons.

Display was prepared from the supplied saved STEP BREP with matching source
SHA256 metadata. The independent fresh import subsequently finished successfully:
three valid solids, 43,959 total faces. Fresh report: generated/mouse-hats/
inspection/assembly-53.json. The displayed shapes were then replaced with the
fresh import's solids and saved. Aggregate face count is dominated by the embedded
faceted references and is not a useful standalone measure of carrier complexity.

## Older source recovery — 52 STEP

User confirms required geometry is supplied, possibly in older STEP/F3D files,
and authorizes source recovery. Opened 52nassembly.step directly in the pinned
FreeCAD runtime via checks/show_step52.py. Five solids (45, 10, 16, 52, 37 faces)
are displayed as 52-1 through 52-5 in a separate inspection document. Their
identities are recorded below; this does not establish that all missing parts
have been located. No Fusion installation or manual export is needed for this
inspection. 53 remains the carrier baseline unless deliberately revised.

### User-confirmed 52 identities and revision history

| Solid | Identity | Revision caveat |
| --- | --- | --- |
| 52-1 | Skull-mounted baseplate | Older, shorter version with drop-in M2 nut. Later design uses an M2 heat-set insert pocket and greater height; source of those changes remains to be established. |
| 52-2 | Socket | Receives 52-5 and attaches to the end of 52-4. User sees no threads and suspects this already has the newer insert pocket; exact geometry/specification unverified. |
| 52-3 | Mount stem | Couples carrier assembly to baseplate. |
| 52-4 | Carrier and single arm | Older arm iteration; keep 53 carrier as newer reference. |
| 52-5 | Ball and camera sensor/lens holder | User confirms this is the missing mating holder. Source candidate for reconstruction. |

User recalls the updated baseplate used the same M2 heat-set insert channel as
the socket. This is design intent, not confirmation of insert outside dimensions.
If newer baseplate/arm changes are absent from supplied CAD, user accepts
reproducing them later as explicit revisions. Establish geometry parity first;
do not mix inferred improvements into a claim of exact source reproduction.
Cap and retaining clip remain unlocated in the inspected STEP solids.

### Print-in-place source clue

User mainly worked with versions called print-in-place, with pieces assembled
in their intended arrangement, rather than interrogating individual components.
Filename search found old/df-hardware/camera-assembly/cad/52nassembly/
52nassemblyPrintinplace.stl. Only its filename was inspected; no mesh comparison
or geometry import was performed. The corresponding 52 F3D may contain useful
body/component names or configurations, but this is not yet verified. The phrase
alone does not establish fused geometry or a functioning printed joint.

### Fusion archive name evidence

checks/inspect_fusion_names.py reads design metadata with Windows tar/libarchive
(the archives use Zstandard compression). It does not decode CAD geometry.
50 F3D contains LeftCap and LeftCamClip; 52 F3D contains RightCap, RightCamClip,
RightCamClip (1), RemoveBody-RightCamClip and RemoveBody-LeftCap. These are
printable strings in design history, not proof of current unsuppressed bodies.
Next recovery step is inspecting 52 F3D in Fusion, including timeline history if
the bodies are absent at its endpoint, then exporting recovered parts as STEP.
No source archive was modified. Report: generated/mouse-hats/inspection/
fusion-name-clues.json. A separate 50 STEP import is also in progress to identify
its generically named solids; no claim of cap/clip recovery from that STEP yet.

## Newly supplied 58 source — supersedes missing-part search

User added old/58nassembly.step and old/58nassembly.f3d and installed Fusion.
Both preserved and hashed in docs/source-58.json. The STEP imports directly into
the pinned FreeCAD runtime, so manual Fusion work is not currently needed.
The older 50 import completed, but further recovery there is deferred in favor
of this more complete newer candidate.

58 imports seven valid solids, saved in generated/mouse-hats/inspection/
58-reference.FCStd with a report in assembly-58.json:
- RightCap: 69 faces.
- Baseplate: 34 faces.
- RightCamHolder (1): 37 faces.
- RightCamClip (1): 18 faces.
- Main (1): 89 faces.
- Baseplatecut: 4,241 faces.
- Body44: 11 faces; visually socket-like, functional identity unconfirmed.

Import initially used generic labels. Source names restored by matching each
STEP solid's shell face count to the imported solid. All seven counts are unique;
the script asserts one-to-one coverage and rejects ambiguity. No geometry edited.
Original placement is preserved, including overlapping baseplate alternatives.
This is not yet a verified finished assembly. 58 is the leading baseline candidate;
next resolve Baseplate versus Baseplatecut and confirm required interfaces before
reconstruction. Cap/clip source geometry is now available without Fusion export.

User subsequently confirmed 58 is exactly the desired source and recognizes
the displayed clipped-together arrangement. It is now the accepted reconstruction
baseline. This confirms intended source/appearance, not physical fit testing.
Started camera clip local-frame preparation; see reconstruction-plan.md.
