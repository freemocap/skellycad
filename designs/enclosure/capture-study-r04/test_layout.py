import json,unittest
from pathlib import Path
import numpy as np
from optimize import layout
from geometry import project,visibility

class LayoutTests(unittest.TestCase):
    def setUp(self):self.settings=json.loads(Path(__file__).with_name('study.json').read_text())
    def test_top_usable_edges_match_floor(self):
        c=layout(self.settings,300,0,100,45)[-1]
        uv,_,_=project(c,np.array([[0,0,0],[500,500,0]]))
        self.assertTrue(np.allclose(np.abs(uv),np.array(c['pixels'])*.45))
    def test_square_sensors_and_height(self):
        cams=layout(self.settings,300,0,100,45)
        for c in cams:
            self.assertEqual(c['pixels'][0],c['pixels'][1]);self.assertEqual(c['sensor_mm'][0],c['sensor_mm'][1])
        self.assertTrue(all(250<=c['position_mm'][2]<=300 for c in cams[:4]))
    def test_selected_side_views_cover_floor_corners(self):
        cams=layout(self.settings,300,0,100,45)
        corners=np.array([[0,0,0],[500,0,0],[500,500,0],[0,500,0]])
        for c in cams[:4]:self.assertTrue(visibility(c,corners)[0].all())
    def test_clipped_cell_volume_conservation(self):
        from polyclip import box_faces,clip
        def volume(faces):
            return abs(sum(np.dot(f[0],np.cross(f[i],f[i+1]))/6 for f in faces for i in range(1,len(f)-1)))
        box=box_faces([0,0,0],[500,500,500]);n=np.array([1,1,0])/np.sqrt(2);d=500/np.sqrt(2)
        a=clip(box,n,d);b=clip(box,-n,-d)
        self.assertAlmostEqual(volume(a),500**3/2,places=5)
        self.assertAlmostEqual(volume(a)+volume(b),500**3,places=5)
    def test_coplanar_clip_and_empty_clip(self):
        from polyclip import box_faces,clip
        box=box_faces([0,0,0],[500,500,500])
        self.assertEqual(len(clip(box,[1,0,0],500)),6)
        self.assertEqual(clip(box,[1,0,0],-1),[])

if __name__=='__main__':unittest.main()
