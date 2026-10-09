"""Preserve exact currently executed builder/component/render-helper sources.
Fail closed if the source files changed since the immutable image metadata.
No textures or copyrighted research are copied.
"""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[1];rev=sys.argv[1];era=sys.argv[2] if len(sys.argv)>2 else '2026'
meta=json.loads((R/f'renders/{rev}/{era}_front.json').read_text())
D=R/f'manifests/checkpoints/{rev}/builder/scripts';D.mkdir(parents=True,exist_ok=True)
expected={'build_station.py':meta['build_code_sha256'],**json.loads(meta['saved_component_sha256']),'render_review_checkpoint.py':meta['render_helper_sha256']}
rows=[]
for name,sha in expected.items():
 p=R/'scripts'/name;b=p.read_bytes();actual=hashlib.sha256(b).hexdigest();assert actual==sha,(name,'source changed since image',actual,sha)
 dest=D/name;dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==b,('immutable snapshot changed',dest)
 else:dest.write_bytes(b)
 rows.append(dict(file=str(dest.relative_to(R)),sha256=sha,role='Exact recorded source'))
for name in ['artifact_provenance.py','validate_scene.py','check_uv_area.py','check_public_interfaces.py','check_floor_overlaps.py','check_hall_roof_clearance.py','check_era_conditions.py','inventory_packed_materials.py','check_field_material_scope.py','export_lod.py','compact_preview.cjs','validate_khronos.cjs','check_glb_roundtrip.py','validate_assets.py']:
 b=(R/'scripts'/name).read_bytes();dest=D/name
 if dest.exists():assert dest.read_bytes()==b
 else:dest.write_bytes(b)
 rows.append(dict(file=str(dest.relative_to(R)),sha256=hashlib.sha256(b).hexdigest(),role='Runtime/validation utility captured at checkpoint'))
manifest={'checkpoint':rev,'image_metadata':f'renders/{rev}/{era}_front.json','sources':rows,'asset_payload_hashes':'../packed_material_inventory_2017.json and../packed_material_inventory_2026.json','note':'Exact executed builder/component/render-helper bytes match recorded image metadata. Use the unchanged supplied project assets at their relative paths. This snapshot directory is not itself the project root. Blender serialization may vary on rebuild; this is source-level recovery, not a promise of byte-identical BLEND output.'}
p=D.parent/'source_manifest.json';data=json.dumps(manifest,indent=2)
if p.exists():assert p.read_text()==data
else:p.write_text(data)
print(p)
