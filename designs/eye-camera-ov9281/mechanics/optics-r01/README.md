# CIL829 lens fit study

The supplied lens is imported into an editable FreeCAD document above the
selected R08 sensor head. Its axis follows the sensor's active-area datum from
the inherited KiCad footprint, rather than the center of the sensor package.
The R08 circuit and species assemblies are unchanged.

The supplier PDF specifies a 10 mm front diameter, an M8 × 0.35 thread,
6.6 ± 0.3 mm from the front shoulder to the rear, and 3.1 ± 0.3 mm from the rear
to the image plane. The 14.7 ± 0.3 mm total track length is a reference dimension;
the drawing assumes 0.4 mm coverglass. Optical specifications are 2.8 mm EFL,
F/2.55 and no filter [@commonlandsCil829Drawing].

The STEP imports as five valid solids. Its front diameter is 10 mm and physical
barrel length is 11.567 mm, consistent with the drawing's nominal 11.6 mm.
However, its member filename says `F3.0-M08ANIR`, and its internal product says
`F3.0-M08A650`. A 0.3 mm flat optical element is present. All supplied solids are
preserved; no element has been removed or identified as an IR-cut filter. This
is usable mechanical reference geometry, but its optical variant is unresolved
[@commonlandsCil829Step].

## Inspect in FreeCAD

Open the document selected in `active-model.json`. It contains the actual R08
PCB copper, supplied lens solids, active-area reference and optical axis. The
hidden M8 cylinder is an interface envelope, not a completed threaded holder.

Select **EDIT HERE — provisional image height and focus travel (mm)** in the
tree. `FocusTravel` moves the lens along its axis; 0, 0.5 and 1.0 mm were checked.
`ImagePlaneHeight` defaults to an explicit 1.2 mm assumption above PCB Z=0.
Neither parameter is a demonstrated focus distance. Sensor die height,
coverglass, close-focus travel, holder seating, visible-blocking filter and
940 nm performance remain to be qualified. The supplier's 1.4 g lens mass also
exceeds the reported 0.7 g whole Pupil reference camera [@commonlandsCil829Drawing].

## Reproduce

Use the pinned FreeCAD Python from `docs/development.md`. The build requires the
verified R08 STEP exports in `generated/ov9281-r08-desktop`; these are generated
by `export_r06_review.py --revision R08` from the matching native checkpoint.
Provide the user-supplied PDF and ZIP and choose a new output directory:

```powershell
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-camera-ov9281/build_optics_review.py --zip C:/Users/jonma/Downloads/CIL829-F2.5-M08ANIR.zip --pdf C:/Users/jonma/Downloads/CIL829-F2.5-M08ANIR.pdf --output generated/ov9281-optics-fit-02
```

Success produces a native document and `review.json`. The script checks source
hashes, solid validity, drawing envelope dimensions and parameter recomputation.
Source copies are retained beside the generated document. It does not validate
physical fit or camera operation. `open_optics_review.FCMacro` opens review 01
in the existing desktop window and saves its view images.
