"""Actual authored-mesh clearance between visible hall upper surfaces and copper roof.
A geometric clash test, not structural/MEP design certification or surveyed Z.
"""
import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from artifact_provenance import file_sha256
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];era=sys.argv[sys.argv.index('--')+1];roof=bpy.data.objects['hall hipped copper roof'];me=roof.data
verts=[roof.matrix_world@v.co for v in me.vertices];bvh=BVHTree.FromPolygons(verts,[list(p.vertices) for p in me.polygons],all_triangles=False)
rows=[];fail=[];minimum=999
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or not (ob.name.startswith('sail vault bay') or ob.name=='hall vertical decorated spandrel field'):continue
 low=999;count=0
 for ve in ob.data.vertices:
  p=ob.matrix_world@ve.co;hit,normal,index,distance=bvh.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),200)
  if hit is None:continue
  delta=hit.z-p.z;low=min(low,delta);minimum=min(minimum,delta);count+=1
  if delta<.20:fail.append(dict(object=ob.name,vertex=ve.index,point_m=list(p),roof_z_m=hit.z,clearance_m=delta))
 rows.append(dict(object=ob.name,vertices_checked=count,min_clearance_m=low))
report=dict(source_blend_sha256=file_sha256(bpy.data.filepath),era=era,minimum_clearance_m=minimum,criterion_m=.20,scope='Actual sail-surface and decorated-wall vertices versus copper roof mesh, vertical clearance only',checked=rows,failures=fail,limitations=['Roof profile and sail boundary are explicitly inferred modeling controls','Clearance threshold is a visualization clash guard, not a structural/MEP design requirement','Not a full-scene intersection test'])
(R/'manifests'/f'hall_roof_clearance_{era}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not fail,fail[:5]
