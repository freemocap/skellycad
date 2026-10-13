"""Fill the vestigial notch in the PCB backing, preserving the lip snips."""
from pathlib import Path
import json,runpy
import FreeCAD as App

HERE=Path(__file__).resolve().parent
api=runpy.run_path(str(HERE/'build_mount.py'));api['load_modules']()
ROOT=api['ROOT'];OUT=ROOT/'generated/mouse-hats/model/tray-cleanup'

def main():
    doc=App.openDocument(str(ROOT/'generated/mouse-hats/model/lip-trim/trimmed-mount.FCStd'))
    data=json.loads((api['RECON']/'main_carrier/profiles.json').read_text())
    backing=next(f for f in data['features'] if f['name']=='TrayBacking')
    sketch=runpy.run_path(str(api['RECON']/'main_carrier/build.py'))['sketch']
    profiles=[]
    # Pinned measured outline: vertices 19 -> 0 -> 1 trace the recessed notch.
    # Closing that triangle restores the straight end edge between 19 and 1.
    for suffix,points in zip(('Rear','Front'),backing['profiles_mm']):
        profiles.append(sketch(doc,'NotchFill'+suffix,[points[i] for i in (19,0,1)]))
    fill=doc.addObject('Part::Loft','NotchFill')
    fill.Sections=profiles;fill.Solid=True;fill.Ruled=True
    result=doc.addObject('Part::Fuse','CleanedTrayAndMount')
    result.Label='PCB tray + stem — lip corners trimmed, end notch filled'
    result.Base=doc.TrimmedTrayAndMount;result.Tool=fill;result.Refine=True
    doc.recompute();result.Shape.check(True)
    assert len(result.Shape.Solids)==1
    removed=doc.TrimmedTrayAndMount.Shape.cut(result.Shape,0.001)
    if removed.Solids:removed.check(True)
    assert removed.Volume<1e-7
    cap=App.openDocument(str(ROOT/'generated/mouse-hats/reconstruction/pcb-cap/01-pcb-cap-candidate.FCStd'))
    overlap=result.Shape.common(cap.PCBCap.Shape,0.001)
    if overlap.Solids:overlap.check(True)
    assert overlap.Volume<1e-7
    report=dict(added_volume_mm3=result.Shape.Volume-doc.TrimmedTrayAndMount.Shape.Volume,
                removed_volume_mm3=removed.Volume,cap_overlap_mm3=overlap.Volume,
                valid_solids=len(result.Shape.Solids),comparison_tolerance_mm=0.001)
    OUT.mkdir(parents=True,exist_ok=True)
    doc.Label='SOURCE — PCB tray + stem — trimmed lip and straight end'
    doc.saveAs(str(OUT/'cleaned-tray.FCStd'))
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report)
    return doc

if __name__=='__main__':main()
