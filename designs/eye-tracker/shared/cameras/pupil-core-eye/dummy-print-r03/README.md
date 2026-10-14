# Camera dummy R03

Replaces the R02 lens cuboid with a square housing, circular collar, recessed bore and two locating pins. Units: mm. R02 remains intact. No species checkpoint is changed.

User measurements: 6.3 square; 2.7 from mounting base to square corners; approximately 2.9 to collar rim. The user selected the middle-row fifth holder in the CCOM photograph as the shape reference [@ccomMiniatureLensHolders].

Chosen approximations: 5.4 collar diameter, smooth 4.0 bore with 0.35 floor, two diagonal 0.5 diameter pins extending 0.2 below the base. Pin positions and thread pitch were not measured. This is a dummy, not a functional threaded optical mount. Collar knurling is omitted. The head board remains 6 mm wide, so the measured housing overhangs by 0.15 mm each side.

Build with the pinned FreeCAD Python running build.py, then the CAD tooling Python running package.py and package_u1.py. Open the generated FCStd through tools/cad/open_in_running.py. Geometry validation checks solid validity, material overlap and connected assembly. Physical fit, stiffness and successful slicing remain unverified. U1 materials retain red, black and white PLA and yellow TPU assignments from R02.
