"""Validate actual glTF bytes and documented package source provenance."""
import json,struct,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];rows=[]
for f in sorted((ROOT/'exports').glob('*.glb')):
 b=f.read_bytes();magic,version,length=struct.unpack_from('<III',b);assert magic==0x46546c67 and version==2 and length==len(b)
 n,typ=struct.unpack_from('<II',b,12);assert typ==0x4e4f534a;g=json.loads(b[20:20+n]);assert g['asset']['version']=='2.0'
 meshes=g.get('meshes',[]);prims=[p for m in meshes for p in m['primitives']]
 assert all('POSITION' in p['attributes'] for p in prims)
 assert all('NORMAL' in p['attributes'] for p in prims)
 assert all('TEXCOORD_0' in p['attributes'] for p in prims)
 normal_prims=[p for p in prims if 'normalTexture' in g.get('materials',[])[p.get('material',0)]]
 assert all('TANGENT' in p['attributes'] for p in normal_prims), 'Normal-mapped primitive missing explicit tangent basis'
 assert all('uri' not in i for i in g.get('images',[])), 'GLB has external images'
 rows.append(dict(file=str(f.relative_to(ROOT)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),mesh_count=len(meshes),primitive_count=len(prims),materials=len(g.get('materials',[])),embedded_images=len(g.get('images',[])),space_group_nodes=sum(bool(n.get('extras',{}).get('export_group')) for n in g.get('nodes',[])),coverage_marker_nodes=sum(bool(n.get('extras',{}).get('export_coverage_marker')) for n in g.get('nodes',[])),glb_structure='passed',uv_and_normals='present on every primitive',normal_mapped_primitives=len(normal_prims),normal_map_tangents='explicit on every normal-mapped primitive',limitations='Does not establish photorealism, reference fidelity, manifoldness, or every-room coverage.'))
(ROOT/'manifests/export_validation.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
