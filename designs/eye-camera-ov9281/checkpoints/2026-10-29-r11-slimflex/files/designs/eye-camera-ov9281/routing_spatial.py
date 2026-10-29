"""Exact nearest-point distances for routing heuristics, without extra packages."""
import math

class NearestPoints:
    def __init__(self,points):
        points=sorted(set(tuple(p) for p in points))
        if not points:raise ValueError('At least one destination is required')
        def build(rows,axis):
            if not rows:return None
            rows.sort(key=lambda p:p[axis]);middle=len(rows)//2
            return rows[middle],axis,build(rows[:middle],1-axis),build(rows[middle+1:],1-axis)
        self.root=build(points,0)

    def distance(self,x,y):
        point=(x,y);best=float('inf')
        def visit(node):
            nonlocal best
            if node is None:return
            q,axis,left,right=node;dx,dy=x-q[0],y-q[1];best=min(best,dx*dx+dy*dy)
            delta=point[axis]-q[axis];near,far=(left,right) if delta<0 else (right,left)
            visit(near)
            if delta*delta<best:visit(far)
        visit(self.root)
        return math.sqrt(best)
