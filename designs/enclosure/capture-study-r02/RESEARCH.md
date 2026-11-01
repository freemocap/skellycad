# Capture geometry and camera candidates

Reviewed 2026-10-29. This is a design-screening note, not a purchasing approval
or demonstrated five-camera capture system. The Amazon IFWATER/ELP-style camera
supplied by the user establishes the desired housing and manual-lens style;
its shutter, synchronization and removable-filter capabilities are not assumed.
The first study prioritizes the floor and lower 200 mm of the 500 mm cube.

## What to optimize

OptiTrack recommends distributing cameras around the capture volume, overlapping
their views, and using different elevations when this improves visibility. It
requires at least two synchronized views for triangulation and notes the
tradeoff between coverage and image detail at different working distances.
Its guidance concerns optical marker tracking; markerless animals introduce
additional correspondence and self-occlusion problems [@optitrackPlacementR02].

Our engineering interpretation is to measure at least three things separately:
the region seen by two or more cameras, the region with a useful ray-intersection
angle, and image sampling in pixels/mm. Five visible cameras with nearly
collinear rays do not imply strong depth estimation. Treat angle thresholds,
pixel-error assumptions and floor/volume weights as study parameters, not
manufacturer recommendations. Report redundancy of three or more views and
full-cube coverage alongside the preferred lower-volume result. An empty-space
frustum model remains optimistic about animal, tether and enclosure occlusions.

OpenCV documents the pinhole projection using camera intrinsics and world-to-camera
pose, extended with distortion coefficients for real lenses. Calibrate every
assembled camera/lens/filter configuration and jointly estimate extrinsics;
do not replace calibration with nominal CAD placement [@opencvCalibR02].

For the study's local uncertainty diagnostic, let `J` contain image-coordinate
derivatives with respect to 3D position. Assuming independent isotropic image
errors of standard deviation `sigma`, use `sigma^2 (J^T J)^-1` when the matrix is
well-conditioned. This linearized geometric estimate excludes calibration,
timing, motion blur and correspondence errors. The choices `sigma=0.5 px`,
minimum acute ray angle 20°, and a 3 mm feature spanning at least 3 pixels are
explicit study assumptions, not measured performance or universal thresholds.

## Lens and sensor geometry

For an ideal rectilinear camera, horizontal field of view is
`2 atan(sensor_width / (2 focal_length))`, with the analogous vertical equation.
Edmund Optics also cautions that lens principal planes and real lens data matter
when converting optical working distance to mechanical spacing [@edmundFovR02].

For a downward-looking square image at height `h` above a square floor of side
`L`, the ideal floor-fitting full angle is `2 atan(L/(2h))`. For example, `L=500`
and `h=446 mm` gives about **58.6°** along both image axes. This is a derived
floor-only fit: the footprint narrows above the floor, so it does not cover the
same 500 mm width at every height. At 200 mm above that floor, the same lens
covers only about **276 mm** square. Add framing margin and compare the entire
priority volume before choosing optics.

A square physical sensor is optional. A centered square crop produces a square
image while discarding pixels and narrowing the wider field of view. Cropping
does not add angular coverage or guarantee a higher delivered frame rate.
Model the actual crop dimensions, not a stretched image or the nominal optical
format such as “1/4 inch.”

The OV9281 manufacturer specifies 1280 × 800 pixels at 3 µm pitch: the derived
active readout rectangle is 3.84 × 2.40 mm. This differs from the separately
listed total image area. Its 120 fps sensor capability is for MIPI/DVP and must
not be attributed automatically to a USB camera [@ov9281ProductA01].

## Representative products

Prices below are observations, not delivered quotes. Camera electronics, lens,
host/controller, filters, mounts and synchronization hardware must fit the budget
together. Unknown unit prices do not pass the sub-USD-300 purchasing gate.

| Candidate | Verified mode and optics | Price and remaining questions |
| --- | --- | --- |
| Waveshare OV9281 1MP USB Camera (A), SKU 31671 | Mono global shutter, USB2; manufacturer advertises 1280 × 720 at 120 fps. Fixed-focus 1.65 mm M7 lens, unspecified-axis 105° FOV, no IR filter. | USD 25.99 listed. Low-cost mono/IR experiment; external trigger and focus at the required distances are unverified. Not the requested C/CS manual-varifocal format. [@waveshareOv9281R02] |
| Arducam B0495 AR0234 USB3 module | Color global shutter; datasheet excerpt lists 1920 × 1200 at 50 fps or 960 × 600 at 80 fps. M12 manual-focus 3.6 mm lens, integral IR-cut, default focus 2 m–infinity. | Current unit price not verified. Must establish close focus and trigger support. Published lens FOV and ideal focal-length geometry differ; use calibrated intrinsics. [@arducamB0495R02] |
| e-con See3CAM_24CUG | Color AR0234 global shutter, USB3, M12, external hardware trigger. Specifications list HD at 120 fps and FHD at 60 fps, with UYVY/MJPEG output. | Page shows **volume** pricing from USD 99; unit sample price is blank. Overview claims 120 fps full resolution, conflicting with its mode-specific table: require a confirmed mode table and quote. Filter swapping and close focus unverified. [@econ24CugR02] |
| Raspberry Pi Global Shutter Camera | IMX296 color, 1456 × 1088, C/CS mount and documented common external trigger. Requires a CSI host rather than direct USB. | Historical launch price USD 50, excluding lens and host; current complete-system quote needed. Installed IR-cut removal is permanent and voids warranty, not a reversible filter swap. [@rpiGsLaunchR02; @rpiGsIntegrationR02] |

For the AR0234 examples, the documented 1920 × 1200 array and 3 µm pixels imply
5.76 × 3.60 mm. A centered 1200 × 1200 crop uses 3.60 × 3.60 mm and discards
37.5% of native pixels. Higher-resolution idealized profiles are useful for
trade studies but are not proof that a complete global-shutter camera fits the
budget [@econ24CugR02].

## Integration gates

Global shutter describes exposure across one sensor; it does not synchronize
independent cameras. The Raspberry Pi documentation demonstrates a shared
trigger and explains model-specific wiring and fixed controls. Use the selected
camera's documented electrical interface rather than generalizing those wiring
instructions to USB boards [@rpiGsIntegrationR02].

Before purchasing five cameras, verify one unit's actual output modes, timestamp
behavior, trigger operation, exposure limits, near focus and lens image circle.
Then test five simultaneous streams on the intended USB/CSI topology. Check
whether lower-resolution modes crop, bin or resize. Measure exposure skew and
dropped frames using a shared visible timing event. Recalibrate after optical
changes. For IR/visible switching, require an explicitly removable filter holder
and compatible lens; no candidate above is verified as a reversible filter system.

Review scope: primary product/specification excerpts, calibration model and
placement guidance were inspected. Waveshare and Arducam details were available
through indexed manufacturer excerpts; direct fetches returned 403/404. No
hardware was purchased, contacted, synchronized or physically tested.
