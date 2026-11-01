"""Compare saved geometry numerically; rendering may add BREP triangulation."""
from pathlib import Path
import FreeCAD as App
import Part,json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'generated/ov9281-r11-mechanics';PATH=OUT/'OV9281-R11-MATCHED.FCStd'
def measurements(doc):
    result={}
    for o in doc.Objects:
        if o.TypeId=='Part::Feature' and not o.Shape.isNull():
            # Display tessellation can slightly shrink a mesh-derived cylinder
            # bound. Compare exact geometry, independent of viewport meshing.
            s=o.Shape;b=s.optimalBoundingBox(False,False)
            result[o.Name]={'volume':round(s.Volume,8),'area':round(s.Area,8),'bounds':[round(x,8) for x in [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]],'counts':[len(s.Solids),len(s.Faces),len(s.Edges)],'global_matrix':[round(x,10) for x in o.getGlobalPlacement().toMatrix().A]}
    return result
def main():
    doc=App.openDocument(str(PATH));actual=measurements(doc)
    expected=json.loads((OUT/'geometry-measurements.json').read_text());assert actual==expected,'Saved geometry differs from measured pre-render geometry'
    with zipfile.ZipFile(PATH) as z:assert z.testzip() is None
    App.closeDocument(doc.Name);p=OUT/'validation.json';r=json.loads(p.read_text());r['native_sha256']=hashlib.sha256(PATH.read_bytes()).hexdigest();r['rendered_geometry_measurements_unchanged']=True;r['geometry_measurements_count']=len(actual);p.write_text(json.dumps(r,indent=2)+'\n');print('Saved geometry verified:',len(actual),'features')
if __name__=='__main__':main()
