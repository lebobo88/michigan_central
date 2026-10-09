"""Small, bounded random-access GLB reader. Python 3.10+, standard library only."""
import sys
sys.dont_write_bytecode = True
import copy, hashlib, json, math, struct
from pathlib import Path
BLOCK = 1024 * 1024
TYPES = {5126: ('f',4),5125:('I',4),5123:('H',2),5121:('B',1),5122:('h',2),5120:('b',1)}
WIDTH = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def sha(data): return hashlib.sha256(data).hexdigest()
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(BLOCK),b''):h.update(b)
    return h.hexdigest()
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
class GLB:
    def __init__(self,path):
        self.path=Path(path); self.size=self.path.stat().st_size; self.doc=None; self.start=None
        with self.path.open('rb') as f:
            head=f.read(12)
            if len(head)!=12 or struct.unpack('<4sII',head)!=(b'glTF',2,self.size):raise ValueError('Invalid GLB header')
            off=12
            while off<self.size:
                f.seek(off); n,kind=struct.unpack('<II',f.read(8))
                if n%4 or off+8+n>self.size:raise ValueError('Invalid GLB chunk')
                if kind==0x4e4f534a:
                    if self.doc is not None or n>32*BLOCK:raise ValueError('Duplicate/oversized JSON')
                    chunks=[];left=n
                    while left:b=f.read(min(BLOCK,left));chunks.append(b);left-=len(b)
                    self.doc=json.loads(b''.join(chunks))
                elif kind==0x004e4942:
                    if self.start is not None:raise ValueError('Duplicate BIN')
                    self.start=off+8;self.bin_size=n
                else:raise ValueError('Unsupported chunk')
                off+=8+n
        if self.doc is None or self.start is None:raise ValueError('Missing JSON/BIN')
    def region_hash(self,start,size):
        h=hashlib.sha256()
        with self.path.open('rb') as f:
            f.seek(start)
            while size:
                b=f.read(min(BLOCK,size))
                if not b:raise ValueError('Truncated region')
                h.update(b);size-=len(b)
        return h.hexdigest()
    def layout(self,index):
        a=self.doc['accessors'][index]
        if 'sparse' in a or a.get('normalized',False):raise ValueError('Only plain unnormalized accessors supported')
        v=self.doc['bufferViews'][a['bufferView']]
        if v.get('buffer',0)!=0:raise ValueError('External buffer')
        fmt,unit=TYPES[a['componentType']];width=WIDTH[a['type']];row=width*unit;stride=v.get('byteStride',row)
        count=a['count'];local=a.get('byteOffset',0);base=v.get('byteOffset',0)+local
        if count<1 or stride<row or local+(count-1)*stride+row>v['byteLength'] or base+(count-1)*stride+row>self.bin_size:raise ValueError('Invalid accessor range')
        return {'start':self.start+base,'stride':stride,'row_bytes':row,'count':count,'type':a['type'],'componentType':a['componentType'],'fmt':'<'+fmt*width}
    def array(self,index):
        d=self.layout(index);out=bytearray()
        with self.path.open('rb') as f:
            chunk_rows=max(1,BLOCK//d['stride'])
            for i in range(0,d['count'],chunk_rows):
                count=min(chunk_rows,d['count']-i);f.seek(d['start']+i*d['stride']);raw=f.read((count-1)*d['stride']+d['row_bytes'])
                if d['stride']==d['row_bytes']:out.extend(raw)
                else:
                    for j in range(count):out.extend(raw[j*d['stride']:j*d['stride']+d['row_bytes']])
        return bytes(out)
    def descriptor(self,index):
        a=self.doc['accessors'][index]
        return {k:copy.deepcopy(v) for k,v in a.items() if k not in ('bufferView','byteOffset')}
    def primitive(self,name):
        found=[(i,m) for i,m in enumerate(self.doc['meshes']) if m.get('name')==name]
        if len(found)!=1 or len(found[0][1]['primitives'])!=1:raise ValueError('Ambiguous mesh '+name)
        i,m=found[0];p=m['primitives'][0]
        if p.get('mode',4)!=4:raise ValueError('Not triangle mode')
        return i,p
    def material(self,index):
        def texture(index):
            t=copy.deepcopy(self.doc['textures'][index]);im=self.doc['images'][t.pop('source')]
            if 'uri' in im or 'bufferView' not in im:raise ValueError('External image')
            v=self.doc['bufferViews'][im['bufferView']]
            t['embedded_image']={'sha256':self.region_hash(self.start+v.get('byteOffset',0),v['byteLength']),'mimeType':im.get('mimeType')}
            if 'sampler' in t:t['sampler']=self.doc['samplers'][t['sampler']]
            return t
        def walk(item,key=''):
            if isinstance(item,list):return [walk(v) for v in item]
            if not isinstance(item,dict):return item
            r={k:walk(v,k) for k,v in item.items()}
            if key.lower().endswith('texture') and 'index' in r:r['resolved_texture']=texture(r.pop('index'))
            return r
        return walk(self.doc['materials'][index])
def rows(data,desc):
    return list(struct.iter_unpack('<'+TYPES[desc['componentType']][0]*WIDTH[desc['type']],data))

def scene_transforms(doc):
    """Canonical local/world matrices and exact named hierarchy for all GLB nodes."""
    nodes=doc.get('nodes',[]);names=[n.get('name') for n in nodes]
    if any(not n for n in names) or len(set(names))!=len(names):raise ValueError('Every node must have a unique name')
    parents={};local={};world={};active=set()
    for i,n in enumerate(nodes):
        for c in n.get('children',[]):
            if not isinstance(c,int) or not 0<=c<len(nodes) or c in parents:raise ValueError('Invalid/multiple-parent node')
            parents[c]=i
        if 'matrix'in n:
            a=n['matrix']
            if len(a)!=16 or any(k in n for k in ('translation','rotation','scale')):raise ValueError('Invalid node matrix')
            m=[[a[c*4+r] for c in range(4)] for r in range(4)]
        else:
            t=n.get('translation',[0,0,0]);x,y,z,w=n.get('rotation',[0,0,0,1]);scale=n.get('scale',[1,1,1])
            if abs(x*x+y*y+z*z+w*w-1)>1e-4:raise ValueError('Nonunit node quaternion')
            m=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),t[0]],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),t[1]],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),t[2]],[0,0,0,1]]
            for r in range(3):
                for c in range(3):m[r][c]*=scale[c]
        if not all(math.isfinite(x) for row in m for x in row):raise ValueError('Nonfinite transform')
        local[i]=m
    def evaluate(i):
        if i in world:return world[i]
        if i in active:raise ValueError('Node hierarchy cycle')
        active.add(i);m=local[i]
        if i in parents:
            p=evaluate(parents[i]);m=[[sum(p[r][k]*m[k][c] for k in range(4)) for c in range(4)] for r in range(4)]
        active.remove(i);world[i]=m;return m
    return {names[i]:{'parent':names[parents[i]] if i in parents else None,'local_matrix':local[i],'world_matrix':evaluate(i),'mesh_name':doc['meshes'][n['mesh']].get('name') if 'mesh'in n else None} for i,n in enumerate(nodes)}
