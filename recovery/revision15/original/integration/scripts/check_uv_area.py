"""UV-area diagnostic, triangulated source mesh without destructively changing editable topology."""
import bpy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from artifact_provenance import file_sha256
r=Path(__file__).resolve().parents[1];era=sys.argv[sys.argv.index('--')+1];rows=[];total=0;bad=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 me=o.data;me.calc_loop_triangles();uv=me.uv_layers.active.data;n=0
 for t in me.loop_triangles:
  if t.area<1e-12:continue
  a,b,c=[uv[i].uv for i in t.loops];area=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5
  total+=1
  if area<1e-12:n+=1;bad+=1
 if n:rows.append(dict(object=o.name,collapsed_uv_triangles=n,triangles=len(me.loop_triangles),material=me.materials[0].name))
rows.sort(key=lambda q:-q['collapsed_uv_triangles'])
report=dict(source_blend_sha256=file_sha256(bpy.data.filepath),era=era,triangles_tested=total,collapsed_uv_triangles=bad,ratio=bad/max(1,total),objects=rows,limit='Finite nonzero triangle UV area is necessary but not sufficient for seam quality, physical scale, or distortion. This checks authored source before modifiers.')
(r/'manifests'/f'uv_area_{era}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
