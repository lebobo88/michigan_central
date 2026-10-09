"""Read-only Blender structural checks. Not architectural or photorealism certification."""
import bpy,sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from artifact_provenance import file_sha256,surface_vertex_bounds
from mathutils import Vector
r=Path(__file__).resolve().parents[1];era=sys.argv[sys.argv.index('--')+1];s=bpy.context.scene
meshes=[o for o in s.objects if o.type=='MESH'];assert meshes
assert s.unit_settings.system=='METRIC' and s.unit_settings.scale_length==1
assert all(o.data.uv_layers for o in meshes)
assert all(math.isfinite(c) for o in meshes for v in o.data.vertices for c in v.co)
assert all(o.data.materials for o in meshes)
assert all(math.isfinite(c) for o in meshes for uv in o.data.uv_layers.active.data for c in uv.uv)
degenerate=[dict(object=o.name,count=sum(p.area<1e-10 for p in o.data.polygons)) for o in meshes]
degenerate=[q for q in degenerate if q['count']]
normal_issues=[o.name for o in meshes if any(not all(math.isfinite(c) for c in p.normal) for p in o.data.polygons)]
assert not normal_issues
images=[im for im in bpy.data.images if im.source=='FILE'];assert all(im.packed_file or im.packed_files for im in images)
# Reference photography must not be embedded as a material image.
assert not any('research' in im.filepath or 'study_only' in im.filepath for im in images)
for o in meshes:
 assert 'space' in o
# Simple line-of-sight reporting catches accidental connecting-wall obstructions.
deps=bpy.context.evaluated_depsgraph_get();rays=[]
for ob in s.objects:
 if ob.type!='CAMERA':continue
 d=ob.rotation_euler.to_quaternion()@Vector((0,0,-1));hit,loc,normal,face,target,matrix=s.ray_cast(deps,ob.location,d,distance=400)
 rays.append(dict(camera=ob.name,first_hit=target.name if hit else None,distance_m=round((loc-ob.location).length,3) if hit else None,interpretation='Diagnostic only. Natural columns, doors and ceilings can be valid first hits.'))
contact_checks=[]
for o in meshes:
 if o.name.startswith('interior column squared plinths') or o.name.startswith('ticket lobby paired columns shared stone plinths'):
  floor_z=.06 if o.get('space','').startswith('03 ') else .13 if o.get('space','').startswith('04 ') else None
  if floor_z is not None:
   measured=min((o.matrix_world@v.co).z for v in o.data.vertices);contact_checks.append(dict(object=o.name,space=o['space'],base_z=measured,floor_z=floor_z,gap_m=measured-floor_z));assert abs(measured-floor_z)<.001
surface_bounds=surface_vertex_bounds(meshes);export_bounds=surface_bounds['bounds_m']
report=dict(source_blend_sha256=file_sha256(bpy.data.filepath),era=era,blender=bpy.app.version_string,metric_units='passed',all_meshes_have_uvs_materials_finite_vertices='passed',all_file_images_packed='passed',no_reference_photographs_embedded='passed',mesh_objects=len(meshes),exported_mesh_bounds_m=export_bounds,bounds_method=surface_bounds['method'],unreferenced_vertex_diagnostic=surface_bounds['unreferenced_vertex_diagnostic'],column_floor_contact_checks=contact_checks,all_uv_coordinates_finite='passed',all_polygon_normals_finite='passed',degenerate_polygon_diagnostic=degenerate,camera_ray_diagnostics=rays,limitations=['No as-built certification','No every-room coverage claim','No manifoldness guarantee; architectural surface shells are intentional','Fine ornament and wear remain interpretive'])
(r/'manifests'/f'scene_validation_{era}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
