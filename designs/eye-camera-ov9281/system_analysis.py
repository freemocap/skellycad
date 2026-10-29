"""Reproducible arithmetic, not an optical/electrical digital twin.

Thin-lens basis [@edmundBasicLensSelection]; sensor area
[@omnivisionOv9281Brief]; candidate lens [@commonlandsCil829].
"""
import json, math

def analysis():
    focal=2.8; f_number=2.55; sensor_width=3.896; sensor_height=2.453
    # Object/image distances are from ideal principal planes. They are NOT
    # barrel clearances or measured front-surface working distances.
    def conjugate(u):return focal*u/(u-focal)
    focus=[]
    for u in [10,15,20]:
        image=conjugate(u);magnification=image/u
        # Chosen 6 um geometric blur criterion; ignores diffraction/aberration.
        delta=.006/((focal/f_number)*image)
        focus.append({'object_principal_plane_distance_mm':u,
            'image_principal_plane_distance_mm':image,
            'ideal_full_array_fov_mm':[sensor_width/magnification,sensor_height/magnification],
            'ideal_6um_blur_object_range_mm':[1/(1/u+delta),1/(1/u-delta)]})
    travel=conjugate(10)-conjugate(20)
    return {'model':'Paraxial thin-lens sensitivity study; no ray tracing or qualification',
        'lens_candidate':'CIL829-F2.5-M08ANIR; evaluation candidate only',
        'focal_length_mm':focal,'f_number':f_number,'sensor_diagonal_mm':math.hypot(sensor_width,sensor_height),
        'focus_cases':focus,'ideal_image_distance_adjustment_mm':travel,
        'equivalent_M8x0_35_turns':travel/.35,
        'lens_mass_g_published':1.4,'user_reference_whole_camera_mass_g':.7,
        'payloads':[{'width':w,'height':h,'fps':fps,'raw8_MB_s':w*h*fps/1e6,
                     'raw8_Mbit_s':w*h*fps*8/1e6}
                    for w,h,fps in [(1280,800,120),(640,400,100),(400,400,120)]],
        'snapshot_buffer_bytes':640*400,'application_plus_CSI_backup_bytes':2*640*400,
        'limits':['Actual 640x400 mode binning/crop field of view is not qualified.',
            'No compound lens prescription, 940 nm MTF, filter transmission or front-surface datum available.',
            'Full-array FOV and blur estimates are ideal geometry, not a selected lens performance promise.',
            'USB numbers exclude packet overhead and do not establish achievable rate.',
            'The 1.4 g candidate lens alone exceeds the user reference whole-camera mass.']}

if __name__=='__main__':print(json.dumps(analysis(),indent=2))
