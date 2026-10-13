"""Fresh-reopen control checks for the retainer and coordinated holder/clip."""
from build import *
import holder_features,clip_features

carrier=App.openDocument(str(OUT/'carrier.FCStd'));holder=App.openDocument(str(OUT/'holder.FCStd'))
a=carrier.LongerPCBRetainers;b=holder.ThickerHolderWalls;c=holder.ExtendedClip
baseline=[x.Shape.Volume for x in [a,b,c]]
for upper,lower,wall in [(1.0,.5,.4),(1.5,.7,.5)]:
    a.Extension=upper;a.LowerExtension=lower;b.OutwardThickness=wall
    carrier.recompute();holder.recompute()
    for x in [a,b,c]:
        assert not x.Shape.isNull() and x.Shape.isValid() and len(x.Shape.Solids)==1
        x.Shape.check(True)
    expected=c.Base.Shape.BoundBox.XLength+2*wall
    assert abs(c.Shape.BoundBox.XLength-expected)<1e-5
assert all(abs(x.Shape.Volume-v)<1e-6 for x,v in zip([a,b,c],baseline))
(OUT/'edit-validation.json').write_text(json.dumps({'reopen_edit_restore':'passed',
    'tested_upper_extensions_mm':[1,1.5],'tested_lower_extensions_mm':[.5,.7],
    'tested_wall_additions_mm':[.4,.5],'clip_width_follows_wall_addition':True},indent=2))
print('Reopen, coordinated edits and restore passed.')
