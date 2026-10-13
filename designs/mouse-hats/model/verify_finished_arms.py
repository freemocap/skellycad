"""Fresh reopen and radius edit/restore verification for the arm finish."""
from build_finished_arms import App, OUT, validate
import json

doc = App.openDocument(str(OUT/'finished-arm-carrier.FCStd'))
obj = doc.JunctionFillets
baseline = obj.Shape.Volume
results = []
for tray, socket in [(0, 0), (.4, .2), (.5, .3)]:
    obj.TrayRootRadius = tray
    obj.SocketRootRadius = socket
    doc.recompute()
    assert not obj.State or 'Invalid' not in obj.State, obj.State
    results.append(validate(doc))
assert abs(obj.Shape.Volume-baseline) < 1e-6
(OUT/'edit-validation.json').write_text(json.dumps(results, indent=2)+'\n')
print('Fresh reopen, zero radii, reduced radii and restore passed.')
