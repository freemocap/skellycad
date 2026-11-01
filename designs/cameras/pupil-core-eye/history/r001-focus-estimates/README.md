# Adjustable miniature lens: conditional focus estimates

The user reports on 2026-10-30 that this physical lens is not glued: it screws in
and out. Treat focus as adjustable for this unit. That observation supersedes
applying the general glued-lens description to it. The reported 1.7 mm focal
length remains the best available lens value; focus adjustment moves the image
plane relative to the sensor rather than intentionally changing focal length.

## Assessment

Focusing near the current modeled eye location is plausible. A 1.7 mm thin lens
needs only about **0.256 mm extension from infinity focus** to focus at 13 mm.
This is small relative to the model's several-millimetre lens assembly. Available
thread engagement, close-focus aberrations and actual optical spacing are still
unknown. This supports testing the adjustable lens before moving the camera.

The 13 mm scenario rounds the R02 corneal-axis intersection of 12.919 mm, measured
from its schematic projection center. For the equations below, 13 mm is assumed
to be the optical object distance from the front principal plane. Those datums
are not proven equivalent. The pupil is seen through the cornea; its apparent
plane is not represented by the outer corneal mesh.

Comparable miniature board lenses support a plausible **f/2 to f/2.8** starting
range, with f/2.4 a useful central scenario. This is an inference from catalog
lenses, not an aperture measurement of this lens. Outer barrel diameter cannot
identify the internal aperture. See [candidate research](lens-candidates.md)
[@iadiyM5OpticalCandidates2026; @towinM4ShortLens2026].

## Focus adjustment

For focal length `f`, object distance `s`, and image distance `v`, the thin-lens
equation gives `v = f*s/(s-f)`. Required extension beyond infinity focus is
`v-f = f*f/(s-f)` [@edmundBasicLensSelection]. Image distances refer to optical
principal planes, not the lens barrel's rear face. Manufacturer BFL and TTL are
separate mechanical/optical integration quantities.

| Target distance, mm | Image distance for f=1.7 mm | Extension from infinity | Turns if pitch is 0.35 mm |
| --- | --- | --- | --- |
| 10 | 2.048 mm | 0.348 mm | 0.99 |
| 13 | 1.956 mm | 0.256 mm | 0.73 |
| 15 | 1.917 mm | 0.217 mm | 0.62 |
| 20 | 1.858 mm | 0.158 mm | 0.45 |
| 30 | 1.802 mm | 0.102 mm | 0.29 |

Changing focus from 20 to 13 mm calls for about 0.098 mm more separation, roughly
0.28 turn at that example pitch. These are differences from a known focus setting,
not instructions to turn an unknown lens position by a prescribed amount.
Generally, moving the lens away from the sensor brings focus closer. The small
change in object distance caused by translating the lens is ignored in this
first-order travel comparison.

The actual thread diameter and pitch need measurement. The CAD holder was scaled
from an M5 x 0.35 drawing to a 6.3 mm envelope, so its bore/thread is a visual
mock-up rather than proof of a real M5 fit [@iadiyM5HolderDrawing].

## Depth of field at a 13 mm focus setting

These are **additional geometric defocus** bounds, not guarantees of total image
sharpness. Assume f=1.7 mm, an effective 1.2 mm sensor width at 400 pixels
(about 3 micrometres per output sample), and allow a 6 micrometre geometric blur
diameter, approximately two output samples. That is a chosen illustration, not
a pupil-tracking accuracy requirement. A one-sample criterion roughly halves
the tabulated depth; both are included in the calculation output.

| Assumed aperture | Near–far interval, mm | Total depth, mm |
| --- | --- | --- |
| f/2.0 | 12.42–13.64 | 1.22 |
| f/2.4 | 12.31–13.78 | 1.47 |
| f/2.8 | 12.20–13.91 | 1.72 |
| f/4 | 11.88–14.35 | 2.46 |
| f/5.6 | 11.49–14.97 | 3.48 |

For a thin lens with aperture diameter `D=f/N`, sensor plane fixed at `v`, and
another object at distance `u`, similar triangles give
`blur = D*v*abs(1/s - 1/u)`. Solving for the permitted blur `c` gives
`near = s/(1 + N*c*(s-f)/f^2)` and
`far = s/(1 - N*c*(s-f)/f^2)` while the latter denominator is positive.
These local derivations model defocus only. Real depth of field requires an
image-detail and contrast criterion [@edmundDofR05].

Stopping down is not a free improvement. At an illustrative 850 nm wavelength,
the ideal Airy diameter is about 5.7 micrometres at f/2.4, 9.5 at f/4 and 13.4
at f/5.6 for this near-focus scenario. Calculation uses
`2.44*wavelength*N*(1+m)` with thin-lens magnification `m` and unit pupil
magnification [@edmundAiryFocus2026]. Actual wavelength and pupil magnification
are unverified. Diffraction and aberrations are **not included** in the 6 micrometre
defocus allowance and cannot be interpreted as a two-pixel total-blur guarantee.
At a fixed lens and distance, f/4 admits about 36% as much light as f/2.4; that
matters for short exposures at 120 fps [@edmundApertureR05]. The existing lens may
have a fixed aperture even though its focus is adjustable.

## Focal-length options at the same 13 mm distance

Using a 1.2 mm effective sensor width, finite-conjugate magnification gives
`field_width = sensor_width*(s-f)/f` [@edmundBasicLensSelection].

| Lens scenario | Approximate field width | Extension from infinity | Geometric depth with 6 micrometre defocus allowance |
| --- | --- | --- | --- |
| Existing 1.7 mm, assumed f/2.4 | 8.0 mm | 0.256 mm | 1.47 mm |
| IADIY-like 1.75 mm f/2.4 | 7.7 mm | 0.272 mm | 1.38 mm |
| IADIY-like 2.2 mm f/2.2 | 5.9 mm | 0.448 mm | 0.77 mm |
| IADIY-like 2.9 mm f/2.8 | 4.2 mm | 0.833 mm | 0.52 mm |

The catalog focal lengths/apertures are real options; the 13 mm performance
above is a local theoretical scenario, not vendor-qualified performance
[@iadiyM5OpticalCandidates2026]. Longer focal lengths put more pixels on the eye
but reduce coverage, focus tolerance and often available mechanical travel.
The 2.2 mm option is a plausible next comparison if greater eye magnification is
needed. The 2.9 mm option is more demanding and may lose coverage during eye motion.

Finite-distance focusing also changes the simple coverage calculation: the
1.7 mm scenario gives about 8 mm across at 13 mm, rather than the roughly 9 mm
predicted by the nominal pinhole frustum. This illustrates its approximation;
do not replace the accepted mean-frustum reference with an unmeasured new
calibration. The actual image geometry should be checked after focus adjustment.

## Candidate selection and next measurements

The first action is to try the existing adjustable lens at the intended mounting
position and illumination. Record best focus and the usable depth interval at
400 x 400. For a replacement, measure the actual barrel thread and available
travel, then request a lens qualified around 13–15 mm optical object distance
with transmission at the actual eye-illumination wavelength. Verify image circle,
rear-element clearance, BFL, mounting envelope and image quality. Stock IR-cut
variants can be inappropriate for an IR eye camera; [the candidate note](lens-candidates.md)
records the available filter options. No candidate is currently a verified drop-in.

Run `python -B designs/eye-tracker/shared/cameras/pupil-core-eye/focus-estimates-r01/calculate.py`
from the repository root. It writes `generated/eye-tracker/shared/focus-estimates-r01/estimates.json`
and checks zero defocus at the target plus agreement with the chosen blur at each
near/far bound. This task changes no CAD geometry or selected checkpoint.
