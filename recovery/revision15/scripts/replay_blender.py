"""Portable R14 -> R15 source replay. Run only via recover.py. Never renders.
Original study top-level code is NOT executed. Seven pinned definitions only.
"""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:raise RuntimeError("Optimized Python would disable required assertion gates")
import ast,argparse,hashlib,json,math,shutil,sys
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector
PKG=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PKG/'scripts'))
from glb_io import digest,sha
ap=argparse.ArgumentParser();ap.add_argument('--era',choices=['2017','2026'],required=True);ap.add_argument('--r14',required=True);ap.add_argument('--output',required=True);ap.add_argument('--export',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);ERA=a.era;OUT=Path(a.output).resolve();source=Path(a.r14).resolve()
contract=json.loads((PKG/'recovery_contract.json').read_text());pin=contract['inputs'][ERA]
if bpy.app.version!=(5,2,2):raise RuntimeError('Exact replay requires Blender 5.2.2; received '+bpy.app.version_string)
if digest(source)!=pin['r14_blend_sha256']:raise RuntimeError('R14 source hash mismatch')
# Runtime copies make unchanged historic check scripts write beneath this NEW output.
for name in ['scripts','manifests']:(OUT/name).mkdir(exist_ok=True)
original=PKG/'original/integration/scripts'
check_names=['validate_scene.py','check_public_interfaces.py','check_floor_overlaps.py','check_era_conditions.py','check_uv_area.py','check_concourse_floor_material.py','check_field_material_scope.py','check_integrated_details.py','check_glass_shells.py','check_lobby_interfaces.py']
for name in check_names+['artifact_provenance.py','placement_checks.py','bounded_import_checks.py','candidates/glass_shell_rules.py','candidates/elevator_lobby_detail.py']:
    dst=OUT/'scripts'/name;dst.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(original/name,dst)
sys.path.insert(0,str(OUT/'scripts'));from placement_checks import check_placements
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;bpy.context.view_layer.update()
assert s['era']==ERA and sum(o.type=='MESH' for o in s.objects)==pin['expected_base_meshes']
def signature(ob):
    d=hashlib.sha256();d.update(json.dumps({'type':ob.type,'matrix':[list(r) for r in ob.matrix_world],'parent':ob.parent.name if ob.parent else None,'hide_render':ob.hide_render,'space':ob.get('space'),'modifiers':[(m.name,m.type) for m in ob.modifiers]},sort_keys=True).encode())
    if ob.type=='MESH':
        me=ob.data
        for seq,prop,n,dtype in [(me.vertices,'co',3,np.float32),(me.loops,'vertex_index',1,np.int32),(me.polygons,'loop_start',1,np.int32),(me.polygons,'loop_total',1,np.int32),(me.polygons,'material_index',1,np.int32)]:
            data=np.empty(len(seq)*n,dtype=dtype);seq.foreach_get(prop,data);d.update(data.tobytes())
        for uv in me.uv_layers:
            data=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',data);d.update(uv.name.encode());d.update(data.tobytes())
        d.update(json.dumps([m.name if m else None for m in me.materials]).encode())
    return d.hexdigest()
before={ob.name:signature(ob) for ob in s.objects};materials={m.as_pointer() for m in bpy.data.materials};images={im.as_pointer() for im in bpy.data.images}
refpath=PKG/f'original/integration/manifests/study_placement_reference_{ERA}.json';ref=json.loads(refpath.read_text());names=[r['name'] for r in ref['objects']]
assert len(names)==pin['expected_new_meshes'] and not any(n in bpy.data.objects for n in names)
old=bpy.data.objects.get('concourse west small opening profiled lintel');assert old and old.type=='MESH' and any(m and m.name==f'Concourse terracotta dressings {ERA}' for m in old.data.materials)
terra=bpy.data.materials[f'Concourse terracotta dressings {ERA}'];metal=bpy.data.materials[f'Concourse retained portal metal {ERA}']
text=(PKG/'original/study/build_study.py').read_bytes();assert sha(text)==contract['study_generator_sha256'];tree=ast.parse(text);defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in contract['geometry_function_names']];assert len(defs)==7
namespace={'bpy':bpy,'bmesh':bmesh,'math':math,'Vector':Vector,'s':s,'ERA':ERA,'terra':terra,'metal':metal,'cy':63.4,'front':29.4894,'new':[]}
exec(compile(ast.Module(body=defs,type_ignores=[]),'pinned original geometry definitions','exec'),namespace);namespace['add_detail']();new=namespace['new'];assert [o.name for o in new]==names
# Exact original MetricUV computation occurs inside mesh(), BEFORE this recenter.
for ob in new:
    center=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
    for v in ob.data.vertices:v.co-=center
    ob.location=center
bpy.context.view_layer.update()
collection=bpy.data.collections.new('05 CONCOURSE | west portal source-supported relief study');s.collection.children.link(collection)
parent=bpy.data.objects['05 CONCOURSE | source-informed masonry and floor'];assert parent.get('export_group')
for ob in new:
    world=ob.matrix_world.copy()
    for coll in list(ob.users_collection):coll.objects.unlink(ob)
    collection.objects.link(ob);ob.parent=parent;ob.matrix_world=world;ob['space']=parent.name;ob['era']=ERA;ob['revision15_role']='Bounded source-supported west portal detail; qualified dimensions and condition';ob.hide_select=False
bpy.context.view_layer.update();placement=check_placements(refpath)
removed=set(before)-{o.name for o in s.objects};added={o.name for o in s.objects}-set(before)
assert removed=={'concourse west small opening profiled lintel'} and added==set(names)
assert all(signature(bpy.data.objects[n])==h for n,h in before.items() if n not in removed)
assert {m.as_pointer() for m in bpy.data.materials}==materials and {im.as_pointer() for im in bpy.data.images}==images
assert sum(o.type=='MESH' for o in s.objects)==pin['expected_r15_meshes']
for ob in new:
    assert len(ob.data.materials)==1 and ob.data.materials[0] in [terra,metal]
    bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.free()
    assert not ob.modifiers
# Mandatory per-detail probes, no hidden geometry.
dg=bpy.context.evaluated_depsgraph_get()
for z in [.2,1.7,2.45]:
    for y in [62.05,63.4,64.75]:assert not s.ray_cast(dg,Vector((27.,y,z)),Vector((1,0,0)),distance=7.)[0]
for y in [55.25,71.55]:
    for z in [.2,1.7,2.275]:
        for ob in new:
            inv=ob.matrix_world.inverted();start=inv@Vector((27.,y,z));end=inv@Vector((31.,y,z));assert not ob.ray_cast(start,(end-start).normalized(),distance=(end-start).length)[0]
assert (not any('West restored lower' in n for n in names))==(ERA=='2017')
camname='Camera concourse_portal_refinement';d=bpy.data.cameras.new(camname);cam=bpy.data.objects.new(camname,d);s.collection.objects.link(cam);cam.location=(20.2,58.3,3.15);cam.rotation_euler=(Vector((29.15,63.3,3.45))-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=37;d.clip_end=1000
s['revision']='revision15_concourse_only';s['revision14_parent_blend_sha256']=pin['r14_blend_sha256'];s['revision15_recovery_script_sha256']=digest(__file__);s['revision15_scope']='Only west concourse portal crown/panel/grille detail. North-pediment revision08 is not integrated. Unobserved west continuation remains unresolved.'
s['revision15_detail_qualification']='Source-relative geometry;2017 retained-shell persistence is qualified from2010/May2017 reference families;2026 restored grilles are not copied backward; no new image maps.'
s['west_portal_detail_study']=json.dumps({'era':ERA,'added_objects':len(new),'removed_objects':sorted(removed),'changed_floor_or_opening_controls':False,'source_study':'Portable exact pinned definitions; study BLEND not needed','full_scene_qa_required':True})
assert not any('/research/' in im.filepath or 'study_only' in im.filepath for im in bpy.data.images)
assert all(im.source!='FILE' or im.packed_file or im.packed_files for im in bpy.data.images), 'R14 must contain packed image payloads'
bpy.context.preferences.filepaths.save_version=0;s.render.threads_mode='FIXED';s.render.threads=2;blend=OUT/f'michigan_central_{ERA}_recovered.blend';assert not blend.exists();bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
(OUT/'manifests/source_detail_placements.json').write_text(json.dumps(placement,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(blend));s=bpy.context.scene;bpy.context.view_layer.update();placement=check_placements(refpath)
assert all(signature(bpy.data.objects[n])==h for n,h in before.items() if n not in removed)
(OUT/'manifests/reopened_detail_placements.json').write_text(json.dumps(placement,indent=2))
original_argv=sys.argv[:];sys.argv=[sys.argv[0],'--',ERA]
for name in check_names:
    p=OUT/'scripts'/name;exec(compile(p.read_bytes(),str(p),'exec'),{'__file__':str(p),'__name__':'recovery_check_'+name[:-3]})
sys.argv=original_argv
assert not json.loads((OUT/f'manifests/floor_overlap_{ERA}.json').read_text())['overlaps']
assert not [r for r in json.loads((OUT/f'manifests/public_interface_checks_{ERA}.json').read_text())['checks'] if r['status']=='REVIEW']
assert not json.loads((OUT/f'manifests/uv_area_{ERA}.json').read_text())['collapsed_uv_triangles']
assert not json.loads((OUT/f'manifests/scene_validation_{ERA}.json').read_text())['degenerate_polygon_diagnostic']
report={'era':ERA,'source_replay_passed':True,'source_sha256':digest(blend),'source_blend':str(blend),'blender_version_tuple':list(bpy.app.version),'r14_sha256':digest(source),'new_details':len(names),'all_retained_object_signatures_unchanged':True,'every_detail_source_and_reopened_matrix_and_bounds_checked':True,'full_numerical_strict_clean':False,'blender_version':bpy.app.version_string,'binary_identical_blend_claim':False,'rendered':False}
if a.export:
    bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT')
    for ob in s.objects:
        if (ob.type=='MESH' and ob.name!='landscape context') or ob.get('export_group') or ob.get('export_coverage_marker'):ob.hide_select=False;ob.select_set(True)
    target=OUT/f'michigan_central_{ERA}_raw.glb';assert not target.exists()
    bpy.ops.export_scene.gltf(use_selection=True,filepath=str(target),export_format='GLB',export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True)
    sys.path.insert(0,str(PKG/'original/dependencies'));from repair_glb_tangents import repair_glb_tangents
    report['baseline_zero_tangent_repair']=repair_glb_tangents(target,OUT/'manifests/zero_tangent_repair.json');report['raw_glb']=str(target)
(OUT/'manifests/source_recovery.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
