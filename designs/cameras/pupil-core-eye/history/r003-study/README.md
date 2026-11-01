# Camera R03: provisional JST SH selection

The user selected SH tentatively on 2026-10-13. R03 replaces the connector box
with the imported four-position, horizontal-entry **SM04B-SRSS-TB**, 1.0 mm pitch.
The source model and license remain under R02 `connector-candidates/`
[@kicadConnectorModels; @kicadLibraryLicense]. `connector-selection.json` records
its hash, provisional status and registration.

The STEP is translated without scaling or rotation: its width center and front
bounding edge match the former envelope, and its seating plane is at the PCB
surface Z=0. Exact footprint position and mating direction still need inspection.
The separate candidate group is omitted from R03; R02 remains available for
comparison. Caliper dimensions, bends and lens references are unchanged.

Open `open.FCMacro` in the existing FreeCAD session. It creates the three editable
camera configurations with the SH connector attached. Output files are
`generated/eye-tracker/shared/camera-study-r03/camera-measured-r03.FCStd` and
`camera-measured-r03.step`. The shared builder validates ribbon length, measured
board extents, imported connector geometry and the 24-solid STEP export.

This selects a component for the camera study, not a new accepted mouse or rat
complete assembly. Exact connector identity and physical fit remain provisional.
