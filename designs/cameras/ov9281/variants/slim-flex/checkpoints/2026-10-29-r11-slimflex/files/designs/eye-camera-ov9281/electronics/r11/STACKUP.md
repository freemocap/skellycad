# R11 construction contract

R11 implements selected candidate C. The public six-layer template gives a
0.303 mm component region and a 0.166 mm two-layer neck [@wurthSlimFlex0302026].
The rounded constituent values sum to 0.304 mm; retain that 0.001 mm discrepancy
until the fabricator supplies its final construction. This is a design basis,
not approval to fabricate.

The central pair of layers remains through the neck: physical L3 = In2.Cu and
L4 = In3.Cu. The outer four copper layers stop before the flexible region.
Use one native KiCad board for continuous connectivity. Mechanical drawings and
a separate region validator describe the local layer removal; KiCad's global
stackup alone cannot establish that the regional construction is correct.

## Routing and supports

The published standard permits stacked/staggered anylayer microvias, with
75 um trace/space, 225 um minimum microvia pads and 70 um finished laser holes.
Its standard copper-to-outline distance is 0.3 mm. It calls for teardrops,
no vias in bending areas and copper openings for drying. Cold-bonded FR4
stiffeners use 50 um adhesive [@wurthSlimRules2023].

R11 chooses 0.25 mm via lands and adjacent-layer laser transitions. Longer
transitions are chains of adjacent-layer structures, not R10 through-vias.
If KiCad represents internal laser structures as blind/buried vias, the explicit
layer-span and construction validator remains authoritative about their process;
that EDA representation does not authorize mechanically drilled holes.

Route long MIPI sections on In2.Cu over In3.Cu ground, maintaining the
same signal/reference relationship into the neck. The main USB pair is on F.Cu
over In3.Cu, with the intermediate In1/In2 layers cleared beneath its uniform
section. Its reference separation is 0.126 mm. The connector/ESD input fanout
uses In2.Cu and remains a separate, nonuniform launch qualification. Clear other copper from the
immediate high-speed corridor instead of assuming the 20 um outer-layer spacing
can reuse R10's impedance geometry. Recalculate width/gap with explicit material
assumptions before routing. Preserve ground-return paths at paired transitions;
record short pad launches separately from uniform transmission-line sections.

Use drying openings outside the high-speed reference corridor. Continuous local
reference strips require fabricator review; a geometrically intact return plane
does not by itself establish moisture/process compliance or channel performance.

Reserve 0.1 mm FR4 plus 0.05 mm adhesive for local supports, with no component
courtyard under them. Keep vias and components out of the free neck and hold
transitions at least 1 mm back from it. These setbacks are conservative project
choices. A 2.5 mm bend radius accommodates the published two-layer flex-to-install
10-times-thickness rule even at the template's +0.05 mm neck tolerance. The
planned 90-degree bend is an installation example, not a dynamic-flex rating.

`construction.json` separates source rules from project choices. Exact material
permittivities, manufacturing compensation, stiffness, bonding and thermal
performance remain qualification items. No supplier contact is required to
create this offline engineering candidate, and none has been authorized.

The controller support has two 4 x 2.5 mm windows for its bulk capacitors.
The remaining 80 mm2 support area and adhesive bond require mechanical
qualification. The head retains an 8 mm square support ring.

The native global stackup explicitly represents 0.292 mm of copper, dielectric
and mask. KiCad does not assign a separate thickness to the ENIG surface finish.
The overall board setting and mechanical component regions retain the source
0.303 mm target; the 0.001 mm constituent rounding difference remains recorded.
This native stackup is insufficient as a standalone fabrication instruction.

The routed board uses a ground plane on In3.Cu, a controller 3.3 V plane on
In4.Cu and a local processor-core plane on In1.Cu. Filled copper tapers reinforce
accessible pad/via junctions. `teardrops.json` lists constrained junctions that
need fabrication review; their presence is not a waiver of the supplier rule
[@wurthSlimRules2023].
