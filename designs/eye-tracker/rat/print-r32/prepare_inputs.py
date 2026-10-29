from pathlib import Path
import json,hashlib,shutil,numpy as np,trimesh
R=Path.cwd();S=R/'designs/eye-tracker/rat/print-r32';O=R/'generated/eye-tracker/rat/print-r32';OLD=R/'generated/eye-tracker/rat/print-r27';manifest=json.loads((S.parent/'print-r27/print-pack.json').read_text());audit=json.loads((OLD/'anatomy-validation.json').read_text());deriv=json.loads((OLD/'skull-derivative.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/'skull-print-world.stl')==audit['skull_source_sha256']
assert sha(OLD/'anatomy/RAT-R27-Snapmaker-U1.3mf')==manifest['files']['anatomy/RAT-R27-Snapmaker-U1.3mf']
assert sha(OLD/'LICENSE-source.txt')==manifest['files']['LICENSE-source.txt']
a=trimesh.load_mesh(O/'RatDesignSkull.stl');b=trimesh.load_mesh(OLD/'RatDesignSkull.stl');assert np.array_equal(a.faces,b.faces) and np.allclose(a.vertices,b.vertices,atol=1e-6)
assert sha(OLD/'RatDesignSkull.stl')==deriv['source_sha256']
shutil.copy2(OLD/'skull-print-world.stl',O/'skull-print-world.stl');shutil.copy2(OLD/'LICENSE-source.txt',O/'LICENSE-source.txt');shutil.copy2(OLD/'skull-derivative.json',O/'skull-derivative.json')
report={'units':'mm','anatomy_source':'Existing R27 printable skull derivative retained without remeshing','skull_derivative_sha256':sha(O/'skull-print-world.stl'),'r32_skull_matches_r27_geometry':True,'u1_template':'generated/eye-tracker/rat/print-r27/anatomy/RAT-R27-Snapmaker-U1.3mf','u1_template_sha256':sha(OLD/'anatomy/RAT-R27-Snapmaker-U1.3mf'),'baseplate_world_shift_from_R27_mm':[0,0,-2],'source_checkpoint':json.loads((S.parent/'compact-binocular-r32/review.json').read_text())}
(S/'lineage.json').write_text(json.dumps(report,indent=2));print('EXISTING_PRINT_INPUTS_VERIFIED')
s=(S.parent/'print-r27/build_anatomy.py').read_text().replace('print-r27','print-r32').replace('RAT-R27','RAT-R32').replace('RAT R27','RAT R32').replace('ET-RAT-ALIGNED-TIP-R27','ET-RAT-COMPACT-BINOCULAR-R32')
s=s.replace("template=ROOT/'designs/mouse-hats/skull-print/inputs/orca-source-project.3mf'", "template=ROOT/'generated/eye-tracker/rat/print-r27/anatomy/RAT-R27-Snapmaker-U1.3mf'")
s=s.replace("settings['filament_colour']=['#FF0000','#202020','#FFFFFF','#FFFF00']", "assert settings['filament_colour']==['#FF0000','#202020','#FFFFFF','#FFFF00']")
(S/'build_anatomy.py').write_text(s)
