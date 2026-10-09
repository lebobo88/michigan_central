import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[1];ST=R/'manifests/concourse_portal_refinement/revision01';manifest=json.loads((ST/'artifact_manifest.json').read_text())['files']
for era in ['2017','2026']:
 source=ST/f'concourse_west_portal_{era}_STUDY.blend';sha=hashlib.file_digest(source.open('rb'),'sha256').hexdigest();assert sha==manifest[source.name]['sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows=[]
 for rec in json.loads((ST/f'qa_{era}.json').read_text())['new_geometry']:
  ob=bpy.data.objects[rec['name']];ev=ob.evaluated_get(dg);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg);v=np.array([tuple(ev.matrix_world@p.co) for p in me.vertices],dtype=float)
  rows.append({'name':ob.name,'matrix_world':[list(r) for r in ob.matrix_world],'evaluated_matrix_world':[list(r) for r in ev.matrix_world],'evaluated_world_bounds':[v.min(0).tolist(),v.max(0).tolist()],'evaluated_vertices':len(v),'evaluated_polygons':len(me.polygons)});ev.to_mesh_clear()
 (O/f'manifests/study_placement_reference_{era}.json').write_text(json.dumps({'era':era,'study_blend_sha256':sha,'scope':'Every approved appended detail, evaluated after view-layer update','objects':rows},indent=2));print('PLACEMENT_REFERENCE',era,len(rows),flush=True)
