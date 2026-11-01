# Rat eye + world camera W06

**Print correction:** use `export_print_in_place.py` and the `print-in-place-v2/` output. The earlier detached-holder print layout is superseded and must not be printed. Both holders are captive: print each ball already inside its socket. The corrected exporter applies one rigid transform to the carrier and both holders, preserves both 0.333165 mm clearances, and supplies them together in one STL. Only clips and baseplate are separately arranged. This changes the print layout, not the accepted W06 hardware geometry.

W06 advances the world-camera optical datum exactly 2 mm along skull/world +X from the hash-verified R05 complete assembly. The camera remains level, looking forward. Y/Z and the right-eye placement are preserved. `source.json` records the parent checkpoint; `review.json` selects and hashes the complete W06 assembly.

The ribbon is solved from its fixed PCB interface at unchanged 32.85 mm length, 4 mm width and 0.25 mm thickness. The minimum inside bend radius is 4.0348 mm. Both world supports are rebuilt and seated into the existing carrier and joint, with a 90-degree terminal relationship and concave root/joint fillets. The accepted holder geometry is reused rigidly. Functional openings and the skull/baseplate interface are unchanged. RAT W06 replaces the old text within its existing rail.

`final-validation.json` in the generated revision records geometry, interfaces, view clearance and anatomy checks. These do not demonstrate physical ribbon compliance or hardware fit. Inherited camera mock-up/holder and clip/holder overlaps are recorded separately.

## Print export

`export.py` verifies the complete assembly hash and exports six matched print parts. `study_holder_export.py` selects an axis-aligned holder placement whose actual serialized mesh passes validation; it changes no functional geometry. Run that script before `export.py` with the pinned FreeCAD Python runtime. The stable holder export derives from the accepted R04 holder, reused unchanged in W06.

The carrier bed normal minimizes the length-weighted out-of-bed component of all four support centerlines. Its RMS arm angle to the bed is 23.48 degrees. Both clips are flat; holders use separate orientations. Carrier and holder overhangs need slicer supports. Native shapes preserve their volumes. Saved STLs pass FreeCAD closure/self-intersection checks and independent trimesh watertightness, winding and shell-count checks. The print pack contains six individual STLs, a six-part combined STL and a five-part alternative that omits the unchanged baseplate.

Outputs are under `generated/eye-tracker/rat/eye-world-print-r06/`. The selected complete assembly and print-layout native files are saved and ZIP-verified. `open.FCMacro` opens a separate saved current review and saves/closes obsolete eye-world review tabs while preserving unrelated documents.
