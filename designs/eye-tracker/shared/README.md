# Shared eye-tracker components

`model.py` provides checkpoint hash verification, matched-part loading, and
manifest-driven print groups. Species exporters supply their interface checks.
The carrier/holder print-in-place pair is one export group in the mouse manifest.

Camera hardware, PCB retention, ball/socket geometry and mounting interfaces are
candidates for future extraction. They are not yet a generic anatomical model.
Keep species measurements and camera placement in the species folder; extract
one component at a time with a mouse geometry comparison as the regression check.
