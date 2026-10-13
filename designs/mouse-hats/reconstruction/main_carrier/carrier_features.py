"""Small FreeCAD feature for a tolerance-aware union of measured profiles."""

class ToleranceUnion:
    def __init__(self, obj):
        obj.addProperty('App::PropertyLinkList','Sources','Construction')
        obj.addProperty('App::PropertyLength','JoinTolerance','Construction')
        obj.JoinTolerance=0.001
        obj.Proxy=self

    def execute(self, obj):
        shapes=[item.Shape for item in obj.Sources]
        obj.Shape=shapes[0].multiFuse(shapes[1:],obj.JoinTolerance.Value).removeSplitter()

    def dumps(self):
        return None

    def loads(self, state):
        pass
