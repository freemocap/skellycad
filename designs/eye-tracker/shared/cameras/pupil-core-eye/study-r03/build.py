from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'study-r02'))
import camera_measured

def build():
 selection=json.loads((HERE/'connector-selection.json').read_text())
 return camera_measured.build(camera_measured.base.ROOT/'generated/eye-tracker/shared/camera-study-r03','r03',selection)
if __name__=='__main__':build()
