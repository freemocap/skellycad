# MouseHats R02 - start here

Status: accepted geometry checkpoint / first-print candidate. This is not a
production-qualified release. Date: 2026-10-09. Units: millimeters.

## Open the design

- START-HERE.pdf: illustrated part map, interfaces, controls and test questions.
- MouseHats_R02.step: AP242 assembly, five named solids in assembled positions.
- MouseHats_R02.FCStd: clean colored assembly snapshot, no proxy dependencies.
- Exploded-reference.FCStd: numbered illustration; not manufacturing placement.
- PARTS.csv: part numbers, quantities and CAD volumes (not estimated mass).
- print/: four intended STL inputs plus PRINT-NOTES.txt.
- source/: parametric checkpoint, code, dimensions and rebuild/open commands.
- VALIDATION.md and step-roundtrip.json: what passed and what did not.
- MANIFEST-SHA256.json: package integrity hashes; RELEASE.json: revision metadata.

## Important exchange qualification

The STEP reimports as five valid solids with correct names, colors and placement.
The deeper Boolean-readiness check reports InvalidCurveOnSurface warnings on
baseplate, carrier, holder and clip. This is a qualified exchange candidate,
not a warning-free STEP certification. Native FreeCAD snapshots are supplied.
A different CAD application's import has not been tested. See VALIDATION.md.

## What is included

One each: MH-001 baseplate; MH-002 carrier (tray, stem, arms, socket fused into one
physical part); MH-003 camera holder (cradle, neck, ball); MH-004 retaining clip;
MH-005 PCB cap. No hidden construction objects in the STEP. No duplicate geometry.
Electronics, ribbon, fasteners, inserts and skull are omitted. Their omission
must not be interpreted as clearance verification or a complete hardware BOM.

The assembly retains the reconstruction's existing coordinate frame; it is not
recentered or independently rearranged. The baseplate bottom is Y=-5 mm and its
protected pocket floor is Y=1.5 mm. The print orientation is a separate decision.
The exploded offsets are illustrative and are not assembly dimensions.

## Working from this checkpoint

Treat this folder as a frozen sharing snapshot. Copy source/ to a new working
folder before editing. Use stable part numbers in feedback. Record the revision,
parameter, observed failure or intended benefit, and interfaces to preserve.
Follow source/README.md to load controls or rebuild the latest edits.
Use a new revision for geometry changes. Never silently replace R02 after sharing.
All original playground work and supplied source files remain in their locations.

## Provenance and scope

Reconstructed from supplied 58 STEP; V5 meshes informed the new arms and camera
pose; tapered 53 mesh informed the baseplate footprint. Raw legacy STEP/F3D/mesh
archives are retained in the playground, not duplicated into this package.
This package does not assign a new license or assert ownership of inherited work.
The source snapshot supports rebuilding R02 from the included native checkpoint;
it is not a complete from-original-import historical reconstruction bundle.
