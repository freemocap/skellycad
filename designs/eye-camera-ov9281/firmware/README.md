# OV9281 snapshot firmware

Both the sensor and synthetic variants compile for **ESP32-P4 revision 3.x**.
The host decoder, control protocol and recording provenance pass twelve tests. No firmware has run on a board and no
physical image has been recorded. This is the first bring-up implementation,
not the 120 fps product firmware.

The sensor variant initializes the public OV9281 driver in its existing
640 × 400 RAW8, 100 fps mode, bypasses Bayer processing, and returns one grayscale
snapshot per host request. Intervening sensor frames are discarded. The
synthetic variant generates a marked test pattern without initializing the
camera. Exposure and gain commands are implemented for the sensor variant,
with driver-bound checks and host acknowledgements. Neither variant implements
UVC or continuous streaming [@espressifOv9281Driver; @espIdfCameraController; @espTinyusbSerialExample].

The host accepts `--exposure-lines` and `--gain-index` with a real port. Wire
commands are `E<decimal lines>\n` and `G<decimal driver-table index>\n`; `F`
requests a frame. A successful control replies `!E OK <value>\n` or
`!G OK <value>\n`. Rejected settings fail the host request; synthetic mode does
not pretend to apply sensor settings. Units are sensor lines and driver gain
indices, not milliseconds or decibels. These controls have compiled and passed
host protocol tests, but have not been exercised on hardware.

## Board contract

Use the R11 assembly population: **R7 absent, R8 populated with 0 ohm**, selecting
SID low and 7-bit SCCB address **0x60**. GPIO7 is SCL and GPIO8 is SDA, through
the schematic's 3.3/1.8 V level shifters. GPIO6 drives the inverting reset
transistor, so HIGH asserts sensor reset. The driver receives reset pin -1;
the application handles that inversion. GPIO5 stays LOW, keeping the reserved
LED control off. SCCB runs at 100 kHz. The selected local head oscillator is
Epson X1G004171003100, supplying 24 MHz from the 1.8 V rail. The R11 driver uses
the same GPIO assignments and reset inversion as the earlier boards.

`board-contract.json` records the R11 pin assignments, flash settings, connector
pinout and capture limits. `verify_r11_firmware.py` compares that contract and
the application constants with the native schematic netlist and effective
build configurations. The selected flash is 4 MB, 3.3 V, DIO at 40 MHz.
The host recording manifest includes the software target and contract hash;
this metadata does not identify or authenticate a connected physical board.
The USB product string also identifies the R11 bench firmware.

The driver's mode-table comment says 800 Mbps per MIPI lane, while its format
metadata contains `mipi_clk = 400000000`. The current receiver setting follows
the 800 Mbps mode-table comment. That choice is **unverified**; resolve clock
versus DDR bit-rate interpretation against the programmed sensor timing and
receiver behavior before calling capture functional [@espressifOv9281Driver].
At the pinned commit, Espressif's higher-level CSI adapter assigns
`mipi_clk / 1000000` directly to `lane_bit_rate_mbps`, which produces 400 for
this metadata. R11 uses the direct CSI controller and retains the explicit
800 Mbps table-header choice. The configurable receiver rate and this
source-level disagreement remain part of the bring-up record
[@espVideoCsiAdapterPinned2026].

One application buffer and one CSI backup buffer require 512,000 bytes before
other allocations. A buffer is queued once, returned by the completion callback,
invalidated from cache, and sent before reuse. A capture timeout asserts reset
and halts the task rather than reusing memory still potentially owned by DMA.
This ownership design has compiled; its timing has not been exercised on silicon.

## Reproduce the builds on Windows

Prerequisites: Git, Python 3.12 and network access for the first setup. Run from
the repository root. The following setup creates local ignored dependencies;
it does not flash hardware. If either checkout already exists, verify its commit
against `toolchain.json` instead of cloning over it.

```powershell
git clone --branch v5.5.6 --depth 1 https://github.com/espressif/esp-idf.git .cad-tools/esp-idf
git -C .cad-tools/esp-idf submodule update --init --recursive
git clone https://github.com/espressif/esp-video-components.git .cad-tools/esp-video-components
git -C .cad-tools/esp-video-components checkout 789cde3bd09296a13d4e70afe011366b60ac772c
$env:IDF_TOOLS_PATH = Join-Path (Get-Location) '.cad-tools/espressif'
python .cad-tools/esp-idf/tools/idf_tools.py install riscv32-esp-elf cmake ninja
python .cad-tools/esp-idf/tools/idf_tools.py install-python-env
python designs/eye-camera-ov9281/firmware/build.py --output-root generated/camera-firmware-r11
python designs/eye-camera-ov9281/firmware/build.py --synthetic --output-root generated/camera-firmware-r11
```

`build.py` checks the exact IDF and sensor-driver commits before building. IDF
v5.5.6 is pinned because v3.x silicon requires the revised SDK; older P4 firmware
is not interchangeable [@espP4Rev3Guide]. The managed component versions are
pinned in `main/idf_component.yml`. Build outputs, logs, effective sdkconfig,
and binary/source SHA-256 reports are under `generated/camera-firmware-r11/sensor/`
and `generated/camera-firmware-r11/synthetic/`. Success requires exit code 0 and
`compiled: true` in each build report. No automatic flash step is provided.

## Exercise recording without hardware

```powershell
python -B -m unittest discover -s designs/eye-camera-ov9281/firmware/host -p 'test_*.py' -v
python designs/eye-camera-ov9281/firmware/host/camera_link.py --simulate --frames 3 --output generated/camera-loopback-new
python designs/eye-camera-ov9281/verify_r11_firmware.py
```

Choose a new output directory on each recording run. It contains grayscale PGM
files and `recording.json`. Simulation marks every frame `synthetic: true` and
`physical_capture_demonstrated: false`. This tests packet parsing and file writing;
it does not emulate the ESP32-P4 or optics. Tests cover fragmented input, an
independent CRC fixture, corruption recovery, bounded input storage, flags and
saved-file provenance. The older `verify_offline.py` remains an R08 audit;
it is not the verification entry point for this R11 checkpoint.

After a physical board passes electrical checks and the appropriate firmware is
flashed, install `pyserial==3.5` into a project environment and run the same host
script with `--port COMx` instead of `--simulate`. Replace COMx with the actual
CDC port. The script records only CRC-valid complete frames. Check the synthetic
flag before treating them as sensor images. Sensor UART logs use the programming
interface. USB VID/PID 0xCAFE/0x4011 are development values, not assigned product
identifiers. USB power descriptors and the bus-power budget are unqualified.

## Wire format

The host sends ASCII `F`. The device replies with a 32-byte little-endian header
followed by `width × height` RAW8 bytes. Python struct: `<4sHHHHIQII`.

| Field | Bytes | Meaning |
| --- | ---: | --- |
| Magic | 4 | `SKY1` |
| Version | 2 | 1 |
| Flags | 2 | Bit 0: synthetic; other bits must be zero |
| Width, height | 2 each | Pixel dimensions |
| Sequence | 4 | Device frame counter |
| Timestamp | 8 | Device uptime in microseconds at completion; not exposure start |
| Payload length | 4 | Width × height |
| CRC32 | 4 | IEEE CRC-32 of payload only |

The request queue holds one pending command. The host sends requests sequentially.
USB interruption can truncate a frame; the host searches for the next valid
header and CRC. This protocol makes no synchronization or sustained-rate promise.

## Dependency review

Reviewed local licenses: ESP-IDF, `esp_cam_sensor`, `esp_sccb_intf` and
`esp_tinyusb` use Apache-2.0; TinyUSB uses MIT. The example API basis is public
domain/CC0. Dependency source and license files remain in the pinned checkouts
or managed-component cache, not copied into this design. Existing hardware
attribution remains beside each native revision.

The actual sensor link map includes the OV9281 driver and excludes the named
IPA/H.264 and radio libraries checked in `verify_offline.py`. This is a scoped
dependency inspection, not an assertion that every SDK/toolchain file has one
license or that the chip's ROM is open source. No separately licensed codec or
private sensor register document was needed to build this snapshot path.
