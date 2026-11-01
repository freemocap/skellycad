# R05: 5–50 mm manual-varifocal lens screen

This study applies the user's reported **5–50 mm** focal range to the enclosure
cameras while retaining square sensors and 250–300 mm corner heights. It does
not identify or reverse-engineer the exact physical lens. R04 stays unchanged.

## Reading the controls

The conventional interpretation of the reported markings is:

| Marking | Meaning |
| --- | --- |
| 5–50 mm | Focal-length range: 5 mm is widest; 50 mm is narrowest. |
| 1:1.6 | Maximum relative aperture, f/1.6; not the zoom ratio or current iris position. |
| T / W | Telephoto / wide: changes focal length and field of view. |
| C / O | Likely closed / open iris; the reported zero is probably the letter O. |
| Infinity / N | Far / near focus: changes the plane of sharpest focus. |
| 1/2.7 inch | Nominal sensor-format/image-circle class; do not convert it directly into active sensor millimeters. |
| CS | Lens mount; camera flange distance and rear clearance must match. |
| IR | Usually denotes IR-related correction/compatibility; not proof of an IR-pass filter or a removable IR-cut filter. |

These letter interpretations are provisional until the lens model or a close
photo of the markings is available. The small screws generally lock each ring.
Changing zoom may require refocusing; do not assume a varifocal lens is parfocal.
Mount standards are distinct even when threads fit [@edmundMountsR05]. Similar
5–50 mm f/1.6 lenses exist with different iris controls; their specifications
must not be substituted for this unidentified manual lens.

## What the constrained optimization found

R04's synthetic corner sensors are 5.544 mm square and use approximately
2.326 mm focal length. The top sensor is 5.2992 mm square with a 4.292 mm lens.
A 5–50 mm lens cannot reach either of those widest required settings.

For coverage alone, 5 mm dominates every longer setting at the same pose:
increasing focal length shrinks the ideal frustum. The sweep therefore searches
84 symmetric height/aim/roll arrangements at the 5 mm endpoint, then verifies
the leading candidates on a 12.5 mm grid. It also records a fixed-pose zoom
curve at 5, 6, 8, 12, 25 and 50 mm.

| Square readout assumption | Five-view floor coverage | Five-view lower-200-mm coverage |
| --- | ---: | ---: |
| R04 wider-lens design | 100% | 62.14% exact geometric volume |
| R04 synthetic sensors, all lenses constrained to 5 mm | 62.25% sampled | 28.48% sampled |
| 3.60 mm square AR0234 ROI, all lenses constrained to 5 mm | 28.00% sampled | 11.94% sampled |

The synthetic-sensor candidate uses height 300 mm, aim point (250,250,-50) mm,
and 45° roll. The negative aim height directs the optical axes below the floor;
it does not move the cameras below their allowed heights. This is a bounded
symmetrical search, not a globally optimal layout.

The top usable floor width at 5 mm is about 429 mm with the synthetic top
sensor, or 292 mm with a 3.6 mm square crop. Neither fills the floor. Physical
image-circle compatibility of the synthetic sensors with a lens labeled
1/2.7 inch is unverified; larger modeled sensors cannot be assumed usable.
The AR0234 crop dimensions come from the previous sourced study
[@econ24CugR02]. The exact camera sensor in the user's hand remains unknown.

## Focus and aperture

Focus changes which distance is sharp; iris controls the tradeoff between light,
depth of field and diffraction. Closing the iris cannot recover missing field
of view. Depth of field must be tied to a resolution criterion rather than
called simply good or bad [@edmundApertureR05; @edmundDofR05].

`study_lenses.py` includes an illustrative paraxial thin-lens screen. At object
distance z, image distance is `v=f*z/(z-f)`. With the sensor at the image distance
v0 for the chosen focus, the geometric defocus-circle diameter is
`(f/N)*abs(v0-v)/v`. This is a local thin-lens derivation, not a measured curve
for the unidentified lens. Distances are axial from the principal plane, not
tape-measure distance from the housing. The calculation holds the pinhole FOV
fixed and neglects focus breathing and finite-focus magnification changes.

For each f-number, the script independently chooses each camera's focus plane
to maximize weighted visible samples with defocus diameter no greater than
two pixels. It then evaluates their joint five-view pass region. This heuristic
does not globally optimize the five focus settings together. The aperture and
150–800 mm focus ranges are hypothetical; the lens's actual near-focus limit
and available f-stops are unknown.

In the synthetic-sensor screen, f/4 with approximately 350 mm axial corner
focus and 310 mm top focus restores nearly all of the 5 mm geometry's coverage
under the two-pixel defocus test. These are bench-test starting estimates only.
At f/4, ideal throughput is 16% of f/1.6 (6.25 times less), so short motion-freezing
exposures may require more illumination. Further stopping down is not a free
improvement: diffraction, especially at longer IR wavelengths, is excluded
from this numerical screen [@edmundApertureR05; @edmundDofR05].

## Artifacts and reproduction

Outputs are in `generated/enclosure/lens-study-r05/`. `results.json` includes
both sensor cases, the zoom curve, focus settings, aperture throughput ratios
and limitations. `selected-layout.json` drives the native
`lens-study-r05.FCStd`. The native model uses a generic three-ring lens envelope,
not measured lens geometry or a verified CS interface; the envelope is 40 mm
long with 30 mm barrel and 34 mm ring diameters. R04 remains the current desktop
review; R05 is a separate comparison file.

Run from the repository root:

```powershell
& tools/cad/.venv/Scripts/python.exe designs/enclosure/lens-study-r05/study_lenses.py
$env:FREECAD_USER_HOME = Join-Path (Get-Location) '.cad-tools/validation-profile'
& ./.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/enclosure/lens-study-r05/build_cad.py
& tools/cad/.venv/Scripts/python.exe -B -m unittest discover -s designs/enclosure/lens-study-r05 -p test_lenses.py -v
```

Require successful CAD validation and native-file integrity before opening the
comparison. The build closes its own saved documents. Rebuilds replace only
generated R05 outputs. Exact lens identity, sensor dimensions, minimum focus,
filter stack, distortion and bench sharpness remain necessary before hardware
selection. The R04-equivalent wider-lens targets should guide a future lens
search instead of assuming the 5–50 mm barrel can reproduce that coverage.
