"""Detached2017 south-core QA; exactly one640px preview, max2CPUthreads.
No main scene is generated. Default2017/2026 integration gates are also checked.
"""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
SKIP_RENDER='--skip-render' in sys.argv
ROOT=Path(__file__).resolve().parents[1]
main=ROOT/'scripts/build_station.py';module=ROOT/'scripts/south_structure.py'
sys.argv=['blender','--','--era','2017','--no-render','--no-export']
ns={'__file__':str(main),'__name__':'south_detached_qa'}
exec(compile(main.read_text().split('# SITE ----------------------------------------------------------')[0],str(main),'exec'),ns)
report={'blender':bpy.app.version_string,'script_sha256':hashlib.sha256(module.read_bytes()).hexdigest(),
 'scope':'Detached 2017 cargo-core subset only, not station-aligned; no Bush train-shed roof',
 'coordinates':'Local deck surface Z0, north cargo-core edge Y0, core X center 0; NO station-global transform',
 'checks':{},'collections':{},'limitations':['Geometry QA does not validate architecture or unverified relative locations','The approximately 570 × 340 ft cargo core is not the full original 1,104 ft shed/platform footprint','Cargo rooms and active freight corridor are omitted','2026 current deck remains blocked by missing perimeter and elevation evidence']}
for era in ['2017','2026']:
 ns['ERA']=era;ns['AGED']=era=='2017';ns['GROUP']='QA sentinel';ns['B']={}
 exec(compile(module.read_bytes(),str(module),'exec'),ns)
 report['checks'][era+'_default_emits_no_geometry']=not ns['B']
 report['checks'][era+'_default_preserves_GROUP']=ns['GROUP']=='QA sentinel'
 report.setdefault('integration_blockers',{})[era]=ns['SOUTH_STRUCTURE_EVIDENCE_PROPERTIES']['blockers']
ns['ERA']='2017';ns['AGED']=True;ns['GROUP']='Local study sentinel';ns['B']={}
ns['SOUTH_STRUCTURE_CONTROL_PATH']=str(ROOT/'manifests/south_structure/local_2017_controls.json')
exec(compile(module.read_bytes(),str(module),'exec'),ns)
assert ns['SOUTH_STRUCTURE_EVIDENCE_PROPERTIES']['status']=='enabled',ns['SOUTH_STRUCTURE_EVIDENCE_PROPERTIES']
assert ns['GROUP']=='Local study sentinel'
B,M,scene=ns['B'],ns['M'],ns['scene'];collections={};room_nodes={}
nonfinite=[];uv_nonfinite=[];degenerate=[];uv_collapsed=[];tris=0
for (group,material,name),(vv,ff,uvs) in B.items():
 if group not in collections:
  col=bpy.data.collections.new(group);scene.collection.children.link(col);collections[group]=col
  node=bpy.data.objects.new(group,None);col.objects.link(node);node['export_group']=True;node['coordinate_space']='DETACHED LOCAL STUDY, NOT STATION ALIGNED';room_nodes[group]=node
 me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.materials.append(M[material]);me.update()
 ob=bpy.data.objects.new(name,me);collections[group].objects.link(ob);ob.parent=room_nodes[group]
 ob['space']=group;ob['accuracy']='Published approximate envelope, photo-proportioned details; see local controls'
 uv=me.uv_layers.new(name='MetricUV');scale=M[material].get('texture_repeat_m',4.)
 for p in me.polygons:
  axis=max(range(3),key=lambda j:abs(p.normal[j]));axes=([1,2] if axis==0 else [0,2] if axis==1 else [0,1])
  for j,li in enumerate(p.loop_indices):
   co=me.vertices[me.loops[li].vertex_index].co
   uv.data[li].uv=tuple(a/scale for a in uvs[p.index][j]) if uvs[p.index] is not None else (co[axes[0]]/scale,co[axes[1]]/scale)
  if p.area<1e-12:degenerate.append([name,p.index,p.area])
 for v in me.vertices:
  if not all(math.isfinite(x) for x in v.co):nonfinite.append(name)
 for u in uv.data:
  if not all(math.isfinite(x) for x in u.uv):uv_nonfinite.append(name)
 me.calc_loop_triangles()
 for tr in me.loop_triangles:
  tris+=1
  a,b,c=[uv.data[j].uv for j in tr.loops]
  uvarea=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5
  if tr.area<1e-12:degenerate.append([name,'triangle',tr.area])
  elif uvarea<1e-12:uv_collapsed.append([name,uvarea])
 stats=report['collections'].setdefault(group,{'objects':0,'vertices':0,'faces':0})
 stats['objects']+=1;stats['vertices']+=len(vv);stats['faces']+=len(ff)
 if any(len(p.vertices)>4 for p in me.polygons):
  mod=ob.modifiers.new('Portable tangent topology for caps','TRIANGULATE');mod.min_vertices=5
allv=[v for values in B.values() for v in values[0]]
report['bounds_m']={'min':[min(v[i] for v in allv) for i in range(3)],'max':[max(v[i] for v in allv) for i in range(3)]}
report['checks'].update({'local_preserves_GROUP':ns['GROUP']=='Local study sentinel','all_vertices_finite':not nonfinite,'all_uvs_finite':not uv_nonfinite,
 'degenerate_polygons_and_triangles':len(degenerate),'collapsed_uv_triangles':len(uv_collapsed),'triangles_tested':tris,
 'all_meshes_materialized_and_uv_mapped':all(o.data.materials and o.data.uv_layers for o in scene.objects if o.type=='MESH'),
 'reference_photos_loaded':any('research' in im.filepath or 'study_only' in im.filepath for im in bpy.data.images)})
report['degenerate_examples']=degenerate[:10];report['collapsed_uv_examples']=uv_collapsed[:10]
assert not nonfinite and not uv_nonfinite and not degenerate and not uv_collapsed,report['checks']
# Remove unused standard material/image resources loaded by the main helper prefix.
for m in list(bpy.data.materials):
 if m.users==0:bpy.data.materials.remove(m)
for im in list(bpy.data.images):
 if im.users==0:bpy.data.images.remove(im)
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
scene['project']='Michigan Central 2017 detached southern cargo-core study'
scene['status']='LOCAL STUDY ONLY; global placement and 2026 geometry unresolved'
scene['source_controls']=(ROOT/'manifests/south_structure/local_2017_controls.json').read_text()
scene['no_bush_roof']=True
world=bpy.data.worlds.new('Detachedstudy neutral environment');scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.57,.64,.73,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
sun=bpy.data.lights.new('Study sunlight','SUN');sun.energy=3.;sun.angle=.10;o=bpy.data.objects.new('Study sunlight',sun);scene.collection.objects.link(o);o.rotation_euler=(.35,-.6,-.4)
pos=(185.,-142.,130.);target=(0.,50.,-1.)
# South-facing overview includes30cargo doors and unroofed platform bands.
pos=(164.,264.,149.);target=(0.,50.,-1.)
d=bpy.data.cameras.new('detached_2017_south_overview');d.type='ORTHO';d.ortho_scale=220.;d.clip_end=1000
cam=bpy.data.objects.new('Camera detached2017southstudy',d);scene.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.cycles.max_bounces=4
scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=640;scene.render.resolution_y=480;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'qa/south_structure/detached_2017_core.png')
path=ROOT/'models/studies/michigan_central_2017_south_core_LOCAL_STUDY.blend';path.parent.mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(path))
report['blend']=str(path.relative_to(ROOT));report['preview']='qa/south_structure/detached_2017_core.png'
report['images_packed']=all(im.packed_file is not None for im in bpy.data.images if im.source=='FILE')
(ROOT/'manifests/south_structure/isolated_qa.json').write_text(json.dumps(report,indent=2))
if not SKIP_RENDER:bpy.ops.render.render(write_still=True)
print('SOUTH_STRUCTURE_QA',json.dumps(report),flush=True)
