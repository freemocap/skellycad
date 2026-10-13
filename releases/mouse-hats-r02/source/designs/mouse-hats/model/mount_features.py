"""Persistable candidate baseplate; measured data and interface are embedded."""
import json
from baseplate_features import construct
from mount_interface import pocket_parameters


class MountPocket:
    def __init__(self, obj, measured, interface):
        for name, data in [('MeasuredJSON', measured), ('InterfaceJSON', interface)]:
            obj.addProperty('App::PropertyString', name, 'Construction')
            setattr(obj, name, json.dumps(data))
            obj.setEditorMode(name, 1)
        obj.addProperty('App::PropertyLength', 'PocketClearance', 'Mount fit',
                        'Additional allowance normal to each bearing/entry face; stem and floor stay fixed.')
        obj.PocketClearance = 0
        obj.Proxy = self

    def execute(self, obj):
        measured = json.loads(obj.MeasuredJSON)
        interface = json.loads(obj.InterfaceJSON)
        params = pocket_parameters(measured, interface, obj.PocketClearance.Value)
        shape = construct(params, measured['bore']['radius_mm'], measured['body_depth_mm'])['Finished']
        shape.check(True)
        if len(shape.Solids) != 1:
            raise ValueError('Expected one baseplate solid')
        obj.Shape = shape

    def dumps(self): return None
    def loads(self, state): pass
