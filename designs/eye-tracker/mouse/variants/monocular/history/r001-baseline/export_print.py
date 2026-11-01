"""Export the selected mouse assembly, preserving carrier/holder positioning."""
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
if str(HERE.parent) not in sys.path:
    sys.path.insert(0, str(HERE.parent))
from shared.model import export_selected
from shared.validation import validate_selected


manifest = json.loads((HERE / 'active-model.json').read_text())
export_selected(HERE / 'active-model.json', lambda doc: validate_selected(doc, manifest))
