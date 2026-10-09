"""Small shared hash helper for source/export validation lineage."""
from pathlib import Path
import hashlib

def file_sha256(path):
    p=Path(path)
    if not p.is_file():raise FileNotFoundError(p)
    h=hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda:f.read(4*1024*1024),b''):h.update(data)
    return h.hexdigest()

def surface_vertex_bounds(objects, exclude_names=('landscape context',)):
    """Bounds of polygon-referenced geometry, not loose authoring control points.
    Transforms actual vertices; a rotated local AABB can otherwise overestimate.
    """
    import numpy as np
    cache={};lo=np.full(3,np.inf);hi=np.full(3,-np.inf);loose=[];instances=0
    for ob in objects:
        if ob.type!='MESH' or ob.name in exclude_names:continue
        key=ob.data.as_pointer()
        if key not in cache:
            v=np.empty(len(ob.data.vertices)*3,dtype=np.float64);ob.data.vertices.foreach_get('co',v)
            ids=np.empty(len(ob.data.loops),dtype=np.int32);ob.data.loops.foreach_get('vertex_index',ids);used=np.unique(ids)
            cache[key]=v.reshape(-1,3)[used]
            if len(used)<len(ob.data.vertices):loose.append(dict(mesh=ob.data.name,unreferenced_vertices=len(ob.data.vertices)-len(used)))
        if not len(cache[key]):continue
        m=np.asarray(ob.matrix_world,dtype=np.float64);w=cache[key]@m[:3,:3].T+m[:3,3]
        lo=np.minimum(lo,w.min(0));hi=np.maximum(hi,w.max(0));instances+=len(w)
    return dict(bounds_m=[lo.tolist(),hi.tolist()],transformed_surface_vertices=instances,unreferenced_vertex_diagnostic=loose,method='Actual world-space polygon-referenced vertices, before source modifiers')
