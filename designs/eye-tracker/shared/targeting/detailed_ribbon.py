"""Construct a finite-thickness ribbon solid from the shared R08 top-surface map, with 0.25 mm thickness below."""
import numpy as np
import FreeCAD as A,Part,Mesh
import ribbon_geometry as g

def ribbon_solid(parameters,nx=8,ny=132):
 flat=np.array([[x,y,0.] for y in np.linspace(0,g.L,ny+1) for x in np.linspace(-g.W/2,g.W/2,nx+1)])
 vertices,_=g.evaluate(parameters,flat);eps=1e-5;dx=(g.evaluate(parameters,flat+[eps,0,0])[0]-g.evaluate(parameters,flat-[eps,0,0])[0])/(2*eps);dy=(g.evaluate(parameters,flat+[0,eps,0])[0]-g.evaluate(parameters,flat-[0,eps,0])[0])/(2*eps);normals=np.cross(dx,dy);normals/=np.linalg.norm(normals,axis=1)[:,None]
 metric={'max_length_error':float(max(abs(np.linalg.norm(dx,axis=1)-1).max(),abs(np.linalg.norm(dy,axis=1)-1).max())),'max_shear':float(abs((dx*dy).sum(1)).max())};faces=[]
 for j in range(ny):
  for i in range(nx):
   a=j*(nx+1)+i;b=a+1;c=a+nx+1;e=c+1;faces.extend([(a,b,e),(a,e,c)])
 count=len(vertices);vv=np.vstack([vertices,vertices-normals*.25]);ff=list(faces)+[tuple(i+count for i in f[::-1]) for f in faces];border=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
 for a,b in zip(border,border[1:]+border[:1]):ff.extend([(a,a+count,b+count),(a,b+count,b)])
 mesh=Mesh.Mesh([[A.Vector(*vv[i]) for i in f] for f in ff]);surface=Part.Shape();surface.makeShapeFromMesh(mesh.Topology,1e-7);solid=Part.makeSolid(surface)
 assert solid.isValid() and mesh.isSolid() and not mesh.hasSelfIntersections();assert max(metric.values())<1e-5
 return solid,mesh,metric
