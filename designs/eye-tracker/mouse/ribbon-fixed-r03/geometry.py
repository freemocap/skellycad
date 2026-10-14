"""Piecewise cylindrical bend zones in an unstretched 32.85 x 4 mm sheet."""
import numpy as np
from scipy.spatial.transform import Rotation
L=32.85
W=4.
BASE=np.array([5.53706399647303,12.78,16.5])
FRAME=np.array([[0,0,1],[1,0,0],[0,1,0.]])

def zones(p):
 end=.15;out=[]
 for r,t,a,g in np.asarray(p).reshape(-1,4):
  axis=np.array([np.cos(a),np.sin(a),0]);n=np.array([-np.sin(a),np.cos(a),0])
  span=r*abs(t);yc=end+g+2*abs(np.tan(a));c=np.array([0,yc,0])
  rot=Rotation.from_rotvec(axis*t).as_matrix()
  shift=c+n*r*np.sin(abs(t))+np.array([0,0,np.sign(t)*r*(1-np.cos(t))])-rot@(c+n*span)
  end=yc+span/np.cos(a)+2*abs(np.tan(a))
  out.append((r,t,c,n,axis,span,rot,shift,end))
 return out

def evaluate(p,points):
 pts=np.asarray(points);result=np.zeros_like(pts);remaining=np.ones(len(pts),bool);R=np.eye(3);T=np.zeros(3)
 for r,t,c,n,a,span,rot,shift,end in zones(p):
  d=(pts-c)@n;before=remaining&(d<=0);result[before]=pts[before]@R.T+T
  bend=remaining&(d>0)&(d<span);dd=d[bend];q=(pts[bend]-c)@a;ang=dd/r
  mapped=c+q[:,None]*a+(r*np.sin(ang))[:,None]*n+(np.sign(t)*r*(1-np.cos(ang)))[:,None]*np.array([0,0,1])
  result[bend]=mapped@R.T+T;remaining&=d>=span;T=R@shift+T;R=R@rot
 result[remaining]=pts[remaining]@R.T+T
 return result@FRAME.T+BASE,FRAME@R

def endpoint(p):return evaluate(p,np.array([[0,L,0.]]))
