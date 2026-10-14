# Camera dummy R08

R08 retains the R07 notched lens, connector, LEDs and optical datum. The TPU
ribbon now occupies the same Z interval as both PLA boards: 0 to 0.25 mm in
the print frame. This replaces R07's raised 0.175 to 0.325 mm ribbon with a
continuous flat substrate whose boundaries change material only.

Dimensions are in millimetres. The 0.25 mm common thickness is a mock-up
choice based on the existing board thickness, not a new physical measurement.
The optical axis and hypothetical sensor plane are CAD reference geometry;
printing exports contain only the four physical material regions.

Build and packaging scripts preserve R07 and selected species checkpoints.
Geometry validation checks coplanar slab bounds, closed meshes, zero material
volume overlap and a connected assembly. Physical fit, stiffness and sliced
print results remain unverified.
