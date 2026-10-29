# Record the first camera

Uses the existing Windows FFmpeg installation. The camera must expose a
DirectShow video device; use vendor software for proprietary SDK-only formats
[@ffmpegDshow]. From the repository root:

```powershell
./tools/electronics/record-camera.ps1 -Action List
./tools/electronics/record-camera.ps1 -Action Modes -Device 'EXACT CAMERA NAME'
```

Substitute the returned camera name. Choose an advertised resolution and frame
rate. Listing commands normally exit nonzero because no output is opened; inspect
their text for the list or a genuine access error. Do not infer USB modes from
the sensor frame-rate specification.

```powershell
New-Item -ItemType Directory -Force generated/camera-capture
./tools/electronics/record-camera.ps1 -Action Record -Device 'EXACT CAMERA NAME' -Size 400x400 -Fps 120 -Seconds 10 -Output generated/camera-capture/first-target.mkv
```

FFV1 preserves decoded frames, not information lost in upstream MJPEG encoding.
The script refuses overwrites, captures no audio, does not control illumination
and does not set exposure. Set exposure/gain with vendor controls and record
settings alongside the clip. Inspect actual resolution, frame count and timing:

```powershell
ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=codec_name,width,height,avg_frame_rate,nb_read_frames -of json generated/camera-capture/first-target.mkv
ffprobe -v error -select_streams v:0 -show_entries frame=best_effort_timestamp_time -of csv=p=0 generated/camera-capture/first-target.mkv
```

Requested FPS and metadata do not establish measured capture rate or absence of
drops. For a host-only smoke test use SelfTest instead of Record, omit Device,
and select a new output path. It generates a test pattern without opening a camera.
