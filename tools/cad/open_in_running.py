"""Send files to FreeCAD's existing desktop IPC listener; never launch or close it.

Uses the native OpenFile protocol in GuiApplication.cpp / MainWindow.cpp.
Run outside the sandbox to reach the user's desktop. Optional expected PID
prevents delivery to a different instance. Accepts FCStd and FCMacro files.
"""
import argparse, ctypes, json
from ctypes import wintypes as W
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--expected-pid',type=int);p.add_argument('files',nargs='+');a=p.parse_args()
files=[Path(f).resolve(strict=True) for f in a.files]
assert all(f.suffix.lower() in ['.fcstd','.fcmacro'] for f in files)
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.CreateFileW.argtypes=[W.LPCWSTR,W.DWORD,W.DWORD,ctypes.c_void_p,W.DWORD,W.DWORD,W.HANDLE]
k.CreateFileW.restype=W.HANDLE
h=k.CreateFileW(r'\\.\pipe\FreeCAD',0xC0000000,0,None,3,0,None)
if h==W.HANDLE(-1).value:raise ctypes.WinError(ctypes.get_last_error())
try:
 pid=W.DWORD()
 if not k.GetNamedPipeServerProcessId(W.HANDLE(h),ctypes.byref(pid)):raise ctypes.WinError(ctypes.get_last_error())
 if a.expected_pid and pid.value!=a.expected_pid:raise RuntimeError(f'Expected desktop PID {a.expected_pid}; listener is {pid.value}')
 payload=''.join('OpenFile:'+f.as_posix()+'\n' for f in files).encode('utf-8')
 count=W.DWORD()
 if not k.WriteFile(W.HANDLE(h),payload,len(payload),ctypes.byref(count),None):raise ctypes.WinError(ctypes.get_last_error())
 assert count.value==len(payload)
 print(json.dumps({'existing_process_id':pid.value,'submitted_files':[str(f) for f in files]}))
finally:k.CloseHandle(W.HANDLE(h))
