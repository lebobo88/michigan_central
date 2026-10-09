"""Seal only the corrected, actually imported and pixel-reviewed checkpoint."""
import hashlib,json,datetime
from pathlib import Path
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parents[1];R=O.parents[1];M=O/'manifests';h=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest();read=lambda n:json.loads((M/n).read_text())
rows=[];pairs=[];summaries=[];files=[]
for era in ['2017','2026']:
 line=read(f'export_lineage_{era}.json');source=R/line['source'];glb=R/line['export'];assert h(source)==line['source_sha256'] and h(glb)==line['glb_sha256'];files += [source,glb]
 qa=read(f'source_qa_passed_{era}.json');assert qa['passed'] and qa['source_sha256']==h(source)
 delta=read(f'revision15_full_geometry_{era}.json');assert delta['comparison']['passed'] and delta['sha256']==h(glb)
 for phase in ['source_detail','reopened_source','import_detail']:
  d=read(f'{phase}_placements_{era}.json');assert d['passed'] and d['objects_checked']==(48 if era=='2017' else 166) and d['maximum_matrix_delta']==0 and d['maximum_bounds_delta_m']==0
 material=read(f'material_identity_{era}.json');semantic=read(f'material_portability_{era}.json');assert material['all_inherited_material_graph_and_embedded_image_payloads_identical'] and material['revision15_glb_sha256']==h(glb) and semantic['passed'] and semantic['sha256']==h(glb)
 matches=[p for p in M.glob(f'khronos_{era}*.json') if json.loads(p.read_text()).get('artifact_sha256')==h(glb)];assert matches,era
 k=json.loads(matches[0].read_text());assert k['artifact_sha256']==h(glb) and k['issues']['numErrors']==k['issues']['numWarnings']==0 and not k['issues']['truncated']
 for mode in ['source','import']:
  rev=read(f'{mode}_review_{era}.json');assert rev['passed'] and rev['source_blend_sha256']==h(source) and rev['full_glb_sha256']==h(glb) and len(rev['renders'])==2
  if mode=='import':assert rev['every_detail_placement_verified'] and rev['maximum_detail_bounds_delta_m']==0 and len(rev['public_routes_rechecked'])==(18 if era=='2017' else 25)
  for render in rev['renders']:
   p=R/render['file'];assert h(p)==render['sha256'];files.append(p);rows.append({'era':era,'mode':mode,'file':render['file'],'sha256':render['sha256'],'pixel_inspected':True,'placement_corrected':True})
 for view in ['concourse_source_eye','concourse_portal_refinement']:
  a=np.array(Image.open(R/f'renders/revision15_concourse/source_{era}_{view}.png').convert('RGB'),dtype=np.float32);b=np.array(Image.open(R/f'renders/revision15_concourse/import_{era}_{view}.png').convert('RGB'),dtype=np.float32);pairs.append({'era':era,'view':view,'mean_absolute_rgb_difference_0_255':float(np.abs(a-b).mean()),'scope':'Diagnostic only; minor sampling differences are expected, not a substitute for pixel inspection'})
 summaries.append({'era':era,'source_sha256':h(source),'glb_sha256':h(glb),'new_detail_meshes':48 if era=='2017' else 166,'full_export_mesh_nodes':line['expected_mesh_nodes'],'new_detail_strict_clean':True,'inherited_payloads_unchanged':True,'full_export_globally_strict_clean':False,'khronos_errors':0,'khronos_warnings':0,'all_detail_world_transform_and_bounds_deltas':0.0,'material_count_unchanged':material['used_materials_after']})
retry=read('import_2026_retry_process_result.json');assert retry['exit_code']==0 and retry['signal'] is None and retry['quality_unchanged'] and not retry['geometry_hidden_removed_or_decimated'] and not retry['textures_resized']
frozen=read('frozen_inputs_verified.json')
for r in frozen['rows']:assert h(R/r['file'])==r['expected'],r['file']
frozen['reverified_at_seal_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(M/'frozen_inputs_verified.json').write_text(json.dumps(frozen,indent=2))
pixel={'status':'Passed corrected bounded-integration pixel review; no photoreal/full-station certification','rows':rows,'matched_pair_diagnostics':pairs,'observations':['Added panel borders and rails are visibly in the correct west-portal location in both source and actual-import views','Restored lower grilles appear only in2026;2017 retains open stripped lower side frames','Matched source/import views preserve the station context and public openings','Both eras retain unchanged known fidelity limitations, including pale2017 floor, simplified wear, dark restored portal detail and qualified glass response'],'remaining_risk':'Inherited full-export UV/tangent/degenerate-triangle defects remain explicit and require separate revision16 repair; clean Khronos and Blender previews do not erase those defects','failed_evidence':'attempt01_superseded and attempt02_memory_pressure are rejected/interrupted attempts, never accepted delivery images'}
(M/'PIXEL_REVIEW.json').write_text(json.dumps(pixel,indent=2))
plan=M/'INHERITED_EXPORT_DEFECTS_AND_REPAIR_PLAN.md';text=plan.read_text();start=text.index('Status:');end=text.index('\n\n',start);text=text[:start]+'Status: corrected revision15 concourse integration is sealed as a bounded WIP checkpoint. Source, per-detail placement, actual full-GLB import and eight matched render views passed. New details are strict-zero and all retained inherited payloads are byte-identical to revision14. The inherited full-export defects below are NOT repaired; revision15 is not globally strict-clean or a dependable finished asset. Earlier attempt01 hashes and placement passes are superseded evidence only.'+text[end:];plan.write_text(text)
files += [O/'README.md']+list((O/'scripts').glob('*.py'))+list(M.glob('*.json'))+list(M.glob('*.md'))
manifest={'revision':'revision15_concourse_only','sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Corrected bounded integration sealed; full-station fidelity and inherited strict-export defects remain open','summaries':summaries,'pixel_views_reviewed':len(rows),'frozen_inputs_unchanged':frozen['files'],'north_pediment_revision08_integrated':False,'variants_or_archives_repacked':False,'no_new_maps_or_private_continuation':True,'memory_retry':retry,'files':{str(p.relative_to(R)):{'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(set(files))}}
(O/'checkpoint_manifest.json').write_text(json.dumps(manifest,indent=2));print('REVISION15_SEALED',len(rows),len(files),json.dumps(summaries),flush=True)
