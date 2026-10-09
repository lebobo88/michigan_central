"""Read compact review GLBs back through Blender's actual glTF importer."""
import bpy,sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from artifact_provenance import file_sha256,surface_vertex_bounds
from mathutils import Vector
R=Path(__file__).resolve().parents[1];era=sys.argv[sys.argv.index('--')+1];p=R/'exports'/f'michigan_central_{era}_compact_review.glb'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(p))
mesh=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert mesh
assert all(o.data.uv_layers for o in mesh);assert all(o.data.materials for o in mesh)
assert all(math.isfinite(q) for o in mesh for v in o.data.vertices for q in v.co)
surface_bounds=surface_vertex_bounds(mesh);bounds=surface_bounds['bounds_m']
markers=[o.name for o in bpy.context.scene.objects if o.get('export_coverage_marker')];groups=[o.name for o in bpy.context.scene.objects if o.get('export_group')]
assert len(markers)>=8;assert groups
original=json.loads((R/'manifests'/f'scene_validation_{era}.json').read_text())['exported_mesh_bounds_m'];deviation=max(abs(bounds[j][i]-original[j][i]) for j in range(2) for i in range(3))
# Microdetail removal may change a small protrusion, but must not rescale/rotate the building.
assert deviation<.02, (bounds,original,deviation)
report=dict(glb_sha256=file_sha256(p),source_blend_sha256=json.loads((R/'manifests'/f'scene_validation_{era}.json').read_text()).get('source_blend_sha256'),era=era,file=str(p.relative_to(R)),blender=bpy.app.version_string,import_status='passed',finite_meshes_uvs_materials='passed',mesh_count=len(mesh),room_groups=len(groups),unresolved_coverage_markers=markers,bounds_method=surface_bounds['method'],bound_tolerance_m=.02,bounds_m=bounds,source_bounds_m=original,max_envelope_difference_m=deviation,limit='Tests actual Blender import, metadata and broad metric envelope; does not certify every rendered material or architectural detail.')
(R/'manifests'/f'glb_roundtrip_{era}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
