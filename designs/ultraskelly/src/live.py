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
    # Paths are compared normalised: a module imported through 'C:/...' would otherwise never match 'C:\\...'
    # and would silently keep running stale code.
    code = (f"import sys, importlib, os\n"
            f"_norm = lambda path: os.path.normcase(os.path.normpath(path))\n"
            f"sys.path.insert(0, {str(SRC)!r}) if {str(SRC)!r} not in sys.path else None\n"
            f"for _n, _m in [(n, m) for n, m in list(sys.modules.items())\n"
            f"               if getattr(m, '__file__', None) and _norm(os.path.dirname(m.__file__)) == _norm({str(SRC)!r})]:\n"
            f"    if os.path.exists(_m.__file__):\n"
            f"        importlib.reload(_m)  # pick up edits to every UltraSkelly source module\n"
            f"    else:\n"
            f"        del sys.modules[_n]  # its source file was removed\n"
            f"import {args.builder}\n"
            f"{args.builder}.main({rest!r})\n")
    server = xmlrpc.client.ServerProxy('http://127.0.0.1:9875', allow_none=True)
    result = server.execute_code(code, args.timeout)
    print(result.get('message') if result.get('success') else result.get('error'))
    raise SystemExit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
