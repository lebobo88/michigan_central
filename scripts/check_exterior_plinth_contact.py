"""Actual saved-mesh plinth/apron contact checks, not surveyed site elevations."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from artifact_provenance import file_sha256
E=sys.argv[sys.argv.index('--')+1];s=bpy.context.scene;assert E==s['era']
o=bpy.data.objects.get('exterior column plinths');assert o and o.type=='MESH'
me=o.data;adj=[set() for _ in me.vertices]
for e in me.edges:
 a,b=e.vertices;adj[a].add(b);adj[b].add(a)
remaining=set(range(len(me.vertices)));groups=[]
while remaining:
 stack=[remaining.pop()];ids=[]
 while stack:
  i=stack.pop();ids.append(i)
  for j in adj[i]:
   if j in remaining:remaining.remove(j);stack.append(j)
 groups.append(ids)
assert len(groups)==14,('expected fourteen monumental exterior plinths',len(groups))
accepted=('2017 broad paved station apron','2017 central flagpole plaza and side lobes','north forecourt gray paved apron','central entrance apron with curved side notches')
floors=[q for q in s.objects if q.type=='MESH' and any(q.name.startswith(n) for n in accepted)];assert floors
verts=[];faces=[]
for q in floors:
 off=len(verts);verts.extend([tuple(q.matrix_world@v.co) for v in q.data.vertices])
 for p in q.data.polygons:
  n=q.matrix_world.to_3x3()@p.normal
  if n.z>.999:faces.append(tuple(off+i for i in p.vertices))
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False)
rows=[];issues=[]
for ids in groups:
 points=[o.matrix_world@me.vertices[i].co for i in ids];mins=[min(p[k] for p in points) for k in range(3)];maxs=[max(p[k] for p in points) for k in range(3)]
 x=(mins[0]+maxs[0])/2;y=(mins[1]+maxs[1])/2;dx=(maxs[0]-mins[0])*.4;dy=(maxs[1]-mins[1])*.4;samples=[]
 for xx,yy in [(x,y),(x-dx,y-dy),(x-dx,y+dy),(x+dx,y-dy),(x+dx,y+dy)]:
  hit,n,face,distance=bvh.ray_cast(Vector((xx,yy,5)),Vector((0,0,-1)),10)
  if hit is None:issues.append(dict(x=xx,y=yy,reason='No actual apron under footing'));continue
  gap=mins[2]-hit.z
  samples.append(dict(x=xx,y=yy,apron_top_z_m=hit.z,plinth_bottom_z_m=mins[2],gap_m=gap))
  if gap>.002 or gap<-.08:issues.append(dict(x=xx,y=yy,gap_m=gap,reason='Visible air gap or unexpectedly deep model embedding'))
 rows.append(dict(center_x=x,center_y=y,bounds_m=[mins,maxs],samples=samples))
report=dict(era=E,source_blend_sha256=file_sha256(bpy.data.filepath),passed=not issues,plinth_components=len(groups),actual_apron_objects=[q.name for q in floors],checks=rows,issues=issues,limits='Tests physical contact against the actual authored paving mesh at five points per plinth. Accepts small foundation embedding; does not establish surveyed ground levels, pedestal profiles or the published40ft measurement convention.')
(R/'manifests'/f'exterior_plinth_contact_{E}.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(era=E,passed=not issues,plinths=len(groups),issues=len(issues)),indent=2))
assert not issues,'Exterior plinth/apron contact failed; see report'
