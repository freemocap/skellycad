import unittest
import numpy as np
from study_lenses import blur_mm

class LensTests(unittest.TestCase):
    def test_focus_plane_has_zero_geometric_defocus(self):
        self.assertAlmostEqual(float(blur_mm(5,1.6,350,np.array(350))),0)
    def test_stopping_down_halves_defocus(self):
        a=blur_mm(5,2,350,np.array([200,500]));b=blur_mm(5,4,350,np.array([200,500]))
        np.testing.assert_allclose(a,2*b)
    def test_thin_lens_direct_geometry(self):
        # 5 mm lens: focused at 105 mm -> image at 5.25 mm.
        # Object at 55 mm -> image at 5.5 mm. f/2 pupil = 2.5 mm.
        self.assertAlmostEqual(float(blur_mm(5,2,105,np.array(55))),2.5*.25/5.5)

if __name__=='__main__':unittest.main()
