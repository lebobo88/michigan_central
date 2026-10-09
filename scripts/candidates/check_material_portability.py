"""Semantic GLB color/PBR regression; schema validity is insufficient.

Fails when an affected used material loses the authored palette, channel
variation, or normal; also catches any unreviewed default-white used material.
Actual image bytes are decoded in linear light, multiplied by the glTF factor,
and compared against freshly parsed source controls. No Blender needed.
"""
from pathlib import Path
import argparse,io,json,sys
import numpy as np
from PIL import Image
from material_portability import ROOT,OUT,read_glb,used_materials,source_specs,sha256
from make_portable_material_channels import srgb_to_lin


def texture_pixels(path,doc,binary,texture_index):
    tex=doc['textures'][texture_index]
    if 'source' not in tex:raise ValueError('Compressed-only texture not supported by this regression')
    image=doc['images'][tex['source']]
    if 'bufferView' not in image:raise ValueError('Expected embedded GLB image')
    view=doc['bufferViews'][image['bufferView']]
    if view.get('buffer',0)!=0 or binary is None:raise ValueError('Expected GLB BIN buffer')
    with Path(path).open('rb') as f:
        f.seek(binary[0]+view.get('byteOffset',0));data=f.read(view['byteLength'])
    arr=np.asarray(Image.open(io.BytesIO(data)).convert('RGB'),dtype=np.float64)/255
    return arr


def check(path,era,allow_subset=False):
    path=Path(path);doc,binary=read_glb(path);used=used_materials(doc);specs=source_specs(era)
    audit=json.loads((OUT/'source_export_audit.json').read_text())
    baseline={x['name']:x for x in audit['eras'][str(era)]['affected']}
    expected=set(baseline)
    actual_names={doc['materials'][i].get('name') for i in used}
    failures=[];rows=[]
    if not allow_subset:
        for name in sorted(expected-actual_names):failures.append({'name':name,'issues':['Expected used material is absent']})
    for mi,refs in used.items():
        m=doc['materials'][mi];name=m.get('name',str(mi));pbr=m.get('pbrMetallicRoughness',{})
        factor=np.array(pbr.get('baseColorFactor',[1,1,1,1])[:3]);issues=[]
        texture=pbr.get('baseColorTexture')
        white=texture is None and np.max(np.abs(factor-1))<1e-7
        if name not in specs:
            if white:failures.append({'name':name,'issues':['Unreviewed used material defaults to white; add a source-backed explicit exception if intentional']})
            continue
        s=specs[name];want=np.array(s['expected_mean_linear'])
        if name in baseline and s['source_function_sha256']!=baseline[name]['source_function_sha256']:
            issues.append('Source constructor changed since audit; re-review graph semantics before rebasing expectation')
        if texture:
            data=srgb_to_lin(texture_pixels(path,doc,binary,texture['index']))*factor
            mean=data.mean(axis=(0,1));std=data.std(axis=(0,1))
        else:
            mean=factor;std=np.zeros(3)
        if white:issues.append('No baseColorFactor or baseColorTexture: default white')
        # Relative palette check with a small 8-bit quantization allowance.
        tol=np.maximum(want*.025,.001)
        if np.any(np.abs(mean-want)>tol):issues.append('Linear-light mean outside source palette tolerance')
        # There is no approved flat fallback in this candidate: all affected
        # sources contain noise/ramp variation and get a small original map.
        if texture is None or np.max(std)<max(float(want.max())*.002,.00005):
            issues.append('Authored variation silently lost or texture is constant')
        rough=pbr.get('roughnessFactor',1);metal=pbr.get('metallicFactor',1)
        if abs(rough-s['roughness'])>1e-5:issues.append('Authored scalar roughness changed')
        if abs(metal-s['metallic'])>1e-5:issues.append('Authored scalar metallic changed')
        if 'metallicRoughnessTexture' in pbr:issues.append('Unexpected textured roughness/metallic; source is deliberately scalar')
        if 'normalTexture' not in m:issues.append('Procedural bump lost with no portable normal replacement')
        else:
            ntex=m['normalTexture'];n=texture_pixels(path,doc,binary,ntex['index'])*2-1
            norm=np.linalg.norm(n,axis=2)
            if abs(ntex.get('scale',1)-1)>1e-5:issues.append('Unexpected normal strength; candidate amplitude is already encoded')
            if np.max(np.abs(norm-1))>.025 or n[:,:,2].min()<.7:issues.append('Invalid or excessive tangent normal')
        if texture and not all(r['has_uv0'] for r in refs):issues.append('Textured primitive lacks TEXCOORD_0')
        row={'name':name,'primitive_count':len(refs),'expected_mean_linear':want.tolist(),
             'actual_mean_linear':mean.tolist(),'actual_std_linear':std.tolist(),
             'actual_factor':factor.tolist(),'basecolor_texture':texture,'roughness':rough,'metallic':metal,'issues':issues}
        rows.append(row)
        if issues:failures.append({'name':name,'issues':issues})
    result={'glb':str(path),'sha256':sha256(path),'era':str(era),'passed':not failures,
            'material_count_checked':len(rows),'failure_count':len(failures),'failures':failures,'materials':rows,
            'scope':'Source-palette and channel portability, not architectural likeness or exact old-noise parity'}
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--era',required=True,choices=['2017','2026'])
    ap.add_argument('--glb');ap.add_argument('--output');ap.add_argument('--allow-subset',action='store_true')
    a=ap.parse_args();p=a.glb or ROOT/f'exports/michigan_central_{a.era}.glb'
    r=check(p,a.era,a.allow_subset)
    out=Path(a.output or OUT/f'regression_existing_{a.era}.json');out.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:r[k] for k in ['glb','passed','material_count_checked','failure_count']},indent=2))
    return 0 if r['passed'] else 1

if __name__=='__main__':sys.exit(main())
