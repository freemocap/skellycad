# Rat eye R02: material regions and local frame

Open [the independent eye](rat-eye-definition-r02.FCStd) for the reusable model,
or [the skull placement study](rat-skull-eyes-placement-r02.FCStd) for its right
and left instances. Both use the same `create_eye` function in `../eye_model.py`.
The independent model requires no skull, camera assembly, or placement file.

## Geometry and colors

The C-oblate-cornea shape is retained from R01. Two oblate spheroid surface
patches meet at the existing limbus. `eye-definition.json` records each patch's
semiaxes, center and retained side of the joining plane. The equation for each
patch is `(x²+y²)/a² + (z-zc)²/b² = 1`. Its literature basis and shape assumptions
remain those documented in [the original model note](../README.md)
[@hughes1979RatEye].

Cornea and sclera are separate colored mesh objects inside one movable `App::Part`.
The right eye uses teal/warm white, and the left uses blue/cool white. These colors
are display identifiers, not anatomical pigmentation or optical properties.
Each region is closed with a shared internal planar disk. They partition the
solid envelope; they do not represent actual corneal or scleral tissue thickness.
There is no pupil or iris geometry.

The whole and component STLs use millimetres and share the local frame below.
STL does not store colors; the native FreeCAD documents preserve appearance and
the editable object hierarchy. Display axes are excluded from all STLs.

## Reference frame

**Origin:** analytic volume centroid of the entire uniform exterior envelope.
This is a geometric definition, not a tissue-weighted mass center or measured
eye rotation center. It is 0.105406 mm posterior to the old R01 axial midpoint.
The analytic first moment `integral(z * pi * rho(z)² dz)` divided by total
volume defines this shift; both spheroid patches contribute.

**+Z:** anterior, pointing outward through the corneal apex.

**+Y:** superior, the chosen top direction perpendicular to Z.

**+X:** `Y cross Z`. Consequently `X cross Y = Z`, and the basis determinant is +1.

The unplaced eye has identity orientation. Because the surface is rotationally
symmetric, geometry alone cannot determine which direction is top; +Y fixes
that otherwise arbitrary roll. In a placement with outward direction `z` and
skull dorsal direction `d`, the code constructs:

```text
z = normalize(outward)
y = normalize(d - dot(d,z)*z)
x = cross(y,z)
```

This is done independently for each eye. A parallel up/forward pair is rejected.
No reflection or negative scale is used. Both Y axes point dorsally, while the
X axes differ as required by handedness; requiring both X axes to point rostrally
would be incompatible with these outward Z axes and upward Y axes.

The registered skull frame has +X rostral, +Y dorsal, and +Z anatomical right.
Thus the positive-Z orbital eye is **Right**, and the negative-Z eye is **Left**.
These are the animal's sides. The definition also accommodates a subsequent
rigid rotation of the skull's placement.

For this centered eye, corneal apex Z is +3.250906 mm and posterior pole Z is
-3.040094 mm. The asymmetric endpoints are expected for a volume-centroid
origin. Overall dimensions remain 6.410 × 6.410 × 6.291 mm.

## Placement and editing

The prior open document's transforms were captured in `source-placement.json`.
Recentring is compensated in the world transform, preserving the anterior and
posterior endpoints and analytic envelope position. The axisymmetric surface
is rolled to align Y upward; its polygon sampling can rotate by that roll.
`frame-validation.json` records both complete rotations and centroids.

To move an eye, select **Right eye** or **Left eye** at the parent level and edit
**Data > Placement** or use **Transform**. Its two regions and axes move together.
Moving a material child separately would break the eye. The nested **Local XYZ**
group toggles all display guides; their positive arrows use X red, Y green, Z blue.
Hide the material regions to inspect the central origin marker.

Save manual changes as a new revision. The R01 studies and selected monocular
camera assembly remain unchanged. Skull placement remains a visual estimate.
The skull retains scienceminer's CC BY-SA attribution (version unspecified in
the supplied license); see `../../skull/provenance.json`.

## Reproduce and validate

From the repository root:

```powershell
& tools/cad/.venv/Scripts/python.exe designs/eye-tracker/rat/references/eyes/prepare_r02.py
& .cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe designs/eye-tracker/rat/references/eyes/validate_r02.py
```

The preparation script rebuilds centered material STLs and their definition into
ignored `generated/eye-tracker/rat/eye-materials-r02/`. Retained R02 artifacts are
not overwritten. Run `../review-r02.FCMacro` inside the existing FreeCAD GUI to
recreate both native documents into that generated directory from retained assets.

Checks cover component watertightness, conserved exterior triangles and total
volume, centroid residual, orthonormal right-handed frames, unchanged apex
positions, and reopened native hierarchy. The native validator moves parents
in memory to confirm that materials and axes follow, then closes without saving.
The centered triangulated envelope centroid differs from the analytic origin
by about 0.000023 mm because of tessellation. This is numerical agreement, not
an anatomical-accuracy estimate.
