"""Exact embedded-channel byte identity for the authored portable full-GLB maps."""
from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts/candidates'))
from material_portability import read_glb,used_materials,sha256
manifest=json.loads((R/'assets/portable_public_finishes/manifest.json').read_text());audit=json.loads((R/'manifests/material_portability/source_export_audit.json').read_text());rows=[]
for era in ['2017','2026']:
 glb=R/f'exports/michigan_central_{era}.glb';glb_hash=sha256(glb);doc,binary=read_glb(glb);used=used_materials(doc);lookup={doc['materials'][i].get('name'):doc['materials'][i] for i in used}
 for source in audit['eras'][era]['affected']:
  name=source['name'];m=lookup[name];rec=manifest['materials'][name]
  for channel,tex,filename in [('basecolor',m['pbrMetallicRoughness']['baseColorTexture']['index'],rec['basecolor']),('normal',m['normalTexture']['index'],rec['normal_by_era'][era])]:
   image=doc['images'][doc['textures'][tex]['source']];v=doc['bufferViews'][image['bufferView']]
   with glb.open('rb') as f:f.seek(binary[0]+v.get('byteOffset',0));payload=f.read(v['byteLength'])
   actual=hashlib.sha256(payload).hexdigest();expected=rec['sha256'][filename]
   rows.append(dict(era=era,name=name,channel=channel,source_file='assets/portable_public_finishes/'+filename,source_sha256=expected,embedded_sha256=actual,bytes=len(payload),identical=actual==expected,full_glb_sha256=glb_hash))
report=dict(passed=all(x['identical'] for x in rows),channels_checked=len(rows),rows=rows,scope='Exact full-GLB embedded PNG payload identity. Does not claim the 2D channels exactly match the prior Generated-node noise or physical site reflectance.')
(R/'manifests/portable_full_payload_identity.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['passed','channels_checked']}));assert report['passed']
