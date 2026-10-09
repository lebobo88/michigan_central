"""One canonical full export per era, preserving original source custom normals."""
import bpy,sys,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[1];ERA=sys.argv[sys.argv.index('--')+1]
sys.path.insert(0,str(R/'scripts'));from artifact_provenance import file_sha256
from repair_glb_tangents import repair_glb_tangents
source=R/f'models/checkpoints/revision15/michigan_central_{ERA}.blend';out=R/f'exports/revision15/michigan_central_{ERA}.glb'
if out.exists():
 assert '--replace-superseded' in sys.argv
 prior=json.loads((O/f'attempt01_superseded/manifests/export_lineage_{ERA}.json').read_text());assert file_sha256(out)==prior['glb_sha256'], 'Refuse to overwrite an unrecognized export'
qa=json.loads((O/f'manifests/source_qa_passed_{ERA}.json').read_text());assert qa['passed'] and qa['source_sha256']==file_sha256(source)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;assert s.get('revision')=='revision15_concourse_only';assert s.get('era')==ERA
sys.path.insert(0,str(O/'scripts'));from placement_checks import check_placements
placements=check_placements(O/f'manifests/study_placement_reference_{ERA}.json');(O/f'manifests/reopened_source_placements_{ERA}.json').write_text(json.dumps(placements,indent=2))
bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');selected=[]
for ob in s.objects:
 if (ob.type=='MESH' and ob.name!='landscape context') or ob.get('export_group') or ob.get('export_coverage_marker'):
  ob.hide_select=False;ob.select_set(True);selected.append(ob.name)
expected_meshes=[ob.name for ob in s.objects if ob.type=='MESH' and ob.name!='landscape context'];study=json.loads((R/f'manifests/concourse_portal_refinement/revision01/qa_{ERA}.json').read_text());added=[row['name'] for row in study['new_geometry']]
assert all(n in selected for n in added)
modifier_inventory=[{'object':ob.name,'mesh':ob.data.name,'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),'custom_normals':ob.data.has_custom_normals,'modifiers':[{'name':m.name,'type':m.type,'render':m.show_render,'viewport':m.show_viewport} for m in ob.modifiers]} for ob in s.objects if ob.type=='MESH']
(O/f'manifests/source_modifier_inventory_{ERA}.json').write_text(json.dumps(modifier_inventory,indent=2))
bpy.ops.export_scene.gltf(use_selection=True,filepath=str(out),export_format='GLB',export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True)
repair=repair_glb_tangents(out,O/f'manifests/zero_tangent_repair_{ERA}.json')
report={'era':ERA,'source':str(source.relative_to(R)),'source_sha256':file_sha256(source),'export':str(out.relative_to(R)),'glb_sha256':file_sha256(out),'bytes':out.stat().st_size,'mesh_node_names_expected':expected_meshes,'expected_mesh_nodes':len(expected_meshes),'expected_group_count':sum(bool(o.get('export_group')) for o in s.objects),'expected_marker_count':sum(bool(o.get('export_coverage_marker')) for o in s.objects),'new_detail_names':added,'source_saved_before_export':True,'source_normals_or_modifiers_recomputed':False,'export_applies_inherited_modifiers':True,'baseline_zero_tangent_repair_only':repair,'full_numerical_strict_status':'Pending baseline-delta audit; do not infer a globally clean result from Khronos conformance','export_helper_sha256':file_sha256(__file__)}
(O/f'manifests/export_lineage_{ERA}.json').write_text(json.dumps(report,indent=2));print('REVISION15_EXPORTED',ERA,report['expected_mesh_nodes'],report['bytes'],flush=True)
