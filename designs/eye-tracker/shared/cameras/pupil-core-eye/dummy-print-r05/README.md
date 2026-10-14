# Camera module R05 with optical datum

Integrates the user-accepted protruding dummy lens from lens-m5-r03 at the prior lens center in the full camera module. Units: mm. R04 and selected species checkpoints are preserved. Source hashes, including the accepted lens STEP, are verified before building.

CameraModule groups all physical parts and optical references so they move together. OpticalAxis starts at the accepted lens bounding-box center and points outward along +Z, through the center of its convex face. SensorFrame defines a hypothetical sensor center at the PCB top directly beneath the lens; its +Z is the same normal. SensorPlane is an optional hidden plane. These are geometric datums, not calibrated entrance-pupil or active-sensor measurements. Origin and direction properties are in the camera-module frame; apply CameraModule.Placement when using them in a posed assembly.

The new lens is mounted at the previous lens center with no change to ribbon route or board outlines. Embedded locating pins are clipped at the PCB underside, and intersecting PCB material is assigned to the black lens region. The remaining four material regions retain red/black/white PLA and yellow TPU. Axis and sensor references are excluded from all physical STEP/STL/3MF exports.

Run build.py with pinned FreeCAD Python, then package.py and package_u1.py with CAD tooling Python. Open review.FCMacro through the existing desktop listener. Validation checks source hashes, connected valid solids, non-overlapping material regions, board/ribbon dimensions and optical-axis alignment with the sensor-plane normal. Physical fit, slicing and calibrated optical behavior remain unverified.
