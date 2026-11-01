# Shared camera utilities

Reusable routing geometry, interconnect analysis and cross-section solvers live
here. Their unit tests run with the CAD tools Python environment:

```powershell
tools/cad/.venv/Scripts/python.exe -B -m unittest discover -s designs/cameras/ov9281/shared -p test_*.py -v
```

Design-specific callers use the [isolated replay workflow](../../../../docs/organization-guide.md#replaying-pre-cleanup-builders).
A fresh `--current` workspace includes edits to these utilities and variant sources.
Historical replay keeps the archived utilities unchanged.
