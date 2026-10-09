"""Standalone bounded concourse-roof QA. No execution/import of main builder.

Pure Python: --geometry-only runs inexpensive batch/scope/UV/normal checks.
Blender: --era2017 or --era2026 materializes this component only, checks actual
mesh triangles and tangents, optionally renders one bounded preview and exports
an isolated GLB. CPU2threads,720x480,12samples. Ask the lead for a Blender slot.
All outputs are restricted to manifests/concourse_roof_detail/.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manifests/concourse_roof_detail'
MODULE=ROOT/'scripts/concourse_roof_detail.py'


class _FakeSocket:
    def __init__(self):self.links=[];self.default_value=None
class _FakeNode:
    def __init__(self):self.inputs={k:_FakeSocket() for k in ['Base Color','Roughness','Metallic','Transmission Weight']}
class _FakeNodes:
    def __init__(self):self.principled=_FakeNode()
    def get(self,key):return self.principled if key=='Principled BSDF' else None
class _FakeTree:
    def __init__(self):self.nodes=_FakeNodes();self.links=[]
class _FakeMat(dict):
    def __init__(self,name):super().__init__();self.name=name;self.node_tree=_FakeTree()
    def copy(self):return _FakeMat(self.name+' copy')


def _area2(points):return sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(points,points[1:]+points[:1]))
def _sub(a,b):return tuple(x-y for x,y in zip(a,b))
def _cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def _dot(a,b):return sum(x*y for x,y in zip(a,b))
def _norm(a):return math.sqrt(_dot(a,a))


def make_namespace(era,real=False):
    ns={'ERA':era,'AGED':era=='2017','ROOT':ROOT,'GROUP':'QA sentinel',
        'B':{},'M':{},'__file__':str(MODULE),'__name__':'concourse_roof_component_qa'}
    if real:
        import bpy
        for name,col,rough,metal,trans in [
            ('Roof steel',(.08,.075,.069),.5,.75,0),
            ('Roof dark copper',(.035,.044,.040),.62,.45,0),
            ('Glass clear',(.88,.94,.97),.045,0,.98),
        ]:
            m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
            p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough
            p.inputs['Metallic'].default_value=metal;p.inputs['Transmission Weight'].default_value=trans
            ns['M'][name]=m
    else:
        ns['M']={k:_FakeMat(k) for k in ('Roof steel','Roof dark copper','Glass clear')}
    def addmesh(v,f,material,name=None,uv=None,face_uv=None):
        key=(ns['GROUP'],material,name or material)
        if key not in ns['B']:ns['B'][key]=[[],[],[]]
        vv,ff,uu=ns['B'][key];n=len(vv);vv.extend(v)
        ff.extend(tuple(n+i for i in face) for face in f)
        uu.extend(face_uv if face_uv is not None else [[uv[i] for i in face] if uv is not None else None for face in f])
    ns['addmesh']=addmesh
    return ns


def run_geometry(era,real=False):
    ns=make_namespace(era,real)
    # Sentinel proves precise names and group are both required for replacement.
    expected={
      ('05 CONCOURSE | restored glazing and structural roof','Roof steel','concourse window mullions'): [[(0,0,0)],[],[]],
      ('05 CONCOURSE | restored glazing and structural roof','Roof steel','concourse brick parapet'): [[(0,1,0)],[],[]],
      ('OTHER ROOM','Roof steel','concourse primary truss chords'): [[(0,2,0)],[],[]],
    }
    ns['B'].update(expected)
    old=('05 CONCOURSE | restored glazing and structural roof','Roof steel','concourse primary truss chords')
    ns['B'][old]=[[(0,3,0)],[],[]]
    exec(compile(MODULE.read_bytes(),str(MODULE),'exec'),ns)
    report={'era':era,'module_sha256':hashlib.sha256(MODULE.read_bytes()).hexdigest(),
        'scope':'Isolated roof component only, no main station execution or integration validation',
        'checks':{},'geometry':{},'metadata':ns['CONCOURSE_ROOF_METADATA'],
        'copyright':'No study/source pixels loaded or included in the geometry, preview or export'}
    report['checks']['group_restored']=ns['GROUP']=='QA sentinel'
    report['checks']['exact_legacy_roof_removed']=old not in ns['B']
    report['checks']['all_nonroof_sentinels_unchanged']=all(ns['B'].get(k)==v for k,v in expected.items())
    for k in expected:del ns['B'][k]
    errors=[];vertex_count=face_count=0;closed_components=0;signed_volumes=[]
    for key,(vv,ff,uvs) in ns['B'].items():
        if len(ff)!=len(uvs):errors.append([key[2],'face UV count'])
        vertex_count+=len(vv);face_count+=len(ff)
        if not all(math.isfinite(x) for p in vv for x in p):errors.append([key[2],'nonfinite vertex'])
        # Each emitted extrusion is a disconnected, closed component. Test edge
        # orientation and signed volume without relying on Blender auto-fixes.
        edges={};neighbours={i:set() for i in range(len(vv))};fvol=[]
        for face,uv in zip(ff,uvs):
            if uv is None or len(uv)!=len(face):errors.append([key[2],'missing explicit UV']);continue
            if not all(math.isfinite(x) for p in uv for x in p):errors.append([key[2],'nonfinite UV'])
            if abs(_area2(uv))<1e-12:errors.append([key[2],'zero polygon UV area'])
            pts=[vv[i] for i in face];origin=pts[0]
            normal=[0.,0.,0.];volume=0.
            for i in range(1,len(pts)-1):
                a=_cross(_sub(pts[i],origin),_sub(pts[i+1],origin))
                normal=[x+y for x,y in zip(normal,a)]
                volume+=_dot(origin,_cross(pts[i],pts[i+1]))/6
            fvol.append(volume)
            if _norm(normal)<1e-12:errors.append([key[2],'zero geometric polygon area'])
            for a,b in zip(face,face[1:]+face[:1]):
                neighbours[a].add(b);neighbours[b].add(a)
                edges.setdefault(tuple(sorted((a,b))),[]).append((a,b))
        bad=[e for e,uses in edges.items() if len(uses)!=2 or uses[0]!=tuple(reversed(uses[1]))]
        if bad:errors.append([key[2],'nonmanifold or inconsistent edge winding',len(bad)])
        seen=set();components=[]
        for start in range(len(vv)):
            if start in seen:continue
            todo=[start];seen.add(start);component=set()
            while todo:
                v=todo.pop();component.add(v)
                for q in neighbours[v]-seen:seen.add(q);todo.append(q)
            components.append(component)
        owner={v:j for j,c in enumerate(components) for v in c};volumes=[0.]*len(components)
        for face,vol in zip(ff,fvol):volumes[owner[face[0]]]+=vol
        for vol in volumes:
            if vol<=1e-11:errors.append([key[2],'nonpositive component volume',vol])
        closed_components+=len(components);signed_volumes.extend(volumes)
        report['geometry'][key[2]]={'vertices':len(vv),'faces':len(ff),'closed_components':len(components)}
    names=[k[2] for k in ns['B']]
    report['checks']['no2017roof_skins']=era!='2017' or not any('glazing panels' in n or 'opaque outer roof strips' in n for n in names)
    report['checks']['restored2026skins_present']=era!='2026' or all(any(s in n for n in names) for s in ['individual glazing panels','opaque outer roof strips','pressure caps'])
    report['checks']['fourteen_qualified_stations_retained']=len(ns['CONCOURSE_ROOF_METADATA']['stations_x_m'])==14
    report['checks']['lower_laylight_and_bush_roof_absent']=not any('laylight' in n or 'Bush' in n for n in names)
    report['checks']['no_duplicate_center_post_batch']=sum('single central' in n for n in names)==1
    report['checks']['all_faces_explicit_metric_uv_closed_outward_mesh']=not errors
    report['geometry_totals']={'vertices':vertex_count,'faces':face_count,'closed_components':closed_components,
        'minimum_positive_component_volume_m3':min(signed_volumes),'batches':len(ns['B'])}
    report['errors']=errors[:30]
    assert all(report['checks'].values()),report['checks']
    assert not errors,errors[:15]
    return ns,report


def validate_glb(path):
    import struct
    import numpy as np
    data=path.read_bytes();off=12;doc=None;binary=None
    while off<len(data):
        size,kind=struct.unpack_from('<II',data,off)
        if kind==0x4e4f534a:doc=json.loads(data[off+8:off+8+size])
        elif kind==0x004e4942:binary=data[off+8:off+8+size]
        off+=8+size
    types={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'};dims={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
    def acc(i):
        a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];dt=np.dtype(types[a['componentType']]);n=dims[a['type']]
        return np.ndarray((a['count'],n),dtype=dt,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dt.itemsize*n),dt.itemsize))
    errors=[];triangles=vertices=0;primitive_count=0
    for mesh in doc.get('meshes',[]):
        for prim in mesh['primitives']:
            primitive_count+=1;attrs=prim['attributes']
            if not all(k in attrs for k in ('POSITION','NORMAL','TEXCOORD_0','TANGENT')):
                errors.append([mesh.get('name'),'missing export attribute']);continue
            p,n,u,t=[acc(attrs[k]).astype(float) for k in ('POSITION','NORMAL','TEXCOORD_0','TANGENT')]
            vertices+=len(p);idx=acc(prim['indices']).reshape(-1,3);triangles+=len(idx)
            if not all(np.isfinite(a).all() for a in (p,n,u,t)):errors.append([mesh.get('name'),'nonfinite'])
            if np.any(abs(np.linalg.norm(n,axis=1)-1)>1e-4):errors.append([mesh.get('name'),'normal length'])
            if np.any(abs(np.linalg.norm(t[:,:3],axis=1)-1)>1e-4):errors.append([mesh.get('name'),'tangent length'])
            if np.any(abs((n*t[:,:3]).sum(axis=1))>1e-4):errors.append([mesh.get('name'),'nonorthogonal tangent'])
            if np.any(abs(abs(t[:,3])-1)>1e-4):errors.append([mesh.get('name'),'invalid tangent handedness'])
            a,b,c=p[idx[:,0]],p[idx[:,1]],p[idx[:,2]]
            if np.any(np.linalg.norm(np.cross(b-a,c-a),axis=1)<1e-10):errors.append([mesh.get('name'),'degenerate triangle'])
            a,b,c=u[idx[:,0]],u[idx[:,1]],u[idx[:,2]]
            area=abs((b[:,0]-a[:,0])*(c[:,1]-a[:,1])-(b[:,1]-a[:,1])*(c[:,0]-a[:,0]))
            if np.any(area<1e-12):errors.append([mesh.get('name'),'collapsed UV triangle'])
    result={'primitives':primitive_count,'vertices':vertices,'triangles':triangles,'errors':errors,'sha256':hashlib.sha256(data).hexdigest(),
        'images':len(doc.get('images',[])),'external_buffers':any('uri' in b for b in doc.get('buffers',[]))}
    assert not errors,errors
    return result


def run_blender(era,skip_render=False,skip_export=False,camera='concourse_roof_axial'):
    import bpy
    from mathutils import Vector
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for m in list(bpy.data.materials):bpy.data.materials.remove(m)
    ns,report=run_geometry(era,real=True);scene=bpy.context.scene
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    objects=[];errors=[];triangles=0
    for (group,material,name),(vv,ff,fu) in ns['B'].items():
        me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.materials.append(ns['M'][material]);me.update()
        ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);objects.append(ob)
        ob['space']=group;ob['era']=era;ob['reconstruction_status']='Isolated inferred roof detail, not a surveyed steel fabrication'
        uv=me.uv_layers.new(name='MetricUV')
        for face in me.polygons:
            for j,li in enumerate(face.loop_indices):uv.data[li].uv=fu[face.index][j]
        me.calc_loop_triangles()
        for tri in me.loop_triangles:
            triangles+=1;us=[tuple(uv.data[i].uv) for i in tri.loops]
            if tri.area<1e-12 or abs(_area2(us))<1e-12:errors.append((name,tri.index,tri.area,_area2(us)))
        if any(len(p.vertices)>4 for p in me.polygons):
            mod=ob.modifiers.new('Portable tangent topology for section caps','TRIANGULATE');mod.min_vertices=5
    report['blender']={'version':bpy.app.version_string,'triangles_tested':triangles,'mesh_uv_errors':errors}
    assert not errors,errors[:15]
    report['checks']['no_reference_images_loaded']=not any('research' in im.filepath or 'study_only' in im.filepath for im in bpy.data.images)
    scene['project']='Michigan Central isolated source-informed concourse roof detail'
    scene['era']=era;scene['status']='Bounded component study, not a complete station model or integration acceptance'
    scene['roof_evidence']=json.dumps(ns['CONCOURSE_ROOF_METADATA'])
    scene['copyright']='No source photographs used as textures or included'
    if not skip_export:
        bpy.ops.object.select_all(action='DESELECT')
        for ob in objects:ob.select_set(True)
        path=OUT/('concourse_roof_'+era+'_ISOLATED.glb')
        bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_format='GLB',export_apply=True,
            export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_extras=True)
        report['glb']=validate_glb(path)
    # Render context is kept in its own named collection and excluded from GLB.
    world=bpy.data.worlds.new('Neutral roof detail study light');world.use_nodes=True;scene.world=world
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.50,.59,.70,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
    sun=bpy.data.lights.new('Study sunlight','SUN');sun.energy=2.5;sun.angle=.15
    so=bpy.data.objects.new('Study sunlight',sun);scene.collection.objects.link(so);so.rotation_euler=(.45,-.6,-.45)
    area=bpy.data.lights.new('Neutral study roof fill','AREA');area.energy=3500;area.shape='RECTANGLE';area.size=40;area.size_y=16
    ao=bpy.data.objects.new('Neutral study roof fill',area);scene.collection.objects.link(ao);ao.location=(0,63.4,6)
    ao.rotation_euler=(Vector((0,63.4,12))-ao.location).to_track_quat('-Z','Y').to_euler()
    spec=ns['CONCOURSE_ROOF_CAMERAS'][camera];d=bpy.data.cameras.new(camera);cam=bpy.data.objects.new(camera,d);scene.collection.objects.link(cam)
    cam.location=spec['location'];cam.rotation_euler=(Vector(spec['target'])-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=spec['lens_mm'];d.clip_end=300
    scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.cycles.max_bounces=5
    scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=720;scene.render.resolution_y=480;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.render.filepath=str(OUT/('preview_'+era+'_'+camera+'.png'))
    scene.render.film_transparent=False
    blend=OUT/('concourse_roof_'+era+'_ISOLATED.blend');bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    report['outputs']={'blend':str(blend.relative_to(ROOT)),'preview':None if skip_render else str(Path(scene.render.filepath).relative_to(ROOT))}
    if not skip_render:bpy.ops.render.render(write_still=True)
    return report


def main():
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    ap=argparse.ArgumentParser();ap.add_argument('--geometry-only',action='store_true');ap.add_argument('--era',choices=['2017','2026'],default='2026')
    ap.add_argument('--skip-render',action='store_true');ap.add_argument('--skip-export',action='store_true')
    ap.add_argument('--camera',choices=['concourse_roof_axial','concourse_roof_connection','concourse_roof_exterior'],default='concourse_roof_axial')
    args=ap.parse_args(argv);OUT.mkdir(parents=True,exist_ok=True)
    if args.geometry_only:
        results={era:run_geometry(era)[1] for era in ('2017','2026')}
        (OUT/'geometry_only_qa.json').write_text(json.dumps(results,indent=2))
        print(json.dumps({k:{'checks':v['checks'],'geometry_totals':v['geometry_totals'],'bounds':v['metadata']['replacement']['actual_mesh_bounds_m']} for k,v in results.items()},indent=2))
    else:
        report=run_blender(args.era,args.skip_render,args.skip_export,args.camera)
        (OUT/('isolated_qa_'+args.era+'.json')).write_text(json.dumps(report,indent=2))
        print('CONCOURSE_ROOF_QA',json.dumps(report),flush=True)

if __name__=='__main__':main()
