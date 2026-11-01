import unittest
from cross_section import capacitance,solve

class FieldChecks(unittest.TestCase):
    base=dict(width=.1,gap=.2,height=.1,copper=.02,er=4.,step=.005,domain=.6)
    def test_homogeneous_capacitance_scaling(self):
        a,_=capacitance(**self.base,homogeneous=1)
        b,_=capacitance(**self.base,homogeneous=4)
        self.assertAlmostEqual(b/a,4,places=8)
    def test_wider_trace_reduces_impedance(self):
        a=solve(**self.base);b=solve(**dict(self.base,width=.15))
        self.assertLess(b['zdiff_ohm'],a['zdiff_ohm'])
        self.assertLess(a['residual'],1e-9)
    def test_vacuum_delay(self):
        a=solve(**dict(self.base,er=1))
        self.assertAlmostEqual(a['effective_er'],1,places=8)
        self.assertAlmostEqual(a['delay_ps_mm'],3.335640952,places=7)
    def test_mesh_refinement(self):
        a=solve(**self.base);b=solve(**dict(self.base,step=.0025))
        self.assertLess(abs(a['zdiff_ohm']/b['zdiff_ohm']-1),.04)
    def test_finite_ground_guard(self):
        infinite=solve(**self.base,guard_gap=.1)
        finite=solve(**self.base,guard_gap=.1,guard_width=.1)
        absent=solve(**self.base)
        self.assertLess(infinite['zdiff_ohm'],finite['zdiff_ohm'])
        self.assertLess(finite['zdiff_ohm'],absent['zdiff_ohm'])

if __name__=='__main__':unittest.main()
