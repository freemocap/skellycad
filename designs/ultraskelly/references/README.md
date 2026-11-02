# UltraSkelly references

Vendor CAD and datasheets for the parts the mounts hold. `vendor.json` lists
every file with its source URL, SHA-256, size, licence and citation key. Vendor
models and drawings give nominal geometry; measure the physical part before
relying on a fit.

## Retention

The repository keeps a copy only when the vendor's licence permits
redistribution and the file names no person. It pins every other file by URL
and SHA-256.

| Vendor file | Retention | Licence |
| --- | --- | --- |
| Raspberry Pi 5 STEP archive (`pi5/`) | Repository (Git LFS) | MIT, inside the archive |
| Adafruit DC and Stepper Motor HAT STEP (`adafruit/`) | Repository (Git LFS) | MIT, `adafruit/LICENSE.txt` |
| Adafruit PCA9685 16-channel servo driver breakout STEP (`adafruit/`) | Repository (Git LFS) | MIT, `adafruit/LICENSE.txt` |
| OMT Raspberry Pi 5 case 3MF (`omt-case/`), community design | Repository (Git LFS) | MIT, `omt-case/LICENSE.txt` |
| Raspberry Pi 5 mechanical drawing | Fetch | None stated |
| Raspberry Pi AI HAT+ product brief | Fetch | None stated |
| Stereolabs ZED Mini STEP and datasheet | Fetch | None stated |
| Luxonis OAK-1 PCBA and enclosure STEP | Fetch | None stated at the download location |
| Luxonis OAK-1 datasheet | Fetch | MIT, but its PDF metadata names a person |

Files under `references/` are stored byte for byte: `.gitattributes` turns off
line-ending conversion here so the SHA-256 values stay valid.

## Fetch and verify

From the repository root:

1. Download the pinned files into `generated/ultraskelly/vendor/<id>/`:

   ```powershell
   python -B designs/ultraskelly/src/vendor.py fetch
   ```

   The tool rejects a download whose SHA-256 differs from `vendor.json`. A
   rejection means the vendor changed or removed the file.
2. Check every repository and fetched file:

   ```powershell
   python -B designs/ultraskelly/src/vendor.py verify
   ```

   Each line reports `ok`, `missing` or `MISMATCH`.
3. Optional: record STEP bounding boxes with the pinned FreeCAD Python:

   ```powershell
   & '.cad-tools/FreeCAD_1.1.4-Windows-x86_64-py311/bin/python.exe' -B designs/ultraskelly/src/vendor.py extents
   ```

   The report goes to `generated/ultraskelly/vendor/extents.json`.

Builders call `vendor.path(<id>)`, which fetches a pinned file on first use and
checks its hash.
