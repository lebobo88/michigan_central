"""Read-only bounded field-material placement and physical-scale check."""
import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from artifact_provenance import file_sha256
E=sys.argv[sys.argv.index('--')+1];s=bpy.context.scene
name='2017 aged limestone wall fields';targets=[]
allowed={'north facade continuous stone piers','north facade end pier','north side-wing end infill',name}
for o in s.objects:
 if o.type!='MESH' or not any(m and m.name==name for m in o.data.materials):continue
 assert E=='2017' and o.name in allowed,(E,o.name)
 assert o.get('space','').startswith('01 EXTERIOR'),o.name
 ys=[(o.matrix_world@v.co).y for v in o.data.vertices]
 assert min(ys)>=-.526 and max(ys)<=4.926,(o.name,min(ys),max(ys))
 targets.append(dict(object=o.name,vertices=len(o.data.vertices),polygons=len(o.data.polygons),y_range_m=[min(ys),max(ys)]))
assert bool(targets)==(E=='2017')
if E=='2017':
 m=bpy.data.materials[name];assert m['texture_repeat_m']==4.0
 for channel in ['basecolor','roughness','normal','height']:
  n=m.node_tree.nodes[channel];assert 'stone_field_aging_2017' in n.image.filepath
report=dict(era=E,source_blend_sha256=file_sha256(bpy.data.filepath),passed=True,targets=targets,scope='Only north planar wall fields; separate columns, arch profiles, molding and ornament excluded',repeat_m=4.0,limitations='Authoring-scale and placement checks only; generated course layout/stains are interpretive and unmeasured')
(R/'manifests'/f'field_material_scope_{E}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
