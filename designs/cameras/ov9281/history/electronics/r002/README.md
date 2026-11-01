# R02: connected OV9281 / ESP32-P4X circuit draft

Open `camera.kicad_sch` in KiCad. This revision contains actual component pins,
wires and net labels, with project-local symbols and footprints. It is an
electrical draft; there is no custom PCB layout or fabrication release.

## What changed

- Preserved one Antmicro OV9281 channel, including 32 reference components.
  Restored the PVDD, VH and additional bypass networks omitted from R01
  [@antmicroOv9281Board]. R01 remains preserved as an incomplete extraction.
- Added the official current-revision P4X symbol, with a 16 MB PSRAM variant as
  the design basis. Corrected the library electrical types of VDD_ANA (101) and
  VDD_BAT (102) from bidirectional to power input, consistent with their supply
  functions; physical pin numbers are unchanged
  [@espressifKicadLibrary; @esp32P4Datasheet].
- Added external QSPI flash, 40 MHz crystal circuit, reset/boot pull-ups and
  UART programming connections. GPIO37/38 connect to UART0; GPIO35/36 provide
  boot-mode control. Crystal part and load capacitors remain unselected
  [@esp32P4HardwareGuide].
- Added system and core buck stages. The core circuit follows the v3.x
  feedback arrangement. The system divider gives nominal 3.318 V from the
  0.6 V feedback reference. Inductor current rating, effective capacitance,
  transients and thermal behavior still need qualification
  [@esp32P4HardwareGuide; @tiTlv62569].
- Connected six camera differential signals to the dedicated CSI pins and USB
  to the dedicated high-speed pins. Added USBLC6-2P6 protection. Four-contact
  JST SH is a footprint candidate; its proposed VBUS/D-/D+/GND numbering is
  ours, not verified compatibility with a Pupil cable
  [@esp32P4Datasheet; @stUsblc6].
- Added 3.3 V / 1.8 V open-drain I2C translation and a reset transistor.
  GPIO6 high asserts sensor reset; low releases it. Control-edge timing and
  pull-up sizing remain bench checks. GPIO5 is reserved for LED control.

`J102` is a logical 24-contact harness allocation, deliberately without a
physical connector footprint. It documents the intended signals while the
actual connector, flex stackup, and head/controller component partition are
resolved. The 24 MHz camera oscillator is present; its physical location is
not frozen. `J104` reserves the LED driver interface; it does not implement
LED current regulation or an emitter.

## Checks performed

KiCad 10.0.7 exports a 101-component netlist. Validation checks 236 controller
and supporting-component pin assignments, independently checks the CSI mapping,
power-domain separation and programming pins, and compares the connectivity of
the 32 retained reference components with the upstream netlist. All pass.
ERC reports zero errors and zero warnings with the existing KiCad default
disabled checks documented in the report. No ERC rules were disabled to obtain
this result. Supply flags identify the external supply and regulator output
rails; they do not validate power capability or startup sequencing.

Run from the repository root:

```powershell
python designs/eye-camera-ov9281/validate_r02.py
```

Success exits zero and updates `validation.json`. Reports and comparison
netlists go to `generated/ov9281-r02-validation/`. The schematic SVG was rendered
and inspected for sheet-level placement; this does not validate physical fit.

## Remaining before layout release

Select crystal/load capacitors, inductor and capacitor part numbers, the flex
connector and LED driver/emitter. Recheck supply sequencing, USB enumeration
current/inrush, absolute limits and the complete BOM. Partition the head and
controller, then lay out controlled-impedance camera/USB connections. Resolve
mechanical optics and connector clearance with the actual parts. Firmware,
USB bandwidth, IR images, current, heat and mass have not been tested.

The included `bom-draft.csv` is a review list, not a purchase list. Standard
passive footprints are provisional; in particular, high-capacitance parts may
need larger packages after voltage-bias and effective-capacitance checks.

## Rebuild and provenance

Antmicro inputs and selected Espressif assets are pinned under `../../reference`.
Source hashes, upstream commits and local symbol changes are recorded in
`source-record.json`. Antmicro assets retain Apache-2.0. Espressif and KiCad
library assets retain CC-BY-SA-4.0 with the electronic-design exception;
included notices and the upstream license apply
[@antmicroOv9281License; @espressifKicadLibrary; @kicadLibraryLicense].

Use a new output directory to rebuild; do not overwrite an open editor file:

```powershell
python designs/eye-camera-ov9281/build_r02.py generated/ov9281-r02-rebuild
& 'C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/python.exe' designs/eye-camera-ov9281/export_reference_footprints.py generated/ov9281-r02-rebuild
```

The second command exports required embedded reference footprints; it preserves
existing library files. Installed KiCad 10.0.7 libraries supply standard parts.
Third-party 3D model paths have not been resolved; no complete 3D assembly is
claimed.
