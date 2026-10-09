"""Compare every used original material and its embedded channel payloads across revisions."""
import json,struct,hashlib,sys
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[1]
def read(path):
 raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+size]);start=28+size
 images=[]
 for im in d.get('images',[]):
  v=d['bufferViews'][im['bufferView']];payload=raw[start+v.get('byteOffset',0):start+v.get('byteOffset',0)+v['byteLength']];images.append({'mime':im.get('mimeType'),'sha256':hashlib.sha256(payload).hexdigest()})
 textures=[]
 for tex in d.get('textures',[]):textures.append({'image':images[tex['source']],'sampler':d.get('samplers',[])[tex['sampler']] if 'sampler'in tex else None})
 def canonical(value,key=''):
  if isinstance(value,list):return [canonical(v) for v in value]
  if not isinstance(value,dict):return value
  return {k:(textures[v] if k=='index' and key.endswith('Texture') else canonical(v,k)) for k,v in sorted(value.items())}
 used={p['material'] for m in d['meshes'] for p in m['primitives'] if 'material'in p}
 return {d['materials'][i]['name']:canonical(d['materials'][i]) for i in used}
for era in ['2017','2026']:
 old=read(R/f'exports/michigan_central_{era}.glb');new=read(R/f'exports/revision15/michigan_central_{era}.glb');missing=sorted(set(old)-set(new));extra=sorted(set(new)-set(old));changed=[n for n in sorted(set(old)&set(new)) if old[n]!=new[n]]
 result={'era':era,'baseline_glb_sha256':hashlib.file_digest((R/f'exports/michigan_central_{era}.glb').open('rb'),'sha256').hexdigest(),'revision15_glb_sha256':hashlib.file_digest((R/f'exports/revision15/michigan_central_{era}.glb').open('rb'),'sha256').hexdigest(),'used_materials_before':len(old),'used_materials_after':len(new),'missing':missing,'extra':extra,'changed':changed,'all_inherited_material_graph_and_embedded_image_payloads_identical':not(missing or extra or changed),'scope':'All used glTF material definitions, samplers and embedded image bytes; not physical reflectance certification'}
 (O/f'manifests/material_identity_{era}.json').write_text(json.dumps(result,indent=2));print(result);assert result['all_inherited_material_graph_and_embedded_image_payloads_identical'],result
