"""Isolated, additive west portal study from immutable revision14 source.
No source images are loaded. All dimensions and finishing values are inferred.
"""
import bpy,bmesh,math,json,hashlib,sys,argparse
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/scratch/253ae098be12/michigan-central');O=Path(__file__).parent
sys.path.insert(0,str(R/'scripts'))
from qa_concourse_roof_detail import validate_glb
sys.path.insert(0,str(O))
from orthogonalize_dentil_tangents import repair
ap=argparse.ArgumentParser();ap.add_argument('--era',choices=['2017','2026'],required=True);ap.add_argument('--baseline',action='store_true');ap.add_argument('--samples',type=int,default=24);ap.add_argument('--width',type=int,default=1000);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);ERA=args.era
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.unit_settings.system='METRIC';bpy.context.preferences.filepaths.save_version=0
baseline=json.loads((O/'frozen_baseline.json').read_text());source=R/f'models/michigan_central_{ERA}.blend'
assert hashlib.file_digest(source.open('rb'),'sha256').hexdigest()==baseline['protected'][str(source.relative_to(R))]
with bpy.data.libraries.load(str(source),link=False) as (a,b):
 wanted=[n for n in a.objects if n.startswith('concourse west')]
 wanted += [n for n in a.objects if n in ['concourse restored flush terrazzo field','concourse restored flush terrazzo bands','concourse qualified2017 unpatterned floor']]
 b.objects=wanted
for ob in b.objects:
 if ob: s.collection.objects.link(ob)
# Preserve original source vertices/materials in the bounded context. Crop only
# the main floor in the NEW study to reduce contextual export size and extent.
for ob in list(s.objects):
 if 'floor' in ob.name and 'west' not in ob.name:
  bm=bmesh.new();bm.from_mesh(ob.data)
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(18.,0,0),plane_no=(1,0,0),clear_inner=True,clear_outer=False)
  bm.to_mesh(ob.data);bm.free();ob['study_context_crop']='floor truncated at X18; not a source model edit'
terra=next(m for m in bpy.data.materials if m.name==f'Concourse terracotta dressings {ERA}')
metal=next(m for m in bpy.data.materials if m.name==f'Concourse retained portal metal {ERA}')
cy=63.4;front=29.4894;new=[]
def mesh(name,verts,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);s.collection.objects.link(ob);me.materials.append(mat);uv=me.uv_layers.new(name='MetricUV');scale=mat.get('texture_repeat_m',1.36)
 for f in me.polygons:
  axis=max(range(3),key=lambda i:abs(f.normal[i]));ids=([1,2] if axis==0 else [0,2] if axis==1 else [0,1])
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p[ids[0]]/scale,p[ids[1]]/scale)
 ob['era']=ERA;ob['status']='Source-supported west portal detail study, photo-relative dimensions';ob['source_reference']='Historic Detroit post_p48; period qualifications in EVIDENCE.md';new.append(ob);return ob

def extrude(name,poly,x0,x1,mat):
 n=len(poly);v=[(x,y,z) for x in [x0,x1] for y,z in poly];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]
 f += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return mesh(name,v,f,mat)
def box(name,x0,x1,y0,y1,z0,z1,mat):return extrude(name,[(y0,z0),(y1,z0),(y1,z1),(y0,z1)],x0,x1,mat)
def rounded(y0,y1,z0,z1,r,n=5):
 out=[]
 for y,z,st in [(y1-r,z1-r,0),(y0+r,z1-r,90),(y0+r,z0+r,180),(y1-r,z0+r,270)]:
  for i in range(n+1):
   a=math.radians(st+i*90/n);out.append((y+r*math.cos(a),z+r*math.sin(a)))
 return out

def ring(name,y0,y1,z0,z1,r,w,x0,x1,mat):
 outer=rounded(y0,y1,z0,z1,r);inner=rounded(y0+w,y1-w,z0+w,z1-w,max(.004,r-w));n=len(outer)
 v=[(x,y,z) for x in [x0,x1] for p in [outer,inner] for y,z in p];f=[]
 for i in range(n):
  j=(i+1)%n;f += [(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),(i,2*n+i,2*n+j,j),(n+j,3*n+j,3*n+i,n+i)]
 return mesh(name,v,f,mat)
def bead(name,y,z,r,x0,x1,mat):
 poly=[(y+r*math.cos(i*2*math.pi/10),z+r*math.sin(i*2*math.pi/10)) for i in range(10)];return extrude(name,poly,x0,x1,mat)

def add_detail():
 # Replace ONLY the two rectangular small-opening lintel batches in this study.
 for ob in list(s.objects):
  if ob.name=='concourse west small opening profiled lintel':bpy.data.objects.remove(ob,do_unlink=True)
 for side in [-1,1]:
  y=cy+side*8.15;prefix=f'West small feature {side:+d} '
  # Shared old masonry form is corroborated by 2010 west-end and May2017
  # unidentified doorway. No loss map copied from either photograph.
  for k,(w,z,h,depth) in enumerate([(1.55,2.35,.14,.20),(1.67,2.46,.10,.26),(1.80,2.535,.05,.32),(1.87,2.595,.075,.36)]):
   box(prefix+f'stepped cornice {k}',front-.59-depth,front-.54,y-w/2,y+w/2,z-h/2,z+h/2,terra)
  width=1.61;zbase=2.638;rise=.16
  poly=[(y-width/2,zbase),(y+width/2,zbase)]+[(y+width*.5*math.cos(i*math.pi/24),zbase+rise*math.sin(i*math.pi/24)) for i in range(25)]
  # Remove consecutive duplicate endpoints from the analytic segmental crown.
  clean=[]
  for p in poly:
   if not clean or math.dist(p,clean[-1])>1e-7:clean.append(p)
  if math.dist(clean[0],clean[-1])<1e-7:clean.pop()
  extrude(prefix+'shallow curved crown',clean,front-.84,front-.56,terra)
  extrude(prefix+'centered tapering key',[(y-.115,2.29),(y+.115,2.29),(y+.165,2.52),(y-.165,2.52)],front-.87,front-.68,terra)
  if side<0:
   # North feature remains BLIND. Raised inner frame rests on the retained
   # shallow blind slab; no opening or room is created.
   ring(prefix+'blind inset terracotta frame',y-.47,y+.47,.53,2.18,.055,.073,front-.75,front-.54,terra)
   box(prefix+'blind panel sill',front-.80,front-.53,y-.59,y+.59,.46,.54,terra)
 # Opaque intermediate band: three rounded inset border fields, regularized
 # attachment heads. Exact molding and fastener counts remain interpretive.
 zones=[(cy-2.37,cy-1.72),(cy-1.50,cy+1.50),(cy+1.72,cy+2.37)]
 for i,(a,b) in enumerate(zones):
  ring(f'West portal opaque band rounded panel border {i}',a,b,3.84,4.45,.07,.028,front-.199,front-.147,metal)
 for u in [cy-2.39,cy-1.64,cy+1.64,cy+2.39]:
  for j in range(7):bead('West portal regularized band attachment head',u,3.79+j*.115,.014,front-.217,front-.194,metal)
 # Layered lower rail stays entirely above the established 2.55m opening.
 for j,(lo,hi,w,depth) in enumerate([(2.56,2.615,4.82,.23),(2.62,2.69,4.76,.20),(2.70,2.745,4.88,.24)]):
  box(f'West portal layered lower head rail {j}',front-depth,front-.14,cy-w/2,cy+w/2,lo,hi,metal)
 if ERA=='2026':
  for side in [-1,1]:
   mid=cy+side*2.00;a=mid-.255;b=mid+.255;lo=.46;hi=1.98
   ring(f'West restored lower grille inset frame {side}',a-.045,b+.045,lo-.045,hi+.045,.018,.035,front-.211,front-.153,metal)
   # Two diagonal families of narrow physical bars, clipped to the inset.
   # An opaque original backing remains behind: no invented through-room.
   pitch=.068;bw=.007
   for slope in [-1,1]:
    for k in range(-28,29):
     c=k*pitch;points=[]
     for u in [a,b]:
      z=lo+slope*(u-a)+c
      if lo-1e-8<=z<=hi+1e-8:points.append((u,z))
     for z in [lo,hi]:
      u=a+(z-lo-c)/slope
      if a-1e-8<=u<=b+1e-8:points.append((u,z))
     pts=[]
     for p in points:
      if not any(math.dist(p,q)<1e-7 for q in pts):pts.append(p)
     if len(pts)!=2 or math.dist(*pts)<.012:continue
     (u0,z0),(u1,z1)=pts;du=u1-u0;dz=z1-z0;l=math.hypot(du,dz);nu=-dz/l*bw/2;nz=du/l*bw/2
     poly=[(u0+nu,z0+nz),(u1+nu,z1+nz),(u1-nu,z1-nz),(u0-nu,z0-nz)]
     extrude(f'West restored lower physical diamond grille {side} {slope} {k}',poly,front-.185-(slope+1)*.003,front-.178-(slope+1)*.003,metal)
if not args.baseline:add_detail()

# Recenter new tiny geometry to avoid large-coordinate float32 tangent errors.
for ob in new:
 center=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
 for v in ob.data.vertices:v.co-=center
 ob.location=center

# Verification gate, both inherited context and added mesh. New objects are
# individually closed solids with finite explicit UVs and positive volume.
qa={'era':ERA,'source_sha256':baseline['protected'][str(source.relative_to(R))],'baseline':args.baseline,'added_objects':len(new),'checks':{},'errors':[],'new_geometry':[]}
for ob in s.objects:
 if ob.type!='MESH':continue
 me=ob.data;me.calc_loop_triangles();uv=me.uv_layers.active
 if not uv:qa['errors'].append([ob.name,'missing UV']);continue
 for t in me.loop_triangles:
  a,b,c=[uv.data[i].uv for i in t.loops];area=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))
  if t.area<1e-12 or area<1e-12:qa['errors'].append([ob.name,'degenerate geometry/UV',t.index]);break
 if ob in new:
  bm=bmesh.new();bm.from_mesh(me);nonman=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
  qa['new_geometry'].append({'name':ob.name,'triangles':len(me.polygons),'nonmanifold_edges':nonman,'volume_m3':vol})
  if nonman or vol<=0:qa['errors'].append([ob.name,'topology/volume',nonman,vol])
qa['checks']['mesh_uv_and_new_closed_solid_topology']=not qa['errors']
qa['checks']['2017_no_restored_grille']=ERA!='2017' or not any('restored lower' in ob.name for ob in s.objects)
# Central passage ray probes traverse the actual appended source and additions.
deps=bpy.context.evaluated_depsgraph_get();hits=[]
for z in [.2,1.7,2.45]:
 for y in [cy-1.35,cy,cy+1.35]:
  origin=Vector((27.,y,z));direction=Vector((1,0,0));hit,loc,n,idx,ob,mat=s.ray_cast(deps,origin,direction,distance=7.)
  if hit:hits.append({'height':z,'y':y,'object':ob.name,'x':loc.x})
qa['passage_hits']=hits;qa['checks']['central_passage_clear']=not hits
qa['checks']['no_source_photographs_loaded']=not any('/research/' in im.filepath for im in bpy.data.images)
assert all(qa['checks'].values()),qa
# Source-relative study lighting, never asserted to replicate a capture.
w=bpy.data.worlds.new('Bounded study neutral daylight');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.44,.50,.58,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.32;s.world=w
for name,loc,energy,size,target in [('Cloud daylight',(23.,60.,10.),1500,6,(29.,63.,4.)),('Soft right return',(24.,70.,5.5),650,5,(29.,63.,4.))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.cycles.max_bounces=6;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=args.width;s.render.resolution_y=round(args.width*.78);s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.3
cameras={'west_portal':((13.0,63.4,4.15),(29.25,63.4,4.6),30.),'detail_oblique':((20.2,58.3,3.15),(29.15,63.3,3.45),37.),'small_crown':((25.,69.,2.0),(29.,71.55,2.0),49.)}
if args.baseline:cameras={k:v for k,v in cameras.items() if k=='west_portal'}
qa['renders']=[]
for name,(loc,target,lens) in cameras.items():
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;s.camera=o
 name=('baseline_' if args.baseline else '')+ERA+'_'+name;s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);qa['renders'].append({'path':s.render.filepath,'camera_location':loc,'target':target,'lens_mm':lens,'samples':args.samples})
if not args.baseline:
 # Export the entire isolated scene, including inherited locked context.
 # Preserve original custom normals; do not recompute/bake their shading.
 bpy.context.view_layer.update()
 for ob in s.objects:
  if ob.type=='MESH':
   world=ob.matrix_world.copy();ob.parent=None;ob.matrix_world=world;ob.hide_select=False;ob.hide_set(False);ob.hide_viewport=False
 bpy.ops.object.select_all(action='DESELECT')
 for ob in s.objects:
  if ob.type=='MESH':ob.hide_select=False;ob.select_set(True)
 path=O/f'concourse_west_portal_{ERA}_STUDY.glb';bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=False,export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_extras=True)
 repair(path,O/f'tangent_precision_{ERA}.json')
 qa['glb']=validate_glb(path)
 # Pack only inherited material assets. Never pack a research image.
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/f'concourse_west_portal_{ERA}_STUDY.blend'))
(O/(('baseline_' if args.baseline else '')+f'qa_{ERA}.json')).write_text(json.dumps(qa,indent=2));print('STUDY_QA',json.dumps(qa['checks']),flush=True)
