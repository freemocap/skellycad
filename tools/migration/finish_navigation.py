from pathlib import Path
import hashlib,json,re,os
ROOT=Path.cwd();OUT=ROOT/'docs/migration/repo-cleanup-2026-10-31'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
extra={}
base='designs/cameras/ov9281'
for family,name in [('architecture','three-board-r01'),('mechanics','optics-r01'),('packaging','selection-r01'),('packaging','size-mass-r01')]:
 stem,rev=name.rsplit('-r',1);extra[f'{base}/history/{family}/{name}']=f'{base}/history/{family}/r{int(rev):03d}-{stem}'
shared={'copper_retention.py','cross_section.py','interconnect_graph.py','routing_geometry.py','routing_spatial.py','system_analysis.py','test_cross_section.py','test_interconnect_graph.py','test_routing_spatial.py'}
for p in (ROOT/base).iterdir():
 if not p.is_file() or p.name in ['README.md','ROADMAP.md']:continue
 if p.name in shared:dest=f'{base}/shared/{p.name}'
 elif p.name in ['working-review.json','WORKING-REVIEW.md','STATUS.md']:dest=f'{base}/variants/slim-flex/history/r011-working-review/{p.name}'
 elif p.name=='controller-selection.json':dest=f'{base}/history/electronics/r008/{p.name}'
 else:
  match=re.search(r'r(\d\d)',p.name)
  revisions=[int(match[1])] if match else [int(n) for n in re.findall(r'(?:electronics/r|ov9281-r)(\d\d)',p.read_text(encoding='utf-8',errors='replace'))]
  rev=max(revisions) if revisions else None
  if rev==11:dest=f'{base}/variants/slim-flex/src/{p.name}'
  elif rev:dest=f'{base}/history/'+('mechanics' if 'mechanic' in p.name else 'electronics')+f'/r{rev:03d}/{p.name}'
  elif 'optics' in p.name or 'compact_review' in p.name:dest=f'{base}/history/mechanics/r001-optics/{p.name}'
  else:dest=f'{base}/history/tooling/{p.name}'
 extra[p.relative_to(ROOT).as_posix()]=dest
base='designs/cameras/og0tc'
for p in (ROOT/base).iterdir():
 if p.is_file() and p.name!='README.md':
  family='electronics' if 'electronics' in p.name else 'mechanical' if 'mechanical' in p.name else 'integration'
  rev=2 if 'r02' in p.name else 1
  extra[p.relative_to(ROOT).as_posix()]=f'{base}/history/{family}/r{rev:03d}/{p.name}'
base='designs/cameras/pupil-core-eye'
for name in ['pcb-envelope.brep','pupil-core-eye-camera.blend','pupil-core-eye-camera.jpg']:
 extra[f'{base}/{name}']=f'{base}/references/inherited-geometry/{name}'
extra=dict(sorted(extra.items(),key=lambda x:len(x[0]),reverse=True))
def relocate(s):
 for old,new in extra.items():
  if s==old or s.startswith(old+'/'):return new+s[len(old):]
 return s
files=[]
for old,new in extra.items():
 source=(ROOT/old).resolve();assert source.is_relative_to(ROOT) and source.exists(),old
 candidates=[source] if source.is_file() else [p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 for p in candidates:
  a=p.relative_to(ROOT).as_posix();b=relocate(a);q=(ROOT/b).resolve()
  assert q.is_relative_to(ROOT) and not q.exists(),b
  files.append({'old':a,'new':b,'sha256':sha(p)})
(OUT/'navigation-finish-map.json').write_text(json.dumps({'prefixes':extra,'files':files},indent=2))
for r in files:
 p=ROOT/r['old'];q=ROOT/r['new'];q.parent.mkdir(parents=True,exist_ok=True);p.rename(q);assert sha(q)==r['sha256']
# Extend the original map and resolve transitional identifiers as well.
for name in ['path-aliases.json']:
 p=OUT/name;d=json.loads(p.read_text());d={k:relocate(v) for k,v in d.items()};d.update(extra);d=dict(sorted(d.items(),key=lambda x:len(x[0]),reverse=True));p.write_text(json.dumps(d,indent=2))
p=OUT/'move-map.json';d=json.loads(p.read_text());d['prefixes']={k:relocate(v) for k,v in d['prefixes'].items()}
for r in d['files']:r['new']=relocate(r['new'])
p.write_text(json.dumps(d,indent=2))
for name,keys in [('moves-completed.json',['new']),('checkpoint-catalog.json',['checkpoint','manifest']),('retained-packages.json',['retained'])]:
 p=OUT/name;d=json.loads(p.read_text())
 for r in d:
  for k in keys:
   if k in r:r[k]=relocate(r[k])
 p.write_text(json.dumps(d,indent=2))
p=OUT/'original-navigation.json';d=json.loads(p.read_text());p.write_text(json.dumps({k:relocate(v) for k,v in d.items()},indent=2))
# Update relative links affected by this final placement, keeping frozen records intact.
inverse={r['new']:r['old'] for r in files};changes=[]
for p in ROOT.glob('designs/**/*.md'):
 if any(x in p.parts for x in ['checkpoints','references','managed_components','mouse-hats','cad-foundations','kicad-foundations']) or p.name=='overview-before-cleanup.md':continue
 rel=p.relative_to(ROOT).as_posix();old=ROOT/inverse.get(rel,rel)
 try:s=p.read_text(encoding='utf-8');encoding='utf-8'
 except UnicodeDecodeError:s=p.read_text(encoding='cp1252');encoding='cp1252'
 def link(m):
  target=m[1];ref,sep,anchor=target.partition('#')
  if not ref or re.match(r'^[a-z]+:',ref,re.I):return m[0]
  candidate=(old.parent/ref).resolve()
  if not candidate.is_relative_to(ROOT):return m[0]
  dest=ROOT/relocate(candidate.relative_to(ROOT).as_posix())
  if not dest.exists():return m[0]
  return ']('+os.path.relpath(dest,p.parent).replace('\\','/')+(sep+anchor if sep else '')+')'
 new=re.sub(r'\]\(([^)]+)\)',link,s)
 if new!=s or encoding!='utf-8':p.write_text(new,encoding='utf-8');changes.append(rel)
(OUT/'navigation-finish-links.json').write_text(json.dumps(changes,indent=2))
for old in extra:
 p=ROOT/old
 if p.is_dir():
  for sub in sorted(p.rglob('*'),key=lambda x:len(x.parts),reverse=True):
   if sub.is_dir() and not any(sub.iterdir()):sub.rmdir()
  if not any(p.iterdir()):p.rmdir()
print('Finished ownership of',len(files),'files; refreshed',len(changes),'documents')
