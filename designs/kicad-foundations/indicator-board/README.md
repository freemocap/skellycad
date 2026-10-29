# Indicator board: first schematic

Open `electronics/01-connected-schematic/indicator.kicad_pro` with KiCad's
project manager, then open its schematic. This checkpoint contains J1 (power
connector), R1 (330 ohm illustrative resistor) and D1 (generic LED), with three
connected nets. No footprints or PCB layout have been assigned yet.

Read [lesson 01](../lessons/0001-circuit-and-board.html). The 5 V supply and 330 ohm
resistance are teaching assumptions. No LED part or electrical rating has been
selected; this is not ready for fabrication or powered testing.

## Rebuild and validate

Run from the repository root. The generator requires an installed KiCad 10
symbol library and standard Python. It refuses an existing output directory.

```powershell
python designs/kicad-foundations/indicator-board/build_schematic.py --output generated/kicad-foundations/my-first-rebuild
python designs/kicad-foundations/indicator-board/validate_schematic.py --cli "$env:LOCALAPPDATA/Programs/KiCad/10.0/bin/kicad-cli.exe" --output generated/kicad-foundations/my-first-validation
```

For another install location, pass `--kicad-root` to the generator and use the
installed CLI path for validation. Choose a fresh directory on each run. The
validator checks the retained lesson checkpoint, exports a netlist and SVG, and
fails on an ERC violation or a mismatch in the intended pin connections.
[@kicad10Cli; @kicadSchematicFormat]

Do not rebuild over an open document. Use a new directory and open the result
yourself. Keep this checkpoint unchanged; subsequent lessons create new stages.

## Provenance and limits

The schematic embeds the installed KiCad symbols `Device:R`, `Device:LED` and
`Connector_Generic:Conn_01x02`. `source-record.json` records library hashes and
the checkpoint hash. These symbols are by KiCad library contributors under
CC-BY-SA 4.0 with the KiCad library design-use exception. [@kicadLibraryLicense]
No separate symbol library collection is redistributed.

Validation on 2026-10-27 with KiCad 10.0.7: three expected components, three exact
pin-to-pin nets and zero reported ERC violations. All component pins here are
passive; ERC does not establish source voltage, LED polarity suitability or
operating current. No footprints, mechanical fit or physical testing validated.
Sandbox registry warnings did not prevent CLI exports or checks.
