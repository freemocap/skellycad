"""Fresh-process external-link, placement, edit propagation and overlap checks."""
import itertools
import json
import build
import FreeCAD as App

build.load_modules()
doc = App.openDocument(str(build.FILE))
manifest = json.loads((build.HERE/'parts.json').read_text())
report = {'units': 'mm', 'parts': {}, 'pairs': {}, 'edits': [],
          'boolean_tolerance_mm': 0.001, 'physical_fit_validated': False}
for entry in manifest['parts']:
    link = doc.getObject(entry['name'])
    source = link.LinkedObject
    source.Document.recompute()
    doc.recompute()
    actual = link.Shape
    expected = source.Shape.copy()
    expected.Placement = build.placement(entry['local_to_assembly']).multiply(expected.Placement)
    center_error = (actual.Solids[0].CenterOfMass-expected.Solids[0].CenterOfMass).Length
    bounds_error = max(abs(getattr(actual.BoundBox,k)-getattr(expected.BoundBox,k))
                       for k in ('XMin','XMax','YMin','YMax','ZMin','ZMax'))
    assert center_error < 1e-7 and bounds_error < 1e-7, (entry['name'],center_error,bounds_error)
    actual.check(True)
    assert len(actual.Solids) == 1
    report['parts'][entry['name']] = dict(volume_mm3=actual.Volume, faces=len(actual.Faces),
        center_error_mm=center_error, bounds_error_mm=bounds_error, valid=True,
        external_document=source.Document.FileName)
    print('Link checked:',entry['name'],flush=True)

for part, target, prop, delta in [('Cap','Dimensions','VentRadius',0.1),
                                  ('Baseplate','Baseplate','BoreRadius',0.1)]:
    link = doc.getObject(part)
    sd = link.LinkedObject.Document
    control = sd.getObject(target)
    original = float(getattr(control,prop))
    before = link.Shape.Volume
    try:
        setattr(control,prop,original+delta)
        sd.recompute(); doc.recompute()
        after = link.Shape.Volume
        assert abs(after-before) > 1e-4
        link.Shape.check(True)
        report['edits'].append(dict(part=part,property=prop,before_mm3=before,after_mm3=after))
    finally:
        setattr(control,prop,original)
        sd.recompute(); doc.recompute()
    assert abs(link.Shape.Volume-before) < 1e-7

for a,b in itertools.combinations([p['name'] for p in manifest['parts']],2):
    sa,sb = doc.getObject(a).Shape,doc.getObject(b).Shape
    common = sa.common(sb,0.001)
    try:
        if common.Solids:
            common.check(True)
        result = dict(valid=True,overlap_mm3=common.Volume)
    except Exception as exc:
        result = dict(valid=False,overlap_mm3=None,error=str(exc))
    report['pairs'][a+' / '+b] = result
    print(a,b,result,flush=True)

for name in ('Socket','Holder'):
    spheres=[]
    for face in doc.getObject(name).Shape.Faces:
        surface=face.Surface
        if type(surface).__name__ == 'Sphere':
            spheres.append(dict(radius_mm=surface.Radius,center_mm=list(surface.Center)))
    report['parts'][name]['spheres']=spheres
seat = min(report['parts']['Socket']['spheres'], key=lambda s: s['radius_mm'])
ball = report['parts']['Holder']['spheres'][0]
report['ball_socket_center_offset_mm'] = (App.Vector(*ball['center_mm'])-App.Vector(*seat['center_mm'])).Length
report['ball_socket_note'] = 'Inherited nonconcentric placement; radius difference is not uniform clearance.'
(build.OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Saved validation.json; no edited source document was saved.',flush=True)
