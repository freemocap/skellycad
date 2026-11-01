"""Finish a task-owned headless process after all useful documents are saved/closed.

The pinned Windows Qt/FreeCAD runtime can hang during DLL teardown after checks
finish. This function exits only its own process; never call it in desktop IPC.
"""
import os
import sys


def finish_isolated(code):
    sys.stdout.flush()
    sys.stderr.flush()
    if os.name == 'nt':
        import ctypes
        kernel=ctypes.windll.kernel32
        kernel.GetCurrentProcess.restype=ctypes.c_void_p
        kernel.TerminateProcess.argtypes=[ctypes.c_void_p,ctypes.c_uint]
        if not kernel.TerminateProcess(kernel.GetCurrentProcess(),code):
            raise ctypes.WinError()
    else:
        os._exit(code)
