# Construction comparison

All candidates retain OV9281 and the on-module ESP32-P4. Tether mass is excluded.
These are **screening estimates with checked courtyard packing**, not finished boards
or manufacturer quotations. R10 remains the verified electrical checkpoint.

| Candidate | Module screening mass | Cost position |
| --- | --- | --- |
| A — Thin modular boards | 1.63–2.87 g; nominal 2.16 g | Lowest candidate complexity; still custom thin six-layer assembly. |
| B — Custom ultrathin rigid-flex | 0.72–1.63 g; nominal 1.10 g | Premium custom construction, dense assembly and microvia development. |
| C — Published SLIM.flex construction | 0.84–1.87 g; nominal 1.27 g | Premium HDI flex assembly; published construction basis, no project quote. |

A uses 32 x 16 mm controller, 14 x 14 mm head, retained 24-contact connector and
separate wide flex. Its proposed 0.4 mm six-layer rigid construction needs a new
stackup review. It preserves all existing physical package types, so it is the
least disruptive comparison but does not meet the mass target.

B fits a 24 x 12 mm controller and 12 x 12 mm head. C needs a 26 x 12.5 mm
controller and 12.5 x 12.5 mm head to reserve space for its local supports. Both
use a 32.85 x 8 mm free flex.
The 8 mm width reserves room for the existing interconnect signals; it is not a
routed or impedance-checked flex. Both eliminate the inter-board connector by
integrating the flex, retain the board-side four-contact USB connector, and
assume smaller equivalent flash, regulators, switches and selected passives.
`options.json` lists every reference and each conditional package substitution.
No replacement order codes or electrical equivalence are asserted. Small-part
assembly is available, including 0201/01005 [@pcbwayAssemblyCapabilities2026],
but capacitance under bias, current, voltage, heat and assembly constraints must
be checked before any substitution enters the schematic.

B's 0.25 mm, six-layer, 12 um copper component regions and 0.12 mm two-layer
flex are aggressive custom process targets. A matching manufacturer construction
has not been established. HDI process availability [@pcbwayHdi2026] does not
establish those dimensions, price or electrical behavior.

C has a stronger public construction basis: Wuerth's SLIM.flex template specifies
0.303 mm component regions and a 0.166 mm two-layer flex option, with standard
microvias only [@wurthSlimFlex0302026]. Current through-vias cannot be transplanted
into that stackup; PTHs would increase outer copper thickness. Local support under
the P4 and lens is an additional mass allowance, not a stiffness qualification.
Its polyimide construction is not automatically lighter than every rigid option.

## What buys the largest reductions

R10's copper is approximately 1.24 g. Smaller outlines and thinner qualified
copper have the largest board-level leverage. Preserve return-path requirements;
do not remove reference copper simply to achieve a mass number. Conditional
package substitutions and removal of J102 reduce the nominal package allowance
from 0.799 g to 0.483 g. The retained P4 is still 0.135–0.230 g by engineering
estimate; manufacturer weight is unresolved. The checked 48.24 mm3 hollow holder reduces another
roughly 0.066 g in the nominal scenario, subject to the actual support geometry.

None of the nominal candidates is below one gram yet. B and C have low scenarios
below it, but their uncertainty intervals cross the target. The study therefore
supports a **subgram development target, not a subgram claim**. Obtain actual
package/lens weights and qualified stackups before making a release decision.

## Cost decision

No supplier quote or public price is being represented as a project price.
Compare quotes later at identical quantities (for example 5, 20 and 100 assembled
modules), with tooling, fabrication, assembly, small-part handling, inspection,
parts, yield allowance and shipping separated. The comparative cost order is an
engineering expectation; actual panel utilization and vendor processes can
change it. Keep a full-module target and report the tether separately in every
quote scenario. No files have been uploaded and no vendor has been contacted.

## Packing refinement

All three candidates now have checked two-sided courtyard placements. A preserves
package types, not current placement; Q201 moves to the underside in each study.
C required more area than its initial 24 x 12 mm sketch. Its local underside
supports are a 10 x 10 x 0.15 mm P4 plate and an 8 x 8 mm ring with a 6.5 mm
opening, also 0.15 mm thick. Their combined volume is 18.2625 mm3. Backside
components avoid these supports. This does not establish stiffness, bonding,
thermal behavior or fabrication approval. The 24-contact solder-lap area remains
reserved in A; B/C replace that interface with continuous flex.

The CAD support mass now uses its actual solid volume, not the earlier rounded
50 mg nominal allowance. The resulting nominal totals are 2.158 g (A), 1.098 g
(B) and 1.270 g (C). The source JSON carries the unrounded values.
