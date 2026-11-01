# R06: budget USB camera baseline

> **Withdrawn as a hardware recommendation.** The user requires a physically
> square active sensor array, not a square software crop. Both the IADIY and
> ELP selections below use rectangular sensors and fail that requirement.
> Retain these calculations only as cropped-sensor comparisons. No camera is
> currently selected for purchase. The current requirements are listed stock
> from any supplier, physically square sensor, approximately 1024 × 1024 at
> 30 fps, USB UVC, and under USD 200 including a suitable lens. The earlier
> global-shutter requirement also remains in force. Do not substitute a crop,
> square housing or square individual pixels for a square active sensor array.

## Procurement update: Amazon stock takes priority

The user rejected the IADIY lead time. **The IADIY selection below is superseded
for purchasing**, while its numerical study remains a historical comparison.
Use **ELP-USBGS1200P01-L21**, Amazon ASIN **B0C3C459JT**, as the immediate
prototype baseline: https://www.amazon.com/dp/B0C3C459JT . The seller describes
an AR0234 global-shutter USB UVC board, 1920 × 1200 MJPEG, and a 2.1 mm M12 lens
[@elpAmazonL21R06].

Live Amazon inspection on 2026-10-29 showed USD 72.99, In Stock, ships from
Amazon, sold by ELP USB CAMERA, with a quantity selector including five units.
The unsigned-in browser's default location was Nashville 37217: it showed
Prime delivery October 31 or ordinary free delivery November 3. This is evidence
of US fulfillment, **not a delivery promise to the user's address or a confirmed
five-unit order**. Check the user's checkout delivery date before purchase.
Five units at that displayed price total USD 364.95 before tax.

Start with the supplied lens for availability and refocus/coverage testing.
The 2.8 mm top-lens target remains a later optical substitution, not a verified
Amazon lens purchase in this update. Stream 1920 × 1200, center-crop columns
360–1559 to 1200 square, then resize to 1024 square; target 30 fps MJPEG and
verify the exact UVC frame intervals on hardware. The nominal square remains
3.6 mm for 3 micrometer pixels, but the actual ELP lens is not the ideal pinhole
lens in the earlier numerical run. Its advertised 120-degree horizontal FOV
indicates that focal length alone is insufficient to transfer those results.
Do not attribute the earlier 97.75%/64.30% coverage to this camera without
calibration and a new evaluation. No hardware was purchased and no CAD changed.

## Earlier IADIY comparison (retained)

Select five **IADIY CM2M60M12QG** board cameras, with the color option, for the
next enclosure geometry iteration. Use the supplier's **2.1 mm M12 lens option
on four corners** and **2.8 mm on top**. These are prototype selections, not
bench-qualified optics. No hardware was ordered.

The manufacturer's storefront lists USD 98 base price and availability with
7–21 day delivery, selectable lenses and optical filters, plus USD 2 for a 1 m
USB cable (reviewed 2026-10-29). Allow USD 110–140 per camera including option
allowances and printed enclosure hardware, excluding tax/shipping. Lens/filter
variant surcharges are not verified. Use the visible-light/IR-cut option for
the initial color prototype; keep IR experimentation for a later revision
[@iadiyUsbR06].

The module has an OG02B10 global-shutter sensor, USB 2 UVC interface and M12
holder. The documented 1600 × 1200 MJPEG mode reaches 60 fps; uncompressed YUV
only reaches 5 fps at that resolution. Target 30 fps MJPEG capture through
OpenCV's OS video backend. Exact 30 fps UVC negotiation must be checked on the
unit: the public table specifies the maximum mode rather than every supported
frame interval. If only 60 fps is exposed, retain alternate frames to produce
30 fps output, while accounting for the unchanged input USB load
[@iadiyUsbDatasheetR06]. No device or OpenCV capture was tested here. Shared
exposure synchronization between five modules is not established by UVC or by
the presence of global shutters.

## Image and geometry convention

Acquire 1600 × 1200, take the central 1200 × 1200 square (columns 200–1399),
then resize to 1024 × 1024. Do not crop directly to 1024 × 1024: that would
reduce coverage. The sensor's reported 3 micrometer pitch gives a nominal
3.6 mm square readout for this geometry. This assumes a one-to-one native
pixel mapping in the selected stream; vendor scaling/cropping and calibration
remain to be checked. Resizing changes output sampling, not the viewed angle
[@iadiyUsbDatasheetR06].

With the existing 5% margin on each image edge, the 2.8 mm top lens at 450 mm
height gives a nominal usable floor width of 520.7 mm. An exact 500 mm fit
would use 2.916 mm. Thus the standard 2.8 mm option gives a small framing margin.
The 2.1 mm corner lens has approximately 81.2 degrees square FOV before the
edge margin, under an ideal rectilinear projection. Retain heights of
250–300 mm and compare aim and roll numerically.

Run `tools/cad/.venv/Scripts/python.exe -B designs/enclosure/usb-baseline-r06/evaluate.py`
from the repository root. It searches 72 symmetric poses for each of three
corner focal lengths (1.5, 1.8 and 2.1 mm), then refines the leading twelve
per lens on a 12.5 mm grid. The selected output uses the available 2.1 mm lens;
the other two are hypothetical sensitivity comparisons, not selected products.
The score remains 60% five-view floor coverage plus 40% five-view coverage in
the lower 200 mm. Two-, three-, four- and five-view metrics are retained.

The selected 2.1/2.8 mm combination reaches **97.75% sampled five-view floor
coverage** and **64.30% sampled five-view lower-volume coverage**. These are
geometric predictions only: actual lens distortion, focus, occlusion, timing
and edge sharpness are excluded. The supplier does not provide a sufficient
projection model for the selected lens options, so these focal-length-based
frustums are not calibrated predictions of those physical lenses.

Outputs are `generated/enclosure/usb-baseline-r06/results.json` and
`selected-layout.json`. This revision records the procurement baseline and
numerical poses; it does not replace the existing FreeCAD document or claim
a printable housing fit. Use a purchased M12 holder with an adjustable,
lockable lens seat inside the eventual printed shell; verify that delivered
lenses can be refocused and are not permanently bonded before housing design.
