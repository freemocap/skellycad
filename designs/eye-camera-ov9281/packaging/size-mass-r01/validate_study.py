"""Check study accounting, retained identities, geometry reports and source integrity."""
from pathlib import Path
import hashlib,json,math,zipfile,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def read(name):return json.loads((HERE/name).read_text(encoding='utf-8'))
def main():
    baseline=read('component-budget.json');expected={(r['board'],r['reference']) for r in baseline if r['high_g']>0};assert len(expected)==106
    options=read('options.json')['variants'];packing=read('packing.json')['variants'];geometry=read('geometry-validation.json');results=[]
    for v,p,g in zip(options,packing,geometry['candidates']):
        assert v['id']==p['id']==g['id'];ids={(q['board'],q['reference']) for q in p['parts']};target=expected if v['id']=='A' else expected-{('controller','J102')};assert ids==target and len(ids)==len(p['parts'])
        assert v['no_tether_in_total'] and p['module_mass_excludes_tether']
        assert not v['electrically_validated'] and not v['manufacturing_approved']
        mass=v['mass_g'];assert mass['total'][0]<=mass['total'][1]<=mass['total'][2]
        for i in range(3):
            assert math.isclose(sum(mass[k][i] for k in ['boards','components','optics','solder_adhesive_retention']),mass['total'][i],abs_tol=1e-9)
            assert math.isclose(sum(q['mass_g'][i] for q in v['parts']),mass['components'][i],abs_tol=1e-9)
        assert g['physical_reservation_overlap_count']==g['stiffener_component_overlap_count']==0 and g['holder_valid_solid']
        if v['id']!='A':assert math.isclose(mass['optics'][1],.085+.011+g['holder_mass_g_at_1_2_density'],abs_tol=1e-9)
        if v['id']=='C':assert math.isclose(g['stiffener_volume_mm3'],(100+64-6.5**2)*.15,abs_tol=1e-8)
        assert all(c['in_outline'] and c['courtyard_overlap_count']==0 for c in p['checks'])
        ET.parse(HERE/f'candidate-{v["id"]}.svg')
        results.append({'id':v['id'],'physical_reference_count':len(ids),'accounting_pass':True,'nominal_below_one_gram':mass['total'][1]<1})
    source=read('source-hashes.json')
    for path,digest in source.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    native=ROOT/geometry['native_path'];assert hashlib.sha256(native.read_bytes()).hexdigest()==geometry['native_sha256']
    with zipfile.ZipFile(native) as z:assert z.testzip() is None and 'Document.xml' in z.namelist()
    assert geometry['invalid_shapes']==[] and geometry['native_top_view_visually_reviewed']
    for name in ['comparison-top.png','compact-bottom.png']:
        image=native.parent/name;assert image.read_bytes().startswith(b'\x89PNG\r\n\x1a\n') and image.stat().st_size>10000
    report={'pass':True,'units':'g and mm','module_target_g':1,'external_tether_excluded':True,'candidate_checks':results,'preserved_source_count':len(source),'source_hashes_unchanged':True,'native_zip_verified':True,'native_sha256':geometry['native_sha256'],'not_hardware_validation':True}
    (HERE/'study-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
