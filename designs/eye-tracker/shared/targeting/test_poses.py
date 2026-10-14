import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from poses import aim_sensor,axis_error,rigid

class TargetingTests(unittest.TestCase):
 def test_known_lens_offset_and_forward_ray(self):
  R=np.diag([1.,-1.,-1.]);T=aim_sensor([1,2,3],[1,2,13],[.1,5,1],R)
  np.testing.assert_allclose(T[:3,3],[.9,7,14],atol=1e-12)
  error=axis_error(T,[.1,5,1],[1,2,3]);self.assertAlmostEqual(error['forward_distance_mm'],10);self.assertLess(error['axis_miss_mm'],1e-12)
 def test_common_world_frame_change_preserves_target_solution(self):
  target=np.array([4,1,-8]);lens=np.array([1,2,10]);local=[.1,5,1];R=np.diag([1.,-1.,-1.]);first=aim_sensor(target,lens,local,R)
  Q=Rotation.from_euler('xyz',[.3,-.5,.8]).as_matrix();translation=np.array([3,-2,9]);A=np.eye(4);A[:3,:3]=Q;A[:3,3]=translation
  second=aim_sensor(Q@target+translation,Q@lens+translation,local,Q@R);np.testing.assert_allclose(second,A@first,atol=1e-11)
 def test_mirroring_and_scale_rejected(self):
  for factor in [-1,1.01]:
   T=np.eye(4);T[0,0]=factor
   with self.assertRaises(ValueError):rigid(T)
 def test_degenerate_lens_target_rejected(self):
  with self.assertRaises(ValueError):aim_sensor([0,0,0],[0,0,0],[0,0,0],np.eye(3))
 def test_ambiguous_half_turn_requires_roll(self):
  with self.assertRaises(ValueError):aim_sensor([0,0,0],[0,0,1],[0,0,0],np.eye(3))
if __name__=='__main__':unittest.main()
