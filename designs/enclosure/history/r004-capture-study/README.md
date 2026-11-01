# Capture study R04: five-view overlap at the floor

R04 changes the objective from a qualifying camera pair to **all five geometric
views overlapping**, with weights of 60% floor coverage and 40% coverage in the
lower 200 mm. All five sensor/readout shapes are square. Corner optical centers
remain 250–300 mm above the floor. R01–R03 remain preserved.

The 432-layout sweep and finer verification select four cameras at **300 mm**,
aimed at **(250, 250, 0) mm**, with **45° roll** and **100° nominal horizontal
and vertical FOV**. Corner coordinates remain 45/455 mm in x/y. The down-tilt is
about 46° below horizontal. The roll puts a square image diagonal in the
vertical aiming plane, using its corners to accommodate the floor footprint.
This is a finite symmetric search, not a global optimum.

The top camera stays at (250, 250, 450) mm, pointed vertically downward with
image axes aligned to the floor. Its focal length is calculated so the **usable**
square exactly meets the 500 × 500 mm floor boundary. With the existing 5% margin
on each edge, `f = sensor_width × 0.9 × 450 / 500`, or 4.292352 mm for the
synthetic 5.2992 mm sensor. Its full FOV is about 63.4°, narrower than R03's
105°. Thus this change is optically a zoom-in to eliminate wall overspill.

The fitted top footprint necessarily shrinks with height: its width is
`500 × (1 − z/450)` mm. At z=200 mm it is only 277.8 mm wide. Integrating its
area from z=0 to 200 gives a maximum five-view lower-volume fraction of about
62.14%, even with perfect corner coverage. Covering more of that elevated
volume in all five views would require relaxing the exact floor fit.

The numerical 12.5 mm grid reports five-view geometric floor coverage rising
from R03's 5.25% to **100%**, and lower-volume coverage from 30.97% to **62.75%**.
The sampled 62.75% slightly exceeds the continuous top-only bound because of
grid discretization; use `cad-validation.json` for exact geometric volumes.
Camera-body occlusion and qualifying-pair metrics are reported separately.
Animal, tether, optical distortion and real calibration remain unmodeled.

## FreeCAD review

The default visible object is `AtLeast5Views_GeometricOnly`. The tree now includes
**at least 2, 3, 4, and 5 views** under `OverlapSummary`. Select an object and
press Space to toggle it. Hide the five-view object when comparing the four-view
region. The five distinctly colored individual frustums remain under
`ClippedViews`, initially hidden.

`preserve_view.FCMacro` saves the user's R03 display changes to a separate
`r03-user-review.FCStd` and records its view. `open.FCMacro` opens R04 once,
preserves that view, verifies the saved native file, then closes the backed-up
R03 review. Unrelated documents are untouched.

The CAD builder uses convex plane clipping to partition the cube into cells,
avoiding failed Boolean cuts at coincident rolled-camera boundaries. It verifies
that cell volumes sum to the cube, that all cells are valid, that 600 CAD point
classifications agree with projection, and that camera bodies clear the frame.
The native document is saved, ZIP-checked and reopened before desktop review.

## Reproduce

From the repository root, use the existing numerical environment and the pinned
FreeCAD environment described in `docs/development.md`:

```powershell
$env:OPENBLAS_NUM_THREADS = '1'
& tools/cad/.venv/Scripts/python.exe designs/enclosure/capture-study-r04/optimize.py
$env:FREECAD_USER_HOME = Join-Path (Get-Location) '.cad-tools/validation-profile'
& ./.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/enclosure/capture-study-r04/build_cad.py
& tools/cad/.venv/Scripts/python.exe -B -m unittest discover -s designs/enclosure/capture-study-r04 -p test_layout.py -v
```

Save and close the live R04 review before rebuilding its generated path.
Outputs are under `generated/enclosure/capture-study-r04/`. The original R01
native model and matching validation record are required for the frame copy.
The research and ideal-pinhole assumptions remain those documented in
[R02](../r002-capture-study/RESEARCH.md). Sensor dimensions and focal lengths are
synthetic design targets, not selected commercial lenses or proven physical fit.
