"""Shared measured bearing planes; all distances are in assembly-frame mm."""
from copy import deepcopy
import math


def stem_profiles(measured, interface):
    result = deepcopy(measured)
    for feature in result['features']:
        if feature['name'] not in ('MountSection00_0', 'MountSection01_0'):
            continue
        for points in feature['profiles_mm']:
            for side, indices in zip(interface['bearing_faces'], ((0, 1), (7, 6))):
                n = side['normal']
                d = side['stem_offset_mm']
                for index, axis in zip(indices, (2, 0)):
                    point = points[index]
                    # Keep the section Y and the other boundary coordinate fixed.
                    point[axis] = (d-sum(n[k]*point[k] for k in range(3) if k != axis))/n[axis]
    return result


def pocket_parameters(measured, interface, clearance):
    if not math.isfinite(clearance) or not 0 <= clearance <= 0.1:
        raise ValueError('PocketClearance must be between 0 and 0.1 mm; wider changes need validation')
    result = deepcopy(measured)
    for index, face in enumerate(interface['bearing_faces'], 5):
        result['socket_planes_a'][index] = {
            'normal': face['normal'],
            'offset_mm': face['stem_offset_mm'] + face['nominal_pocket_allowance_mm'] + clearance}
    for index, face in enumerate(interface['entry_faces'], 5):
        result['socket_planes_b'][index] = {
            'normal': face['normal'], 'offset_mm': face['offset_mm'] + clearance}
    return result
