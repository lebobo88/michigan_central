"""Candidate-only source palette audit and narrow portable PBR replacement.

Does not run or edit a station build by itself. Pure-Python functions parse the
actual GLB JSON and authored sec_material/west_material call sites. Blender-only
apply_candidate_materials() must be called explicitly in an authorized copy.
"""
from pathlib import Path
import ast, hashlib, json, re, struct

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'manifests/material_portability'


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_glb(path):
    """Read just JSON and BIN location; never silently truncate JSON."""
    with Path(path).open('rb') as f:
        magic, version, length = struct.unpack('<4sII', f.read(12))
        assert (magic, version) == (b'glTF', 2)
        assert length == Path(path).stat().st_size
        size, kind = struct.unpack('<II', f.read(8))
        assert kind == 0x4e4f534a
        doc = json.loads(f.read(size))
        head = f.read(8)
        binary = None
        if head:
            size, kind = struct.unpack('<II', head)
            assert kind == 0x004e4942
            binary = (f.tell(), size)
    return doc, binary


def used_materials(doc):
    result = {}
    for mi, mesh in enumerate(doc.get('meshes', [])):
        for pi, p in enumerate(mesh['primitives']):
            if 'material' not in p:
                continue
            row = result.setdefault(p['material'], [])
            row.append({'mesh': mesh.get('name', str(mi)), 'primitive': pi,
                        'has_uv0': 'TEXCOORD_0' in p['attributes']})
    return result


def _args(call, env):
    # Evaluate only argument expressions in checked project source. No import,
    # statement execution, bpy, or material-graph execution is required.
    def ev(node):
        return eval(compile(ast.Expression(node), '<source palette>', 'eval'),
                    {'__builtins__': {}, 'str': str}, env)
    return [ev(a) for a in call.args], {k.arg: ev(k.value) for k in call.keywords}


def source_specs(era):
    """Extract authored controls afresh, so regression is not a stale hand-copy."""
    aged = str(era) == '2017'
    specs = {}
    for module, fun in [('secondary_spaces.py', 'sec_material'),
                        ('west_public_rooms.py', 'west_material')]:
        path = ROOT / 'scripts' / module
        source = path.read_text()
        tree = ast.parse(source)
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == fun)
        for call in ast.walk(tree):
            if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == fun):
                continue
            names = {n.id for n in ast.walk(call) if isinstance(n, ast.Name)}
            envs = [{'AGED': aged}]
            if {'c', 'i'} & names:
                # The only parameterized material call is the explicitly authored
                # five-color abstract-marking palette, not arbitrary scene code.
                loop = next(n for n in tree.body if isinstance(n, ast.For)
                            and call in list(ast.walk(n)))
                colors = ast.literal_eval(loop.iter.args[0])
                envs = [{'AGED': aged, 'i': i, 'c': c} for i, c in enumerate(colors)]
            for env in envs:
                args, kw = _args(call, env)
                name, color = args[:2]
                if fun == 'sec_material':
                    defaults = [.55, 0, .08, 7]
                    values = args[2:] + defaults[len(args[2:]):]
                    rough, metal, spread, scale = values
                    rough = kw.get('roughness', rough); metal = kw.get('metal', metal)
                    spread = kw.get('variation', spread); scale = kw.get('scale', scale)
                    distance, strength, repeat = (.018 if aged else .002), .15, 4.0
                    coord = 'Generated normalized by each original object bounds; no authored physical repeat'
                else:
                    if aged or kw.get('grain', args[4] if len(args) > 4 else False):
                        continue  # The accepted walnut image channels are untouched.
                    rough = kw.get('rough', args[2] if len(args) > 2 else .45)
                    metal = kw.get('metal', args[3] if len(args) > 3 else 0)
                    spread, scale, distance, strength, repeat = .055, 17.6, .0007, .1, 1.0
                    coord = 'Metric UV x 2.2 then Noise Scale 8; 17.6 base cycles per metre'
                low = [min(.99, max(.003 if fun == 'sec_material' else 0, c * (1-spread))) for c in color]
                high = [min(.99, max(.003 if fun == 'sec_material' else 0, c * (1+spread))) for c in color]
                specs[name] = dict(name=name, era=str(era), source_module='scripts/' + module,
                    source_line=call.lineno, source_call=ast.get_source_segment(source, call),
                    source_function_sha256=hashlib.sha256(ast.get_source_segment(source, function).encode()).hexdigest(),
                    base_color_linear=list(color), ramp_low_linear=low, ramp_high_linear=high,
                    expected_mean_linear=[(a+b)/2 for a,b in zip(low,high)],
                    expected_mean_basis='Symmetric ColorRamp endpoints evaluated at nominal Noise Fac 0.5; not a measured scene-wide procedural mean',
                    roughness=rough, metallic=metal, variation=spread, noise_scale=scale,
                    source_noise_detail=3, source_noise_roughness=(.5 if fun == 'sec_material' else .65), source_coordinates=coord,
                    source_bump_distance_m=distance, source_bump_strength=strength,
                    existing_uv_repeat_m=repeat,
                    candidate_base_cycles_per_repeat=scale,
                    candidate_base_wavelength_m=repeat/scale,
                    slug=re.sub(r'[^a-z0-9]+','_',name.lower()).strip('_'))
    return specs


def audit_existing():
    OUT.mkdir(exist_ok=True)
    report = {'scope': 'Actual full GLB JSON and packed shader inventories; no Blender execution',
              'eras': {}, 'unique_affected_names': [], 'untouched_material_policy':
              'Only named sec_material and non-grain west_material graphs without an exportable color are candidates'}
    for era in ('2017','2026'):
        path = ROOT / f'exports/michigan_central_{era}.glb'
        g, _ = read_glb(path); used = used_materials(g); specs = source_specs(era)
        invpath = ROOT / f'manifests/packed_material_inventory_{era}.json'
        inventory = json.loads(invpath.read_text())
        inv = {m['material']:m for m in inventory['shader_inventory']}
        affected, unknown, all_used = [], [], []
        for mi, refs in used.items():
            m = g['materials'][mi]; pbr = m.get('pbrMetallicRoughness',{})
            name = m.get('name', str(mi)); factor = pbr.get('baseColorFactor', [1,1,1,1])
            white = 'baseColorTexture' not in pbr and max(abs(v-1) for v in factor[:3]) < 1e-7
            all_used.append({'name':name,'primitive_count':len(refs),'has_color_texture':'baseColorTexture' in pbr,
                             'actual_factor':factor,'has_normal_texture':'normalTexture' in m})
            if name in specs:
                entry = dict(specs[name], material_index=mi, primitive_count=len(refs), uses=refs,
                             actual_glb_material=m, inventory=inv.get(name), missing_color=white,
                             missing_normal='normalTexture' not in m)
                affected.append(entry)
                if name not in report['unique_affected_names']: report['unique_affected_names'].append(name)
            elif white:
                unknown.append({'name':name,'material':m,'uses':refs})
        report['eras'][era] = dict(full_glb=str(path.relative_to(ROOT)), glb_sha256=sha256(path),
            source_blend_sha256=inventory['source_blend_sha256'], inventory_sha256=sha256(invpath),
            used_material_count=len(used), affected_count=len(affected), affected=affected,
            unknown_default_white=unknown, all_used_materials=all_used)
    (OUT/'source_export_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def apply_candidate_materials(materials, era, asset_root=None):
    """Explicitly opt-in in an authorized scene copy; no UV/geometry/map overwrite.

    Maps use current MetricUV unchanged: 4 m/repeat for secondary and 1 m/repeat
    for west. Roughness/metallic remain exact authored constants. Source graph
    nodes remain in the .blend, disconnected for inspectability.
    """
    import bpy
    asset_root = Path(asset_root or OUT/'candidate_assets')
    manifest = json.loads((asset_root/'manifest.json').read_text())
    specs = source_specs(era); results=[]
    for name,spec in specs.items():
        material = materials.get(name)
        if material is None or not material.users:
            continue
        nt = material.node_tree; p = nt.nodes.get('Principled BSDF')
        if p is None: raise RuntimeError(f'Missing expected Principled node: {name}')
        if any(n.type == 'TEX_IMAGE' and n.image for n in nt.nodes):
            raise RuntimeError(f'Refusing to overwrite existing image maps: {name}')
        rec = manifest['materials'][name]
        assert rec['source_function_sha256'] == spec['source_function_sha256'], name
        assert rec['base_color_linear'] == spec['base_color_linear'], name
        assert rec['roughness'] == spec['roughness'] and rec['metallic'] == spec['metallic'], name
        for socket in ['Base Color','Normal']:
            for link in list(p.inputs[socket].links): nt.links.remove(link)
        p.inputs['Base Color'].default_value=(*spec['base_color_linear'],1)
        material.diffuse_color=(*spec['base_color_linear'],1)
        p.inputs['Roughness'].default_value=spec['roughness']; p.inputs['Metallic'].default_value=spec['metallic']
        for channel,filename in [('basecolor',rec['basecolor']),('normal',rec['normal_by_era'][str(era)])]:
            path=asset_root/filename
            assert sha256(path)==rec['sha256'][filename], path
            tex=nt.nodes.new('ShaderNodeTexImage'); tex.name='Portable original '+channel
            tex.image=bpy.data.images.load(str(path),check_existing=True)
            tex.image.colorspace_settings.name='sRGB' if channel=='basecolor' else 'Non-Color'
            tex.extension='REPEAT'; tex.image.pack()
            if channel=='basecolor': nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
            else:
                nm=nt.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=1
                nt.links.new(tex.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],p.inputs['Normal'])
        material['portability_candidate']='Original periodic 2D image approximation of authored noise/ramp; not exact procedural parity'
        material['portability_source_color_linear']=spec['base_color_linear']
        material['portability_existing_uv_repeat_m']=spec['existing_uv_repeat_m']
        material['portability_base_wavelength_m']=spec['candidate_base_wavelength_m']
        material['texture_provenance']='Original deterministic periodic noise from existing procedural palette; no photograph pixels'
        material['physical_limit']='Metric frequency is an explicitly assumed reinterpretation of original Generated noise; scalar roughness/metallic preserved, no measured surface claims'
        results.append(name)
    return results


if __name__=='__main__':
    result=audit_existing()
    print(json.dumps({'affected_by_era':{e:r['affected_count'] for e,r in result['eras'].items()},
        'unique_affected':len(result['unique_affected_names']),
        'unexplained_default_white':{e:len(r['unknown_default_white']) for e,r in result['eras'].items()}},indent=2))
