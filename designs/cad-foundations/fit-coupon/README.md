# 3. Clearance coupon and embossed labels

36 × 16 × 4 mm coupon for a fictional 3.0 mm pin. Three holes are 3.1, 3.3,
3.5 mm diameter: 0.1, 0.3, 0.5 mm DIAMETRAL clearance. Centered radial gaps
are half those amounts. No actual pin or printer fit was measured.

Open checkpoints/01-clearance-coupon.FCStd or 02-embossed-labels.FCStd.
Use ../replay.py stages `plain` and `labels` for safe fresh builds. model.py owns
geometry and validation. Historical build.py and label_step.py use FitCoupon and
fixed checkpoint paths and should only be run in a working copy.

PinDiameter and hole radii use native expressions. Raised text is a creation-time
snapshot: regenerate labels after changing diameters. Text size is 3 mm, relief
0.6 mm, embedded 0.1 mm for fusion. Regeneration requires the font named in
parameters.json (C:/Windows/Fonts/arialbd.ttf on the original machine). The font
is not redistributed. label-record.json preserves its original hash and labels.

Build checks include valid one-solid output, hole sizes/spacing and removed
volume; embossed output checks include relief and fusion volume. Physical fit,
small label strokes, nozzle/layer effects and process bias remain untested.
Clearance is intentional size difference; tolerance is allowed variation.
See CHANGE-NOTES.md for history.
