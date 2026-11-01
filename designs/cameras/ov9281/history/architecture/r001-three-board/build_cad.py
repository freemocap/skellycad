"""Build, save, reload, verify and render matched A01 envelope assemblies.

Run using the repository's pinned FreeCAD Python. Never modifies R11.
"""
from pathlib import Path
import json, hashlib, zipfile, traceback, sys, os
import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore, QtWidgets

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3];OUT=ROOT/'generated/three-board-a01'
D=json.loads((HERE/'placement.json').read_text());V=App.Vector
Gui.showMainWindow();Gui.getMainWindow().hide()
app=QtWidgets.QApplication.instance();app.setQuitOnLastWindowClosed(False)
exit_code=1

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(option):
    doc=App.newDocument('ThreeBoard_'+option);doc.Label='A01 | three-board placement | '+option+' backing'
    native=OUT/('THREE-BOARD-A01'+('' if option=='FR4' else '-STEEL')+'.FCStd')
    doc.saveAs(str(native))
    head=doc.addObject('App::Part','HeadAssembly');head.Label='HEAD-MOUNTED ASSEMBLY | target <1 g'
    base=doc.addObject('App::Part','BaseStation');base.Label='BASE STATION | enclosure or backpack'
    groups={};shapes=[];bodies=[]
    def add(group,name,shape,color,label=None,evidence='Architecture envelope; not production geometry'):
        obj=doc.addObject('Part::Feature',name);obj.Label=label or name;obj.Shape=shape;group.addObject(obj)
        obj.addProperty('App::PropertyString','Evidence','Study').Evidence=evidence
        obj.ViewObject.ShapeColor=color;obj.ViewObject.LineColor=(.18,.22,.28)
        assert shape.isValid() and not shape.isNull(),name
        shapes.append(obj);return obj
    def box(group,name,x,y,z,w,h,t,color,label=None):return add(group,name,Part.makeBox(w,h,t,V(x,y,z)),color,label)
    for name,b in D['boards'].items():
        g=doc.addObject('App::Part',name.capitalize());g.Label=name.upper();(base if name=='base' else head).addObject(g);groups[name]=g
        x,y=b['origin'];w,h=b['size'];t=b['thickness']
        box(g,name+'_substrate',x,y,0,w,h,t,(.72,.49,.12) if name!='base' else (.16,.40,.32),f'{name} {w} x {h} x {t} mm finished envelope')
        if name!='base':
            s=D['supports'][option];a=s['adhesive'];st=s['thickness']
            box(g,name+'_adhesive',x,y,-a,w,h,a,(.80,.75,.61))
            box(g,name+'_backing',x,y,-a-st,w,h,st,(.66,.69,.71) if option=='steel' else (.47,.53,.48),f'{option} backing {st} mm')
    box(head,'LocalFlex',14,2.25,(.303-.166)/2,25,5.5,.166,(.83,.62,.20),'LOCAL FLEX | 25 x 5.5 x 0.166 mm; no routed copper')
    colors={'sensor':(.13,.50,.49),'LED':(.82,.21,.28),'serializer':(.15,.23,.32),'processor':(.15,.23,.32),'connector':(.83,.81,.71)}
    for p in D['parts']:
        b=D['boards'][p['board']];x,y=p['center'];w,h,t=p['body'];ox,oy=b['origin']
        shape=Part.makeBox(w,h,t,V(ox+x-w/2,oy+y-h/2,b['thickness']))
        ob=add(groups[p['board']],p['ref'],shape,colors.get(p['kind'],(.30,.34,.39)),p['ref']+' | '+(p['mpn'] or p['kind']+' reserve'),p['evidence'])
        ob.addProperty('App::PropertyString','Side','Study').Side='Front'
        bodies.append(ob)
    # Ring leaves sensor and its image path clear. No proprietary lens geometry.
    ring=Part.makeBox(8,8,1.4,V(3,1,.303)).cut(Part.makeBox(6,6,1.4,V(4,2,.303)))
    add(groups['head'],'LensHolderReservation',ring,(.20,.20,.24),'OPTICS RESERVE | 8 x 8 holder, unqualified')
    filter_obj=add(groups['head'],'IRFilterReservation',Part.makeCylinder(2.6,.2,V(7,5,1.203)),(.25,.50,.68),'IR PASS FILTER RESERVE | spectrum unqualified')
    filter_obj.ViewObject.Transparency=55
    barrel=Part.makeCylinder(3,2.5,V(7,5,1.703)).cut(Part.makeCylinder(2.55,2.5,V(7,5,1.703)))
    add(groups['head'],'LensBarrelReservation',barrel,(.21,.21,.25),'THREADED LENS ENVELOPE | thread/focus not modeled')
    lens=add(groups['head'],'LensGlassReservation',Part.makeCylinder(2.5,.15,V(7,5,4.053)),(.22,.46,.62))
    lens.ViewObject.Transparency=35
    # Nonphysical schematic tether is a wire, not included in assembly mass/STEP.
    link=doc.addObject('Part::Feature','TetherDiagram');link.Label='TETHER SCHEMATIC | 0.30 / 0.60 m, NOT TO SCALE'
    link.Shape=Part.makePolygon([V(57,5,.5),V(66,5,.5),V(77,5,.5)]);link.ViewObject.LineColor=(.25,.46,.68);link.ViewObject.LineWidth=3
    status=doc.addObject('App::FeaturePython','StudyStatus');status.Label='READ FIRST | architecture only; no fabrication or physical fit'
    for key,val in [('Revision','THREE-BOARD-A01'),('PlacementSHA256',sha(HERE/'placement.json')),('Mass','Nominal 0.871 g FR4 / 0.929 g steel; estimated, high scenarios >1 g'),('Status','Body envelopes only; passive allocations unqualified; no routed copper or electrical connectivity'),('Optics','No qualified close-focus IR lens; datum and retention provisional')]:
        status.addProperty('App::PropertyString',key,'Evidence');setattr(status,key,val)
    doc.recompute()
    collisions=[]
    for i,a in enumerate(shapes):
        for b in shapes[i+1:]:
            if a.Shape.BoundBox.intersect(b.Shape.BoundBox):
                vol=a.Shape.common(b.Shape).Volume
                if vol>1e-7:collisions.append([a.Name,b.Name,vol])
    assert not collisions,collisions
    expected={o.Name:round(o.Shape.Volume,8) for o in shapes}
    doc.recompute();doc.save()
    App.closeDocument(doc.Name)
    with zipfile.ZipFile(native) as z:assert 'Document.xml' in z.namelist() and z.testzip() is None
    doc=App.openDocument(str(native))
    assert all(round(doc.getObject(k).Shape.Volume,8)==v for k,v in expected.items())
    view=Gui.activeDocument().activeView()
    Gui.getMainWindow().resize(1600,900)
    Gui.activateWorkbench('PartWorkbench');Gui.updateGui()
    def camera(center,rotation,height,aspect):
        rot=App.Rotation(*rotation);pos=V(*center)+rot.multVec(V(0,0,160));axis=rot.Axis
        view.setCamera('#Inventor V2.1 ascii\nOrthographicCamera { position %s %s %s orientation %s %s %s %s nearDistance 0.1 farDistance 1000 focalDistance 160 aspectRatio %s height %s }' % (pos.x,pos.y,pos.z,axis.x,axis.y,axis.z,rot.Angle,aspect,height))
        Gui.updateGui()
    camera((58.5,15,0),(.2798481423,.3647051996,.1159168959,.8804762392),80,2)
    view.saveImage(str(OUT/('assembly-'+option+'.png')),1800,900,'White')
    doc.getObject('BaseStation').Visibility=False;doc.getObject('TetherDiagram').Visibility=False
    camera((28.5,5,0),(0.0,0.0,0.0,1.0),24,1800/650);view.saveImage(str(OUT/('head-top-'+option+'.png')),1800,650,'White')
    camera((28.5,5,0),(1.0,0.0,0.0,0.0),24,1800/650);view.saveImage(str(OUT/('head-bottom-'+option+'.png')),1800,650,'White')
    # STEP includes only main physical reserve assembly; no diagram wire.
    Part.export([doc.getObject(k) for k in expected],str(OUT/('THREE-BOARD-A01-'+option+'.step')))
    doc.getObject('BaseStation').Visibility=True;doc.getObject('TetherDiagram').Visibility=True
    camera((58.5,15,0),(.2798481423,.3647051996,.1159168959,.8804762392),80,2);doc.recompute();doc.save();App.closeDocument(doc.Name)
    with zipfile.ZipFile(native) as z:assert z.testzip() is None
    return dict(option=option,native=native.name,sha256=sha(native),solid_count=len(expected),body_count=len(bodies),
        intersections=collisions,saved_reloaded_volume_check=True,zip_integrity=True,task_document_closed=True,
        placement_sha256=sha(HERE/'placement.json'),physical_fit_verified=False,routing_verified=False)

def main():
    global exit_code
    try:
        report={'status':'pass','scope':'Solid validity, volume intersections, saved-file reload and matching placement source only','variants':[build('FR4'),build('steel')]}
        (OUT/'cad-validation.json').write_text(json.dumps(report,indent=2)+'\n')
        exit_code=0
        if (OUT/'cad-error.txt').exists():(OUT/'cad-error.txt').unlink()
    except Exception:
        (OUT/'cad-error.txt').write_text(traceback.format_exc())
    finally:
        # All documents have been saved and closed before success. FreeCAD's
        # embedded Qt runtime can hang in Python interpreter finalization.
        os._exit(exit_code)

QtCore.QTimer.singleShot(0,main)
app.exec()
sys.exit(exit_code)
