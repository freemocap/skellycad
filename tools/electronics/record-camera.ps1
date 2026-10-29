<# Windows camera bring-up using existing FFmpeg. [@ffmpegDshow]
Enumerate first; select the explicit camera name and an advertised mode.
No default webcam is opened. SelfTest records only a synthetic test pattern.
FFV1 preserves decoded frames; it cannot restore information lost in camera MJPEG.
#>
[CmdletBinding()]
param(
    [ValidateSet('List','Modes','Record','SelfTest')][string]$Action = 'List',
    [string]$Device,
    [ValidatePattern('^\d+x\d+$')][string]$Size = '400x400',
    [ValidateRange(1,480)][int]$Fps = 120,
    [ValidateRange(1,3600)][int]$Seconds = 10,
    [string]$Output,
    [string]$Ffmpeg = 'ffmpeg'
)
$ErrorActionPreference = 'Stop'
$exe = (Get-Command $Ffmpeg -ErrorAction Stop).Source
if ($Action -eq 'List') {
    & $exe -hide_banner -list_devices true -f dshow -i dummy
    # FFmpeg deliberately exits nonzero after listing without an output.
    return
}
if ($Action -in @('Modes','Record') -and [string]::IsNullOrWhiteSpace($Device)) {
    throw 'Specify -Device using the exact video device name returned by -Action List.'
}
if ($Action -eq 'Modes') {
    & $exe -hide_banner -list_options true -f dshow -i "video=$Device"
    return
}
if ([string]::IsNullOrWhiteSpace($Output)) { throw 'Specify a new -Output path ending in .mkv.' }
if ([IO.Path]::GetExtension($Output) -ne '.mkv') { throw 'Use a .mkv output file.' }
if (Test-Path -LiteralPath $Output) { throw 'Output exists; choose a new path.' }
$outputPath = [IO.Path]::GetFullPath($Output)
if (-not (Test-Path -LiteralPath ([IO.Path]::GetDirectoryName($outputPath)))) {
    throw 'Create the output directory first.'
}
$ffArgs = @('-hide_banner','-nostdin','-n')
if ($Action -eq 'SelfTest') {
    $ffArgs += @('-f','lavfi','-i',"testsrc2=size=${Size}:rate=${Fps}")
} else {
    $ffArgs += @('-f','dshow','-rtbufsize','256M','-video_size',$Size,
        '-framerate',"$Fps",'-i',"video=$Device")
}
$ffArgs += @('-t',"$Seconds",'-an','-c:v','ffv1','-fps_mode','passthrough',$outputPath)
& $exe @ffArgs
if ($LASTEXITCODE -ne 0) { throw 'Capture failed. Any partial output is retained for inspection.' }
Write-Host "Saved $outputPath"
Write-Host 'Verify actual frame timing and negotiated mode; a requested FPS is not measured FPS.'
