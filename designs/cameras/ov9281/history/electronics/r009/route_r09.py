"""Local R09 routing experiments with explicit native KiCad import and refill.

Uses [@freerouting250]. Autorouting is connectivity work, not SI qualification.
"""
from pathlib import Path
import argparse, json, re, shutil, subprocess
import pcbnew as p
from extract_head import children
ROOT=Path(__file__).resolve().parents[2]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','import'])
    ap.add_argument('--directory',type=Path,required=True);a=ap.parse_args();out=a.directory.resolve()
    for name in ['head','controller']:
        path=out/(name+'.kicad_pcb')
        if a.action=='prepare':
            text=path.read_text()
            for x in list(children(text)):
                if re.match(r'\((segment|via)\s',x):text=text.replace(x,'',1)
            path.write_text(text)
            b=p.LoadBoard(str(path));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
            dsn=out/(name+'.dsn');assert p.ExportSpecctraDSN(b,str(dsn))
            # ExportSpecctraDSN does not load project netclass widths in this API.
            # Set the published experiment width explicitly in the DSN only.
            text=dsn.read_text()
            text=re.sub(r'\(width 150\)','(width 100)',text)
            text=text.replace('(clearance 150)','(clearance 100)')
            text=text.replace('450:200_um','400:200_um').replace('(circle F.Cu 450)','(circle F.Cu 400)').replace('(circle B.Cu 450)','(circle B.Cu 400)').replace('(circle In1.Cu 450)','(circle In1.Cu 400)').replace('(circle In2.Cu 450)','(circle In2.Cu 400)')
            # Allow layer 3 signal routing; refill the native power zone afterward.
            text=re.sub(r'^\s*\(plane \+3V3.*\n','',text,flags=re.M)
            dsn.write_text(text)
            pro=out/(name+'.kicad_pro');config=json.loads(pro.read_text())
            rules=config['board']['design_settings']['rules']
            rules.update(min_clearance=.1,min_track_width=.1,min_via_diameter=.4,min_hole_clearance=.2,min_hole_to_hole=.2)
            config['net_settings']['classes'][0].update(clearance=.1,track_width=.1,via_diameter=.4,via_drill=.2)
            pro.write_text(json.dumps(config,indent=2)+'\n')
        else:
            b=p.LoadBoard(str(path));assert p.ImportSpecctraSES(b,str(out/(name+'.ses')))
            b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
    if a.action=='prepare':
        record=json.loads((out/'revision.json').read_text())
        record['controller_existing_copper_retained_at_input']=False
        record['routing']='Both rigid boards rerouted; R08 preserved; power and ground zones retained.'
        record['routing_rule_basis']='0.10 mm tracks/clearance; 0.40/0.20 mm vias; 0.20 mm hole clearance. Published process capability basis, not manufacturer approval. [@jlcThinPcbCapabilities]'
        (out/'revision.json').write_text(json.dumps(record,indent=2)+'\n')

if __name__=='__main__':main()
