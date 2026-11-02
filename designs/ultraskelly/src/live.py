"""Run an UltraSkelly builder inside the live project FreeCAD window.

Start that window first with `tools/cad/cad.ps1 start-freecad` and `show-freecad`.
From the repository root:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/live.py mockup --run r001

The builder module is reloaded on every call, so edits take effect without restarting FreeCAD.
"""
import argparse
import sys
import xmlrpc.client
from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'cad'))
from check_runtime import check  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('builder', help='module name in designs/ultraskelly/src, for example mockup')
    parser.add_argument('--timeout', type=float, default=900)
    args, rest = parser.parse_known_args()
    check()  # the endpoint must belong to this repository's FreeCAD runtime
    code = (f"import sys, importlib\n"
            f"sys.path.insert(0, {str(SRC)!r}) if {str(SRC)!r} not in sys.path else None\n"
            f"import cadkit, {args.builder}\n"
            f"importlib.reload(cadkit); importlib.reload({args.builder})\n"
            f"{args.builder}.main({rest!r})\n")
    server = xmlrpc.client.ServerProxy('http://127.0.0.1:9875', allow_none=True)
    result = server.execute_code(code, args.timeout)
    print(result.get('message') if result.get('success') else result.get('error'))
    raise SystemExit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
