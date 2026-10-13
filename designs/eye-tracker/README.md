# Eye tracker

| Folder | Role | Starting state |
| --- | --- | --- |
| [shared](shared/README.md) | Common model selection and export tooling; future reusable geometry | Manifest and matched-part export helpers |
| [human](human/README.md) | Human-specific anatomy, placement and design | Awaiting reference assets |
| [mouse](mouse/README.md) | Mouse anatomy, placement and assembly | Preserved MH-T3-EYE-R10 baseline |
| [rat](rat/README.md) | Rat anatomy, placement and assembly | Awaiting reference assets |
| [marmoset](marmoset/README.md) | Marmoset anatomy, placement and assembly | Awaiting reference assets |

## Boundaries

Shared geometry will own camera hardware interfaces, retention mechanisms and
mount primitives. Species designs own reference anatomy, anatomical landmarks,
mounting position, and the number and poses of camera instances. Camera poses
need explicit coordinate frames and units. Record separate left/right instances
when developing binocular systems; evaluate handed hardware, ribbon routing,
socket motion and skull clearance before accepting a mirrored design.

The initial migration adds shared selection/export tooling and preserves the
mouse geometry. Extract geometric components incrementally, comparing a rebuilt
mouse against its accepted baseline before adapting another species. Human,
rat and marmoset folders intentionally contain no invented anatomical dimensions.

The original [Mouse Hats history](../mouse-hats/INDEX.md) remains at its old
relative paths so earlier studies and replay scripts remain traceable.
