# Current camera status — 2026-10-29

R11 is the current offline engineering checkpoint. See [WORKING-REVIEW.md](WORKING-REVIEW.md)
and [the native-file review](electronics/r11/index.html). Connectivity, nominal
cross-section analysis, matched geometry and compiled snapshot software are
checked; physical operation is not demonstrated. Nominal mass is 1.34 g without
the external tether, so the target is not met. Supply risks, sensor DVDD stress
margin, fabrication, optics and hardware tests remain open.

The earlier status below is retained as history. Its R08/R10 defects and counts
are not the current R11 results; use the linked R11 reports to resume work.

---

# Camera completion record — 2026-10-27

Update 2026-10-28: see the [current working review](WORKING-REVIEW.md) for the
R10 corrective routing and matched compact-optics assembly. All three boards
pass native DRC, with no unconnected items; 471 pad/net comparisons and all 24
interconnect checks pass. All 21 audit findings have recorded dispositions.
Impedance tolerance, channel timing and hardware operation remain unqualified. The R08 evidence
below remains the selected baseline record; it is not the newest working trial.

**The engineering checkpoint is saved; the camera design is not complete.**
R08 contains native KiCad work, a checked copper/board model, compiled ESP32-P4
snapshot firmware, and tested host recording software. It is not ready to order
or assemble. Hardware absence is not the only remaining blocker: substantial
PCB, component, optical and illumination design work remains possible on the
computer.

## Completed and evidenced

| Result | Evidence and limit |
| --- | --- |
| Native circuit and three-board draft | `electronics/r08/`: controller 32 × 20 mm, head 14 × 14 mm, flex 35.3 × 12.5 mm; flat inspection envelope 76 mm long |
| More verified PCB connections | 16 new paths, seven vias; unconnected items 66 → 57; existing R07 copper and geometry retained |
| Electrical interface consistency | 456 schematic-to-pad checks, 24 flex path and XY alignment checks; R7 absent/R8 populated |
| Native mechanical review | Actual substrate and copper STEP exports; no validated component bodies, lens assembly or mating heights |
| Compiled firmware | Sensor and synthetic variants target P4 v3.x, IDF v5.5.6; SHA-256 evidence in `verification/offline-report.json` |
| Host recording implementation | Eight passing parser tests; synthetic PGM recording; no physical capture |
| First-order system calculations | RAW8 bandwidth, buffer size and thin-lens focus sensitivity; no electrical, thermal or full optical simulation |
| Native review inventory | 103 footprints in `electronics/r08/inventory.json`; incomplete purchasing data, not an approved BOM |

Ground pads connect within all three individual boards. Native DRC still reports
34 controller and 23 head unconnected items, six open tracks and seven incomplete
vias. The absence of other DRC types under the recorded rules is a narrow
geometric result, not proof of electrical functionality.

## Remaining work that does not require a camera

1. **Repair and audit component selections.** Y1's inherited `7C-24.000MBB-T`
   description specifies 3.3 V, but the native netlist supplies its VDD and enable
   from +1V8. Resolve the exact oscillator and audit the land pattern. Complete
   the P4 v3.x reference-circuit, flash, sensor bias, decoupling and supply-sequence
   review. Complete the actual-part BOM and USB bus-power design.
2. **Finish layout.** Route the 57 remaining connection items, including the
   high-speed links, and eliminate open track/via warnings. Establish manufacturer
   stackup, MIPI/USB impedance and skew constraints, return paths, clock/flash and
   switching-supply geometry. Do not equate autorouter connectivity with these
   checks. No final Gerber/assembly package is released.
3. **Finish the IR head and mechanics.** Add the LED current/enable circuit,
   select actual lens/filter parts, and model their mechanical interfaces. The
   reserved LED signal and bare head PCB are not an infrared camera assembly.
   Verify complete component clearances, lens seating, optical datum and flex
   termination/bending geometry before claiming mechanical completion.
4. **Extend firmware.** Resolve the driver's 400 MHz metadata versus 800 Mbps
   mode-table timing before receiver qualification. Add exposure/gain control,
   robust streaming and host controls. The current one-request/one-snapshot CDC
   service deliberately makes no frame-rate promise.

## Findings that affect the target

The selected design is wider and longer than the user-reported Pupil reference.
It is not a 0.7 g replacement. The P4 alone needs a 10 × 10 mm package
[@esp32P4Datasheet]. Keep the controller choice, but do not claim the current
32 × 20 mm controller is final miniaturization.

CIL829-F2.5-M08ANIR is now retained as an oversized M8 × 0.35 reference:
2.8 mm focal length, F/2.55, 6.4 mm designed image circle and published mass
1.4 g. That lens alone exceeds the reported 0.7 g whole-camera reference.
Its supplied drawing and STEP have been reviewed in the
[lens fit study](mechanics/optics-r01/README.md); the optical variant remains
unresolved. It is not locked into the PCB [@commonlandsCil829;
@commonlandsCil829Drawing; @commonlandsCil829Step]. The
[compact comparison](mechanics/compact-optics.md) recommends CH2021A for the next
mechanical study: 6 mm diameter and 2.65 mm body length. Its 10–20 mm focus,
940 nm image quality and stock remain unverified [@chuanganCh2021a].

`system_analysis.py` estimates about 0.63 mm of image-distance adjustment between
10 and 20 mm object distances for an ideal 2.8 mm lens, equivalent to about
1.81 turns at 0.35 mm pitch. These distances use ideal principal planes; they
are not actual barrel travel or distance from the front glass. The simple model
cannot prove depth of field or an IR focus range for a compound lens
[@edmundBasicLensSelection]. Real optics still need selection and evaluation.

The target 400 × 400 × 120 fps RAW8 stream carries 19.2 MB/s before overhead.
The existing 640 × 400 × 100 fps sensor mode carries 25.6 MB/s. The snapshot
firmware does not deliver either continuous rate. USB, memory and CSI operation
must be measured together before committing to a product rate.

## Work that requires hardware later

Power/current/thermal measurements; sensor identity and register readback;
24 MHz and MIPI signal measurements; USB enumeration and power behavior; real
monochrome frames; frame loss and sustained rate; 940 nm focus/field of view at
the intended working distances; LED output and eye-exposure assessment; physical
assembly, mass and flex durability. Begin optical imaging with a target, not an
eye. LEDs remain off in the current firmware.

## Recheck and inspect

After both firmware builds, run from the repository root:

```powershell
python designs/eye-camera-ov9281/verify_offline.py
python -B tools/check_references.py
python -B -m unittest discover -s tools -p test_references.py -v
```

Success means the saved evidence is consistent and the software checks pass.
`fabrication_ready` and `physical_camera_demonstrated` remain false. To inspect
the native files, open `electronics/r08/OV9281-P4-R08-assembly.kicad_pcb` in
KiCad, and the matched `generated/ov9281-r08-desktop/OV9281-R08-PCB-REVIEW.FCStd`
in FreeCAD. Open `electronics/r08/overview.html` as rendered HTML. The native
documents, not that overview, are the editable engineering artifacts.
