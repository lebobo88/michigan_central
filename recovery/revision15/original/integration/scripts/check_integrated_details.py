"""Actual saved-scene instance/count/provenance checks for revision14 detail modules."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from artifact_provenance import file_sha256
s=bpy.context.scene;era=s['era'];caps=[o for o in s.objects if o.type=='MESH' and o.name.startswith('Original exterior capital ornament')];issues=[]
expected=[-34.4,-27.,-24.3,-15.7,-13.,-7.,-4.3,4.3,7.,13.,15.7,24.3,27.,34.4]
if len(caps)!=14 or len({o.data.name for o in caps})!=1:issues.append('Expected fourteen linked ornaments using one mesh')
caprows=[]
for ob,x in zip(sorted(caps,key=lambda o:o.matrix_world.translation.x),expected):
 p=ob.matrix_world.translation;delta=(p-Vector((x,-1.18,12.742))).length
 caprows.append(dict(object=ob.name,mesh=ob.data.name,origin=list(p),expected_origin_delta_m=delta))
 if delta>1e-4:issues.append('Capital origin drift: '+ob.name)
canopy=[o for o in s.objects if o.type=='MESH' and o.name.startswith(era+' north canopy')];roles={}
for ob in canopy:roles[ob.get('role','unknown')]=roles.get(ob.get('role','unknown'),0)+1
if era=='2017' and roles!={'anchor':1}:issues.append('2017 canopy must contain only bounded retained anchors')
if era=='2026' and not all(roles.get(x)==1 for x in ['glazing','roof_opaque']):issues.append('2026 must contain inset glazing and an opaque perimeter')
lobby=json.loads(s['elevator_lobby_metadata']);spaces=json.loads(s['secondary_space_evidence'])
report=dict(era=era,source_blend_sha256=file_sha256(bpy.data.filepath),passed=not issues,issues=issues,capital_placements=caprows,capital_shared_mesh_count=len({o.data.name for o in caps}),canopy_roles=roles,lobby_metadata=lobby,secondary_space_evidence=spaces,portable_material_change_count=len(json.loads(s['portable_material_changes'])),limitations=['Checks actual integrated counts/transforms/metadata, not exact carved surfaces or historic per-column conditions','Door/fixture widths and all unmeasured vertical/site controls remain approximate'])
(R/f'manifests/integrated_detail_checks_{era}.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(era=era,passed=report['passed'],issues=issues)));assert report['passed']
