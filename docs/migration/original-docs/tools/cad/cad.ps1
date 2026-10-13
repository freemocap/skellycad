param(
    [Parameter(Position=0)]
    [ValidateSet('doctor','inspect','smoke','start-freecad','mcp','test-mcp','stop-freecad','show-freecad')]
    [string]$Task = 'doctor',
    [string]$BlenderPath,
    [string]$MeshPath
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$spec = Get-Content (Join-Path $PSScriptRoot 'toolchain.json') -Raw | ConvertFrom-Json
$localTools = Join-Path $repo '.cad-tools'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$fcBin = Join-Path $localTools (([IO.Path]::GetFileNameWithoutExtension($spec.freecad.archive)) + '/bin')
if (!$BlenderPath) { $BlenderPath = if ($env:CAD_BLENDER) { $env:CAD_BLENDER } else { $spec.blender.default_windows_path } }
$env:CAD_PLAYGROUND_ROOT = $repo
$env:MPLCONFIGDIR = Join-Path $localTools 'matplotlib'
switch ($Task) {
    'doctor' {
        if (!(Test-Path $python)) { throw 'Run tools/cad/bootstrap.ps1 first' }
        & $python -c 'import sys, trimesh, scipy, matplotlib, freecad_mcp; print("CAD Python:",sys.version); print("trimesh:",trimesh.__version__)'
        if ($LASTEXITCODE -ne 0) { throw 'CAD Python import check failed' }
        & (Join-Path $fcBin 'python.exe') -c 'import FreeCAD, Part; print("FreeCAD:",FreeCAD.Version()); assert Part.makeBox(1,2,3).Volume == 6'
        if ($LASTEXITCODE -ne 0) { throw 'FreeCAD import check failed' }
        if (!(Test-Path $BlenderPath)) { throw 'Set CAD_BLENDER to the installed blender.exe path' }
        $blenderVersion = & $BlenderPath --version
        Write-Output $blenderVersion[0]
        if ($blenderVersion[0] -ne ('Blender ' + $spec.blender.tested_version)) { Write-Warning 'Blender differs from the tested toolchain version' }
    }
    'inspect' {
        if (!$MeshPath) { throw 'Provide -MeshPath with an explicit STL path' }
        & $python (Join-Path $PSScriptRoot 'inspect_mesh.py') $MeshPath
    }
    'smoke' { & (Join-Path $fcBin 'python.exe') (Join-Path $PSScriptRoot 'smoke.py') }
    'start-freecad' {
        $profile = Join-Path $localTools 'freecad-profile'
        New-Item -ItemType Directory -Force $profile | Out-Null
        # Refuse duplicate listeners instead of silently controlling another instance.
        & $python -c 'import socket; s=socket.socket(); s.settimeout(1); busy=s.connect_ex(("127.0.0.1",9875))==0; s.close(); raise SystemExit(1 if busy else 0)'
        if ($LASTEXITCODE -ne 0) { throw 'Port 9875 is already in use. Run test-mcp or stop the existing project instance.' }
        $env:FREECAD_USER_HOME = $profile
        $arguments = @('-u', ('"' + (Join-Path $PSScriptRoot 'freecad_runtime.py') + '"'))
        $process = Start-Process (Join-Path $fcBin 'python.exe') -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $profile 'runtime-stdout.log') -RedirectStandardError (Join-Path $profile 'runtime-stderr.log')
        $deadline = (Get-Date).AddSeconds(30)
        do {
            Start-Sleep -Milliseconds 500
            $process.Refresh()
            if ($process.HasExited) { throw ('FreeCAD exited. See ' + (Join-Path $profile 'runtime-stderr.log')) }
            $ready = (Test-Path (Join-Path $profile 'runtime-stdout.log')) -and ((Get-Content (Join-Path $profile 'runtime-stdout.log') -Raw) -match 'CAD_GUI_READY')
        } until ($ready -or (Get-Date) -gt $deadline)
        if (!$ready) { throw 'FreeCAD did not report readiness in 30 seconds; inspect runtime logs before retrying' }
        Write-Output "Project FreeCAD ready, PID $($process.Id). Run test-mcp to check the protocol."
        return
    }
    'mcp' { & (Join-Path $PSScriptRoot '.venv/Scripts/freecad-mcp.exe') --host 127.0.0.1 --freecadcmd ('"' + (Join-Path $fcBin 'freecadcmd.exe') + '"') }
    'test-mcp' { & $python (Join-Path $PSScriptRoot 'test_mcp.py') }
    'stop-freecad' { & $python (Join-Path $PSScriptRoot 'runtime_control.py') stop }
    'show-freecad' { & $python (Join-Path $PSScriptRoot 'runtime_control.py') show }
}
if ($LASTEXITCODE -ne 0) { throw "CAD command '$Task' failed ($LASTEXITCODE)" }
