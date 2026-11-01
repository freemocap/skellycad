"""Illustrative thin-lens focus scenarios, not calibration of the physical lens.

Conjugates and magnification: [@edmundBasicLensSelection]. Defocus limits below
are derived from similar triangles with a thin lens and circular aperture.
Diffraction scale: [@edmundAiryFocus2026]. Distances are in mm.
"""
from pathlib import Path
import json
import math


def scenario(f, n, s, sensor_width=1.2, blur=.006, wavelength=.00085):
    if not all(math.isfinite(v) and v > 0 for v in (f, n, s, sensor_width, blur, wavelength)) or s <= f:
        raise ValueError('Positive finite inputs and object distance greater than focal length required')
    image = f*s/(s-f)
    magnification = image/s
    q = n*blur*(s-f)/(f*f)
    near = s/(1+q)
    far = s/(1-q) if q < 1 else None
    # Fixed sensor at image; aperture D=f/n. Blur for another object distance u:
    def defocus(u):
        return (f/n)*image*abs(1/s-1/u)
    assert abs(defocus(s)) < 1e-12
    assert abs(defocus(near)-blur) < 1e-12
    if far is not None:
        assert abs(defocus(far)-blur) < 1e-12
    return dict(focal_length_mm=f, f_number=n, object_distance_mm=s,
                image_distance_from_principal_plane_mm=image,
                extension_from_infinity_mm=image-f,
                turns_from_infinity_if_pitch_035=(image-f)/.35,
                magnification=magnification, object_field_width_mm=sensor_width/magnification,
                added_geometric_defocus_limit_um=blur*1000,
                near_mm=near, far_mm=far,
                geometric_dof_mm=None if far is None else far-near,
                airy_diameter_um=2.44*wavelength*n*(1+magnification)*1000)


if __name__ == '__main__':
    result = {
        'status': 'Conditional thin-lens scenarios; not measured focus or verified replacement compatibility',
        'assumptions': {'focus_adjustable': 'User reports lens screws in/out, 2026-10-30',
                        'focus_distance_mm': 13, 'distance_datum': 'Optical principal plane, provisionally approximated by CAD nominal center',
                        'effective_sensor_width_mm': 1.2, 'equivalent_output_pitch_um_at_400': 3,
                        'geometric_defocus_thresholds_um': [3, 6],
                        'wavelength_nm': 850, 'wavelength_status': 'Illustrative NIR wavelength; actual emitter not established here',
                        'pupil_magnification': 1, 'thread_pitch_mm': .35,
                        'thread_status': 'Example standard M4/M5 pitch, not measured on user lens',
                        'excluded': ['lens aberrations', 'ocular refraction', 'field curvature', 'sensor cover stack', 'measured optical principal planes']},
        'focus_travel': [scenario(1.7, 2.4, s) for s in (8, 10, 13, 15, 20, 30, 50)],
        'aperture_scenarios': [scenario(1.7, n, 13, blur=c) for c in (.003, .006) for n in (2, 2.4, 2.8, 4, 5.6, 8)],
        'focal_length_scenarios': [scenario(f, n, 13) for f, n in ((1.7, 2.4), (1.75, 2.4), (1.95, 2.4), (2.2, 2.2), (2.9, 2.8))],
        'checks': 'Zero defocus at target; specified blur reproduced at every finite near/far bound'
    }
    out = Path(__file__).resolve().parents[6]/'generated/eye-tracker/shared/focus-estimates-r01'
    out.mkdir(parents=True, exist_ok=True)
    (out/'estimates.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('FOCUS_ESTIMATES_OK:', out/'estimates.json')
