"""Read-only packed image/channel inventory tied to the actual saved scene.
This proves file packaging and shader wiring, not measured reflectance or likeness.
"""
import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from artifact_provenance import file_sha256
E=sys.argv[sys.argv.index('--')+1];s=bpy.context.scene;assert E==s['era']
images=[]
for im in bpy.data.images:
 if im.source!='FILE':continue
 packets=[im.packed_file] if im.packed_file else [q.packed_file for q in im.packed_files]
 assert packets,im.name
 source=Path(bpy.path.abspath(im.filepath)).resolve()
 try:source=str(source.relative_to(R))
 except ValueError:source=str(source)
 assert 'research/' not in source and 'study_only' not in source
 images.append(dict(name=im.name,users=im.users,source=source,pixels=list(im.size),colorspace=im.colorspace_settings.name,packed_payloads=[dict(bytes=q.size,sha256=hashlib.sha256(q.data).hexdigest()) for q in packets]))
materials=[]
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree;tex=[]
 for n in nt.nodes:
  if n.type!='TEX_IMAGE' or not n.image:continue
  outgoing=[]
  for o in n.outputs:
   outgoing += [dict(output=o.name,target_type=link.to_node.bl_idname,target_name=link.to_node.name,input=link.to_socket.name) for link in o.links]
  tex.append(dict(node=n.name,image=n.image.name,colorspace=n.image.colorspace_settings.name,extension=n.extension,interpolation=n.interpolation,outgoing_links=outgoing))
 materials.append(dict(material=m.name,users=m.users,physical_repeat_m=m.get('texture_repeat_m'),provenance=m.get('texture_provenance'),physical_limit=m.get('physical_limit'),texture_nodes=tex,normal_map_nodes=[dict(name=n.name,space=n.space,strength=n.inputs['Strength'].default_value) for n in nt.nodes if n.type=='NORMAL_MAP']))
report=dict(era=E,source_blend_sha256=file_sha256(bpy.data.filepath),file_images=len(images),materials=len(materials),images=images,shader_inventory=materials,checks=dict(all_file_images_packed=True,no_research_images=True),limitations=['Payload hashes verify exact packed bytes, not source authenticity by themselves','Image/channel inventory does not measure material reflectance, normal-map correctness or architecture','Physical repeat values are authored controls; many details remain photo-informed approximations','Height maps are optional sidecars unless an actual shader link is listed; review scenes use no true displacement'])
(R/'manifests'/f'packed_material_inventory_{E}.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['era','source_blend_sha256','file_images','materials','checks']},indent=2))
