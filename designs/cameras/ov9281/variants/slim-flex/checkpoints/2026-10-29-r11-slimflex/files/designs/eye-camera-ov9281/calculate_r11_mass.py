"""Complete-module screening mass; external tether is the sole excluded system part."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];SPEC=ROOT/'designs/eye-camera-ov9281/electronics/r11';PCB=ROOT/'generated/ov9281-r11-electronics';CAD=ROOT/'generated/ov9281-r11-mechanics'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    geo=json.loads((PCB/'native-geometry.json').read_text());mat=json.loads((SPEC/'material-geometry.json').read_text());cad=json.loads((CAD/'validation.json').read_text());parts=json.loads((SPEC/'components.json').read_text())['parts']
    assert geo['board_sha256']==mat['board_sha256']==cad['board_sha256']==sha(PCB/'camera.kicad_pcb');assert cad['native_sha256']==sha(CAD/'OV9281-R11-MATCHED.FCStd')
    areas={'controller':389.,'head':193.,'flex':32.85*8};thick={'F.Cu':.025,'B.Cu':.025,'In1.Cu':.018,'In2.Cu':.018,'In3.Cu':.018,'In4.Cu':.018};ledger=[];poly_volume=0;cu_volume=0
    def add(name,masses,basis,region='complete module'):
        assert 0<=masses[0]<=masses[1]<=masses[2];ledger.append({'name':name,'region':region,'low_g':masses[0],'nominal_g':masses[1],'high_g':masses[2],'basis':basis})
    for region,area in areas.items():
        cu=sum(v['area_mm2']*thick[k] for k,v in geo['copper'][region].items());cu_volume+=cu
        full_cu=area*(.036 if region=='flex' else .122)
        # Component dielectrics total .130. Neck PI plus coverlays also total
        # .130. Etched copper slots are conservatively treated as polymer fill.
        polymer=area*.13+full_cu-cu-mat['filled_via_volume_by_region_mm3'][region];poly_volume+=polymer
        add(region+' copper foils',[cu*.85*8.8/1000,cu*8.91/1000,cu*1.15*9.0/1000],'Native polygon union × layer thickness; copper thickness ±15% screening, density 8.8/8.91/9.0 g/cm3. Not a supplier tolerance.',region)
        add(region+' PI, adhesive and etched-slot fill',[polymer*.7*1.25/1000,polymer*1.42/1000,polymer*1.4*1.6/1000],'0.130 mm dielectric/coverlay sum plus etched-copper slots. Effective polymer density 1.25/1.42/1.60; volume factors 0.7/1/1.4 are screening assumptions, not certified material limits.',region)
    surfaces=mat['surfaces'];opening=sum(x['mask_opening_area_mm2'] for x in surfaces.values());mask_area=2*(areas['head']+areas['controller'])-opening
    finish_area=sum(x['exposed_pad_area_mm2'] for x in surfaces.values());paste_area=sum(x['paste_aperture_area_mm2'] for x in surfaces.values())
    add('Component-region solder mask',[mask_area*.015*1.1/1000,mask_area*.020*1.2/1000,mask_area*.030*1.5/1000],'Region area minus native mask openings; per-face thickness 15/20/30 um and density 1.1/1.2/1.5 g/cm3 assumed.')
    via=mat['filled_via_volume_between_foils_mm3'];add('Filled laser-via copper',[via*.5*8.8/1000,via*8.91/1000,via*1.5*9/1000],'Filled 70 um cylinders in dielectric gaps only; ±50% via-volume screening. Copper lands already counted.')
    add('Exposed-pad surface finish',[finish_area*.003*8/1000,finish_area*.006*9/1000,finish_area*.009*10/1000],'Effective finish thickness 3/6/9 um and density 8/9/10 g/cm3 assumed; actual finish stack and exposed via caps require fabrication data.')
    add('Reflowed solder',[paste_area*.08*.4*7.2/1000,paste_area*.10*.5*7.4/1000,paste_area*.12*.6*7.6/1000],'Native stencil apertures × 80/100/120 um stencil × 40/50/60% metal volume × 7.2/7.4/7.6 g/cm3. Stencil and solder alloy not selected; DNP aperture retained conservatively.')
    for ref,p in parts.items():
        if p['populated']:add(ref+' '+p['mpn'],p['mass_g'],p['mass_evidence'],p['region'])
    supports=cad['support_volumes_mm3'];fr=sum(v for k,v in supports.items() if k.endswith('FR4'));adh=sum(v for k,v in supports.items() if k.endswith('adhesive'))
    add('FR4 supports',[fr*1.7/1000,fr*1.8/1000,fr*1.9/1000],'Exact support volumes including capacitor windows and head ring; generic FR4 density range.')
    add('Support adhesive',[adh*.9/1000,adh*1.2/1000,adh*1.5/1000],'Exact 0.05 mm adhesive geometry; density is an engineering assumption.')
    optics=cad['optical_volumes_mm3'];h=optics['Holder'];f=optics['FilterEnvelope'];bond=optics['HolderBond']
    add('Compact optics holder',[h*1.05/1000,h*1.2/1000,h*1.4/1000],'Exact CAD volume; assumed solid lightweight polymer. No qualified material/process.')
    add('Lens including its barrel',[.04,.085,.15],'Inherited lightweight lens allowance; no qualified optical assembly or measured mass. This interval is not an exhaustive upper bound.')
    add('IR filter',[f*2.2/1000,f*2.5/1000,f*3.0/1000],'5.2 mm diameter × 0.2 mm envelope; glass-density screening only. Coating and spectral performance unqualified.')
    add('Holder bond and lens retention',[bond*.9/1000+.001,bond*1.2/1000+.003,bond*1.5/1000+.010],'Holder bond geometry plus 1/3/10 mg locking allowance; retention method provisional.')
    totals={k:sum(x[k] for x in ledger) for k in ['low_g','nominal_g','high_g']};assert totals['low_g']<totals['nominal_g']<totals['high_g']
    groups={'packages':sum(p['mass_g'][1] for p in parts.values() if p['populated']),'copper':sum(x['nominal_g'] for x in ledger if 'copper' in x['name']),'polymers_and_mask':sum(x['nominal_g'] for x in ledger if 'PI,' in x['name'] or 'solder mask' in x['name']),'solder_and_finish':sum(x['nominal_g'] for x in ledger if x['name'] in ['Reflowed solder','Exposed-pad surface finish']),'supports_and_optics':sum(x['nominal_g'] for x in ledger if x['name'] in ['FR4 supports','Support adhesive','Compact optics holder','Lens including its barrel','IR filter','Holder bond and lens retention'])}
    assert abs(sum(groups.values())-totals['nominal_g'])<1e-10
    report={'revision':'R11','target_g':1.,'external_tether_excluded':True,'included':'Controller, head, integrated flex, all populated packages, board connector, IR LEDs, copper, polymer, solder, finish, supports, adhesive, optics and retention','excluded':'External tether only; Pupil comparison and duplicate bent view are reference geometry, not additional parts','measured':False,'interval_is_statistical':False,'nominal_target_met':totals['nominal_g']<1.,'totals':totals,'nominal_groups_g':groups,'geometry':{'region_areas_mm2':areas,'copper_volume_mm3':cu_volume,'polymer_equivalent_volume_mm3':poly_volume,'mask_area_mm2':mask_area,'finish_area_mm2':finish_area,'paste_area_mm2':paste_area},'parts':ledger,'limitations':['Component masses are engineering intervals except the cited typical buck-inductor mass.','Density, solder, finish and polymer-volume scenarios are not fabrication tolerances or probabilistic bounds.','Optics remain unspecified; even the high scenario is not a guaranteed maximum.','Finished CAD board envelopes already contain copper and must not be added as extra material.','The complete module is not demonstrated under one gram; no physical mass measurement exists.'],'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [PCB/'camera.kicad_pcb',PCB/'native-geometry.json',SPEC/'components.json',SPEC/'material-geometry.json',CAD/'OV9281-R11-MATCHED.FCStd',CAD/'validation.json']}}
    (SPEC/'mass-budget.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'totals':totals,'nominal_groups_g':groups,'target_met':report['nominal_target_met']},indent=2))
if __name__=='__main__':main()
