import os
import Part
from PySide import QtCore,QtWidgets
doc=App.newDocument('ReplayExitProbe')
obj=doc.addObject('Part::Feature','Box');obj.Shape=Part.makeBox(1,2,3)
def done():
    os._exit(0)
QtCore.QTimer.singleShot(0,done)
QtWidgets.QApplication.instance().exec()
