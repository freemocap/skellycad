"""Reopen, baseline agreement, real face offsets, material and interference checks."""
import json
import FreeCAD as App
import build_mount as build

build.load_modules()
from mount_interface import pocket_parameters
doc = App.openDocument(str(build.OUT/'mount-fit.FCStd'))
base = doc.Baseplate
tray = doc.PCBTrayAndMount
interface = json.loads(base.InterfaceJSON)
measured = json.loads(base.MeasuredJSON)
report = {'units': 'mm', 'tolerance_mm': 0.001, 'baseline': {}, 'clearance_probes': [],
          'physical_fit_validated': False}


def checked_volume(shape):
    if shape.Solids: shape.check(True)
    return shape.Volume


for name, obj, file, target in [
    ('tray', tray, 'main-carrier/01-tray-mount-candidate.FCStd','PCBTrayAndMount'),
    ('baseplate', base, 'baseplate/01-baseplate-candidate.FCStd','Baseplate')]:
    old = App.openDocument(str(build.ROOT/'generated/mouse-hats/reconstruction'/file))
    reference = old.getObject(target).Shape
    obj.touch();doc.recompute();obj.Shape.check(True)
    missing = checked_volume(reference.cut(obj.Shape,0.001))
    excess = checked_volume(obj.Shape.cut(reference,0.001))
    assert missing < 1e-7 and excess < 1e-7, (name,missing,excess)
    report['baseline'][name] = dict(missing_mm3=missing, excess_mm3=excess,
                                   volume_difference_mm3=obj.Shape.Volume-reference.Volume)
    App.closeDocument(old.Name)

nominal = base.Shape.copy()
for value in (0,0.025,0.05,0.075,0.1,0):
    base.PocketClearance=value
    base.touch();doc.recompute()
    base.Shape.check(True)
    assert len(base.Shape.Solids)==1
    overlap=checked_volume(base.Shape.common(tray.Shape,0.001))
    added=checked_volume(base.Shape.cut(nominal,0.001))
    removed=checked_volume(nominal.cut(base.Shape,0.001))
    assert overlap<1e-7 and added<1e-7
    assert removed>0 if value else abs(base.Shape.Volume-nominal.Volume)<1e-7
    # Match actual planar faces by normal and offset, never by face index.
    face_errors=[]
    for plane in pocket_parameters(measured,interface,value)['socket_planes_a'][5:]:
        n=App.Vector(*plane['normal']);d=plane['offset_mm']
        candidates=[abs(n.dot(f.CenterOfMass)-d) for f in base.Shape.Faces
                    if type(f.Surface).__name__=='Plane' and abs(abs(f.normalAt(0,0).dot(n))-1)<1e-8]
        error=min(candidates)
        assert error<1e-7
        face_errors.append(error)
    report['clearance_probes'].append(dict(clearance_mm=value,overlap_mm3=overlap,
        added_mm3=added,removed_mm3=removed,bearing_plane_error_mm=face_errors))
    print(report['clearance_probes'][-1],flush=True)

for invalid in (-0.01,0.101,float('nan')):
    try: pocket_parameters(measured,interface,invalid)
    except ValueError: pass
    else: raise AssertionError('Invalid allowance accepted')
report['invalid_inputs_rejected']=True
# Persist an edited candidate to a separate file, then reopen and force recompute.
base.PocketClearance=0.05;doc.recompute()
volume=base.Shape.Volume
doc.saveAs(str(build.OUT/'mount-fit-005-check.FCStd'))
App.closeDocument(doc.Name)
doc=App.openDocument(str(build.OUT/'mount-fit-005-check.FCStd'))
doc.Baseplate.touch();doc.recompute();doc.Baseplate.Shape.check(True)
assert abs(doc.Baseplate.Shape.Volume-volume)<1e-7
assert abs(doc.Baseplate.PocketClearance.Value-0.05)<1e-9
report['edited_save_reopen']='passed at 0.05 mm'
(build.OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('All mount checks passed; baseline files unchanged.',flush=True)
