# Approved E01 electrical-design phase

- [x] **1. Update the design requirements and mass budgets**, retaining the complete head-mounted assembly’s under-one-gram target and making base-station footprint, thickness, connector size and complete backpack mass explicit optimization objectives.
- [x] **2. Verify the component and documentation basis**, checking exact sensor, serializer, receiver, processor and power-component packages, public design information and availability, with unresolved dependencies clearly identified.
- [x] **3. Design the camera-head and interface-board circuits**, creating pin-connected KiCad schematics for the sensor, serializer, clocks, power rails, illumination control, protection and tether interface.
- [x] **4. Design the compact base-station circuits**, creating pin-connected KiCad schematics for the receiver, ESP32-P4, memory, power, USB and programming/debug access while minimizing unnecessary components and bulky connectors.
- [x] **5. Audit the complete electrical chain**, checking pin mappings, voltage compatibility, clocks, reset and startup behavior, remote control, illumination defaults and connector assignments, and correcting every resolvable issue found.
- [x] **6. Build compact placement studies from the actual footprints**, checking component and routing space on all three boards, updating matched FreeCAD assemblies and recalculating head, tether and complete base-station mass estimates.
- [x] **7. Publish the reviewed electrical-design package**, including schematics, BOM, placement files, electrical-rule-check results, cited evidence and all remaining blockers, with a clear handoff to detailed routing.
