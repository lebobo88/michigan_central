"""Bounded correction of four-decimal export tangent rounding in inherited dentils.
Only near-threshold (|n dot t| <=0.0002) rounding is accepted. No positions,
normals, UVs, indices, images, material data, handedness or new detail is changed.
"""
import json,struct,hashlib
from pathlib import Path
import numpy as np

def repair(path,report_path):
 path=Path(path);raw=path.read_bytes();data=bytearray(raw);offset=12;doc=None;start=None
 while offset<len(data):
  count,kind=struct.unpack_from('<II',data,offset)
  if kind==0x4e4f534a:doc=json.loads(data[offset+8:offset+8+count])
  if kind==0x004e4942:start=offset+8
  offset+=count+8
 def acc(i):
  a=doc['accessors'][i];b=doc['bufferViews'][a['bufferView']];assert a['componentType']==5126
  n={'VEC3':3,'VEC4':4}[a['type']];return np.ndarray((a['count'],n),dtype='<f4',buffer=data,offset=start+b.get('byteOffset',0)+a.get('byteOffset',0),strides=(b.get('byteStride',4*n),4))
 rows=[];seen=set();allowed_bytes=set()
 for m in doc['meshes']:
  for p in m['primitives']:
   attrs=p['attributes'];ti=attrs['TANGENT']
   if ti in seen:continue
   seen.add(ti);normal=acc(attrs['NORMAL']).astype(float);tan=acc(ti);v=tan[:,:3].astype(float);dot=(normal*v).sum(1);bad=np.where(abs(dot)>1e-4)[0]
   if not len(bad):continue
   assert m['name'].startswith('concourse west end regularized cornice dentil teeth'),m['name']
   assert max(abs(dot[bad]))<.0002, 'This is not the documented tiny rounding issue'
   old=v[bad].copy();n=normal[bad];v[bad]-=n*(dot[bad]/(n*n).sum(1))[:,None];v[bad]/=np.linalg.norm(v[bad],axis=1)[:,None];tan[bad,:3]=v[bad]
   a=doc['accessors'][ti];b=doc['bufferViews'][a['bufferView']];base=start+b.get('byteOffset',0)+a.get('byteOffset',0);stride=b.get('byteStride',16)
   for i in bad:
    for k in range(12):allowed_bytes.add(base+int(i)*stride+k)
   rows.append({'mesh':m['name'],'vertices':len(bad),'max_abs_dot_before':float(max(abs(dot[bad]))),'max_abs_dot_after':float(max(abs((normal[bad]*tan[bad,:3]).sum(1)))),'max_vector_change':float(max(np.linalg.norm(v[bad]-old,axis=1)))})
 changes=[i for i,(a,b) in enumerate(zip(raw,data)) if a!=b]
 assert set(changes)<=allowed_bytes, 'Non-tangent bytes changed'
 path.write_bytes(data)
 report={'operation':'Orthogonalize only inherited dentil tangents affected by tiny exporter rounding; keep all other bytes identical','sha256_before':hashlib.sha256(raw).hexdigest(),'sha256_after':hashlib.sha256(data).hexdigest(),'rows':rows,'changed_bytes':len(changes),'only_allowed_tangent_xyz_bytes_changed':True}
 Path(report_path).write_text(json.dumps(report,indent=2));return report
