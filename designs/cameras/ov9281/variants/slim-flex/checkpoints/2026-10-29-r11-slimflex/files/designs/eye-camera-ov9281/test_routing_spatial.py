import math,random,unittest
from routing_spatial import NearestPoints

class NearestPointsTests(unittest.TestCase):
    def test_matches_exhaustive_distance(self):
        rng=random.Random(10);points=[(rng.uniform(-5,32),rng.uniform(-5,20)) for _ in range(500)];tree=NearestPoints(points)
        for x,y in points[:10]+[(rng.uniform(-10,40),rng.uniform(-10,30)) for _ in range(100)]:
            self.assertAlmostEqual(tree.distance(x,y),min(math.dist((x,y),p) for p in points),places=12)

    def test_duplicates_and_empty_input(self):
        self.assertEqual(NearestPoints([(1,2)]*4).distance(4,6),5)
        with self.assertRaises(ValueError):NearestPoints([])

if __name__=='__main__':unittest.main()
