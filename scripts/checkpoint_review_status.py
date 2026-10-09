"""Create a source-hash-bound immutable technical checkpoint for both eras.
Run only after all scene, material, export and render checks finish.
"""
from pathlib import Path
import json,sys,shutil
from artifact_provenance import file_sha256
R=Path(__file__).resolve().parents[1];rev=sys.argv[1];views=sys.argv[2:] or ['front','hall_reverse']
D=R/'manifests/checkpoints'/rev;D.mkdir(parents=True,exist_ok=True)
rows=[];files=[]
for E in ['2017','2026']:
 B=R/f'models/michigan_central_{E}.blend';sha=file_sha256(B)
 reportnames=[f'{base}_{E}.json' for base in ['scene_validation','uv_area','public_interface_checks','floor_overlap','hall_roof_clearance','era_condition_checks','glb_roundtrip','export_lineage','metrics','packed_material_inventory','field_material_scope','exterior_plinth_contact','north_upper_contact','concourse_floor_material','glass_shell_checks','lobby_interface_checks','material_portability_full','material_portability_preview_lod','material_portability_compact_review']]+[f'khronos_{E}_{kind}.json' for kind in ['full','preview_lod','compact_review']]
 reports={}
 for name in reportnames:
  source=R/'manifests'/name;assert source.exists(),source
  data=json.loads(source.read_text());reports[name]=data
  if 'source_blend_sha256' in data:assert data['source_blend_sha256']==sha,(name,'source hash mismatch')
  target=D/name
  if target.exists():assert target.read_bytes()==source.read_bytes(),('immutable checkpoint changed',target)
  else:shutil.copy2(source,target)
  files.append(dict(file=str(target.relative_to(R)),sha256=file_sha256(target)))
 assert reports[f'exterior_plinth_contact_{E}.json']['passed'] and reports[f'north_upper_contact_{E}.json']['passed'] and reports[f'concourse_floor_material_{E}.json']['passed']
 assert reports[f'glass_shell_checks_{E}.json']['passed'] and reports[f'lobby_interface_checks_{E}.json']['passed'] and reports[f'material_portability_full_{E}.json']['passed']
 sc=reports[f'scene_validation_{E}.json'];uv=reports[f'uv_area_{E}.json']
 assert not sc['degenerate_polygon_diagnostic'] and not uv['collapsed_uv_triangles']
 assert not sc['unreferenced_vertex_diagnostic']
 assert not reports[f'floor_overlap_{E}.json']['overlaps']
 assert all(q['status']!='REVIEW' for q in reports[f'public_interface_checks_{E}.json']['checks'])
 glbs={}
 for kind in ['full','preview_lod','compact_review']:
  suffix='' if kind=='full' else '_'+kind;g=R/f'exports/michigan_central_{E}{suffix}.glb'
  k=reports[f'khronos_{E}_{kind}.json'];assert k['issues']['numErrors']==0 and k['issues']['numWarnings']==0 and not k['issues'].get('truncated',False)
  _gsha=file_sha256(g);assert k['artifact_sha256']==_gsha and k['artifact_bytes']==g.stat().st_size,('validator artifact mismatch',g)
  glbs[kind]=dict(file=str(g.relative_to(R)),bytes=g.stat().st_size,sha256=_gsha)
 for _kind in ['full','preview_lod','compact_review']:
  _semantic=reports[f'material_portability_{_kind}_{E}.json'];assert _semantic['passed'] and _semantic['sha256']==glbs[_kind]['sha256']
 assert reports[f'glb_roundtrip_{E}.json']['glb_sha256']==glbs['compact_review']['sha256'],'Stale actual-import report'
 renderrows=[]
 for view in views:
  p=R/f'renders/{rev}/{E}_{view}.png';m=p.with_suffix('.json');assert p.exists() and m.exists()
  data=json.loads(m.read_text());assert data['source_blend_sha256']==sha
  renderrows.append(dict(file=str(p.relative_to(R)),sha256=file_sha256(p),metadata=str(m.relative_to(R)),camera=view,exposure=data['runtime_exposure'],helper_sha256=data['render_helper_sha256'],lighting_sha256=data['render_lighting_sha256']))
 rows.append(dict(era=E,source_blend_sha256=sha,build_code_sha256=json.loads((R/f'renders/{rev}/{E}_{views[0]}.json').read_text())['build_code_sha256'],exports=glbs,renders=renderrows,roundtrip_surface_envelope_delta_m=reports[f'glb_roundtrip_{E}.json']['max_envelope_difference_m'],uncapped_khronos='Zero errors and warnings in all three exports; informational unused-attribute notices retained',source_unreferenced_vertices=0,source_degenerate_polygons=0,packed_images=reports[f'packed_material_inventory_{E}.json']['file_images']))
assert len({q['build_code_sha256'] for q in rows})==1,'Era builds have different builder code'
summary=dict(status=f'Synchronized {rev} WIP; full requested architectural and photoreal scope remains open',matched_render_directory=f'renders/{rev}',technical_checkpoint=rows,immutable_report_files=files,bounds_method='Actual polygon-referenced vertices transformed to world space;2 cm conversion tolerance. This checks format transfer, not architectural survey accuracy',image_comparison='Fixed named cameras.2017 Grand Hall uses exposure1.6; lift lobby uses0.8/0.6 for2017/2026; other cameras use0.4. Actual per-frame light states and exposure are recorded in image metadata.',coverage='manifests/space_completeness_qa.json',source_gaps='manifests/source_gaps.json',remaining=['Exact ornament/carving profiles and material reflectance are approximate','2017 wear/scuff placement is original interpretation, with explicitly dated condition evidence separated','Concourse longitudinal bracing, exact floor setting-out and fine metal/terracotta ornament remain unmeasured; west onward circulation is unresolved','Private/hidden rooms and full tenant suites require additional plan/photo coverage','Southern platform/deck global registration and current deck dimensions remain unresolved'])
p=R/f'manifests/review_checkpoint_summary_{rev}.json';assert not p.exists(),p;p.write_text(json.dumps(summary,indent=2));(R/'manifests/live_build_status.json').write_text(json.dumps(summary,indent=2));print(p)
