"""Actual full-GLB empty-scene import, semantic QA, then source-matched rendering.
No station geometry is hidden or moved for rendering. Only the original render-
context ground, lights, world and two cameras are supplied from the saved source.
"""
import bpy,sys,json,math,argparse,gc,resource,time
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];R=O.parents[1];sys.path.insert(0,str(R/'scripts'))
from artifact_provenance import file_sha256,surface_vertex_bounds
sys.path.insert(0,str(O/'scripts'));from bounded_import_checks import finite_and_bounds,BoundedRays
def checkpoint(stage):
 status=Path('/proc/self/status').read_text();rss=[r for r in status.splitlines() if r.startswith(('VmRSS:','VmHWM:'))];print('MEMORY_STAGE',stage,rss,'max_rss_kib',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,flush=True)
assert not (O/'HOLD_FOR_PLACEMENT_CORRECTION').exists(), 'Superseded placement attempt; hold for corrected source/export'
ap=argparse.ArgumentParser();ap.add_argument('--era',required=True);ap.add_argument('--mode',choices=['source','import'],required=True);ap.add_argument('--render',action='store_true');ap.add_argument('--width',type=int,default=1000);ap.add_argument('--samples',type=int,default=16);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);ERA=args.era
src=R/f'models/checkpoints/revision15/michigan_central_{ERA}.blend';glb=R/f'exports/revision15/michigan_central_{ERA}.glb';lineage=json.loads((O/f'manifests/export_lineage_{ERA}.json').read_text());assert file_sha256(src)==lineage['source_sha256'];assert file_sha256(glb)==lineage['glb_sha256']
views=['concourse_source_eye','concourse_portal_refinement'];source_qa=json.loads((O/f'manifests/scene_validation_{ERA}.json').read_text())
report={'era':ERA,'mode':args.mode,'source_blend_sha256':lineage['source_sha256'],'full_glb_sha256':lineage['glb_sha256'],'renders':[]}
if args.mode=='source':bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
else:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.edit.use_global_undo=False;s=bpy.context.scene;checkpoint('before_import');bpy.ops.import_scene.gltf(filepath=str(glb));gc.collect();bpy.context.view_layer.update();checkpoint('after_import_gc')
 meshes=[o for o in s.objects if o.type=='MESH'];names={o.name for o in meshes};expected=set(lineage['mesh_node_names_expected']);missing=sorted(expected-names);extra=sorted(names-expected)
 assert not missing and not extra,(missing,extra)
 assert all(o.data.uv_layers and o.data.materials for o in meshes)
 bounds,vertices_checked=finite_and_bounds(meshes);checkpoint('after_streamed_finite_bounds')
 groups=[o.name for o in s.objects if o.get('export_group')];markers=[o.name for o in s.objects if o.get('export_coverage_marker')]
 assert len(groups)==lineage['expected_group_count'];assert len(markers)==lineage['expected_marker_count']
 want=source_qa['exported_mesh_bounds_m'];deviation=max(abs(a-b) for aa,bb in zip(bounds,want) for a,b in zip(aa,bb));assert deviation<.02,(bounds,want,deviation)
 assert all(bpy.data.objects[n].get('era')==ERA for n in lineage['new_detail_names'])
 assert (not any('West restored lower' in n for n in names))==(ERA=='2017')
 rays=BoundedRays(meshes);hits=[]
 for z in [.2,1.7,2.45]:
  for y in [62.05,63.4,64.75]:
   hits+=rays.hits((27.,y,z),(34.,y,z))
 assert not hits,hits
 checkpoint('after_west_bounded_rays')
 report.update(empty_scene_import=True,mesh_nodes=len(meshes),room_groups=len(groups),coverage_markers=len(markers),all_mesh_names_match=True,all_meshes_have_uv_materials_finite_vertices=True,bounds_m=bounds,source_bounds_m=want,max_envelope_difference_m=deviation,west_nine_passage_probes_clear=True,new_detail_era_split_valid=True)
 sys.path.insert(0,str(O/'scripts'));from placement_checks import check_placements
 placement=check_placements(O/f'manifests/study_placement_reference_{ERA}.json');(O/f'manifests/import_detail_placements_{ERA}.json').write_text(json.dumps(placement,indent=2));report['every_detail_placement_verified']=placement['passed'];report['maximum_detail_bounds_delta_m']=placement['maximum_bounds_delta_m']
 # Repeat all existing source-tested public routes in the actual import.
 routes=json.loads((O/f'manifests/public_interface_checks_{ERA}.json').read_text())['checks'];route_rows=[]
 for route in routes:
  actual_hits=[hit['object'] for hit in rays.hits(route['from_m'],route['to_m'])]
  expected_hits={row['object'] for row in route['hits']};unexpected=set(actual_hits)-expected_hits
  assert not unexpected,(route['connection'],unexpected,expected_hits)
  route_rows.append({'connection':route['connection'],'actual_objects_hit':actual_hits,'source_expected_objects_hit':sorted(expected_hits),'no_new_obstruction':True})
 report['public_routes_rechecked']=route_rows;report['import_ray_method']='Exact object ray tests with conservative segment/AABB pruning; no scene geometry hidden or removed';del rays;gc.collect();checkpoint('after_all_route_checks')
 # Match source lighting without importing source station meshes a second time.
 lightnames=[r['name'] for r in json.loads((R/f'renders/revision14/{ERA}_concourse_source_eye.json').read_text())['light_state']]
 wanted=lightnames+['Camera '+v for v in views]+['landscape context']
 with bpy.data.libraries.load(str(src),link=False) as (a,b):
  assert not(set(wanted)-set(a.objects)),set(wanted)-set(a.objects);b.objects=wanted.copy()
  wn=[n for n in a.worlds if n.startswith('Generic daylight')];assert len(wn)==1,wn;b.worlds=wn
 for ob in b.objects:s.collection.objects.link(ob)
 s.world=b.worlds[0];s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s['era']=ERA
 report['render_context_from_source_only']=[ob.name for ob in b.objects];report['source_station_geometry_appended_for_render']=False
 after_context={o.name for o in s.objects if o.type=='MESH'};assert after_context-names=={'landscape context'} and names<=after_context
 before_objects={o.name for o in s.objects};gc.collect();purged=bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True);assert before_objects=={o.name for o in s.objects};report['unused_in_memory_datablocks_purged']=purged;checkpoint('after_lighting_context_and_orphan_purge')
gc.collect();checkpoint('before_cycles_setup');s.render.use_persistent_data=False;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.cycles.max_bounces=8;s.cycles.transmission_bounces=6;s.cycles.transparent_max_bounces=8;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=args.width;s.render.resolution_y=round(args.width*.68);s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
ns={};exec((R/'scripts/render_lighting.py').read_text(),ns)
for view in views:
 s.camera=bpy.data.objects['Camera '+view];ns['apply_camera_fill_mode'](s,view);p=R/f'renders/revision15_concourse/{args.mode}_{ERA}_{view}.png';s.render.filepath=str(p)
 if args.render:
  assert not p.exists(),str(p);gc.collect();checkpoint('before_render_'+view);bpy.ops.render.render(write_still=True);checkpoint('after_render_'+view);report['renders'].append({'file':str(p.relative_to(R)),'sha256':file_sha256(p),'camera_location':list(s.camera.location),'camera_rotation':list(s.camera.rotation_euler),'lens_mm':s.camera.data.lens,'exposure':s.view_settings.exposure,'samples':args.samples,'resolution':[args.width,round(args.width*.68)]})
report['passed']=True;report['scope']='Full scene import/lineage and matched two-camera review. Inherited exported strict numerical defects are reported separately; not photoreal or complete-station certification.'
p=O/f'manifests/{args.mode}_review_{ERA}.json';p.write_text(json.dumps(report,indent=2));print('REVIEW_PASS',args.mode,ERA,flush=True)
