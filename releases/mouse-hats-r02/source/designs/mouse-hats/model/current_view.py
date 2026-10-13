"""Saved overview/assembled view selector; both presentations reference the same parts."""
import FreeCAD as App


class LayoutControl:
    def __init__(self,obj):
        obj.addProperty('App::PropertyEnumeration','Layout','Presentation')
        obj.Layout=['Numbered parts','Assembled']
        obj.Proxy=self

    def onChanged(self,obj,prop):
        if prop!='Layout' or not App.GuiUp:return
        doc=obj.Document
        for group_name,visible in [('PartsOverview',str(obj.Layout)=='Numbered parts'),
                                   ('Assembled',str(obj.Layout)=='Assembled')]:
            group=doc.getObject(group_name)
            if group:
                for child in group.Group:child.Visibility=visible
        import FreeCADGui as Gui
        if App.ActiveDocument==doc:
            view=Gui.activeDocument().activeView()
            if str(obj.Layout)=='Numbered parts':view.setCameraOrientation(App.Rotation().Q)
            else:view.viewIsometric()
            view.fitAll()

    def dumps(self):return None
    def loads(self,state):pass
