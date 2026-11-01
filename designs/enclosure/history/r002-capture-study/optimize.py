"""Deterministic layout sweep and denser verification; no claimed global optimum."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import numpy as np
from geometry import evaluate, grid, summary

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[2] / 'generated/enclosure/capture-study-r02'


def layout(settings, height=260, delta=0, aim=100, hfov=80, aspect=4/3, roll=0, topfov=65):
    width = round(np.sqrt(settings['corner_pixel_count']*aspect))
    height_px = round(width/aspect)
    sensor = np.array([width, height_px])*settings['corner_pixel_pitch_um']/1000
    focal = sensor[0]/(2*np.tan(np.deg2rad(hfov/2)))
    cameras = []
    d = settings['corner_inset_mm']
    for i,(x,y) in enumerate(((d,d),(500-d,d),(500-d,500-d),(d,500-d))):
        z = height + (delta if i%2 else -delta)
        if z < 75 or z > 440:
            return None
        cameras.append(dict(id=f'C{i+1}', position_mm=[x,y,z], target_mm=[250,250,aim],
            up=[0,0,1], roll_deg=roll, sensor_mm=sensor.tolist(), pixels=[width,height_px], focal_mm=float(focal)))
    cameras.append(dict(id='Top', position_mm=[250,250,settings['top_optical_height_mm']],
        target_mm=[250,250,0], up=[0,1,0], roll_deg=0, sensor_mm=settings['top_sensor_mm'],
        pixels=settings['top_pixels'], focal_mm=float(settings['top_sensor_mm'][0]/(2*np.tan(np.deg2rad(topfov/2))))))
    for c in cameras:
        c.update(near_mm=settings['near_mm'], far_mm=settings['far_mm'], edge_margin=settings['edge_margin'])
    return cameras


def regions(spacing):
    return {'floor':grid(spacing, floor=True), 'lower':grid(spacing, height=200), 'cube':grid(spacing)}


def measure(cameras, settings, points, precision=False):
    return {k:evaluate(cameras,p,settings,precision) for k,p in points.items()}


def score(metrics, weights):
    # Coverage dominates; redundancy and sampling density break broad-FOV ties.
    return sum(weights[k]*(v['qualified_pair_pct'] + .10*v['redundant_pairs_pct']
        + 5*min(v['second_view_px_per_mm_p10']/2, 1)) for k,v in metrics.items())


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--settings', type=Path, default=HERE/'study.json')
    parser.add_argument('--layout', type=Path, help='Evaluate an edited five-camera layout instead of searching')
    args = parser.parse_args()
    settings = json.loads(args.settings.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    if args.layout:
        cameras = json.loads(args.layout.read_text())['cameras']
        if len(cameras)!=5 or len({c['id'] for c in cameras})!=5:
            raise ValueError('Require five cameras with distinct IDs')
        result = measure(cameras, settings, regions(settings['search']['verification_spacing_mm']), True)
        save_json(OUT/'custom-evaluation.json', {k:summary(v) for k,v in result.items()})
        print(json.dumps({k:summary(v) for k,v in result.items()}, indent=2))
        return
    space = settings['search']
    points = regions(space['coarse_spacing_mm'])
    keys = ['height_mm','alternating_height_mm','aim_height_mm','horizontal_fov_deg','aspect_ratio','roll_deg','top_fov_deg']
    trials = []
    for values in itertools.product(*(space[k] for k in keys)):
        cams = layout(settings,*values)
        if cams is None:
            continue
        m = measure(cams, settings, points)
        trials.append({'parameters':dict(zip(keys,values)), 'cameras':cams,
            'score_priority':score(m,settings['weights']), 'score_cube':score(m,{'floor':0,'lower':0,'cube':1})})
    print(f'Coarse search: {len(trials)} feasible layouts', flush=True)
    keep = {}
    for objective in ('score_priority','score_cube'):
        for trial in sorted(trials,key=lambda t:t[objective],reverse=True)[:space['shortlist_count_per_objective']]:
            keep[json.dumps(trial['parameters'])] = trial
    points = regions(space['refinement_spacing_mm'])
    for trial in keep.values():
        m = measure(trial['cameras'],settings,points)
        trial.update(score_priority=score(m,settings['weights']),score_cube=score(m,{'floor':0,'lower':0,'cube':1}),
                     metrics={k:summary(v) for k,v in m.items()})
    selected = max(keep.values(),key=lambda t:t['score_priority'])
    cube = max(keep.values(),key=lambda t:t['score_cube'])
    # Independent pose refinement allows asymmetric arrangements after symmetric sweep.
    # One deterministic coordinate pass: optical height and horizontal aim offsets.
    import copy
    refined = copy.deepcopy(selected)
    for index in range(4):
        for field,component,step in [('position_mm',2,25),('target_mm',0,40),('target_mm',1,40),('target_mm',2,25)]:
            best = refined
            for sign in (-1,1):
                trial = copy.deepcopy(refined)
                trial['cameras'][index][field][component] += sign*step
                if not 75 <= trial['cameras'][index]['position_mm'][2] <= 440:
                    continue
                m = measure(trial['cameras'],settings,points)
                val = score(m,settings['weights'])
                if val > best['score_priority']+1e-9:
                    trial.update(score_priority=val,score_cube=score(m,{'floor':0,'lower':0,'cube':1}),metrics={k:summary(v) for k,v in m.items()})
                    best = trial
            refined = best
    selected = refined
    selected['parameters']['note'] = 'Symmetric sweep seed; cameras contain final independent pose refinement'
    save_json(OUT/'selected-layout.json',selected)
    save_json(OUT/'cube-layout.json',cube)
    save_json(OUT/'shortlist.json',list(keep.values()))
    fine_points = regions(space['verification_spacing_mm'])
    results = {}
    for name,cams in [('baseline',layout(settings)),('floor-priority',selected['cameras']),('cube-priority',cube['cameras'])]:
        m = measure(cams,settings,fine_points,True)
        results[name] = {k:summary(v) for k,v in m.items()}
        if name=='floor-priority':
            arrays = {}
            for k,v in m.items():
                arrays[k+'_points'] = fine_points[k]
                arrays.update({k+'_'+a:b for a,b in v.items() if isinstance(b,np.ndarray)})
            np.savez_compressed(OUT/'samples.npz',**arrays)
    # Threshold sensitivity: ideal assumptions are visible, not hidden in a scalar.
    sensitivity = []
    for feature,angle in ((1,20),(3,10),(3,30),(5,20)):
        s = dict(settings,feature_mm=feature,min_pair_angle_deg=angle)
        m = measure(selected['cameras'],s,points)
        sensitivity.append({'feature_mm':feature,'min_pair_angle_deg':angle,'metrics':{k:summary(v) for k,v in m.items()}})
    corners = np.array(list(itertools.product((0,500),(0,500),(0,200))),float)
    edge = evaluate(selected['cameras'],corners,settings)
    report = {'settings_sha256':hashlib.sha256(args.settings.read_bytes()).hexdigest(),
        'coarse_candidates':len(trials),'refined_candidates':len(keep), 'grid_spacing_mm':space['verification_spacing_mm'],
        'metrics':results,'sensitivity':sensitivity,'lower_box_corner_visible_counts':edge['count'].tolist(),
        'lower_box_corner_pair_counts':edge['pair_count'].tolist(),
        'limitations':['Finite sampled and local search, not global optimum', 'Ideal rectilinear intrinsics; no distortion or depth of field',
        'Camera bodies occlude; animal, tether, lenses and mounts are not occluders', 'Ideal covariance assumes exact calibration and synchronization',
        'Synthetic sensors and lenses have no purchasing or mechanical qualification']}
    save_json(OUT/'results.json',report)
    print(json.dumps(report['metrics'],indent=2),flush=True)


if __name__=='__main__':
    main()
