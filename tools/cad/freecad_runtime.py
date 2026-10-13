"""Dedicated scripted GUI process for the pinned FreeCAD/MCP runtime."""
import os
from pathlib import Path
import runpy
import json
import FreeCADGui as Gui
from PySide import QtWidgets

Gui.showMainWindow()
app = QtWidgets.QApplication.instance()
app.setQuitOnLastWindowClosed(False)
runpy.run_path(str(Path(__file__).with_name("start_mcp.FCMacro")))
Gui.getMainWindow().hide()
profile = Path(os.environ["CAD_PLAYGROUND_ROOT"]) / ".cad-tools/freecad-profile"
(profile / "runtime.json").write_text(json.dumps({"pid": os.getpid(), "root": os.environ["CAD_PLAYGROUND_ROOT"]}), encoding="utf-8")
print("CAD_GUI_READY", flush=True)
app.exec()
