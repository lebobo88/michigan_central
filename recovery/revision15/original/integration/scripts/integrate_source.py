"""Bounded revision15 integration. Never writes a revision14 artifact."""
import bpy,bmesh,sys,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];R=O.parents[1];ST=R/'manifests/concourse_portal_refinement/revision01';ERA=sys.argv[sys.argv.index('--')+1]
sys.path.insert(0,str(O/'scripts'));from apply_component_revision15 import apply_west_portal_detail
from placement_checks import check_placements
h=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
source=R/f'models/michigan_central_{ERA}.blend';dest=R/f'models/checkpoints/revision15/michigan_central_{ERA}.blend'
if dest.exists():
 assert '--replace-superseded' in sys.argv
 prior=json.loads((O/f'attempt01_superseded/manifests/integration_{ERA}.json').read_text());assert h(dest)==prior['revision15_sha256'], 'Refuse to overwrite an unrecognized file'
protected=json.loads((ST/'frozen_baseline.json').read_text())['protected'];assert h(source)==protected[str(source.relative_to(R))]
artifact=json.loads((ST/'artifact_manifest.json').read_text())['files']
for n in [f'concourse_west_portal_{ERA}_STUDY.blend','apply_component.py',f'qa_{ERA}.json']:assert h(ST/n)==artifact[n]['sha256'],n
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;assert s['era']==ERA;bpy.context.view_layer.update()

def signature(ob):
 d=hashlib.sha256();d.update(json.dumps({'type':ob.type,'matrix':[list(r) for r in ob.matrix_world],'parent':ob.parent.name if ob.parent else None,'hide_render':ob.hide_render,'space':ob.get('space'),'modifiers':[(m.name,m.type) for m in ob.modifiers]},sort_keys=True).encode())
 if ob.type=='MESH':
  me=ob.data
  for seq,prop,n,dtype in [(me.vertices,'co',3,np.float32),(me.loops,'vertex_index',1,np.int32),(me.polygons,'loop_start',1,np.int32),(me.polygons,'loop_total',1,np.int32),(me.polygons,'material_index',1,np.int32)]:
   a=np.empty(len(seq)*n,dtype=dtype);seq.foreach_get(prop,a);d.update(a.tobytes())
  for uv in me.uv_layers:
   a=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',a);d.update(uv.name.encode());d.update(a.tobytes())
  d.update(json.dumps([m.name if m else None for m in me.materials]).encode())
 return d.hexdigest()
original={o.name:signature(o) for o in s.objects};base_mesh_count=sum(o.type=='MESH' for o in s.objects)
old_ids={name:{x.as_pointer() for x in getattr(bpy.data,name)} for name in ['materials','meshes','images']}
result=apply_west_portal_detail(ERA,ST);bpy.context.view_layer.update();expected=[r['name'] for r in json.loads((ST/f'qa_{ERA}.json').read_text())['new_geometry']]
added=set(o.name for o in s.objects)-set(original);removed=set(original)-set(o.name for o in s.objects)
assert added==set(expected) and removed=={'concourse west small opening profiled lintel'},(added,removed)
parent=bpy.data.objects['05 CONCOURSE | source-informed masonry and floor'];assert parent.get('export_group')
for n in expected:
 ob=bpy.data.objects[n];world=ob.matrix_world.copy();ob.parent=parent;ob.matrix_world=world;ob['space']=parent.name;ob['era']=ERA;ob['revision15_role']='Bounded source-supported west portal detail; qualified dimensions and condition';ob.hide_select=False
bpy.context.view_layer.update()
placements=check_placements(O/f'manifests/study_placement_reference_{ERA}.json');(O/f'manifests/source_detail_placements_{ERA}.json').write_text(json.dumps(placements,indent=2))
changed=[n for n,sha in original.items() if n not in removed and signature(bpy.data.objects[n])!=sha];assert not changed,changed
assert sum(o.type=='MESH' for o in s.objects)==base_mesh_count+len(expected)-1
# New-material assignment must reuse existing source identities, not copies.
allowed_materials={f'Concourse terracotta dressings {ERA}',f'Concourse retained portal metal {ERA}'}
assert all(all(m and m.name in allowed_materials for m in bpy.data.objects[n].data.materials) for n in expected)
new_errors=[]
for n in expected:
 ob=bpy.data.objects[n];me=ob.data;bm=bmesh.new();bm.from_mesh(me);volume=bm.calc_volume(signed=True);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
 if bad or volume<=0:new_errors.append([n,bad,volume])
assert not new_errors,new_errors
# Precisely bounded open west passage, including the inherited vestibule fragment.
dg=bpy.context.evaluated_depsgraph_get();probes=[]
for z in [.20,1.70,2.45]:
 for y in [62.05,63.4,64.75]:
  hit,loc,n,idx,ob,m=s.ray_cast(dg,Vector((27.,y,z)),Vector((1,0,0)),distance=7.)
  probes.append({'y':y,'z':z,'hit':ob.name if hit else None});assert not hit,probes[-1]
# Neither newly authored side crown intrudes into either small aperture.
for y in [55.25,71.55]:
 for z in [.2,1.7,2.275]:
  for n in expected:
   ob=bpy.data.objects[n];inv=ob.matrix_world.inverted();a=inv@Vector((27.,y,z));b=inv@Vector((31.,y,z));hit,loc,normal,face=ob.ray_cast(a,(b-a).normalized(),distance=(b-a).length)
   assert not hit,(n,y,z,'new detail obstructs old small aperture')
assert (not any('West restored lower' in n for n in expected))==(ERA=='2017')
# Qualified study-close camera in the full model, no geometry hidden or moved.
camname='Camera concourse_portal_refinement';d=bpy.data.cameras.new(camname);cam=bpy.data.objects.new(camname,d);s.collection.objects.link(cam);cam.location=(20.2,58.3,3.15);target=Vector((29.15,63.3,3.45));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=37;d.clip_end=1000
s['revision']='revision15_concourse_only';s['revision14_parent_blend_sha256']=protected[str(source.relative_to(R))];s['revision15_concourse_study_manifest_sha256']=h(ST/'artifact_manifest.json');s['revision15_integration_script_sha256']=h(__file__);s['revision15_component_helper_sha256']=h(O/'scripts/apply_component_revision15.py');s['revision15_scope']='Only west concourse portal crown/panel/grille detail. North-pediment revision08 is not integrated. Unobserved west continuation remains unresolved.'
s['revision15_detail_qualification']='Source-relative geometry;2017 retained-shell persistence is qualified from2010/May2017 reference families;2026 restored grilles are not copied backward; no new image maps.'
# Remove only unreferenced datablocks introduced by append, never original ones.
cleanup=[]
for _ in range(3):
 for name in ['meshes','materials','images']:
  for x in list(getattr(bpy.data,name)):
   if x.as_pointer() not in old_ids[name] and x.users==0:
    cleanup.append([name,x.name]);getattr(bpy.data,name).remove(x)
assert not any('/research/' in im.filepath or 'study_only' in im.filepath for im in bpy.data.images)
for im in bpy.data.images:
 if im.source=='FILE' and not(im.packed_file or im.packed_files):im.pack()
bpy.context.preferences.filepaths.save_version=0;s.render.threads_mode='FIXED';s.render.threads=2;bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
report={'era':ERA,'source_revision14_sha256':h(source),'destination':str(dest.relative_to(R)),'revision15_sha256':h(dest),'base_mesh_count':base_mesh_count,'mesh_count':sum(o.type=='MESH' for o in s.objects),'new_meshes':expected,'removed_objects':sorted(removed),'unchanged_original_object_count':len(original)-len(removed),'changed_original_objects':changed,'every_detail_study_placement_verified':placements['passed'],'maximum_detail_world_bounds_delta_m':placements['maximum_bounds_delta_m'],'new_details_closed_outward_solids':True,'original_materials_reused':True,'west_passage_probes':probes,'new_detail_small_apertures_clear':True,'era_detail_split_valid':True,'append_only_cleanup':cleanup,'full_scene_integration':result,'source_bytes':dest.stat().st_size,'photoreal_or_complete_station_claim':False}
(O/f'manifests/integration_{ERA}.json').write_text(json.dumps(report,indent=2));print('INTEGRATION_SAVED',ERA,report['mesh_count'],report['source_bytes'],flush=True)
# Exact copies of established read-only checks write only under this revision15 root.
checks=['validate_scene.py','check_public_interfaces.py','check_floor_overlaps.py','check_era_conditions.py','check_uv_area.py','check_concourse_floor_material.py','check_field_material_scope.py','check_integrated_details.py','check_glass_shells.py','check_lobby_interfaces.py']
for name in checks:
 p=O/'scripts'/name;print('CHECK_START',name,flush=True);exec(compile(p.read_bytes(),str(p),'exec'),{'__file__':str(p),'__name__':'revision15_check_'+name[:-3]});print('CHECK_PASS',name,flush=True)
# Reporter-only scripts are strict gates here, without weakening their tests.
assert not json.loads((O/f'manifests/floor_overlap_{ERA}.json').read_text())['overlaps']
assert not [x for x in json.loads((O/f'manifests/public_interface_checks_{ERA}.json').read_text())['checks'] if x['status']=='REVIEW']
assert not json.loads((O/f'manifests/uv_area_{ERA}.json').read_text())['collapsed_uv_triangles']
assert not json.loads((O/f'manifests/scene_validation_{ERA}.json').read_text())['degenerate_polygon_diagnostic']
(O/f'manifests/source_qa_passed_{ERA}.json').write_text(json.dumps({'era':ERA,'passed':True,'source_sha256':h(dest),'checks':checks},indent=2));print('ALL_SOURCE_QA_PASS',ERA,flush=True)
