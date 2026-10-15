# Rat eye and skull scale evidence

Reviewed 2026-10-14. This is an evidence audit, not a geometry revision. It uses
the repository clear-technical-writing skill. Values below do not establish a
median adult male rat: cohorts differ in strain, age, preparation and endpoints.

## Eye envelope

Retain the current Hughes-based exterior as the first comparison candidate:
transverse diameter 6.410 mm, exterior axial length 6.291 mm, limbus diameter
5.640 mm, anterior apical radius 2.965 mm and posterior radius 3.230 mm. These
are the existing repository's extraction of Hughes's D.A. rat schematic
(approximately 125 days); this audit did not remeasure the original tables.
The intermediate scleral contour remains a CAD interpolation.
[@hughes1979RatEye]

An independent in-vivo cohort provides a useful size sensitivity case, not a
drop-in replacement: 33 male Brown Norway rats, 10–28 months, body mass
391 ± 64 g. One randomly selected eye per rat gave cornea-to-retina axial
length 6.91 ± 0.44 mm. Corneal radius was 3.39 ± 0.03 mm in eight animals.
Those are means ± SD. The retinal endpoint excludes the posterior outer sclera,
and the older cohort cannot define the external globe of a generic young adult.
Figure 5 shows medians graphically; no numeric median was extracted. Methods,
biometry results and endpoint definitions were reviewed through indexed primary
article text. [@lozanoTwa2013RatEye]

**Action:** compare the existing envelope against a registered globe segmentation
before changing size. Keep the transverse and axial scale controls separate;
do not uniformly enlarge all camera anatomy to match an optical axial length.

## Skull scale checks

Pires et al. report a healthy control group of 12 male Wistar rats aged 180 days,
from two dams. Fixed crania were measured radiographically. These control
means ± SD are useful checks; they are not pooled species medians. Methods and
Tables I–II were inspected. [@pires2020RatSkull]

| Measurement | Control, mm | Endpoint interpretation |
|---|---:|---|
| L2 | 47.81 ± 1.45 | Direct occipital-protuberance to incisor-alveolar-margin distance |
| L4 | 19.64 ± 0.71 | Nasal tip to median nasofrontal suture |
| W3 | 7.40 ± 0.19 | Narrow frontal span at the specified temporal-line level |
| W4 | 17.06 ± 0.41 | Between anteromedial tympanic-bulla edges |
| H3 | 4.97 ± 0.32 | Orbital wall span at infraorbital fissure |
| L7 | 6.25 ± 0.31 | Specified infraorbital-to-supraorbital margin span |

These are landmark distances, not whole-mesh bounding-box dimensions. In
particular H3 is not the globe diameter. The source supplies neither eye centers
nor optical directions. Its limited family sampling also constrains how broadly
the SD represents adult variation. [@pires2020RatSkull]

**Action:** measure at least L2, L4 and W3 on the candidate skull using named
landmarks, report ratios and residuals, and preserve specimen units. A single
uniform scale may serve a declared representative model if the independent
dimensions agree; disagreement requires a shape assessment, not three-axis
warping until every target fits.

## Eye position and direction are separate questions

The Hughes article's p. 587 gives a mean **optic-nerve-head projection** of 58°
temporal and 30° elevated, based on six anesthetized and six dead rats. Its
in-vivo visual-field comparison describes nasal bone at 35° to horizontal.
These observations were reviewed in indexed text of the original article
reprinted in Hughes's thesis. They are not a verified corneal optical axis or
bregma–lambda-frame resting orientation. Do not copy those two angles into CAD
as though all three definitions were equivalent. [@hughes1979RatEye]

Wallace et al. demonstrate that gaze changes with head pitch and roll during
free behavior. The main article and Figure 2 support testing a pose range, but
this review did not recover a universal skull-frame resting optical direction.
The camera target should therefore be a declared neutral modeling convention,
with an angular sensitivity study, rather than a claimed fixed biological rest
pose. [@wallace2013RatEyes]

Belli et al. explicitly compare head reference planes. In female Long Evans
rats aged 5–36 months, the eye-corner/nose plane differs from the whisker-row
plane by +12.3° mean (n=5); leveling bregma–lambda pitches the head approximately
−8.04° relative to that row plane (n=4; median −8.56°, SD 2.04°). These are frame
offsets, not eye-gaze angles. Their facial eye points are rostral/caudal eye
corners, not globe centers. Methods and reference-frame Results/Figure 4 were
reviewed. [@belli2018RatFace]

The 2024 correction changes Figure 9/10 positions and numeric supplementary
values. Use its replacement spreadsheet if deriving facial landmark checks;
do not extract those data from the superseded figure. The correction was
reviewed; its spreadsheet was not downloaded in this audit.
[@belli2024RatFaceCorrection]

## Registration requirements and next comparison

1. Prefer skull and globes from the same physical scan/specimen. A skull-only
   landmark set constrains bone; it cannot determine the missing soft-tissue
   eye center uniquely.
2. Store original millimetre coordinates, a midsagittal plane and an explicit
   bregma–lambda frame. Display bregma, lambda, nasion, incisor-alveolar margin,
   occipital protuberance, bilateral orbital landmarks and tympanic landmarks
   with English names. Distinguish author annotations from local estimates.
3. Fit a globe envelope to segmented outer sclera, then fit corneal apex/limbus
   independently. Define the optical datum from the corneal/schematic symmetry
   axis; do not substitute the optic-nerve exit or an eye-corner midpoint.
4. Compare a registered specimen pose with the existing eye pose and a clearly
   labeled exploratory neutral pose. Report center displacement, axis change,
   globe/skull intersection and reference-frame provenance separately.
5. After anatomical review, reposition the baseplate against the skull surface,
   preserving the requested screw clearance. Then aim cameras, refit supports
   and ribbons, and validate mechanical constraints independently of anatomical
   confidence. Make the filled printable skull a separate derivative.

Until a paired soft-tissue source or direct corneal measurements are available,
the next actionable result is a labeled, scaled skull comparison with an
explicitly estimated eye overlay—not a falsely precise adult male median.
