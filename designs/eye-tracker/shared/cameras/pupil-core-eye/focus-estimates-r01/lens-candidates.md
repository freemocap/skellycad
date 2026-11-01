# Miniature lens candidates — 2026-10-30

The user's direct observation establishes that this particular lens screws in
and out. Treat it as adjustable. Generic Pupil hardware guidance about glued
lenses does not establish the construction of this unit.

The closest dimensional and focal-length lead is the IADIY CL5P1.6 family. These
are candidates for inquiry and experiments, not verified replacements. No lens
was identified as the installed Pupil component, purchased, or physically tested.

| Candidate | Published optics and interface | Assessment for this assembly |
| --- | --- | --- |
| IADIY CL5P1.6I3.6FL1.8 | 1.75 mm, f/2.4; M5×0.35; TTL 3.05 mm; BFL 0.70 mm | Closest nominal alternative to the supplied 1.7 mm focal length. Minimum object distance is not specified in the reviewed sources. |
| IADIY CL5P1.6I3.6FL2.2 / FL2.5 | 2.2 mm f/2.2, TTL 3.2 mm, BFL 0.64 mm; or 2.5 mm f/2.8, TTL 3.4 mm, BFL 0.65 mm; both M5×0.35 | Longer focal-length scenarios for greater magnification. Close-focus performance requires qualification. |
| Towin M401916006520 | 1.9 mm f/2.0; M4×0.25; TTL 3.2 mm; mechanical BFL 0.60 mm; minimum object distance 0.2 m | A credible small M4 example, but its published minimum distance does not support the proposed approximately 13 mm optical-distance scenario. |
| Towin M502716504436F | 2.7 mm f/3.6; M5×0.35; BFL 0.97 mm; minimum object distance 18 mm | A nearby close-focus comparison, not a confirmed solution at 13 mm. The minimum-distance datum is unspecified. |

IADIY values come from its product table and v1.2 datasheet
[@iadiyM5OpticalCandidates2026; @iadiyM5HolderDrawing]. Towin values are from the
respective manufacturer specification tables [@towinM4ShortLens2026;
@towinM5CloseLens2026]. Towin's supplementary fields disagree slightly: 3.3 mm
TTL for the 1.9 mm model and f/3.5 for the 2.7 mm model. Confirm drawings and
aperture with the supplier before relying on these values.

## Conditions for a replacement

Measure the actual thread diameter and pitch first. The existing 6.3 mm CAD
holder is a scaled reconstruction of an M5 holder drawing; its shape does not
prove an actual M5 interface. M4×0.25, M4×0.35 and M5×0.35 are distinct interfaces.
The existing M4×0.35 reference is a 6 mm f/4.5 lens with a 0.2 m minimum distance,
so it is not a promising close substitute [@towinM4LensExample].

The default IADIY filter transmits at most 3% on average over 700–1000 nm;
an IR-pass or other suitable variant is necessary for near-infrared imaging.
Its datasheet explicitly offers alternative filters [@iadiyM5HolderDrawing].
The Towin 2.7 mm model also includes an IR-cut filter. No spectral transmission
curve was established for the 1.9 mm model.

Verify rear-element clearance, thread engagement through the intended focus
travel, optical back focus, and image quality at the actual illumination
wavelength. Published field angles apply to the suppliers' larger sensor formats,
not directly to this roughly 1.2 mm square active region. Matching a thread does
not establish optical or physical fit.

Review scope: manufacturer product specification excerpts and IADIY PDF text,
pages 1–2; no optical prescription, stock availability, price, close-range MTF,
or measured depth-of-field curve was established. No suppliers were contacted.
