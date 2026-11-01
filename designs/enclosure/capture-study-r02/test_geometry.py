import unittest
import numpy as np
from geometry import basis, project, visibility, blocked_by_box, evaluate, frustum_vertices, grid


def camera(name='a', position=(0,0,0)):
    return dict(id=name,position_mm=list(position),target_mm=[position[0],position[1],position[2]+100],
                up=[0,1,0],sensor_mm=[10,10],pixels=[1000,1000],focal_mm=10,near_mm=1,far_mm=1000,edge_margin=0)


SETTINGS = dict(feature_mm=3,min_feature_pixels=3,min_pair_angle_deg=20,pixel_sigma=.5,body_occlusion=False)


class GeometryTests(unittest.TestCase):
    def test_projection_and_clipping(self):
        c=camera();p=np.array([[0,0,100],[49,0,100],[51,0,100],[0,0,-1],[0,0,1001]])
        v,_=visibility(c,p)
        np.testing.assert_array_equal(v,[True,True,False,False,False])
        self.assertEqual(project(c,p)[0][0].tolist(),[0,0])

    def test_square_top_footprint_and_height(self):
        c=camera();c.update(position_mm=[250,250,450],target_mm=[250,250,0],sensor_mm=[5,5],focal_mm=4.5)
        v,_=visibility(c,np.array([[0,0,0],[500,500,0],[0,0,200],[250,250,200]]))
        np.testing.assert_array_equal(v,[True,True,False,True])

    def test_portrait_swaps_coverage(self):
        c=camera();c['sensor_mm']=[10,5]
        p=np.array([[40,0,100],[0,40,100]])
        np.testing.assert_array_equal(visibility(c,p)[0],[True,False])
        c['roll_deg']=90
        np.testing.assert_array_equal(visibility(c,p)[0],[False,True])

    def test_finite_segment_box(self):
        points=np.array([[0,0,10],[10,0,10],[0,0,2]])
        hit=blocked_by_box(np.zeros(3),points,np.zeros(3),np.eye(3),np.array([-1,-1,4]),np.array([1,1,6]))
        np.testing.assert_array_equal(hit,[True,False,False])

    def test_antiparallel_is_not_good_triangulation(self):
        a=camera('a',(0,0,-100));b=camera('b',(0,0,100));b['target_mm']=[0,0,0]
        result=evaluate([a,b],np.array([[0,0,0]]),SETTINGS)
        self.assertEqual(result['visible_ge2_pct'],100)
        self.assertEqual(result['qualified_pair_pct'],0)

    def test_stereo_depth_sigma_matches_closed_form(self):
        a=camera('a',(-100,0,0));b=camera('b',(100,0,0))
        result=evaluate([a,b],np.array([[0,0,500]]),SETTINGS,True)
        expected=np.sqrt(2)*.5*500**2/(1000*200)
        self.assertAlmostEqual(result['ideal_sigma_p95_mm'],expected,places=10)

    def test_frustum_vertices_project_to_sensor_edges(self):
        c=camera();c['edge_margin']=.05
        uv,xyz,_=project(c,frustum_vertices(c))
        np.testing.assert_allclose(np.abs(uv),450,atol=1e-8)
        np.testing.assert_allclose(xyz[:4,2],1)
        np.testing.assert_allclose(xyz[4:,2],1000)

    def test_margin_rejects_edge_and_bad_input(self):
        c=camera();c['edge_margin']=.05
        self.assertFalse(visibility(c,np.array([[49,0,100]]))[0][0])
        c['focal_mm']=0
        with self.assertRaises(ValueError):project(c,np.zeros((1,3)))
        c=camera();c['target_mm']=c['position_mm']
        with self.assertRaises(ValueError):basis(c)

    def test_grid_volume_and_floor(self):
        self.assertEqual(len(grid(25)),20**3)
        self.assertTrue((grid(25,floor=True)[:,2]==0).all())
        with self.assertRaises(ValueError):grid(30)


if __name__=='__main__':unittest.main()
