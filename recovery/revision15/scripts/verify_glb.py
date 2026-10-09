"""Read-only exact accepted payload/material comparison; no original R14 GLB needed."""
import sys
sys.dont_write_bytecode = True
import argparse,collections,json
from pathlib import Path
from glb_io import GLB,sha,digest,canonical,scene_transforms
PKG=Path(__file__).resolve().parents[1]
def verify(path,era):
    g=GLB(path);want=json.loads((PKG/f'original/integration/manifests/revision15_full_geometry_{era}.json').read_text());expected={r['identity']:r for r in want['primitives']};seen=set();occ=collections.Counter();errors=[];material_cache={}
    references=collections.defaultdict(list)
    for node in g.doc.get('nodes',[]):
        if 'mesh'in node:references[node['mesh']].append(node.get('name','unnamed node'))
    for mi,m in enumerate(g.doc['meshes']):
        name=m.get('name',f'unnamed mesh {mi}');ordinal=occ[name];occ[name]+=1
        for pi,p in enumerate(m['primitives']):
            material=g.doc.get('materials',[])[p['material']].get('name') if 'material'in p else None
            identity=json.dumps([name,ordinal,pi,material],separators=(',',':'));rec=expected.get(identity);seen.add(identity)
            if rec is None:errors.append([identity,'unexpected primitive']);continue
            if sorted(references[mi])!=sorted(rec['node_names']):errors.append([identity,'node instances differ'])
            if set(p['attributes'])!=set(rec['attribute_sha256']):errors.append([identity,'attribute set differs'])
            for label,h in rec['attribute_sha256'].items():
                if label not in p['attributes'] or sha(g.array(p['attributes'][label]))!=h:errors.append([identity,label,'payload differs'])
            if 'indices' not in p or sha(g.array(p['indices']))!=rec['indices_sha256']:errors.append([identity,'indices differ'])
    errors.extend([identity,'missing primitive'] for identity in set(expected)-seen)
    mats=json.loads((PKG/f'references/materials_{era}.json').read_text())['materials'];wantmat={m['name']:m['sha256'] for m in mats};actual={}
    for i,m in enumerate(g.doc.get('materials',[])):
        name=m.get('name')
        if name in actual:errors.append([name,'duplicate material name'])
        actual[name]=sha(canonical(g.material(i)))
    if actual!=wantmat:errors.append(['material definitions/samplers/image payload fingerprints differ'])
    expected_nodes=json.loads((PKG/f'references/scene_nodes_{era}.json').read_text())['nodes'];actual_nodes=scene_transforms(g.doc);max_transform_delta=0.0
    if set(expected_nodes)!=set(actual_nodes):errors.append(['node name set differs'])
    for name in set(expected_nodes)&set(actual_nodes):
        x,y=expected_nodes[name],actual_nodes[name]
        if x['parent']!=y['parent'] or x['mesh_name']!=y['mesh_name']:errors.append([name,'node parent or mesh binding differs'])
        for kind in ['local_matrix','world_matrix']:
            delta=max(abs(a-b) for aa,bb in zip(x[kind],y[kind]) for a,b in zip(aa,bb));max_transform_delta=max(delta,max_transform_delta)
            if delta>=1e-5:errors.append([name,kind,'transform differs',delta])
    lineage=json.loads((PKG/f'original/integration/manifests/export_lineage_{era}.json').read_text())
    mesh_nodes=[n.get('name') for n in g.doc['nodes'] if 'mesh'in n]
    if sorted(mesh_nodes)!=sorted(lineage['mesh_node_names_expected']):errors.append(['full mesh node names differ'])
    report={'passed':not errors,'era':era,'file':str(path),'sha256':digest(path),'compared_primitives':len(seen),'mesh_nodes':len(mesh_nodes),'materials':len(actual),'nodes_with_hierarchy_and_world_matrices_checked':len(actual_nodes),'maximum_node_transform_delta':max_transform_delta,'errors':errors,'scope':'Exact accepted geometry, UV, tangent, index and material/image fingerprints; metadata/binary ordering not asserted','full_numerical_strict_clean':False,'inherited_defects_retained':True,'actual_blender_import_checked_here':False}
    if errors:raise ValueError(json.dumps(report,indent=2))
    return report
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--glb',required=True);ap.add_argument('--era',choices=['2017','2026'],required=True);ap.add_argument('--report');a=ap.parse_args();r=verify(a.glb,a.era)
    if a.report:
        with Path(a.report).open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
