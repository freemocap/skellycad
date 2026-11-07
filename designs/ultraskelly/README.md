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
| Neck clamp and enclosure (`enclosure`) | Concept approved on 2026-11-02, lightened on 2026-11-03 with shapes and print settings checked against published FDM guidance, and given a smaller, rounded clamp the same day. A numbered fit set of five clamp sizes was printed on the robot's tube, and the user chose U1 (18.9 mm pocket, for an 18.0 to 18.6 mm tube). On 2026-11-04 the clamp and its lock were converted to M2.5, so the whole mount takes one screw size in two lengths, M2.5 x 16 and M2.5 x 6. The current set is [US-NECK-MOUNT-R010](checkpoints/r010-neck-mount/README.md): reprint only the clamp U and bar, keep the printed R006 enclosure back and carrier, and no part needs supports. A U clamp and front bar (4 x M2.5 into captured nuts) stay on the square tube. The enclosure back is a light frame that carries the Pi on a four-standoff carrier, the Pi stack with its long axis along the tube and the USB end up, and the PCA9685 on a side wing; it slides down onto the clamp's dovetail and one M2.5 screw through the enclosure into the tongue locks it, so the electronics lift off without touching the clamp. |
| Tube splice (`splice`) | Added on 2026-11-06 to join two pieces of the square tube end to end, and made stronger the same day for a joint that flexes. [US-TUBE-SPLICE-R003](checkpoints/r003-tube-splice/README.md) is the neck clamp's U1 cross-section made 70 mm long with an 8 mm base and 20 mm arms, and one 8 mm plate across both tube pieces with an M2.5 x 16 screw into a captured nut at each corner, so each piece is gripped over 35 mm. A 3 mm tongue on the plate reaches between the arms and presses on the tube. The U prints on its back, so bending at the joint runs along its layers, and both parts print solid without supports. Unprinted; geometry checks only. |

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
  height [@homedepotUltraSkelly]. Its sizes are guesses, so the mount does not use
  the mock-up for clearances.
- `hardware_view` lays every board, camera, actuator and supply flat and draws
  their connections: USB, PCIe, I2C jumpers, servo and motor leads and power.
  It uses the vendor models where `references/vendor.json` has them.
- `case_view` places the Pi 5, AI HAT+ and Motor HAT in the community OMT
  Pi 5 case with its lid off [@omtPi5Case].

- `enclosure` builds the neck clamp, the enclosure back and the Pi carrier
  around the Pi stack and PCA9685. `--lifted` shows the quick release.
  `--skeleton-z` places it on the mock-up and reports gaps; it stops while the
  mock-up's spine and the clamp's tube differ.
- `splice` builds the tube splice: the clamp U's cross-section from
  `src/enclosure.json`, with the base, plate, tongue and length that
  `src/splice.json` sets, shown on two tube pieces. It reports the
  cross-section at the joint.
- `print_review` lays out a print checkpoint's STL files on a bed outline,
  after checking them against the checkpoint's manifest hashes.
- `part_images` renders one image per printed part of a run, alone on a bed
  square, and `part_titles` adds a large name band above each image.
- `compare_images` renders each part of an earlier and a new print set at one
  scale, and `compare_sheet` lays the pairs out with their names and grams.
- `clamp_set` builds the numbered clamp fit set from `src/enclosure.json`: five
  U sizes with sunk numbers and one bar, laid out on one plate. `plate_files`
  joins the parts into the plate STL and a 3MF with one named object per part.

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
