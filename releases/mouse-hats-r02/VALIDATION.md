# Validation - R02

## Exchange test

Fresh FreeCAD 1.1.4 process / Open CASCADE 7.8. STEP AP242 in millimeters.
Five component names present exactly once; five closed valid solids.
GUI reimport confirms component colors. Assembly structure retained.
Volume differences < 0.0001 mm3; centroid and analytic bounding-box differences
< 0.00001 mm. Analytic bounds avoid triangulation-dependent box differences.
Exact per-part numbers and warnings are in step-roundtrip.json.

**Deep Boolean check is qualified, not passed:** InvalidCurveOnSurface is reported
on MH-001, MH-002, MH-003 and MH-004 after STEP import. MH-005 passes that check.
The native release shapes passed the same check before export. AP214 and AP242
and surface-curve export variants were investigated; warnings remained.
No geometry or global tolerances were modified to mask the issue. Future STEP
healing/importer investigation remains open. Revalidate before downstream Boolean
editing. Native FreeCAD files are provided as an alternative.
No second CAD application import has been performed.

## Design checks already completed

- Carrier/holder: zero overlap; minimum modeled separation 0.121145958 mm at this pose.
- Clip/holder: tiny contact ~0.0044745 mm3 with recorded 0.0001 mm Boolean tolerance.
- Added holder walls do not intrude into the sensor rail envelope.
- PCB tab extension preserves cap and baseplate clearance.
- Taper: one valid solid; 161.567649 mm3 removed only below the protected mount region.
- Baseplate contact area: 67.482998 -> 21.928303 mm2; no seated-carrier overlap.
- Intended STL shell counts: carrier+holder 2; baseplate, cap, clip 1 each.
- Parameter edits/reopen/restore were tested in the working project.
- The source checkpoint rebuild is tested separately; see source/rebuild-validation.json.

## Physical limitations

No physical print, joint release, retention, ribbon routing, full motion sweep,
load/strength test or slicer support validation has been performed in this workflow.
The gap is a geometric measurement, not a recommended printer capability.
No FEA or thermal simulation supports strength or heat-dissipation claims.
