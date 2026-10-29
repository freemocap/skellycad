"""Connect data 1 P in a new trial; preserve source files and native rules.

This is a connectivity experiment, not a qualified differential interconnect.
All coordinates are millimetres. Full native validation is a separate step.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys
import pcbnew as p
from route_isolated_head_pads import route
from routing_geometry import add_via
from route_head_dovdd import v, xy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args(); src = a.source.resolve(); out = a.output.resolve()
    assert not out.exists()
    b = p.LoadBoard(str(src / 'head.kicad_pcb'))
    pool = list(b.GetTracks())  # Keep removed SWIG wrappers alive until save.
    def pad(n):
        return next(q for q in b.GetPads() if q.GetParentFootprint().GetReference() == 'U1' and q.GetNumber() == n)
    start = v(7.085, 6.507); end = v(4.7583, 13.3)
    changes = []; removed = []; ground_via = v(7.085, 5.507)
    for t in pool:
        power = t.GetNetname() == '+1V8' and t.GetLayer() == p.B_Cu and any(q.x == 6935200 for q in [t.GetStart(), t.GetEnd()])
        inner = t.m_Uuid.AsString() == 'a32151f0-0d11-4538-b3d7-19c08151ec47'
        ground = t.GetNetname() == 'GND' and t.GetLayer() == p.F_Cu and not isinstance(t, p.PCB_VIA) and t.GetEffectiveShape(p.F_Cu).Collide(p.SHAPE_CIRCLE(start, 200000), 100000)
        inner2 = t.GetNetname() in ['/M1_VN1', '/M1_SID'] and t.GetLayer() == p.In2_Cu and not isinstance(t, p.PCB_VIA)
        if ground or inner2 or power or inner:
            removed.append({'uuid':t.m_Uuid.AsString(), 'net':t.GetNetname(), 'start':xy(t.GetStart()), 'end':xy(t.GetEnd())})
            b.Remove(t)
    source = pad('G5'); results = {}
    for point, net in [(start,source.GetNetname()), (end,source.GetNetname()), (ground_via,'GND')]:
        for item in list(b.GetPads()) + list(b.GetTracks()):
            if item.GetNetname() == net:continue
            for layer in [p.F_Cu, p.In1_Cu, p.In2_Cu, p.B_Cu]:
                assert not (item.IsOnLayer(layer) and item.GetEffectiveShape(layer).Collide(p.SHAPE_CIRCLE(point, 200000), 100000)), ('Via blocked', xy(point), item.GetNetname(), item.m_Uuid.AsString())
        for q in b.GetPads():
            for layer in [p.F_Cu, p.B_Cu]:
                assert not(q.IsOnLayer(layer) and q.GetEffectiveShape(layer).Collide(p.SHAPE_CIRCLE(point, 200000), 0)), 'Via overlaps solder pad'
    preview = route(b, source, start=start, targets=[source.GetPosition()], max_nodes=300000, commit=False, ignore_track_nets=['/M1_DVDD', 'GND'])
    assert preview['result'] == 'routed', preview
    points = preview['path_xy_mm']
    more = list(b.GetTracks()); pool.extend(more)
    for t in more:
        if t.GetNetname() in ['/M1_DVDD', 'GND'] and t.GetLayer() == p.F_Cu and not isinstance(t, p.PCB_VIA) and any(t.GetEffectiveShape(p.F_Cu).Collide(p.SHAPE_SEGMENT(v(*aa), v(*bb), 100000), 100000) for aa, bb in zip(points, points[1:])):
            removed.append({'uuid':t.m_Uuid.AsString(), 'net':t.GetNetname(), 'start':xy(t.GetStart()), 'end':xy(t.GetEnd())})
            b.Remove(t)
    results['escape'] = route(b, source, start=start, targets=[source.GetPosition()], max_nodes=300000)
    assert results['escape']['result'] == 'routed', results
    # Attach copper to the sensor pad before adding the source via. KiCad may
    # otherwise assign a floating via to the old ground fill during connectivity.
    for point in [start, end]:add_via(b, point, source.GetNetCode())
    results['ground_escape'] = route(b, pad('E5'), targets=[ground_via], max_nodes=300000)
    assert results['ground_escape']['result'] == 'routed'
    add_via(b, ground_via, pad('E5').GetNetCode())
    for name, net, layer, aa, bb in [
        ('DOVDD','/M1_DOVDD',p.In1_Cu,(7.3839,8.2835),(7.3839,4.2589)),
        ('1V8','+1V8',p.B_Cu,(6.551,7.7886),(7.935,4.7767)),
        ('VN1','/M1_VN1',p.In2_Cu,(3.7624,6.5325),(10.4476,6.3457)),
        ('SID','/M1_SID',p.In2_Cu,(.9282,6.0706),(12.715,8.1028)),
    ]:
        netpad = next(q for q in b.GetPads() if q.GetNetname() == net)
        waypoints = {'DOVDD':[(7.7,6.507),(7.7,5.007)]}.get(name, [])
        points = [aa] + waypoints + [bb]; results[name] = []
        for left, right in zip(points, points[1:]):
            leg = route(b, netpad, layer=layer, start=v(*left), targets=[v(*right)], max_nodes=300000)
            assert leg['result'] == 'routed', (name, left, right, leg)
            results[name].append(leg)
    # In1 carries a ground pour and existing signals. Using it here is recorded
    # as an explicit return-path limitation, not high-speed routing approval.
    for layer in [p.B_Cu, p.In2_Cu, p.In1_Cu]:
        middle = route(b, source, layer=layer, start=start, targets=[end], max_nodes=300000)
        if middle['result'] == 'routed':
            middle['layer'] = b.GetLayerName(layer); results['middle'] = middle; break
    else:
        p.SaveBoard(str(src.parent/'ov9281-data1p-diagnostic.kicad_pcb'), b)
        raise AssertionError(middle)
    for number in ['G3', 'G6', 'H5']:
        results['DVDD_' + number] = route(b, pad(number), max_nodes=300000)
    for number in ['F4', 'E5']:
        results['GND_' + number] = route(b, pad(number), max_nodes=300000)
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones())
    # Refill exposes ground islands made by the new In1 routing. Join both
    # through existing ground vias, then refill and let native DRC verify them.
    results['ground_back_E5'] = route(b, pad('E5'), layer=p.B_Cu, start=ground_via, max_nodes=300000)
    cap = next(q for q in b.GetPads() if q.GetParentFootprint().GetReference() == 'C14' and q.GetNumber() == '2')
    results['ground_back_J201'] = route(b, cap, layer=p.B_Cu, start=v(5.75,13.3), max_nodes=300000)
    assert all(results[k]['result'] == 'routed' for k in ['ground_back_E5','ground_back_J201'])
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones())
    shutil.copytree(src, out, ignore=shutil.ignore_patterns('*.lck', '*.kicad_prl'))
    (out/'validation.json').rename(out/'source-validation-data1p.json')
    p.SaveBoard(str(out/'head.kicad_pcb'), b)
    record = {'source_head_sha256':hashlib.sha256((src/'head.kicad_pcb').read_bytes()).hexdigest(), 'endpoint_changes':changes, 'removed':removed, 'routes':results, 'limit':'Connectivity only; differential impedance, skew and return paths remain unqualified.'}
    (out/'data1p-routing.json').write_text(json.dumps(record, indent=2)+'\n')
    subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')), 'pcb', 'drc', '--format', 'json', '--output', str(out/'checks/data1p-drc.json'), str(out/'head.kicad_pcb')], capture_output=True, check=True)
    d = json.loads((out/'checks/data1p-drc.json').read_text())
    print(json.dumps({'unconnected':len(d['unconnected_items']), 'violations':[x['type'] for x in d['violations']], 'routes':results}, indent=2))

if __name__ == '__main__': main()
