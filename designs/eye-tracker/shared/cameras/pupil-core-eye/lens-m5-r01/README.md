# M5 holder reconstruction

Reconstructed from the supplied IADIY CL5P1.6 v1.2 datasheet, page 2, 6.5 mm holder drawing [@iadiyM5HolderDrawing]. No downloadable manufacturer CAD was found. Units: mm. This independent review model does not change any selected camera or species assembly checkpoint.

Source dimensions: square 6.5, base height 1.6, overall height 2.95 excluding pins, pin spacing 5.7, nominal M5 x 0.35 thread. Applied uniform scale 6.3/6.5 = 0.96923077. Result: square 6.3, base 1.55077, collar rim 2.85923, nominal thread 4.84615 with pitch 0.33923. Scaling also changes the thread, so this is a visual dummy rather than a functional standard M5 mount.

Collar OD 6.5 follows the top-view outline. Base corner radius 0.2, rounded thread groove, and diagonal pin pairing are approximations. Pins use diameter 0.35 and length 0.5 from the drawing callouts; interpretation is provisional. Bore goes through the holder. The drawing table has a P3.5 typo; the sectional callout and page 1 specify M5 x 0.35.

Run build.py with pinned FreeCAD Python to export original and scaled FCStd, STEP and STL. Validation checks solid validity, closed meshes and scaled width. Physical fit and printing are unverified. The supplied PDF is retained unchanged as source-datasheet.pdf.
