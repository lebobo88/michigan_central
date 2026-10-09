"""Saved-scene check: open panes retain thickness, closed boxes do not get two skins."""
import bpy,sys,json,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from artifact_provenance import file_sha256
spec=importlib.util.spec_from_file_location('station_glass_check',R/'scripts/candidates/glass_shell_rules.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
era=sys.argv[sys.argv.index('--')+1];rows=[];issues=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or not any(m and m.name=='Glass clear' for m in ob.data.materials):continue
 st=mod.glass_mesh_topology(ob.data);sol=[m for m in ob.modifiers if m.type=='SOLIDIFY'];ok=(len(sol)==0 if st['closed'] else len(sol)==1 and abs(sol[0].thickness-.008)<1e-5)
 rows.append(dict(object=ob.name,topology=st,solidify_count=len(sol),passed=ok))
 if not ok:issues.append(ob.name)
r=dict(era=era,source_blend_sha256=file_sha256(bpy.data.filepath),passed=not issues,objects=rows,issues=issues,scope='Topological thickness rule only; not a calibrated optical or physical-glazing survey')
(R/f'manifests/glass_shell_checks_{era}.json').write_text(json.dumps(r,indent=2));print(json.dumps(dict(era=era,passed=r['passed'],count=len(rows),issues=issues)));assert r['passed']
