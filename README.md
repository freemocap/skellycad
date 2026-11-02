# SkellyCAD

CAD, eye-tracker hardware, camera electronics and learning projects.
Start with a project below; its README distinguishes selected assemblies,
review candidates and available print packages.

| Project | Start here |
| --- | --- |
| Eye trackers | [Mouse, rat, marmoset and human](designs/eye-tracker/README.md) |
| Camera modules | [Pupil reference and camera development](designs/cameras/README.md) |
| Capture enclosure | [Frame and capture studies](designs/enclosure/README.md) |
| UltraSkelly mounts | [Camera bracket and Pi 5 stack mount](designs/ultraskelly/README.md) |
| Preserved Mouse Hats | [Historical designs and replay](designs/mouse-hats/README.md) |
| CAD Foundations | [FreeCAD lessons](designs/cad-foundations/README.md) |
| KiCad Foundations | [Electronics lessons](designs/kicad-foundations/README.md) |

[Working guide](docs/organization-guide.md) · [Setup and validation](docs/development.md) ·
[Version control](docs/version-control.md) · [Citations](CITATIONS.md)

The preferred Pupil geometry is the [complete R08 module](designs/cameras/pupil-core-eye/README.md).
Historical assemblies retain their pinned geometry and matched parts.

[Repository cleanup plan](docs/repository-organization.md) ·
[Cleanup and preservation record](docs/migration/repo-cleanup-2026-10-31/README.md) ·
[Original import record](docs/migration/README.md)

Local runtimes stay in `.cad-tools/`; working runs go to `generated/`.
The original `old-cad-playground/` remains untouched for the user's migration review.
