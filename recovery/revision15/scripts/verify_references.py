"""Verify compact geometry/UV/index data, transform bounds, source AST and guards."""
import sys
sys.dont_write_bytecode = True
import ast,json,math,struct
from pathlib import Path
from glb_io import sha,rows,WIDTH,TYPES
PKG=Path(__file__).resolve().parents[1]
def verify():
    contract=json.loads((PKG/'recovery_contract.json').read_text());src=(PKG/'original/study/build_study.py').read_bytes()
    if sha(src)!=contract['study_generator_sha256']:raise ValueError('Study source pin')
    tree=ast.parse(src);allowed=contract['geometry_function_names'];defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in allowed]
    if len(defs)!=7 or {n.name for n in defs}!=set(allowed):raise ValueError('Missing/duplicate replay definitions')
    compile(ast.Module(body=defs,type_ignores=[]),'pinned seven definitions','exec')
    reports=[]
    for era in ('2017','2026'):
        d=json.loads((PKG/f'references/details_{era}.json').read_text());blob=(PKG/f'references/details_{era}.bin').read_bytes()
        if sha(blob)!=d['binary_sha256'] or len(d['objects'])!=contract['inputs'][era]['expected_new_meshes']:raise ValueError('Detail payload/count mismatch')
        intervals=[];triangles=0;max_bounds=0.0
        sealed=json.loads((PKG/f'original/integration/manifests/revision15_full_geometry_{era}.json').read_text());by_node={n:r for r in sealed['primitives'] for n in r['node_names']}
        materials={r['name']:r['sha256'] for r in json.loads((PKG/f'references/materials_{era}.json').read_text())['materials']}
        for ob in d['objects']:
            arr={}
            accepted=by_node[ob['name']]
            if ob['material_fingerprint_sha256']!=materials[ob['material_name']]:raise ValueError('Study/final material mismatch')
            for label,a in ob['arrays'].items():
                expected_hash=accepted['indices_sha256'] if label=='indices' else accepted['attribute_sha256'][label]
                if a['sha256']!=expected_hash:raise ValueError('Study/final geometry payload mismatch')
                raw=blob[a['offset']:a['offset']+a['bytes']];desc=a['accessor'];expect=desc['count']*WIDTH[desc['type']]*TYPES[desc['componentType']][1]
                if a['bytes']!=expect or sha(raw)!=a['sha256']:raise ValueError('Array hash/size')
                arr[label]=rows(raw,desc);intervals.append((a['offset'],a['offset']+a['bytes']))
                if not all(math.isfinite(v) for r in arr[label] for v in r):raise ValueError('Nonfinite detail')
            p=arr['POSITION'];u=arr['TEXCOORD_0'];n=arr['NORMAL'];t=arr['TANGENT'];idx=[r[0] for r in arr['indices']]
            if len(idx)%3 or len(p)!=len(u) or len(n)!=len(p) or len(t)!=len(p) or min(idx)<0 or max(idx)>=len(p):raise ValueError('Invalid topology')
            for nn,tt in zip(n,t):
                if abs(sum(x*x for x in nn)**.5-1)>1e-4 or abs(sum(x*x for x in tt[:3])**.5-1)>1e-4 or abs(sum(a*b for a,b in zip(nn,tt)))>1e-4 or abs(abs(tt[3])-1)>1e-4:raise ValueError('Normal/tangent strict check')
            for i in range(0,len(idx),3):
                a,b,c=[p[k] for k in idx[i:i+3]];x=[b[j]-a[j] for j in range(3)];y=[c[j]-a[j] for j in range(3)];area=sum((x[(j+1)%3]*y[(j+2)%3]-x[(j+2)%3]*y[(j+1)%3])**2 for j in range(3))**.5
                a,b,c=[u[k] for k in idx[i:i+3]];uv=abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
                if area<1e-10 or uv<1e-12:raise ValueError('Degenerate detail geometry/UV')
            triangles+=len(idx)//3
            m=ob['placement']['evaluated_matrix_world'];world=[]
            transform=ob['node_transform']
            if set(transform)!={'translation'}:raise ValueError('Unexpected detail node transform contract')
            t=transform['translation'];translation=(t[0],-t[2],t[1])
            if any(abs(translation[j]-m[j][3])>1e-5 for j in range(3)):raise ValueError('Node/source transform mismatch')
            for v in p:
                b=(v[0],-v[2],v[1],1);world.append([sum(m[j][k]*b[k] for k in range(4)) for j in range(3)])
            bounds=[[min(v[j] for v in world) for j in range(3)],[max(v[j] for v in world) for j in range(3)]]
            delta=max(abs(x-y) for a,b in zip(bounds,ob['placement']['evaluated_world_bounds']) for x,y in zip(a,b));max_bounds=max(max_bounds,delta)
            if delta>1e-5:raise ValueError('Detail reference bounds '+ob['name'])
        intervals.sort()
        if intervals[0][0]!=0 or intervals[-1][1]!=len(blob) or any(a[1]!=b[0] for a,b in zip(intervals,intervals[1:])):raise ValueError('Unaccounted reference bytes')
        reports.append({'era':era,'objects':len(d['objects']),'triangles':triangles,'array_bytes':len(blob),'max_reference_world_bounds_delta_m':max_bounds})
    d=json.loads((PKG/'references/inherited_2026.json').read_text());blob=(PKG/'references/inherited_2026.bin').read_bytes();ranges=[]
    if sha(blob)!=d['binary_sha256'] or len(blob)!=1578360 or len(d['objects'])!=4:raise ValueError('Preservation payload mismatch')
    for ob in d['objects']:
        if set(ob['guards'])!={'POSITION','NORMAL','indices'}:raise ValueError('Missing identity guards')
        from glb_io import canonical
        if sha(canonical(ob['material_semantics']))!=ob['material_fingerprint_sha256']:raise ValueError('Material fingerprint')
        for label,a in ob['restore'].items():
            raw=blob[a['offset']:a['offset']+a['bytes']]
            if sha(raw)!=a['sha256'] or len(raw)!=a['accessor']['count']*WIDTH[a['accessor']['type']]*4:raise ValueError('Preservation array hash/size')
            ranges.append((a['offset'],a['offset']+a['bytes']))
    ranges.sort()
    if ranges[0][0]!=0 or ranges[-1][1]!=len(blob) or any(a[1]!=b[0] for a,b in zip(ranges,ranges[1:])):raise ValueError('Preservation byte coverage')
    return {'passed':True,'source_ast_definitions':allowed,'details':reports,'inherited_guarded_primitives':4,'inherited_array_bytes':len(blob),'blender_reconstruction':'NOT YET VALIDATED','blender_launched':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
