# UltraSkelly mounts

3D-printable mounts that hold UltraSkelly's cameras and electronics in fixed,
known positions. UltraSkelly is an Ultra Skelly animatronic skeleton fitted with
a Raspberry Pi 5, a Hailo-8 AI HAT+, Adafruit servo and DC motor HATs, a
Stereolabs ZED Mini behind the eye sockets and a Luxonis OAK-1 behind a hole in
the nasal cavity. The robot software lives in
[freemocap/ultraskelly](https://github.com/freemocap/ultraskelly).

**No complete assembly is selected.** The parts below are in development, and
physical fit is unverified.

| Part | Status |
| --- | --- |
| Camera bracket | Planned. Holds the ZED Mini at the eye sockets and the OAK-1 at the nose hole, and defines each sensor's pose in the head frame. |
| Pi 5 stack mount | Planned. Holds the Pi 5 and its HAT stack on the neck/spine bar or outside the skull, with strain relief for USB, I2C and power leads. |

## Layout

| Folder | Contents |
| --- | --- |
| `src/` | Scripted FreeCAD builders and their parameters. |
| `references/` | Vendor CAD, datasheets and measurement photos, with provenance. |
| `anatomy/` | Measured skull dimensions and the head frame shared by all mounts. |

Working builds go to `generated/ultraskelly/<run>/`. Read the
[working guide](../../docs/organization-guide.md) and the
[development guide](../../docs/development.md) before building or exporting.

Geometry checks and watertight meshes do not establish physical fit. Record
print and fit results separately from geometry validation.
