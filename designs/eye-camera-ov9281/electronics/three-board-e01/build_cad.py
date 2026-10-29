"""Build a matched complete assembly from E01 PCB footprint coordinates.

Package boxes use F.Fab XY and documented/estimated heights. Optics are provisional.
"""
from pathlib import Path
import json,hashlib,zipfile,traceback,os
import FreeCAD as App,FreeCADGui as Gui,Part
from PySide import QtCore,QtWidgets
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'generated/three-board-e01'
D=json.loads((HERE/'placement.json').read_text());M=json.loads((HERE/'mass-budget.json').read_text());V=App.Vector
Gui.showMainWindow();Gui.getMainWindow().hide();app=QtWidgets.QApplication.instance();app.setQuitOnLastWindowClosed(False)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def build():
    doc=App.newDocument('E01');doc.Label='E01 | connected electronics / unrouted placement'
    path=OUT/'THREE-BOARD-E01.FCStd';doc.saveAs(str(path));physical=[];bodies=[];groups={}
    assembly=doc.addObject('App::Part','CompleteAssembly');head=doc.addObject('App::Part','HeadMounted');base=doc.addObject('App::Part','BaseStation');assembly.addObject(head);assembly.addObject(base)
    def add(group,name,shape,color,label=None,body=False):
        assert shape.isValid(),name
        o=doc.addObject('Part::Feature',name);o.Label=label or name;o.Shape=shape;o.ViewObject.ShapeColor=color;group.addObject(o);physical.append(o)
        if body:bodies.append(o)
        return o
    def box(group,name,x,y,z,w,h,t,color,label=None,body=False):return add(group,name,Part.makeBox(w,h,t,V(x,-y-h,z)),color,label,body)
    for region,b in D['boards'].items():
        g=doc.addObject('App::Part',region.title());g.Label=region.upper()+' | '+str(b['size'][0])+' x '+str(b['size'][1])+' mm';(base if region=='base' else head).addObject(g);groups[region]=g
        x,y=b['origin'];w,h=b['size'];z=b['thickness']
        box(g,region+'_substrate',x,y,0,w,h,z,(.10,.30,.24) if region=='base' else (.78,.55,.16),region+' substrate | '+str(z)+' mm')
        if region!='base':
            box(g,region+'_adhesive',x,y,-.05,w,h,.05,(.78,.73,.59))
            box(g,region+'_stiffener',x,y,-.15,w,h,.1,(.41,.46,.41),'FR4 backing | 0.10 mm')
    hw,hh=D['boards']['head']['size'];ix,iy=D['boards']['interface']['origin'];span=D['flat_head_span_mm']
    box(head,'FreeFlex',hw,(hh-5.5)/2,(.303-.166)/2,25,5.5,.166,(.86,.63,.20),'FREE FLEX | 25 x 5.5 x 0.166 mm; not routed')
    for row in D['parts']:
        if not row['populated'] or row['body'][4]<=0 or row['mpn']=='PCB solder land':continue
        b=D['boards'][row['board']];ox,oy=b['origin'];x,y=row['center'];dx,dy,w,h,t=row['body'];ang=row['angle']
        s=Part.makeBox(w,h,t,V(dx-w/2,-dy-h/2,0));s.rotate(V(0,0,0),V(0,0,1),ang);s.translate(V(ox+x,-oy-y,b['thickness']+.025))
        color=(.18,.19,.20) if row['ref'][0] in 'UQ' else (.60,.49,.32) if row['ref'][0]=='C' else (.28,.31,.32)
        if row['ref'].startswith('J'):color=(.82,.81,.73)
        if row['ref'] in ['D201','D202']:color=(.62,.12,.16)
        if row['ref']=='U1':color=(.13,.35,.28)
        ob=add(groups[row['board']],row['ref'],s,color,row['ref']+' | '+row['mpn'],True)
        ob.addProperty('App::PropertyString','Evidence','E01').Evidence=D['body_evidence']
    for folder in ['head-interface','base']:
        padshapes=[];ox,oy=D['boards']['base']['origin'] if folder=='base' else [0,0]
        for pad in json.loads((OUT/folder/'cad-pads.json').read_text()):
            x,y=pad['xy'];w,h=pad['size'];z=.4 if folder=='base' else .303
            s=Part.makeBox(w,h,.018,V(-w/2,-h/2,0));s.rotate(V(0,0,0),V(0,0,1),pad['angle']);s.translate(V(ox+x,-oy-y,z));padshapes.append(s)
        add(base if folder=='base' else head,'Pads_'+folder.replace('-','_'),Part.makeCompound(padshapes),(.83,.69,.32),'ACTUAL PCB PAD LOCATIONS | rectangular display approximations')
    optics=doc.addObject('App::Part','OpticsReservation');head.addObject(optics);optics.Label='PROVISIONAL OPTICS | not a qualified lens'
    cx,cy=hw/2,hh/2;z=.303+.025
    ring=Part.makeBox(8,8,1.4,V(cx-4,-cy-4,z)).cut(Part.makeBox(6,6,1.4,V(cx-3,-cy-3,z)))
    add(optics,'HolderReserve',ring,(.21,.22,.24),'8 x 8 mm holder reservation',True)
    barrel=Part.makeCylinder(3,2.5,V(cx,-cy,z+1.4)).cut(Part.makeCylinder(2.55,2.5,V(cx,-cy,z+1.4)))
    add(optics,'BarrelReserve',barrel,(.16,.17,.18),'6 mm barrel envelope; focus/thread unqualified',True)
    glass=add(optics,'GlassReserve',Part.makeCylinder(2.5,.15,V(cx,-cy,z+3.75)),(.22,.45,.62));glass.ViewObject.Transparency=40
    status=doc.addObject('App::FeaturePython','ReadFirst');status.Label='READ FIRST | ELECTRICAL DRAFT; UNROUTED; MASS TARGET OPEN'
    for k,v in [('Revision','THREE-BOARD-E01'),('PlacementHash',sha(HERE/'placement.json')),('Status','196 schematic components; native footprints and pin nets; no routed traces'),('HeadMass',str(round(M['cases']['nominal']['head_complete_g'],3))+' g nominal estimate, excluding tether; target <1 g not met'),('BackpackMass',str(round(M['cases']['nominal']['base_complete_backpack_g'],3))+' g including enclosure/mount allocation; no battery'),('Scale','All geometry in mm. Free flex 25 mm; head flat span '+str(span)+' mm'),('Optics','8 x 8 holder / 6 mm barrel reserves; no verified lens or optical datum')]:status.addProperty('App::PropertyString',k,'Evidence');setattr(status,k,v)
    # Model-space ruler is annotation geometry, excluded from exported physical assembly.
    ruler=doc.addObject('Part::Feature','Scale10mm');ruler.Label='10 mm SCALE | 1 mm ticks'
    edges=[Part.makeLine(V(0,4,0),V(10,4,0))]+[Part.makeLine(V(i,4,0),V(i,4+(1 if i%5==0 else .5),0)) for i in range(11)]
    ruler.Shape=Part.makeCompound(edges);ruler.ViewObject.LineColor=(.15,.15,.15)
    collisions=[]
    for i,a in enumerate(bodies):
        for b in bodies[i+1:]:
            if a.Shape.BoundBox.intersect(b.Shape.BoundBox) and a.Shape.common(b.Shape).Volume>1e-7:collisions.append([a.Name,b.Name])
    assert not collisions,collisions
    doc.recompute();doc.save();expected={o.Name:round(o.Shape.Volume,7) for o in physical};App.closeDocument(doc.Name)
    with zipfile.ZipFile(path) as zf:assert 'Document.xml' in zf.namelist() and zf.testzip() is None
    doc=App.openDocument(str(path));assert all(round(doc.getObject(n).Shape.Volume,7)==v for n,v in expected.items())
    view=Gui.activeDocument().activeView();Gui.getMainWindow().resize(1600,900);Gui.activateWorkbench('PartWorkbench')
    def camera(center,quat,height,aspect):
        rot=App.Rotation(*quat);pos=V(*center)+rot.multVec(V(0,0,160));a=rot.Axis
        view.setCamera('#Inventor V2.1 ascii\nOrthographicCamera { position %s %s %s orientation %s %s %s %s nearDistance 0.1 farDistance 1000 focalDistance 160 aspectRatio %s height %s }'%(pos.x,pos.y,pos.z,a.x,a.y,a.z,rot.Angle,aspect,height));Gui.updateGui()
    bw,bh=D['boards']['base']['size'];bx,by=D['boards']['base']['origin'];center=((bx+bw)/2,-max(hh,bh)/2,0)
    camera(center,(0,0,0,1),65,2);view.saveImage(str(OUT/'assembly-top.png'),2000,1000,'White')
    camera(center,(.2798481423,.3647051996,.1159168959,.8804762392),80,2);view.saveImage(str(OUT/'assembly.png'),2000,1000,'White')
    doc.getObject('BaseStation').Visibility=False;camera((span/2,-hh/2,0),(0,0,0,1),27,2.8);view.saveImage(str(OUT/'head-top.png'),1960,700,'White')
    doc.getObject('HeadMounted').Visibility=False;doc.getObject('BaseStation').Visibility=True;camera((bx+bw/2,-bh/2,0),(0,0,0,1),bh+5,1.3);view.saveImage(str(OUT/'base-top.png'),1300,1000,'White')
    doc.getObject('HeadMounted').Visibility=True;camera(center,(.2798481423,.3647051996,.1159168959,.8804762392),80,2)
    doc.recompute();doc.save();Part.export([doc.getObject(n) for n in expected],str(OUT/'THREE-BOARD-E01.step'));App.closeDocument(doc.Name)
    with zipfile.ZipFile(path) as zf:assert zf.testzip() is None
    report={'status':'pass','native':path.name,'sha256':sha(path),'placement_sha256':sha(HERE/'placement.json'),'solid_objects':len(expected),'populated_package_objects':sum(x['populated'] and x['body'][4]>0 and x['mpn']!='PCB solder land' for x in D['parts']), 'body_intersections':collisions,'zip_integrity':True,'saved_reloaded_volumes_match':True,'task_documents_closed':True,'physical_fit_verified':False,'routing_verified':False}
    (OUT/'cad-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    if (OUT/'cad-error.txt').exists():(OUT/'cad-error.txt').unlink()
def main():
    code=1
    try:build();code=0
    except Exception:(OUT/'cad-error.txt').write_text(traceback.format_exc())
    finally:os._exit(code)
QtCore.QTimer.singleShot(0,main);app.exec()
