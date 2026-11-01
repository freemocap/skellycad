# Five-camera capture study R02

R02 adds a reusable optical layout study to the 500 mm clear starter cube. It
preserves the R01 frame and uses five generic camera envelopes: four mounted
from the vertical legs and one downward-looking square view at the top center.
The user-selected priority is the floor and lower 200 mm. This is a geometric
candidate for review, not a calibrated or physically qualified capture system.

See [research and hardware candidates](RESEARCH.md) for primary sources, current
price limitations, synchronization, filters and close-focus requirements.

## First result

The deterministic search evaluates 2,304 feasible layouts, retains the best
16 for each of two objectives, reranks their union on a finer grid, and performs
one independent camera-pose refinement pass for the floor-priority result.
It is a bounded sweep plus local refinement, not a global optimum.

The selected candidate has these optical parameters. Heights are above the
interior floor, not the extrusion bottom; add 20 mm for R01 world coordinates.

| Parameter | Four corner views | Top view |
| --- | --- | --- |
| Optical center positions | x/y 45 or 455 mm; C1–C3 at z=75 mm, C4 at z=100 mm | (250, 250, 450) mm |
| Aim point | (250, 250, 180) mm | (250, 250, 0) mm |
| Nominal full field of view | 110° horizontal, landscape; approximately 16:9 | 85° square |
| Synthetic active sensor | 7.392 × 4.160 mm, 1848 × 1040 pixels | 5.2992 × 5.2992 mm, 1536 × 1536 pixels |
| Derived ideal focal length | 2.588 mm | 2.892 mm |

The slight asymmetry is a grid-search outcome, not evidence that C4 should
physically differ by exactly 25 mm. The low placement and upward aim work well
in this mostly empty-space calculation; real animals may occlude these views.
Evaluate higher arrangements with an animal/tether model before treating this
as a mounting recommendation. Current generic camera bodies clear the frame;
support rods are placement reservations, not manufactured bracket designs.

On the 12.5 mm verification grid, the selected candidate provides a qualifying
triangulation pair at **99.81% of floor samples**, **99.46% of lower-volume
samples**, and **98.23% of full-cube samples**. The reference layout's lower-volume
result is 91.13%. At least three views see 99.13% of the selected lower-volume
samples. These are model results, not measured tracking accuracy.

The reference is a synthetic 260 mm camera-height / 100 mm aim-height layout
with 80° side fields and a 65° top field. R01 never specified optics, so it is
not a measured optical baseline for R01. The full-cube objective is also saved
for comparison; its tradeoff is less image detail in the priority region.

## Quantities and assumptions

Each camera has an independent position, target, up vector, roll, active sensor
dimensions, pixel dimensions, focal length, near/far clipping and edge margin.
All use the ideal rectilinear pinhole model [@opencvCalibR02; @edmundFovR02].
The square top image aligns with the x/y floor axes. A rectangular sensor can
supply it through a real square ROI or software crop; changing aspect ratio
must also change active dimensions and pixels, not stretch the image.

The calculation reports these distinct quantities:

- **Visible views:** a point lies inside a camera's usable frustum and is not
  blocked by another generic camera body. Five percent of the image width and
  height is reserved at each edge, leaving 90% along each axis.
- **Qualifying pair:** both views resolve a nominal 3 mm transverse feature at
  at least 3 pixels and have an acute ray-intersection angle of at least 20°.
  Using the acute angle rejects both parallel and antiparallel degeneracy.
- **Redundancy:** at least two qualifying pairs; these pairs can share a camera.
  This is distinct from three visible cameras and from two disjoint pairs.
- **Image detail:** second-best visible view's pixels/mm, including zero when
  two views are unavailable. This is transverse image-plane sampling; a
  foreshortened surface feature can span fewer pixels.
- **Ideal uncertainty:** the worst-axis standard deviation from the local
  projection Jacobians, assuming independent 0.5 px errors and exact poses,
  intrinsics and timing. It excludes calibration bias, synchronization error,
  blur, incorrect point matches and lens distortion. It is not a hardware
  accuracy prediction.

The 70–1000 mm axial clipping interval is a study constraint, not measured depth
of field or verified focus capability. The corner sensor comparison holds
approximate total pixels and pixel pitch fixed while changing aspect ratio.
These synthetic sensor shapes are not claimed purchasable parts.

The score is a weighted sum of qualifying-pair percentage, plus 0.10 times
redundant-pair percentage, plus a detail bonus of up to 5 points. The detail
bonus is `5 × min(p10 second-view pixels/mm / 2, 1)`. Weights are 0.45 floor,
0.45 lower volume and 0.10 full cube. The full-cube comparator uses only the
cube region. These values, feature size and angle are editable choices.

Coarse search spacing is 100 mm; reranking/refinement uses 25 mm; final results
use 12.5 mm. The final grid has 1,600 floor, 25,600 lower-volume and 64,000 cube
samples. Volume samples are cell centers; they do not certify boundary coverage.
The lower box's eight boundary corners are checked separately. Do not interpret
small differences below grid sensitivity as a definitive preference.

## FreeCAD model

`generated/enclosure/capture-study-r02/capture-study-r02.FCStd` contains:

- The copied R01 frame and connectors, with its recorded SHA-256 checked first.
- Five generic camera bodies, optical-center properties and support reservations.
- Full and margin-adjusted frustum solids, plus frustums clipped to the cube.
- Disjoint cells labeled by the cameras whose frustums contain them.
- Geometric regions seen by at least two, at least three, and all five cameras.

Toggle groups or objects with FreeCAD's visibility controls. The default view
shows clipped frustum wireframes and the transparent three-view region. Full
frustums, individual membership cells and alternate overlap thresholds are
hidden initially. `layout.png` shows the camera arrangement without frustums.

**CAD overlap means geometric visibility only.** Its exact volumes exclude
camera-body occlusion and do not impose pixel or triangulation-angle thresholds.
The numerical report includes those additional conditions. Do not substitute a
green CAD overlap region for demonstrated tracking quality.

The CAD build compares 600 point classifications against the analytical
projection, checks the disjoint cells sum to the cube volume, checks body/frame
collisions, and verifies native-file save, ZIP integrity and reopen. The
completed build closes its own documents. Nine mathematical regression tests
cover clipping, projection, square-top footprints, portrait orientation,
occlusion, degeneracy and a closed-form stereo uncertainty case.

## Hardware substitutions and robustness

`sensor-options.json` provides sourced sensor-readout dimensions for OV9281 and
AR0234, plus a derived AR0234 square crop. `report.py` substitutes these while
preserving horizontal FOV and recomputes vertical FOV and pixel coverage. It
writes reusable five-camera JSON layouts for each substitution.

At 110° horizontal FOV, the ideal corner lens becomes approximately **1.344 mm
for OV9281** or **2.017 mm for AR0234**. The square AR0234 top crop needs about
**1.964 mm for 85°**. These are derived optical targets, not lens SKUs; distortion,
image circle, mount, close focus, filter behavior and calibration must be checked.
A 5 mm lens on a 3.60 mm square crop at 450 mm height spans only 324 mm before
edge margin, illustrating why the supplied 5–50 mm product style does not by
itself establish the needed coverage.

`robustness.json` includes loss of each individual camera and a generic
100 × 60 × 70 mm central occluder. The occluder is not an anatomical model;
targets inside it are excluded. Losing a camera also removes its physical body
in this screen, so a disabled camera left in place needs a separate test.
`results.json` varies feature size and minimum triangulation angle. Neither
screen models marker identity, posture, self-occlusion, reflection or motion.

Current pricing research does not establish a complete, synchronized,
reversibly filter-swappable system under USD 300 per camera. Keep price, mode,
trigger and filter verification as purchasing gates. Global shutter and
inter-camera synchronization are separate requirements [@rpiGsIntegrationR02].

## Reproduce or change a layout

Use the repository CAD environment. The numerical scripts need NumPy, SciPy
indirectly through the existing environment, and Matplotlib; FreeCAD uses its
bundled Python. Preserve any reviewed outputs before rerunning these commands,
which replace generated R02 files.

1. Edit `study.json` to change search ranges, weights or thresholds. Keep the
   current 500 mm arena for this revision; the sampling and search code explicitly
   assumes that size. Create a new revision to change the enclosure dimensions.
2. Run the search and reporting scripts from the repository root:

   ```powershell
   $env:OPENBLAS_NUM_THREADS = '1'
   & tools/cad/.venv/Scripts/python.exe designs/enclosure/capture-study-r02/optimize.py
   & tools/cad/.venv/Scripts/python.exe designs/enclosure/capture-study-r02/report.py
   ```

3. To test manually edited independent camera poses or optics, copy a layout
   JSON to a new filename, edit its `cameras` array, then run:

   ```powershell
   & tools/cad/.venv/Scripts/python.exe designs/enclosure/capture-study-r02/optimize.py --layout path/to/layout.json
   ```

   This writes `custom-evaluation.json`; it does not replace the selected layout.
   To build its CAD view, copy that reviewed layout to the generated
   `selected-layout.json` path first. Keep five unique camera IDs and a nonparallel
   up vector. Optical sizes and clipping distances must be positive.

4. Ensure the saved R01 native model and matching `validation.json` exist under
   `generated/enclosure/starter-cube-r01/`. If absent, follow the R01 README to
   rebuild it. Then build R02 in an isolated FreeCAD process:

   ```powershell
   $env:FREECAD_USER_HOME = Join-Path (Get-Location) '.cad-tools/validation-profile'
   & ./.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/enclosure/capture-study-r02/build_cad.py
   ```

5. Require exit code zero, inspect `cad-validation.json`, and open the saved
   native model. Do not use an older success record after a failed build.
   The tests and bibliography checks are:

   ```powershell
   & tools/cad/.venv/Scripts/python.exe -B -m unittest discover -s designs/enclosure/capture-study-r02 -p test_geometry.py -v
   & tools/cad/.venv/Scripts/python.exe -B tools/check_references.py
   & tools/cad/.venv/Scripts/python.exe -B -m unittest discover -s tools -p test_references.py -v
   ```

Outputs include selected/full-cube layouts, shortlist metrics, dense sampled
arrays, sensor substitutions, sensitivity/robustness reports, coverage maps,
comparison chart, native CAD and its validation record. `results.json` records
the settings hash. R01 remains unchanged; R02 has no accepted physical checkpoint.
