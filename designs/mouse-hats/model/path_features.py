"""Editable recovered arm centerlines; these are paths, not printable solids."""
import FreeCAD as App
import Part

class ArmPath:
    def __init__(self,obj,points):
        obj.addProperty('App::PropertyVectorList','SectionCenters','Arm path',
                        'Measured section centers in assembly-frame mm; edit to explore path changes.')
        obj.SectionCenters=[App.Vector(*p) for p in points]
        obj.Proxy=self

    def execute(self,obj):
        curve=Part.BSplineCurve()
        curve.interpolate(list(obj.SectionCenters))
        obj.Shape=curve.toShape()

    def dumps(self):return None
    def loads(self,state):pass
