import unittest
from interconnect_graph import measure

def segment(a,b,layer='F.Cu',uid='a'):
    return dict(a=a,b=b,layer=layer,uuid=uid)
def port(xy,layer='F.Cu'):return dict(xy=xy,layer=layer)

class CenterlineTests(unittest.TestCase):
    def test_straight(self):
        self.assertAlmostEqual(measure([segment((0,0),(3,4))],[],[port((0,0)),port((3,4))])['path_length_mm'],5)
    def test_branch_not_added_to_path(self):
        r=measure([segment((0,0),(10,0)),segment((5,0),(5,7),uid='branch')],[],[port((0,0)),port((10,0))])
        self.assertEqual(r['path_length_mm'],10);self.assertEqual(r['inventory_length_mm'],17)
    def test_layer_change(self):
        r=measure([segment((0,0),(3,0)),segment((3,0),(3,4),'In2.Cu','b')],[dict(xy=(3,0),layers=['F.Cu','In2.Cu'],uuid='via')],[port((0,0)),port((3,4),'In2.Cu')])
        self.assertEqual(r['path_length_mm'],7);self.assertEqual(r['path_via_uuids'],['via'])
    def test_crossing_and_overlap(self):
        r=measure([segment((0,0),(10,0)),segment((5,-5),(5,5),uid='b'),segment((0,0),(3,0),uid='duplicate')],[],[port((0,0)),port((5,5))])
        self.assertEqual(r['path_length_mm'],10)
    def test_unconnected_layers_rejected(self):
        with self.assertRaises(ValueError):measure([segment((0,0),(3,0)),segment((3,0),(3,4),'B.Cu','b')],[],[port((0,0)),port((3,4),'B.Cu')])

if __name__=='__main__':unittest.main()
