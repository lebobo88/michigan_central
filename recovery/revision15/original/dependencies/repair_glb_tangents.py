"""Repair zero export tangents from incident triangle UV derivatives.
Does not alter positions, normals, UVs, topology, materials, or nonzero tangents.
A recorded orthogonal fallback is used only if no valid incident UV derivative exists.
"""
from pathlib import Path
import json,struct,hashlib
import numpy as np

def repair_glb_tangents(path,report_path=None):
 path=Path(path);data=bytearray(path.read_bytes());before=hashlib.sha256(data).hexdigest();offset=12;doc=None;binstart=None
 while offset<len(data):
  size,kind=struct.unpack_from('<II',data,offset)
  if kind==0x4e4f534a:doc=json.loads(data[offset+8:offset+8+size])
  elif kind==0x004e4942:binstart=offset+8
  offset+=8+size
 assert doc is not None and binstart is not None
 sizes={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4};types={5126:'<f4',5125:'<u4',5123:'<u2',5122:'<i2',5121:'u1',5120:'i1'}
 def access(i):
  a=doc['accessors'][i];assert 'sparse' not in a;b=doc['bufferViews'][a['bufferView']];dtype=np.dtype(types[a['componentType']]);n=sizes[a['type']]
  return np.ndarray((a['count'],n),dtype=dtype,buffer=data,offset=binstart+b.get('byteOffset',0)+a.get('byteOffset',0),strides=(b.get('byteStride',dtype.itemsize*n),dtype.itemsize))
 repairs=[];seen=set()
 for mesh in doc.get('meshes',[]):
  for p in mesh['primitives']:
   attrs=p['attributes']
   if 'TANGENT' not in attrs or attrs['TANGENT'] in seen:continue
   seen.add(attrs['TANGENT']);tan=access(attrs['TANGENT']);assert tan.dtype==np.dtype('<f4'), 'Run repair before quantization'
   lengths=np.linalg.norm(tan[:,:3],axis=1);bad=np.where((lengths<1e-8)|(~np.isfinite(lengths)))[0]
   if not len(bad):continue
   assert p.get('mode',4)==4
   pos=access(attrs['POSITION']);norm=access(attrs['NORMAL']);uv=access(attrs['TEXCOORD_0'])
   indices=access(p['indices']).reshape(-1,3) if 'indices'in p else np.arange(len(pos)).reshape(-1,3)
   badmask=np.zeros(len(pos),bool);badmask[bad]=True;triangles=indices[np.any(badmask[indices],axis=1)]
   candidates={int(i):[] for i in bad}
   for tri in triangles:
    a,b,c=map(int,tri);e1=pos[b].astype(float)-pos[a];e2=pos[c].astype(float)-pos[a];du1=uv[b].astype(float)-uv[a];du2=uv[c].astype(float)-uv[a]
    det=du1[0]*du2[1]-du1[1]*du2[0]
    if abs(det)<1e-18:continue
    t=(e1*du2[1]-e2*du1[1])/det;bt=(e2*du1[0]-e1*du2[0])/det;area=np.linalg.norm(np.cross(e1,e2))
    for i in tri:
     if badmask[i]:candidates[int(i)].append((area,t,bt))
   fallback=0;unreferenced_fallback=0;referenced=np.bincount(indices.reshape(-1),minlength=len(pos))>0
   for i in bad:
    n=norm[i].astype(float);n/=np.linalg.norm(n);solution=None
    for _,t,b in sorted(candidates[int(i)],key=lambda v:-v[0]):
     t=t-n*np.dot(n,t);length=np.linalg.norm(t)
     if length>1e-12 and np.isfinite(length):t/=length;solution=(t,-1.0 if np.dot(np.cross(n,t),b)<0 else 1.0);break
    if solution is None:
     fallback+=1;unreferenced_fallback+=int(not referenced[i]);t=np.cross(n,np.eye(3)[np.argmin(abs(n))]);t/=np.linalg.norm(t);solution=(t,1.0)
    tan[i,:3]=solution[0];tan[i,3]=solution[1]
   repairs.append(dict(mesh=mesh.get('name'),vertices_repaired=len(bad),derived_from_incident_uv_triangles=len(bad)-fallback,orthogonal_fallback=fallback,unreferenced_vertex_fallback=unreferenced_fallback))
 if repairs:
  temporary=path.with_suffix(path.suffix+'.tmp');temporary.write_bytes(data);temporary.replace(path)
 result=dict(file=path.name,sha256_before=before,sha256_after=hashlib.sha256(data).hexdigest(),repairs=repairs,operation='Only zero-length tangent vectors repaired; derive from incident triangle position/UV Jacobian and orthogonalize against existing normals. Geometry, UVs and materials unchanged.')
 if report_path:Path(report_path).write_text(json.dumps(result,indent=2))
 return result

if __name__=='__main__':
 import sys
 print(json.dumps(repair_glb_tangents(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None),indent=2))
