"""Actual empty-scene GLB import verification, no rendering or source appends."""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:raise RuntimeError("Optimized Python would disable required assertion gates")
import argparse,json,sys
from pathlib import Path
import bpy
PKG=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--era',required=True);ap.add_argument('--glb',required=True);ap.add_argument('--output',required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);OUT=Path(a.output);ERA=a.era
sys.path.insert(0,str(PKG/'scripts'));from glb_io import digest
sys.path.insert(0,str(PKG/'original/integration/scripts'));from placement_checks import check_placements
from bounded_import_checks import finite_and_bounds,BoundedRays
assert bpy.app.version==(5,2,2)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.edit.use_global_undo=False;bpy.ops.import_scene.gltf(filepath=str(a.glb));bpy.context.view_layer.update();s=bpy.context.scene
lineage=json.loads((PKG/f'original/integration/manifests/export_lineage_{ERA}.json').read_text());meshes=[o for o in s.objects if o.type=='MESH'];names={o.name for o in meshes}
assert names==set(lineage['mesh_node_names_expected']) and len(meshes)==lineage['expected_mesh_nodes']
assert sum(bool(o.get('export_group')) for o in s.objects)==lineage['expected_group_count']
assert sum(bool(o.get('export_coverage_marker')) for o in s.objects)==lineage['expected_marker_count']
assert all(o.data.uv_layers and o.data.materials for o in meshes)
bounds,vertices=finite_and_bounds(meshes);want=json.loads((PKG/f'original/integration/manifests/scene_validation_{ERA}.json').read_text())['exported_mesh_bounds_m'];delta=max(abs(x-y) for aa,bb in zip(bounds,want) for x,y in zip(aa,bb));assert delta<.02
placement=check_placements(PKG/f'original/integration/manifests/study_placement_reference_{ERA}.json');(OUT/'manifests/import_detail_placements.json').write_text(json.dumps(placement,indent=2)+'\n')
assert all(bpy.data.objects[n].get('era')==ERA for n in lineage['new_detail_names'])
assert (not any('West restored lower' in n for n in names))==(ERA=='2017')
rays=BoundedRays(meshes)
for z in [.2,1.7,2.45]:
    for y in [62.05,63.4,64.75]:assert not rays.hits((27.,y,z),(34.,y,z))
routes=json.loads((PKG/f'original/integration/manifests/public_interface_checks_{ERA}.json').read_text())['checks']
for route in routes:
    hits={h['object'] for h in rays.hits(route['from_m'],route['to_m'])};expected={h['object'] for h in route['hits']};assert not hits-expected,(route['connection'],hits-expected)
r={'passed':True,'era':ERA,'glb_sha256':digest(a.glb),'blender_version_tuple':list(bpy.app.version),'actual_empty_scene_import':True,'meshes':len(meshes),'public_routes_checked':len(routes),'west_passage_probes':9,'details_checked':len(lineage['new_detail_names']),'bounds_max_delta_m':delta,'vertices_checked':vertices,'rendered':False,'pixels_not_validated_for_this_reconstruction':True}
(OUT/'manifests/import_recovery.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
