$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$localTools = Join-Path $repo '.cad-tools'
$spec = Get-Content (Join-Path $PSScriptRoot 'toolchain.json') -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force $localTools | Out-Null
$env:UV_CACHE_DIR = Join-Path $localTools 'uv-cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $localTools 'python'
& uv sync --locked --project $PSScriptRoot
if ($LASTEXITCODE -ne 0) { throw 'CAD dependency installation failed' }
$archive = Join-Path $localTools $spec.freecad.archive
if (!(Test-Path -LiteralPath $archive)) {
    Invoke-WebRequest $spec.freecad.url -OutFile ($archive + '.partial')
    if ((Get-FileHash ($archive + '.partial') -Algorithm SHA256).Hash.ToLower() -ne $spec.freecad.sha256) { throw 'FreeCAD download checksum mismatch' }
    Move-Item -LiteralPath ($archive + '.partial') -Destination $archive
}
if ((Get-FileHash $archive -Algorithm SHA256).Hash.ToLower() -ne $spec.freecad.sha256) { throw 'FreeCAD archive checksum mismatch' }
$fcRoot = Join-Path $localTools ([IO.Path]::GetFileNameWithoutExtension($spec.freecad.archive))
$marker = Join-Path $fcRoot '.cad-extracted'
if (!(Test-Path -LiteralPath $marker) -or (Get-Content -LiteralPath $marker -Raw).Trim() -ne $spec.freecad.sha256) {
    & tar -xf $archive -C $localTools
    if ($LASTEXITCODE -ne 0) { throw 'FreeCAD extraction failed' }
    Set-Content -LiteralPath $marker -Value $spec.freecad.sha256
}
$addonRepo = Join-Path $localTools 'freecad-mcp'
if (!(Test-Path -LiteralPath $addonRepo)) {
    & git clone $spec.freecad_mcp.repository $addonRepo
    if ($LASTEXITCODE -ne 0) { throw 'MCP clone failed' }
}
$changes = & git -C $addonRepo status --porcelain
if ($LASTEXITCODE -ne 0 -or $changes) { throw 'MCP checkout is modified; preserve/review local edits before setup' }
& git -C $addonRepo checkout --detach $spec.freecad_mcp.revision
if ($LASTEXITCODE -ne 0) { throw 'MCP pinned checkout failed' }
& (Join-Path $PSScriptRoot 'cad.ps1') doctor
if ($LASTEXITCODE -ne 0) { throw 'CAD environment check failed' }
Write-Output 'CAD setup complete. Run tools/cad/cad.ps1 smoke, inspect, or start-freecad.'
