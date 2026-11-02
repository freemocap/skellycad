# UltraSkelly head frame and skull measurements

Every UltraSkelly mount and every reported sensor pose uses the head frame `H`
defined here. CAD units are millimetres. The frame is attached to the skull, so
it turns with the head's pan and tilt.

**Status:** defined; landmarks not yet measured. `skull-measurements.json`
lists the measurements requested from the robot, with their endpoints. Its
values stay empty until they are measured.

## Landmarks

| Landmark | Definition |
| --- | --- |
| `L` | Center of the skull's left eye-socket opening, in the plane of the socket rim. "Left" is the skull's own left. |
| `R` | Center of the skull's right eye-socket opening, in the plane of the socket rim. |
| `N` | Center of the nose hole, in the plane of its outer rim. |

## Axes

The frame is right-handed, with x forward, y left and z up:

1. The origin `O` is the midpoint of `L` and `R`.
2. `+Y` is the unit vector from `R` to `L`.
3. `+Z` is the part of the vector from `N` to `O` that is perpendicular to `+Y`,
   normalized. It points up the face.
4. `+X` is `+Y × +Z`. It points forward, out of the face.

The camera bracket centers the ZED Mini's lenses on `L` and `R` and the OAK-1's
lens on `N`. Its design therefore gives each sensor's pose in `H`; how closely
the printed bracket matches those poses is a fit question, recorded separately.

## Sensor poses

Each sensor's pose is reported as the transform from its optical frame to `H`:
a rotation and a translation in millimetres. Optical frames follow the image
convention: `+Z` along the optical axis out of the lens, `+X` toward the image's
right and `+Y` toward the image's bottom.

| Sensor | Optical frame origin |
| --- | --- |
| ZED Mini left camera | Left lens optical center. |
| ZED Mini right camera | Right lens optical center, 63 mm from the left along the baseline [@stereolabs2026ZedMiniDatasheet]. |
| OAK-1 | IMX378 lens optical center. |

To place `H` on the robot's body, the record also needs the pan and tilt axes in
`H`. They are measurement items in `skull-measurements.json`.
