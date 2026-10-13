"""Control only the project runtime whose recorded PID matches the live RPC endpoint."""
import json
from pathlib import Path
import sys
import xmlrpc.client

ROOT = Path(__file__).resolve().parents[2]
record = json.loads((ROOT / ".cad-tools/freecad-profile/runtime.json").read_text())
server = xmlrpc.client.ServerProxy("http://127.0.0.1:9875", allow_none=True)
status = server.cad_runtime_identity()
if status.get("pid") != record["pid"] or Path(record["root"]).resolve() != ROOT:
    raise RuntimeError("Endpoint does not match this project's runtime; refusing to control it")
if sys.argv[1] == "show":
    code = "import FreeCADGui as Gui\nGui.getMainWindow().show()\nGui.getMainWindow().raise_()"
elif sys.argv[1] == "stop":
    code = "import FreeCAD as App, FreeCADGui as Gui\nfrom PySide import QtCore, QtWidgets\nassert not any(Gui.getDocument(d.Name).Modified for d in App.listDocuments().values()), 'Save modified documents before stopping FreeCAD'\nQtCore.QTimer.singleShot(500, QtWidgets.QApplication.instance().quit)"
else:
    raise ValueError("Expected show or stop")
result = server.execute_code(code)
if not result.get("success"):
    raise RuntimeError(result.get("error", "FreeCAD control failed"))
print(result)
