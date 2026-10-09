"""Exact per-object import tests with bounded temporary memory.
Spatial pruning is only a mathematically conservative ray candidate test. It
never hides/removes objects or changes the render scene.
"""
import bpy,math,numpy as np
from mathutils import Vector

def finite_and_bounds(meshes):
 lo=np.full(3,np.inf);hi=np.full(3,-np.inf);tested=0
 for ob in meshes:
  me=ob.data;a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);a=a.reshape(-1,3);assert np.isfinite(a).all(),ob.name
  ids=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',ids);a=a[np.unique(ids)].astype(np.float64);m=np.asarray(ob.matrix_world,dtype=np.float64);v=a@m[:3,:3].T+m[:3,3]
  if len(v):lo=np.minimum(lo,v.min(0));hi=np.maximum(hi,v.max(0));tested+=len(v)
 return [lo.tolist(),hi.tolist()],tested

class BoundedRays:
 def __init__(self,meshes):
  self.rows=[]
  for ob in meshes:
   world=ob.matrix_world.copy();v=np.array([tuple(world@Vector(c)) for c in ob.bound_box]);self.rows.append((ob,world,world.inverted(),v.min(0),v.max(0)))
 def hits(self,start,end):
  a=np.array(start,dtype=float);b=np.array(end,dtype=float);d=b-a;found=[]
  for ob,world,inv,lo,hi in self.rows:
   near,far=0.,1.;candidate=True
   for k in range(3):
    if abs(d[k])<1e-12:
     if a[k]<lo[k]-1e-5 or a[k]>hi[k]+1e-5:candidate=False;break
    else:
     t0,t1=(lo[k]-1e-5-a[k])/d[k],(hi[k]+1e-5-a[k])/d[k];near=max(near,min(t0,t1));far=min(far,max(t0,t1))
     if near>far:candidate=False;break
   if not candidate:continue
   origin=inv@Vector(start);finish=inv@Vector(end);direction=finish-origin;distance=direction.length
   if distance<1e-9:continue
   hit,pt,n,idx=ob.ray_cast(origin,direction.normalized(),distance=distance)
   if hit:found.append({'object':ob.name,'distance':float(((world@pt)-Vector(start)).length)})
  return sorted(found,key=lambda x:x['distance'])
