"""Targeted actual-mesh capital bearing and monumental-arch band clearance."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from artifact_provenance import file_sha256
E=sys.argv[sys.argv.index('--')+1];s=bpy.context.scene;assert E==s['era']
def bvh_from(objects,bottom_only=False):
 verts=[];faces=[]
 for o in objects:
  off=len(verts);verts.extend([tuple(o.matrix_world@v.co) for v in o.data.vertices])
  for p in o.data.polygons:
   if bottom_only and p.normal.z>-.999:continue
   faces.append(tuple(off+i for i in p.vertices))
 return BVHTree.FromPolygons(verts,faces,all_triangles=False)
cap=bpy.data.objects['exterior capital abacus'];me=cap.data;adj=[set() for v in me.vertices]
for e in me.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
remaining=set(range(len(me.vertices)));caps=[]
while remaining:
 stack=[remaining.pop()];ids=[]
 while stack:
  i=stack.pop();ids.append(i)
  for j in adj[i]:
   if j in remaining:remaining.remove(j);stack.append(j)
 points=[cap.matrix_world@me.vertices[i].co for i in ids]
 caps.append((sum(p.x for p in points)/len(points),sum(p.y for p in points)/len(points),max(p.z for p in points)))
assert len(caps)==14
bearing=[o for o in s.objects if o.type=='MESH' and o.name=='north interrupted entablature bearing architrave'];assert bearing
bands=[o for o in s.objects if o.type=='MESH' and o.name.startswith('north ') and any(q in o.name for q in ['entablature','cornice dentil backing'])]
bb=bvh_from(bearing,True);allbands=bvh_from(bands);rows=[];issues=[]
for x,y,top in caps:
 hit,n,fi,d=bb.ray_cast(Vector((x,y,top-1)),Vector((0,0,1)),2)
 gap=hit.z-top if hit else None
 rows.append(dict(center_x=x,center_y=y,abacus_top_z_m=top,bearing_bottom_z_m=hit.z if hit else None,gap_m=gap))
 if gap is None or abs(gap)>.005:issues.append(dict(x=x,gap_m=gap,problem='Missing bearing or air/overlap outside mesh contact tolerance'))
clearance=[]
for x in [-20,0,20]:
 for z in [13.20,13.40,14.10]:
  hit,n,fi,d=allbands.ray_cast(Vector((x,-2.2,z)),Vector((0,1,0)),1.4)
  clearance.append(dict(window_center_x=x,z_m=z,projecting_band_hit=bool(hit)))
  if hit:issues.append(dict(x=x,z=z,problem='Projecting entablature crosses monumental arch zone'))
report=dict(era=E,source_blend_sha256=file_sha256(bpy.data.filepath),passed=not issues,capital_bearing_checks=rows,arch_zone_checks=clearance,issues=issues,controls=json.loads(s.get('north_entablature_controls','{}')),limitations='Targets fourteen capital-center bearings and nine monumental-arch band probes on the authored source mesh. Not a structural, survey, carved-profile or whole-facade collision certification.')
(R/'manifests'/f'north_upper_contact_{E}.json').write_text(json.dumps(report,indent=2));print(json.dumps({'era':E,'passed':not issues,'bearings':len(rows),'arch_probes':len(clearance),'issues':issues},indent=2));assert not issues
