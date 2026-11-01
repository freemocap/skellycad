# Shared eye-tracker library

Camera modules are cataloged under [cameras](../../cameras/README.md).
`camera.add_camera` loads the selected complete Pupil module and its optical datum.
`assembly.build_assembly` composes animal recipes with compatible mount geometry.
`model.load_manifest` resolves an explicit selection and verifies its native hash.

[Mount presets](mounts) · [Targeting tools](targeting) · [Earlier shared studies](history/README.md)

`paths.repository_path` resolves frozen pre-cleanup asset identifiers through the
recorded move map. It does not change checkpoint bytes. New records should use
canonical paths. Run moved historical scripts through the isolated replay runner.

[Working guide](../../../docs/organization-guide.md) · [Targeting workflow](../../../docs/eye-tracker-targeting.md)
