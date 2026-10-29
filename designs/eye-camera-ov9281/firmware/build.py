"""Build the pinned firmware with the repository-local ESP-IDF installation.

No flashing, USB communication, or hardware changes. See README for setup.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IDF_COMMIT = '880a203ae603d08a94d06aa01e0d6761958e5e9e'
VIDEO_COMMIT = '789cde3bd09296a13d4e70afe011366b60ac772c'

def run_build(synthetic=False, output_root=None):
    idf = ROOT / '.cad-tools/esp-idf'
    video = ROOT / '.cad-tools/esp-video-components'
    actual = subprocess.check_output(['git', '-C', str(idf), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != IDF_COMMIT:
        raise RuntimeError('Expected the pinned ESP-IDF v5.5.6 checkout')
    assert subprocess.check_output(['git', '-C', str(video), 'rev-parse', 'HEAD'], text=True).strip() == VIDEO_COMMIT
    toolroot = ROOT / '.cad-tools/espressif'
    toolinfo = json.loads((idf / 'tools/tools.json').read_text())
    paths = []
    for name in ('riscv32-esp-elf', 'cmake', 'ninja'):
        tool = next(t for t in toolinfo['tools'] if t['name'] == name)
        version = next(v['name'] for v in tool['versions'] if v['status'] == 'recommended')
        for path in tool['export_paths']:
            directory = toolroot / 'tools' / name / version / Path(*path)
            assert directory.is_dir(), directory
            paths.append(str(directory))
    py = toolroot / 'python_env/idf5.5_py3.12_env/Scripts/python.exe'
    assert py.is_file(), py
    env = os.environ.copy()
    env.update(IDF_PATH=str(idf), IDF_TOOLS_PATH=str(toolroot),
               IDF_PYTHON_ENV_PATH=str(py.parent.parent), IDF_CCACHE_ENABLE='0',
               IDF_COMPONENT_CACHE_PATH=str(toolroot / 'component-cache'))
    env['PATH'] = os.pathsep.join([str(py.parent), *paths, env['PATH']])
    mode = 'synthetic' if synthetic else 'sensor'
    output = (Path(output_root).resolve() / mode) if output_root else ROOT / 'generated' / ('camera-firmware-' + mode)
    output.mkdir(parents=True, exist_ok=True)
    defaults = str(HERE / 'sdkconfig.defaults')
    if synthetic:
        defaults += ';' + str(HERE / 'sdkconfig.synthetic')
    cmd = [str(py), str(idf / 'tools/idf.py'), '-C', str(HERE), '-B', str(output / 'build'),
           '-D', 'SDKCONFIG=' + str(output / 'sdkconfig'), '-D', 'SDKCONFIG_DEFAULTS=' + defaults,
           '-D', 'IDF_TARGET=esp32p4', 'reconfigure', 'build']
    with (output / 'build.log').open('w', encoding='utf-8') as log:
        result = subprocess.run(cmd, env=env, stdout=log, stderr=subprocess.STDOUT)
    print((output / 'build.log').read_text(encoding='utf-8', errors='replace')[-8500:])
    if result.returncode:
        raise SystemExit(result.returncode)
    binaries = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (output / 'build').glob('*.bin')}
    source_files=[HERE/'main/camera_main.c', HERE/'main/Kconfig.projbuild', HERE/'sdkconfig.defaults', HERE/'main/idf_component.yml', HERE/'board-contract.json', HERE/'build.py']
    if synthetic:source_files.append(HERE/'sdkconfig.synthetic')
    report = {'mode': mode, 'board_revision': 'R11', 'idf_commit': actual, 'video_commit': VIDEO_COMMIT,
              'binary_sha256': binaries, 'compiled': True, 'executed_on_hardware': False,
              'source_sha256': {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in source_files}}
    (output / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(output / 'build-report.json')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--synthetic', action='store_true');ap.add_argument('--output-root',type=Path)
    args=ap.parse_args();run_build(args.synthetic,args.output_root)
