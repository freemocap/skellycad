"""Export the selected mouse assembly, preserving carrier/holder positioning."""
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
shared = runpy.run_path(str(HERE.parent / 'shared/model.py'))


def validate(doc):
    assert doc.UpperCatch.Shape.cut(doc.Carrier.Shape).Volume < 1e-6, 'PCB catch missing'
    assert doc.UpperRail.Shape.cut(doc.Carrier.Shape).Volume < 1e-6, 'Cap rail missing'
    assert doc.Carrier.Shape.common(doc.ApproxPCB.Shape).Volume < 1e-6, 'PCB interference'
    assert doc.Carrier.Shape.common(doc.Holder.Shape).Volume < 1e-6, 'Holder interference'


shared['export_selected'](HERE / 'active-model.json', validate)
