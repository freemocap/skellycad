"""Create the named, five-part release assembly from the accepted R02 snapshot."""
from pathlib import Path
import json,csv
import FreeCAD as App
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/cad/toolchain.json').is_file())
OUT=ROOT/'releases/mouse-hats-r02';OUT.mkdir(parents=True,exist_ok=True)
PARTS=[('MH-001','Baseplate','BaseplateReference',(0.87,0.67,0.28)),
 ('MH-002','Carrier','Carrier',(0.23,0.72,0.82)),
 ('MH-003','Camera holder','Holder',(0.66,0.45,0.81)),
 ('MH-004','Sensor retaining clip','ClipReference',(0.85,0.40,0.35)),
 ('MH-005','PCB cap','CapReference',(0.40,0.70,0.46))]

def main():
    source=App.openDocument(str(ROOT/'generated/mouse-hats/print-test/r02/print-in-place-review.FCStd'))
    doc=App.newDocument('MouseHatsR02');doc.Label='MouseHats R02 - accepted print-test candidate'
    assembly=doc.addObject('App::Part','MouseHats_R02');assembly.Label='MouseHats_R02'
    rows=[]
    for ident,label,name,color in PARTS:
        obj=doc.addObject('Part::Feature',ident.replace('-','_'));obj.Label=ident+' '+label
        obj.Shape=source.getObject(name).Shape.Solids[0].copy();assembly.addObject(obj)
        obj.addProperty('App::PropertyString','PartNumber','Release');obj.PartNumber=ident
        obj.addProperty('App::PropertyString','Revision','Release');obj.Revision='R02'
        obj.Shape.check(True);assert obj.Shape.isValid() and len(obj.Shape.Solids)==1
        if App.GuiUp:
            obj.ViewObject.ShapeColor=color;obj.ViewObject.LineColor=(.12,.16,.19)
        rows.append({'part_number':ident,'name':label,'quantity':1,'revision':'R02','volume_mm3':obj.Shape.Volume,
          'area_mm2':obj.Shape.Area,'center_mm':list(obj.Shape.CenterOfMass),
          'bounds_mm':[getattr(obj.Shape.BoundBox,k) for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax']]})
    doc.recompute();doc.saveAs(str(OUT/'MouseHats_R02.FCStd'))
    (OUT/'parts-geometry.json').write_text(json.dumps(rows,indent=2)+'\n')
    with (OUT/'PARTS.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['part_number','name','quantity','revision','volume_mm3']);w.writeheader()
        for r in rows:w.writerow({k:r[k] for k in w.fieldnames})
    return doc

if __name__=='__main__':main()

