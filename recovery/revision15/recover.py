#!/usr/bin/env python3
"""Explicit future recovery driver. Source-only unless --export is requested."""
import sys
sys.dont_write_bytecode = True
import argparse,json,shutil,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
PKG=Path(__file__).resolve().parent;sys.path.insert(0,str(PKG/'scripts'))
from glb_io import digest
from verify_package import verify_directory
from verify_references import verify as verify_refs

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--blender',required=True,help='Path to Blender 5.2.2 executable');p.add_argument('--era',choices=['2017','2026'],required=True);p.add_argument('--r14-blend',required=True);p.add_argument('--output',required=True,help='NEW directory; must not exist');p.add_argument('--export',action='store_true',help='Also export full GLB, restore guarded 2026 arrays, compare payloads, and actual-import check');a=p.parse_args()
    verify_directory(PKG);verify_refs();source=Path(a.r14_blend).resolve();out=Path(a.output).resolve();pin=json.loads((PKG/'recovery_contract.json').read_text())['inputs'][a.era]
    if not source.is_file() or digest(source)!=pin['r14_blend_sha256']:raise ValueError('R14 BLEND is absent or its pinned SHA-256 differs')
    if out.exists() or out==PKG or PKG in out.parents:raise ValueError('Use a new output directory outside this checkpoint package')
    blender=shutil.which(a.blender) if not Path(a.blender).is_file() else str(Path(a.blender).resolve())
    if not blender:raise ValueError('Blender executable not found')
    out.mkdir(parents=True,exist_ok=False)
    def run(script,args,log):
        cmd=[blender,'--background','--threads','2','--python-exit-code','1','--python',str(PKG/'scripts'/script),'--']+args
        with (out/log).open('x') as stream:
            import os
            env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env.pop('PYTHONOPTIMIZE',None)
            result=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,check=False,env=env)
        if result.returncode:raise RuntimeError(f'Blender failed ({result.returncode}); see {out/log}. Output is partial and unaccepted.')
    args=['--era',a.era,'--r14',str(source),'--output',str(out)]+(['--export'] if a.export else [])
    run('replay_blender.py',args,'source_replay.log')
    source_report_path=out/'manifests/source_recovery.json';blend=out/f'michigan_central_{a.era}_recovered.blend'
    if not source_report_path.is_file() or not blend.is_file():raise RuntimeError('Blender exited without required source result files')
    sr=json.loads(source_report_path.read_text())
    required={'era':a.era,'source_replay_passed':True,'source_sha256':digest(blend),'r14_sha256':pin['r14_blend_sha256'],'new_details':pin['expected_new_meshes'],'all_retained_object_signatures_unchanged':True,'every_detail_source_and_reopened_matrix_and_bounds_checked':True,'blender_version_tuple':[5,2,2]}
    if any(sr.get(k)!=v for k,v in required.items()):raise RuntimeError('Saved source result contract/hash mismatch')
    for stage in ['source_detail_placements.json','reopened_detail_placements.json']:
        pr=json.loads((out/'manifests'/stage).read_text())
        if not pr.get('passed') or pr.get('objects_checked')!=pin['expected_new_meshes']:raise RuntimeError('Placement report missing/failing')
    if a.export:
        raw=out/f'michigan_central_{a.era}_raw.glb';final=out/f'michigan_central_{a.era}_recovered.glb'
        if a.era=='2026':
            from preserve_2026 import recover;recover(raw,final,out/'manifests/preservation_recovery.json')
        else:raw.rename(final)
        from verify_glb import verify
        r=verify(final,a.era);(out/'manifests/exact_export_reference_check.json').write_text(json.dumps(r,indent=2)+'\n')
        run('import_check_blender.py',['--era',a.era,'--glb',str(final),'--output',str(out)],'actual_import.log')
        import_path=out/'manifests/import_recovery.json'
        if not import_path.is_file():raise RuntimeError('Blender exited without required import report')
        ir=json.loads(import_path.read_text())
        required={'passed':True,'era':a.era,'glb_sha256':digest(final),'blender_version_tuple':[5,2,2],'actual_empty_scene_import':True,'details_checked':pin['expected_new_meshes'],'meshes':pin['expected_r15_meshes']-1}
        if any(ir.get(k)!=v for k,v in required.items()):raise RuntimeError('Actual import report contract/hash mismatch')
        pr=json.loads((out/'manifests/import_detail_placements.json').read_text())
        if not pr.get('passed') or pr.get('objects_checked')!=pin['expected_new_meshes']:raise RuntimeError('Actual import placement report missing/failing')
    if digest(source)!=pin['r14_blend_sha256']:raise ValueError('Input source changed during recovery')
    result={'era':a.era,'source_recovery_validated':True,'export_and_actual_import_validated':a.export,'output':str(out),'rendered':False,'matched_pixel_acceptance_for_reconstruction':False,'binary_identical_blend_claim':False,'full_station_finished':False,'inherited_export_defects_repaired':False}
    (out/'RECOVERY_RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
