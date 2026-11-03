# UltraSkelly mounts

3D-printable mounts that hold UltraSkelly's cameras and electronics in fixed,
known positions. UltraSkelly is an Ultra Skelly animatronic skeleton fitted with
a Raspberry Pi 5 carrying a Hailo-8 AI HAT+ and an Adafruit DC and Stepper Motor
HAT, a separate PCA9685 servo driver board wired to the stack by jumpers, a
Stereolabs ZED Mini behind the eye sockets and a Luxonis OAK-1 behind a hole in
the nasal cavity. The robot software lives in
[freemocap/ultraskelly](https://github.com/freemocap/ultraskelly).

**No complete assembly is selected.** The parts below are in development, and
physical fit is unverified.

| Part | Status |
| --- | --- |
| Fit coupon | Scripted print test for the Pi 5 hole pattern, M2.5 pilot holes and zip-tie slots. Not yet printed. |
| Camera bracket | Planned. Holds the ZED Mini at the eye sockets and the OAK-1 at the nose hole, and defines each sensor's pose in the head frame. |
| Electronics shelf (`mount`) | First design, not printed. A plate clamps to the 1 inch spine tube with a collar and two M3 set screws. It carries the community OMT Pi 5 case cut down to 30 mm (open top), the PCA9685 on bosses beside it with short I2C jumpers, and zip-tie slots for the bundle into the skull. The PCA9685 jumpers came loose on 2026-11-02, which is why they get a fixed place. |

## Layout

| Folder | Contents |
| --- | --- |
| `src/` | Scripted FreeCAD builders and their parameters. |
| `references/` | Vendor CAD, datasheets and measurement photos, with provenance. |
| `anatomy/` | The [head frame](anatomy/README.md) shared by all mounts, and the measured skull dimensions. |

Working builds go to `generated/ultraskelly/<part>/<run>/`. Read the
[working guide](../../docs/organization-guide.md) and the
[development guide](../../docs/development.md) before building or exporting.

## Live FreeCAD views

Start the pinned FreeCAD window with its localhost code bridge, then build
into it from the repository root:

```powershell
./tools/cad/cad.ps1 start-freecad
./tools/cad/cad.ps1 show-freecad
& 'tools/cad/.venv/Scripts/python.exe' -B designs/ultraskelly/src/live.py mockup --run r001
& 'tools/cad/.venv/Scripts/python.exe' -B designs/ultraskelly/src/live.py hardware_view --run r001
```

- `mockup` draws a simple Ultra Skelly: the 1 inch square spine tube, the neck
  drive and post, the skull with the head frame, and placeholder body parts.
  Its sizes in `src/mockup.json` are estimates around the published 6.5 ft
  height [@homedepotUltraSkelly].
- `hardware_view` lays every board, camera, actuator and supply flat and draws
  their connections: USB, PCIe, I2C jumpers, servo and motor leads and power.
  It uses the vendor models where `references/vendor.json` has them.
- `case_view` places the Pi 5, AI HAT+ and Motor HAT in the community OMT
  Pi 5 case with its lid off [@omtPi5Case].

- `mount` builds the electronics shelf and exports `shelf-plate.stl` and
  `omt-case-cut.stl` for printing.
- `assembly` places the shelf on the mock-up's spine tube and reports its
  gaps to the estimated shoulders, neck drive and jaw.

Each run saves a new folder under `generated/ultraskelly/` and leaves the
document open for review. `snapshot` saves the active view as a PNG.

## Build the fit coupon

The coupon tests the printer before the Pi 5 stack mount is designed. Bosses 1
to 4 carry 1 to 4 index marks and pilot holes of 2.2, 2.4, 2.6 and 2.9 mm, on
the Pi 5's 58 × 49 mm hole pattern [@raspberrypi2025Pi5Drawing]. The tab has
two zip-tie slots, each 5.2 × 2.2 mm, for strain-relief ties up to 4.8 mm wide.
Parameters are in `src/fit-coupon.json`.

Prerequisite: the pinned toolchain from the development guide.

1. From the repository root, build a new run with the pinned FreeCAD Python:

   ```powershell
   & '.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe' -B designs/ultraskelly/src/fit_coupon.py --run r001
   ```

   The builder refuses a run folder that already has files. It saves
   `fit-coupon.FCStd`, `fit-coupon.stl` and `build-report.json` in
   `generated/ultraskelly/fit-coupon/r001/`.
2. Audit the mesh with the tools environment:

   ```powershell
   & 'tools/cad/.venv/Scripts/python.exe' -B tools/cad/inspect_mesh.py generated/ultraskelly/fit-coupon/r001/fit-coupon.stl --output generated/ultraskelly/fit-coupon/r001
   ```

   A good result reports one watertight shell.
3. Print the STL flat, bosses up. Record which pilot hole holds an M2.5 screw
   firmly, whether the Pi 5 seats on all four bosses, and which zip ties pass
   through the slots.

Geometry checks and watertight meshes do not establish physical fit. Record
print and fit results separately from geometry validation.
