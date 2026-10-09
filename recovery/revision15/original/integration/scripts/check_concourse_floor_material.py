"""Concourse-only2017 material and world-metric UV placement regression."""
import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from artifact_provenance import file_sha256
E=sys.argv[sys.argv.index('--')+1];s=bpy.context.scene;name='Concourse 2017 worn mineral floor'
users=[o for o in s.objects if o.type=='MESH' and any(m and m.name==name for m in o.data.materials)]
assert len(users)==(1 if E=='2017' else 0),(E,[o.name for o in users])
if E=='2017':
 o=users[0];assert o.name=='concourse qualified2017 unpatterned floor';m=bpy.data.materials[name];assert m['texture_repeat_m']==4.0
 for channel in ['basecolor','roughness','normal','height']:
  n=m.node_tree.nodes[channel];assert '/concourse_floor_2017/' in n.image.filepath
 for p in o.data.polygons:
  if p.normal.z<.99:continue
  for li in p.loop_indices:
   co=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv=o.data.uv_layers.active.data[li].uv
   assert abs(uv.x-co.x/4)<1e-5 and abs(uv.y-co.y/4)<1e-5
report=dict(era=E,source_blend_sha256=file_sha256(bpy.data.filepath),passed=True,assigned_objects=[o.name for o in users],repeat_m=4.0,scope='Separate material on exactly the2017 main concourse floor. No shared concrete material replacement; 2026 unchanged.',limits='Authored old-mineral/terrazzo/dust material class. Does not establish exact2017 layer composition or damage positions.')
(R/'manifests'/f'concourse_floor_material_{E}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
