"""Ideal rectilinear projection [@opencvCalibR02; @edmundFovR02]. Units: mm.

Visibility thresholds and linearized precision estimates are local study choices.
"""
import itertools
import numpy as np


def basis(camera):
    p = np.asarray(camera['position_mm'], float)
    f = np.asarray(camera['target_mm'], float) - p
    if np.linalg.norm(f) < 1e-9:
        raise ValueError('Camera target must differ from its position')
    f /= np.linalg.norm(f)
    up = np.asarray(camera.get('up', [0, 0, 1]), float)
    r = np.cross(f, up)
    if np.linalg.norm(r) < 1e-8:
        raise ValueError('Up vector must not be parallel to viewing direction')
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    a = np.deg2rad(camera.get('roll_deg', 0))
    return np.array([r*np.cos(a)+u*np.sin(a), u*np.cos(a)-r*np.sin(a), f])


def validate(camera):
    for key in ('sensor_mm', 'pixels'):
        if len(camera[key]) != 2 or min(camera[key]) <= 0:
            raise ValueError(f'{key} must contain two positive dimensions')
    if not 0 < camera['near_mm'] < camera['far_mm'] or camera['focal_mm'] <= 0:
        raise ValueError('Require positive focal length and 0 < near < far')
    if not 0 <= camera.get('edge_margin', 0) < .5:
        raise ValueError('Edge margin must be in [0, 0.5)')
    basis(camera)


def project(camera, points):
    validate(camera)
    xyz = (np.asarray(points) - camera['position_mm']) @ basis(camera).T
    z = xyz[:, 2]
    focal_px = camera['focal_mm'] * np.array(camera['pixels']) / camera['sensor_mm']
    with np.errstate(divide='ignore', invalid='ignore'):
        uv = xyz[:, :2] / z[:, None] * focal_px
    return uv, xyz, focal_px


def blocked_by_box(origin, points, center, axes, low, high):
    """Open segment intersects an oriented box; endpoints do not count as blockers."""
    o = (np.asarray(origin)-center) @ axes.T
    d = (points-origin) @ axes.T
    parallel = np.abs(d) < 1e-12
    safe = np.where(parallel, 1., d)
    t1, t2 = (low-o)/safe, (high-o)/safe
    enter = np.where(parallel, -np.inf, np.minimum(t1, t2)).max(axis=1)
    leave = np.where(parallel, np.inf, np.maximum(t1, t2)).min(axis=1)
    outside = (parallel & ((o < low) | (o > high))).any(axis=1)
    return ~outside & (np.maximum(enter, 1e-6) < np.minimum(leave, 1-1e-6))


def visibility(camera, points, cameras=(), obstacles=()):
    uv, xyz, fp = project(camera, points)
    half = np.asarray(camera['pixels']) * (.5-camera.get('edge_margin', 0))
    visible = (xyz[:, 2] >= camera['near_mm']) & (xyz[:, 2] <= camera['far_mm']) & (np.abs(uv) <= half).all(axis=1)
    for other in cameras:
        if other['id'] == camera['id']:
            continue
        visible &= ~blocked_by_box(np.array(camera['position_mm']), points,
            np.array(other['position_mm']), basis(other), np.array([-18, -15, -45]), np.array([18, 15, -15]))
    for box in obstacles:
        visible &= ~blocked_by_box(np.array(camera['position_mm']), points, np.zeros(3), np.eye(3), np.array(box[0]), np.array(box[1]))
    density = np.min(fp) / np.maximum(xyz[:, 2], 1e-9)
    return visible, density


def grid(spacing, height=500, floor=False):
    if 500 % spacing != 0 or (not floor and height % spacing != 0):
        raise ValueError('Grid spacing must divide the sampled region')
    xy = np.arange(spacing/2, 500, spacing)
    z = np.array([0.]) if floor else np.arange(spacing/2, height, spacing)
    return np.stack(np.meshgrid(xy, xy, z, indexing='ij'), axis=-1).reshape(-1, 3)


def evaluate(cameras, points, settings, precision=False):
    points = np.asarray(points, float)
    vis, density = zip(*(visibility(c, points, cameras if settings.get('body_occlusion', True) else (), settings.get('obstacles', [])) for c in cameras))
    vis, density = np.array(vis), np.array(density)
    qualified = vis & (density * settings['feature_mm'] >= settings['min_feature_pixels'])
    rays = points[None, :, :] - np.array([c['position_mm'] for c in cameras])[:, None, :]
    rays /= np.maximum(np.linalg.norm(rays, axis=2, keepdims=True), 1e-12)
    best = np.zeros(len(points))
    pair_count = np.zeros(len(points), int)
    min_angle = settings['min_pair_angle_deg']
    for i, j in itertools.combinations(range(len(cameras)), 2):
        dot = np.sum(rays[i]*rays[j], axis=1).clip(-1, 1)
        # Acute line intersection angle excludes both parallel and antiparallel rays.
        angle = np.degrees(np.arccos(np.abs(dot)))
        good = qualified[i] & qualified[j] & (angle >= min_angle)
        pair_count += good
        best = np.maximum(best, np.where(good, angle, 0))
    count = vis.sum(axis=0)
    second_density = np.sort(np.where(vis, density, 0), axis=0)[-2]
    result = {'sample_count': len(points), 'visible_ge2_pct': float(np.mean(count>=2)*100),
              'visible_ge3_pct': float(np.mean(count>=3)*100), 'visible_all5_pct': float(np.mean(count==5)*100),
              'qualified_pair_pct': float(np.mean(pair_count>0)*100),
              'redundant_pairs_pct': float(np.mean(pair_count>=2)*100),
              'second_view_px_per_mm_p10': float(np.percentile(second_density, 10)),
              'count': count, 'pair_count': pair_count, 'best_angle': best, 'second_density': second_density}
    if precision:
        info = np.zeros((len(points), 3, 3))
        for i,c in enumerate(cameras):
            _, xyz, fp = project(c, points)
            z = np.maximum(xyz[:, 2], 1e-9)
            jac = np.zeros((len(points), 2, 3))
            jac[:, 0, 0] = fp[0]/z
            jac[:, 1, 1] = fp[1]/z
            jac[:, 0, 2] = -fp[0]*xyz[:, 0]/z**2
            jac[:, 1, 2] = -fp[1]*xyz[:, 1]/z**2
            jac = jac @ basis(c)
            info += np.einsum('nji,njk->nik', jac, jac) * qualified[i, :, None, None] / settings['pixel_sigma']**2
        eigen = np.linalg.eigvalsh(info)[:, 0]
        good = (pair_count>0) & (eigen>1e-12)
        sigma = np.full(len(points), np.nan)
        sigma[good] = 1/np.sqrt(eigen[good])
        result['sigma_worst_axis_mm'] = sigma
        result['ideal_sigma_p95_mm'] = float(np.percentile(sigma[good], 95)) if good.any() else None
    return result


def summary(result):
    return {k:v for k,v in result.items() if not isinstance(v, np.ndarray)}


def frustum_vertices(camera, usable=True):
    """Eight vertices in near/far planes, ordered around each rectangular plane."""
    ratio = np.array(camera['sensor_mm'])/(2*camera['focal_mm'])
    if usable:
        ratio *= 1-2*camera.get('edge_margin', 0)
    local = np.array([[sx*z*ratio[0], sy*z*ratio[1], z]
        for z in (camera['near_mm'], camera['far_mm']) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))])
    return local @ basis(camera) + camera['position_mm']
