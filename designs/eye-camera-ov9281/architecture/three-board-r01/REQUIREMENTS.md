# Three-board architecture requirements

THREE-BOARD-A01 separates the head-mounted camera assembly from an enclosure or backpack base station. R11 is the preserved electrical/mechanical reference, not an input to overwrite. `requirements.json` is the machine-readable contract.

The whole head-mounted assembly targets less than 1.0 g, including optics, local flex, supports, adhesive, connector and strain relief. External tether and base station are tracked separately. No mass has been measured.

Primary recording target: one monochrome 640 x 400 RAW8 stream at 100 fps. 120 fps is a stretch mode requiring a validated sensor configuration. Full-resolution 1280 x 800 at 120 fps is an interface-budget comparison, not a promised USB output mode. R11 only implements snapshots; continuous capture, buffering and loss accounting remain implementation work.

The camera head carries the sensor and optics, with two IR LEDs along the long axis. The interface board carries cable transport and necessary local power circuitry. The base station receives images and provides processing and USB. Sensor bypass capacitors stay close to pins; remote regulation must not replace required local decoupling.

Evaluate 0.30 and 0.60 m tethers. 36 AWG and a four-contact connector are preferences subject to cable loss, impedance and strain validation. Signal shield is additional to the four conductors. Keep wire protocol distinct from USB even if the connector looks similar.

The optical envelope must support focus trials at 10, 15 and 20 mm, visible rejection and the chosen IR wavelength; 940 nm is the current candidate. Actual lens and filter selection are unresolved. Camera sensor image area is 3.896 x 2.453 mm [@omnivisionOv9281Brief].

This phase delivers documented architecture, calculations and initial native CAD. It does not deliver pin-complete schematics, routed boards, a certified cable or a working camera. The source-based component evaluation follows next.
