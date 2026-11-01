# R11 release gates and prototype tests

R11 is a complete offline review candidate. This document is a proposed test
sequence, not a released assembly or eye-use procedure. No physical prototype
has been powered, imaged, weighed or fitted.

## Resolve before ordering

1. Establish a traceable source for the exact OV9281 package and the other
   unavailable/lifecycle-risk parts in `purchasing-bom.json`. Qualify any
   substitute in the component contract, schematic, footprint, effective
   capacitance and mechanical envelope before updating the BOM.
2. Resolve the sensor DVDD margin. With the corrected maximum filter DCR, the
   screen gives 1.159 V at the published 52 mA typical load, but 1.135 V at the
   selected 104 mA stress load, below the 1.14 V minimum. Establish the required
   current/transient envelope and improve delivery where necessary. Do not
   treat passing typical-load arithmetic as power qualification
   [@leopardOv9281Electrical2026; @tiTlv733R11; @tdkMlp2012R11].
3. Qualify the chosen six-layer construction, local layer removal, filled/capped
   adjacent laser vias, drying openings, finish, mask, two-sided assembly and
   windowed supports. Obtain actual material, thickness and impedance data;
   recalculate the channels and mass before releasing fabrication outputs
   [@wurthSlimFlex0302026; @wurthSlimRules2023].
4. Select actual close-focus IR optics, filter and retention. Verify image circle,
   sensor datum, thread, 10–20 mm focus, IR transmission and image quality.
   The current smooth M6-size envelopes are space reservations.
5. Reconcile the under-one-gram target with the 1.34 g nominal estimate. Weigh
   candidate packages/optics and replace assumptions before promising a mass.
   Include all integrated parts and exclude only the external tether.

## Electrical bring-up on the bench

1. Inspect assembly and hidden joints; check polarity, shorts and continuity
   before applying a current-limited supply. Keep illumination disabled.
2. Measure startup, steady-state and load-step voltage at the sensor and P4
   pins. Record sequencing, ripple, current, inrush and temperatures. Acceptance
   follows component limits and the agreed USB power contract, not the model's
   arbitrary 1 A conductor stress load.
3. Confirm the 40 MHz crystal and 24 MHz head oscillator, reset inversion, SID
   strap and SCCB identity. Do not burn flash-voltage eFuses during bring-up.
4. Load the synthetic firmware and verify USB enumeration, host records, CRCs,
   disconnect/reconnect behavior and sustained transport before sensor capture.
5. Load the sensor firmware and resolve the pinned driver's 400 MHz clock
   metadata versus the 800 Mbps mode-header/receiver interpretation. The
   upstream adapter's use of that metadata is retained as conflicting evidence;
   successful compilation does not resolve actual CSI timing
   [@espressifOv9281Driver; @espVideoCsiAdapterPinned2026].
6. Record real monochrome frames from a test target. Verify exposure, gain,
   DMA/cache behavior, dropped frames and throughput. Snapshot support is
   implemented; continuous streaming and UVC remain product work.

## Mechanical and optical validation

1. Check actual package heights, support seating, connector/cable exit and
   programming access against the matched assembly. Recheck the full module
   after adhesive and solder are present.
2. Test focus, field of view, illumination uniformity and visible rejection on
   targets at 10, 15 and 20 mm under the selected IR band. Qualify optical output
   and exposure before any use near an eye.
3. Form the qualified static bend with a fixture, inspect transitions and test
   continuity. The 2.5 mm neutral-radius CAD study is not a fatigue result.
4. Weigh the complete module with optics, supports, retention and connector,
   excluding the external tether. Record scale resolution and actual population.

Review scope: existing component and fabrication references, saved R11 analyses
and pinned firmware source. These tests have not been executed on hardware.
