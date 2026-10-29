# R08 routing and firmware assembly variant

R08 adds **16 verified paths and seven through vias** to R07, preserving all
earlier placements, pads and copper. Nine more unconnected items are resolved:
the controller falls from 37 to 34 and the head from 29 to 23. The flex remains
fully connected. R08 is a checked draft with **57 unconnected items**, not a
fabrication release.

The sensor address population now has R7 absent and R8 populated with 0 ohm.
This selects SID low and matches the firmware driver's 7-bit address 0x60
[@espressifOv9281Driver]. Schematic and PCB population attributes were checked;
the electrical netlist is otherwise identical to R07.

Open `OV9281-P4-R08-assembly.kicad_pcb` for the combined inspection view.
The three manufacturing designs remain separate: `controller.kicad_pcb`,
`head.kicad_pcb`, and `flex-study.kicad_pcb`. The combined file is not a fab input.
Native STEP exports show substrates and copper only; components and optics are
not represented as validated mechanical bodies.

## Verified scope

- All 456 schematic-to-board pad nets match; 24 flex paths and their flat XY
  interface positions match. These checks do not qualify connector mating height.
- All existing copper and placements remain; every added segment and via matches
  `routing-r08.json`. Every added path reaches its declared endpoints.
- No net loses connectivity. No shorts, spacing errors or copper slivers occur
  under the saved draft rules. Six open tracks and seven incomplete vias still
  produce warnings. DRC is **not clean for fabrication**.
- ERC reports zero messages under the inherited settings; ignored categories
  remain visible in `checks/erc.rpt`.
- Rigid stackups remain 0.6 mm and the flex 0.1 mm. Trace impedance, current
  capacity, manufacturing process and assembled fit are unqualified.

The new head paths can use 0.10 mm widths with 0.15 mm spacing. The earlier R07
4 mm local-escape restriction does not describe every R08 route; inspect the
recorded lengths and layers. No MIPI or USB differential-pair routing was added.
The router trial's unused escape vias and copper-sliver-producing additions
were discarded before this revision was selected.

`inventory.json` lists 103 native footprints with values, available MPN fields,
population, sides and placements. It is a review inventory, not an approved BOM.
J104 remains a schematic reservation, not a built LED driver. Y1's inherited
3.3 V part description conflicts with its +1V8 supply; exact part and land
pattern review are required. The reference design's reuse license does not
establish that every inherited component choice is correct for this adaptation.

## Reproduce

Use KiCad 10's bundled Python from the repository root. Choose unused output
directories; the scripts refuse to overwrite a previous experiment.

```powershell
& 'C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/python.exe' designs/eye-camera-ov9281/build_r08.py --output generated/r08-trial-new
& 'C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/python.exe' designs/eye-camera-ov9281/refine_r08.py --input generated/r08-trial-new --output generated/r08-refined-new
& 'C:/Users/jonma/AppData/Local/Programs/KiCad/10.0/bin/python.exe' designs/eye-camera-ov9281/validate_r06.py --directory generated/r08-refined-new --parent designs/eye-camera-ov9281/electronics/r07 --revision OV9281-P4-R08
```

The refinement retains a reviewed subset of nets. KiCad object UUIDs and route
choices can differ between runs. A replay must pass native validation before
selection; the current checkpoint is identified by `validation.json` hashes.
The validator writes review artifacts, so run it on a new experiment rather
than on an accepted checkpoint. Read `../../firmware/README.md` for software
builds and `../../STATUS.md` for remaining release gates.
