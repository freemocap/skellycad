# Adult mouse and rat eye audit

This review adds visible geometric optical axes to the complete mouse R10 and
rat R06 review assemblies. It does not replace eye shapes or move anatomy.
Representative adult laboratory animals are the target; no strain-specific fit
is claimed. The selected species checkpoints remain unchanged.

## Shape findings

| Quantity (mm) | Current mouse | Published mouse comparison | Current rat |
|---|---:|---:|---:|
| Transverse exterior diameter | 3.000 | Approximately 3.3 is a provisional design scale | 6.410 |
| Exterior axial length | 2.894 | 3.34 at 100 days, different posterior endpoint | 6.291 |
| Corneal patch / limbus diameter | 1.471 | 2.3–2.6 | 5.640 |
| Anterior apical corneal radius | 0.893 | 1.414–1.493 | 2.965 |

The mouse mesh fits a body spheroid with semiaxes 1.50, 1.50, 1.26 mm and a
corneal spheroid with semiaxes 0.75, 0.75, 0.63 mm. The axial direction joins their
centers. Apical radius is a squared divided by b for a spheroid with radial
semiaxis a and axial semiaxis b. Current meshes match the prior fitted Mouse Hats
inputs. Join vertices depart from the fitted surfaces by up to 0.00304 mm.
See [numeric audit](mouse-shape-audit.json) and historical
`designs/mouse-hats/skull-print/cornea-fit.json`.

The current mouse cornea is too narrow and sharply curved for these adult
references. Fixed-eye limbus measurements were 2.3 ± 0.1 mm in 129/SVJ,
2.6 ± 0.2 mm in C57BL/6, and 2.6 ± 0.1 mm in BALB/c, at 6–8 weeks
[@henriksson2009MouseCornea]. Frozen-section and in-vivo anterior radii were
1.414 ± 0.019 and 1.493 ± 0.080 mm; axial length reached 3.34 mm at 100 days,
but that endpoint includes retina and does not explicitly include the exterior
scleral shell [@schmucker2005MouseEye]. The model's radius is about 37–40% smaller.

For a subsequent generic adult mouse revision, use 2.6 mm limbus diameter and
1.45 mm anterior radius as provisional targets, with an approximately 3.3 mm
globe scale. Fit exterior axial length separately and disclose the shell assumption.
These are engineering defaults, not a population mean or a measured specimen.
A broader, flatter cornea is supported; simply enlarging the existing small cap
will not control all three dimensions. Mouse/rat schematic similarity supports
this direction, without justifying exact scaling [@remtullaHallett1985MouseEye].

The rat exterior uses Hughes's 115–130-day D.A. rats: 6.410 mm transverse,
6.291 mm exterior axial, 5.64 mm limbus diameter, 2.11 mm corneal sag and
2.965 mm apical corneal radius [@hughes1979RatEye]. Its joined oblate spheroids
are a schematic approximation: the posterior radius is about 3.624 mm versus
3.23 mm reported, and the join has a slope discontinuity. The colored solids
are exterior partitions, not tissue layers. This is better grounded than the
manual mouse model, but not an exact anatomical reconstruction. Older Brown
Norway measurements have different dimensions and endpoints
[@lozanoTwa2013RatEye]; do not mix them into one presumed universal adult eye.

## Position and orientation

The rat placement is a visual estimate: centers are (0.75, ±8.35, 0) mm in a
frame with +X rostral, +Y left and +Z dorsal. Current axes are ±70.753 degrees
azimuth and +13.887 degrees elevation. Center separation is 16.7 mm. None of
these placement numbers is a published resting-pose measurement.

For mice, Oommen and Stahl inferred an ambulatory rest direction of 64 degrees
lateral from the midsagittal plane and 22 degrees above the earth horizon, while
the lambda–bregma line was 29 degrees nose-down. The cohort was ten C57BL/6 mice,
5–10 months old. This combines tilt responses with spontaneous head posture;
it is not a universal fixed eye pose [@oommenStahl2008MouseOrientation].
The current mouse mesh world frame is not registered to that skull/horizon
frame. Applying those angles directly, or adding pitch to elevation as scalar
angles, would be incorrect; use a complete 3D frame transformation.

Rat behavior also shows strong gaze dependence on head pitch and roll
[@wallace2013RatEyes]. This review did not establish a defensible universal
static rat rest angle or stereotaxic globe-center coordinates for either local
skull. Historical angle claims cited secondhand were not treated as verified
primary measurements.

Confidence is strong that the mouse cap needs revision, moderate in the rat's
schematic exterior proportions, and low in the anatomical accuracy of either
assembly's globe centers and fixed poses. Accurate placement needs skull-frame
registration (midsagittal plane, bregma/lambda or equivalent landmarks), orbital
landmarks and ideally registered soft-tissue imaging. A chosen nominal gaze can
then be documented separately from behavioral variation.

## Optical datums and validation

Green and magenta lines mark the two eye axes; cyan remains the camera axis.
Each eye's +Z points forward through the corneal apex. Lines extend behind the
posterior pole and ahead of the cornea, with an outward arrow. They are reference
geometry and have `ExportForPrinting = false`; exports must still explicitly
exclude them. This is a geometric symmetry axis, not a calibrated visual axis.
The frame origin is the fitted mouse body center or the rat envelope centroid,
not a measured ocular rotation center.

Rat axes inherit existing eye placements. Mouse meshes are wrapped in fitted
eye frames, so their axes follow subsequent frame movement. World vertex
preservation was checked to 0.00001 mm (observed maximum 0.000000067 mm).
Axis/apex residuals are below 0.00001 mm. No anatomy or hardware was refitted;
existing holder and ribbon interference from the source reviews remains.
Geometry validation does not establish physical fit.

Read `docs/development.md` before rebuilding. Run `add_axes.py` with the pinned
FreeCAD bundled Python and the desired species revision's `recipe.json`.
The script verifies source and selected-checkpoint hashes before writing under
`generated/`. Send the species `open.FCMacro` through the existing desktop pipe
for review. Frozen native files and their hashes are recorded in each revision's
`review.json`; they preserve the matched assembly, including the detailed camera.

The bibliography records review scope for each source. This was a targeted
literature audit, not a systematic review. No exact strain, specimen registration
or demonstrated physical fit is implied.
