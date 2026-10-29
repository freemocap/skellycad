# Compact optics comparison — 2026-10-27

**Prefer the CHANCCTV CH2021A for the next compact mechanical study.** It is a
size candidate, not an approved optical part. Keep the supplied CIL829 study as
reference; its size does not match the user's Pupil-style target. No native PCB,
selected camera checkpoint or species assembly changes with this recommendation.

## What the earlier Pupil work established

The selected CAMERA-DUMMY-R08 uses the lens-m5-r05 reconstruction: a 6.3 mm
square holder, approximately 4.84 mm barrel diameter and a barrel top 3.7 mm
above the mounting base. The last height follows the user's measurement; the
diameter and details remain approximate. See the
[build and validation definitions](../../eye-tracker/shared/cameras/pupil-core-eye/lens-m5-r05/build.py).
The exact Pupil lens part number was not established.

The holder came from the IADIY CL5P1.6 drawing, scaled from 6.5 to 6.3 mm. That
scales its thread too, so it is a visual mock-up, not a standard M5 mount. The
IADIY family has a 3.6 mm image circle and a default IR-cut filter, with other
filter options advertised [@iadiyM5HolderDrawing]. Reusing that exact family
would require accepting a smaller sensor region and obtaining the appropriate
filter variant. Reducing output resolution alone does not establish a smaller
optical footprint: binning or subsampling can still use the full sensor area.

## Size and optical candidates

Dimensions are mm. Body length excludes the gap to the sensor; total track
length (TTL) reaches the image plane. Neither is automatically height above PCB.

| Candidate | Physical envelope | Optical track | Assessment |
| --- | --- | --- | --- |
| Pupil reconstruction | Holder 6.3 square; barrel about 4.84 diameter; top 3.7 above mounting base | Not calibrated | Target profile, not identified functional optics |
| Commonlands CIL829 | Front diameter 10; imported body length 11.567 | Drawing TTL 14.7 | Preserve as oversized reference [@commonlandsCil829Drawing; @commonlandsCil829Step] |
| CHANCCTV CH2021A | Diameter 6, body length 2.65; M6 x 0.35 | TTL 3.85; mechanical rear clearance 1.20 | Preferred compact study: 3 mm EFL, F/2.4, 4.8 mm maximum image circle, no IR-cut filter [@chuanganCh2021a] |
| CHANCCTV CH2010AC | M6.5, body length 4.15 | TTL 5.68 | Alternative for 850 nm: built-in bandpass, published mass 0.3 g; supplied 5205A holder is 10 mm square [@chuanganCh2010ac] |

CH2021A is 40% smaller in diameter and about 77% shorter in body length than
the imported CIL829. These ratios compare lenses, not complete mounted assemblies.
An M6 holder necessarily needs an outside wall beyond its 6 mm bore; it cannot
simply use the reconstructed 6.3 mm square M5 housing.

## Qualification limits and next design inputs

OV9281 has a published image area of 3.896 x 2.453 mm (approximately 4.60 mm
diagonal), so CH2021A's 4.8 mm maximum image circle passes a nominal size screen.
This does not establish edge sharpness or illumination. Its specified chief-ray
angle limit is below 28.4 degrees; the sensor product page lists 9 degrees.
The ray-angle profiles need compatibility review [@omnivisionOv9281Brief;
@chuanganCh2021a].

CH2021A specifies a minimum object distance of 0.1 m. Adjustable mounting might
permit closer focus, but 10–20 mm from the front glass is outside the published
range. No reviewed source establishes 940 nm transmission, MTF or close-focus
performance. No IR-cut filter also means no visible suppression; the required
IR-pass or bandpass filter remains a separate design input [@chuanganCh2021a].

For the next study, use the unscaled M6 x 0.35 interface, provision axial focus
adjustment, and check holder walls, sensor coverglass clearance and filter space.
Do not infer a finished holder height from TTL. Keep sensor image-plane Z
explicitly provisional until package/coverglass dimensions are established.

CH2010AC is an 850 nm alternative, not a substitute for the currently planned
940 nm LEDs. Its 4.6 mm maximum image circle leaves little nominal margin, its
listed minimum focus is also 0.1 m, and its catalog FOV should not be transferred
to our sensor without checking [@chuanganCh2010ac].

The manufacturer's product listing provides public drawings and a quote path;
stock, minimum order and delivery time were not verified. This is not yet a
confirmed direct-purchase solution [@chuanganMiniLensCatalog]. No supplier was
contacted and no purchase was made.

Review scope: local Pupil reconstruction README, build source and selection
manifest; public IADIY PDF text; CHANCCTV PDF specification text and catalog
entries. No optical prescription, physical sample or manufacturer STEP for the
new compact candidates was reviewed.
