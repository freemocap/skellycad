# Representative adult eye envelopes

Mouse R11 and rat R07 replace both eyes in the complete camera assemblies while
retaining the optical axes. The user requested approximate adult male laboratory
anatomy. These are representative adult design values, **not measured male
population medians**: the reviewed eye-biometry sources do not establish those
medians. No unsupported sex correction has been added.

| Parameter, mm | Mouse | Rat |
|---|---:|---:|
| Exterior transverse diameter | 3.30 | 6.410 |
| Exterior axial length | 3.34 | 6.291 |
| Limbus diameter | 2.60 | 5.640 |
| Anterior apical curvature radius | 1.45 | 2.965 |
| Posterior apical curvature radius | 1.65 (assumed) | 3.230 |

## Evidence and construction

Mouse limbus diameter uses the adult C57BL/6 mean; published strain means span
2.3–2.6 mm [@henriksson2009MouseCornea]. The chosen anterior radius lies between
section and in-vivo measurements. The 3.34 mm axial target comes from 100-day
mouse biometry, whose posterior endpoint is retinal, not explicitly exterior
sclera [@schmucker2005MouseEye]. Using it as the exterior mockup length is an
explicit shell approximation. The 3.30 mm width and spherical posterior pole
are design assumptions consistent with the approximate adult scale; they are
not additional measurements. The spherical corneal cap is simpler than real
aspheric anatomy. See the [preceding audit](../eye-anatomy-audit-r01/README.md).

Rat dimensions retain the Hughes schematic exterior, now also matching its
reported 3.23 mm posterior curvature [@hughes1979RatEye]. The original oblate
corneal cap is retained. Overall width, length, limbus diameter, corneal sag and
anterior radius are unchanged. The intermediate scleral contour is interpolated,
not measured. This avoids mixing unrelated cohorts or posterior endpoints.

The sclera uses piecewise cubic Hermite interpolation of squared radius versus
axial position. Constraints set the posterior pole, posterior curvature,
equatorial maximum radius, limbus radius and corneal tangent. Radius increases
to the equator and decreases to the limbus without overshoot. The profile is
position- and tangent-continuous, including at the limbus; second derivatives
need not be continuous. This is a schematic exterior, not a validated optical
or mechanical tissue model. Independent closed cornea/sclera envelope regions
share an internal disk; the whole-eye STL omits that disk.

## Placement and interfaces

Eye frame origins and directions are preserved from mouse R10 / rat R06.
Mouse origins remain the old fitted body centers. Rat origins remain the old
envelope centroids, not the centroids of the revised contour. Both axes remain
+Z anterior. Camera hardware, ribbon route, arm seating and skull geometry are
unchanged, verified by native shape signatures and world placements.

Skull scale remains 1.0. The available skulls lack verified specimen dimensions
and registration; scaling them to an assumed body weight would add false
precision. Thus this revision improves eye dimensions and shape, not measured
skull scale or resting gaze. The explicit targeting policy in each recipe keeps
the existing eye targets and camera pose. Existing hardware interference remains.

The rat right eye already intersects its skull slightly; the revised contour
also intersects it. Surface-triangle crossing counts alone do not measure overlap
severity. The per-assembly validation and containment records separate this
anatomical fit issue from hardware clearance. Do not silently move the eye or
shrink literature dimensions merely to make an unregistered skull fit.

## Build and review

Read `docs/development.md` first. From the repository root:

1. Run `tools/cad/.venv/Scripts/python.exe designs/eye-tracker/shared/adult-eyes-r01/generate.py`.
   This writes meshes and definitions to `generated/eye-tracker/adult-eyes-r01`.
2. Run the pinned FreeCAD bundled Python on `integrate.py`, supplying the mouse
   `adult-anatomy-r11/recipe.json` or rat `adult-anatomy-r07/recipe.json`.
   Source and selected-checkpoint hashes must pass before integration.
3. Run `check_containment.py` with the CAD tools virtual environment after both
   assemblies exist. Inspect surface crossings separately from sampled containment.
4. Open each revision's `open.FCMacro` through the existing desktop FreeCAD pipe.
   It displays the complete assembly with cornea, sclera and both eye axes.

Closed, consistently wound meshes, target dimensions, shared partition volumes,
and unchanged non-eye geometry are checked during generation/integration.
These checks do not demonstrate anatomical registration or physical fit.
Frozen complete assemblies and their hashes live in each species review folder.
The selected baseline checkpoints remain unchanged.

## What a registered model would contain

A registered skull-and-eye model places bone and soft tissue from the same
specimen into one physical coordinate system. It includes millimetre spacing,
the transforms between scans, anatomical labels and recoverable landmarks.
Registration is the alignment step; segmentation is tracing the structures.
A typical workflow uses CT for bone and MRI or cryosections for eyes, aligns
shared landmarks/fiducials, then checks the alignment in all three slice planes.
Digimouse documents such a workflow [@dogdas2007Digimouse].

For this project, the practical route is to import an existing registered head,
extract skull and both eyes without changing their relative positions, define
midsagittal and bregma–lambda frames, and fit a higher-detail corneal model to the
image-derived globe. Retain original images so alignment can be checked. Record
voxel spacing, fit residuals and landmark uncertainty. A postmortem eye pose still
needs a separate behavioral rest-gaze convention. Atlas-to-existing-skull fitting
would require another registration and remains an estimate for that skull.

### Available starting points

- **Mouse: Digimouse.** A 28 g male nude mouse with registered skeleton and eyes
  on a 0.1 mm grid. It is one specimen, not the median laboratory male
  [@dogdas2007Digimouse]. The provider offers registered CT/cryosections/labels
  and a tessellated atlas in ANALYZE/MATLAB formats. Download listings were
  verified; archives and license terms have not yet been evaluated for import
  [@uscDigimouseDownloads].
- **Rat: Duke's 2025 Wistar cohort.** Ten models, six male, include eyes and skull
  from registered 0.2 mm CT/MRI. This is the strongest matched-anatomy lead found.
  The paper says data are shared on request; it also describes intended laboratory
  distribution. A public direct archive was not verified [@segars2025WistarPhantoms].
  Duke's MOBY/ROBY provider page has a resource request route; availability of the
  newer cohort must be confirmed [@dukeMobyRoby].

We therefore do not need to reconstruct everything from scratch. Import and
conversion work is still required; these are imaging atlases rather than ready
FreeCAD eye-camera assemblies. A brain-only atlas is not automatically a source
of segmented skull and eyes.

## Recorded assembly checks

The mouse has zero detected eye/skull or eye/hardware surface crossings. The
rat left eye also clears both. The rat right eye has 18 eye/skull triangle
crossings, versus 6 in its previous mesh; different tessellations mean these
counts cannot quantify a change in penetration depth. No sampled eye surface
points or tested skull vertices lay inside the opposing geometry. This is an
unresolved localized surface intersection, not demonstrated anatomical clearance.

The preserved rat camera ray misses its eye-frame center by less than 0.000001 mm.
The inherited mouse ray misses its eye-frame center by 2.402 mm; its prior target
was a surface proxy. This revision does not claim corrected mouse camera aim.
A camera-targeting revision must resolve that separately and refit the ribbon
and arms if the sensor pose changes.
