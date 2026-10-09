"""Per-detail evaluated transforms AND world-space bounds, never aggregate-only."""
import bpy,numpy as np,json
from pathlib import Path

def check_placements(reference_path,strict=True):
 reference=json.loads(Path(reference_path).read_text());bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows=[];errors=[]
 for rec in reference['objects']:
  ob=bpy.data.objects.get(rec['name'])
  if ob is None:errors.append({'name':rec['name'],'error':'missing object'});continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg);v=np.array([tuple(ev.matrix_world@p.co) for p in me.vertices],dtype=float);bounds=np.array([v.min(0),v.max(0)]);matrix=np.array(ev.matrix_world,dtype=float);dm=float(np.max(np.abs(matrix-np.array(rec['evaluated_matrix_world']))));db=float(np.max(np.abs(bounds-np.array(rec['evaluated_world_bounds']))))
  row={'name':ob.name,'evaluated_matrix_world':matrix.tolist(),'evaluated_world_bounds':bounds.tolist(),'matrix_max_delta':dm,'bounds_max_delta_m':db,'evaluated_vertices':len(v),'evaluated_polygons':len(me.polygons),'passed':dm<1e-5 and db<1e-5};ev.to_mesh_clear();rows.append(row)
  if not row['passed']:errors.append(row)
 report={'era':reference['era'],'study_blend_sha256':reference['study_blend_sha256'],'passed':not errors,'tolerance_m':1e-5,'matrix_tolerance':1e-5,'objects_checked':len(rows),'maximum_matrix_delta':max(r['matrix_max_delta'] for r in rows),'maximum_bounds_delta_m':max(r['bounds_max_delta_m'] for r in rows),'objects':rows,'errors':errors}
 if strict:assert not errors,errors[:3]
 return report
