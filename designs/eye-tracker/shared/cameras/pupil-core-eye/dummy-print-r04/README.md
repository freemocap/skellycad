# Camera dummy R04

Adds a rounded helical internal screw thread to the R03 lens housing. The nominal M4 diameter comes from the user; 0.35 mm pitch is a modeling approximation. The modeled root diameter is 4.08 mm and bore diameter is 3.6 mm. This visual dummy thread is not a validated mechanical fit or an ISO tolerance-class thread.

All other geometry and material assignments inherit R03. Square width 6.3 mm, corner height 2.7 mm, collar rim 2.9 mm. R03 and accepted assembly checkpoints remain unchanged. Source morphology and approximation details are recorded in ../dummy-print-r03/README.md. Rebuild using build.py with pinned FreeCAD Python, followed by package.py and package_u1.py with CAD tooling Python. Physical printing remains unverified.
