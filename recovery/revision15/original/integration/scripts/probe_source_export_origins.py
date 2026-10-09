"""Read-only raw/evaluated mesh diagnostics for inherited UV/degenerate families.
No source file is saved or edited. Read data before and after inherited modifiers.
"""
import bpy,sys,json,math,numpy as np
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[1]
def stats(me):
 me.calc_loop_triangles();uv=me.uv_layers.active
 if uv is None:return {'missing_uv':True}
 p=np.empty(len(me.vertices)*3,dtype=np.float64);me.vertices.foreach_get('co',p);p=p.reshape(-1,3)
 idx=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',idx);idx=idx.reshape(-1,3)
 loops=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('loops',loops);loops=loops.reshape(-1,3)
 u=np.empty(len(uv.data)*2,dtype=np.float64);uv.data.foreach_get('uv',u);u=u.reshape(-1,2)
 a,b,c=p[idx[:,0]],p[idx[:,1]],p[idx[:,2]];area=np.linalg.norm(np.cross(b-a,c-a),axis=1)
 a,b,c=u[loops[:,0]],u[loops[:,1]],u[loops[:,2]];ua=np.abs((b[:,0]-a[:,0])*(c[:,1]-a[:,1])-(b[:,1]-a[:,1])*(c[:,0]-a[:,0]))
 result={'triangles':len(idx),'geometry_degenerate_under_1e_10':int(np.count_nonzero(area<1e-10)),'geometry_exact_zero':int(np.count_nonzero(area==0)),'uv_collapsed_under_1e_12':int(np.count_nonzero(ua<1e-12)),'uv_exact_zero':int(np.count_nonzero(ua==0)),'minimum_geometry_double_area':float(area.min()),'minimum_uv_double_area':float(ua.min()),'custom_normals':me.has_custom_normals}
 try:
  me.calc_tangents(uvmap=uv.name);t=np.empty(len(me.loops)*3,dtype=np.float64);me.loops.foreach_get('tangent',t);t=t.reshape(-1,3);n=np.array([tuple(v.vector) for v in me.corner_normals],dtype=np.float64);dot=np.abs((t*n).sum(1));length=np.linalg.norm(t,axis=1)
  result['blender_computed_tangents']={'loops':len(t),'zero_length':int(np.count_nonzero(length<1e-8)),'nonorthogonal_over_1e_4':int(np.count_nonzero(dot>1e-4)),'substantial_over_2e_4':int(np.count_nonzero(dot>2e-4)),'maximum_abs_normal_dot':float(dot.max())}
 except Exception as e:result['blender_tangent_probe_error']=repr(e)
 return result
rows=[]
for era in ['2017','2026']:
 source=R/f'models/checkpoints/revision15/michigan_central_{era}.blend';bpy.ops.wm.open_mainfile(filepath=str(source));dg=bpy.context.evaluated_depsgraph_get();baseline=json.loads((O/f'manifests/baseline_full_geometry_{era}.json').read_text())
 for row in baseline['primitives']:
  issues=row['issues'];severe=row['metrics'].get('max_abs_normal_tangent_dot',0)>2e-4
  if not ('degenerate triangle' in issues or 'collapsed UV triangle' in issues or severe):continue
  name=row['node_names'][0];ob=bpy.data.objects[name];raw=stats(ob.data);ev=ob.evaluated_get(dg);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
  evaluated=stats(me);ev.to_mesh_clear()
  rec={'era':era,'object':name,'export_mesh':row['mesh'],'material':row['material'],'normal_mapped':row['material_has_normal_texture'],'modifiers':[{'name':m.name,'type':m.type,'width':getattr(m,'width',None),'segments':getattr(m,'segments',None)} for m in ob.modifiers],'raw_source':raw,'evaluated_source':evaluated,'frozen_export_issues':{k:v['count'] for k,v in issues.items()},'frozen_export_triangles':row['triangles'],'frozen_export_max_normal_tangent_dot':row['metrics']['max_abs_normal_tangent_dot']}
  rows.append(rec);print('SOURCE_ORIGIN_PROBE',era,name,raw['geometry_degenerate_under_1e_10'],evaluated['geometry_degenerate_under_1e_10'],row['issues'].get('degenerate triangle',{}).get('count',0),flush=True)
result={'scope':'Read-only targeted original raw/evaluated data from revision15 with unchanged inherited object fingerprints. No repair or render performed. Tangent counts are mesh loops here versus unique export vertices in GLB, so do not directly subtract those counts.','thresholds':{'geometry_double_area':1e-10,'uv_double_area':1e-12,'normal_tangent_abs_dot':1e-4},'rows':rows}
(O/'manifests/source_export_origin_probe.json').write_text(json.dumps(result,indent=2));print('SOURCE_ORIGIN_PROBE_COMPLETE',len(rows),flush=True)
