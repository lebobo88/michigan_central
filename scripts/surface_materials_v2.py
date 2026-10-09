"""Source-informed original PBR refinements; no reference pixels are used.
Run after base material creation, before other modules copy those materials.
"""
_SURFACE_V2_ROWS=[]
_surface_v2_targets=[('Exterior Indiana limestone','limestone_2017_pale',4.0),('Grand Hall floor assembly','great_hall_floor_2017',1.0)] if AGED else [('Rose Tennessee marble','rose_marble_polished',1.2),('Grand Hall floor assembly','great_hall_floor_2026',1.0)]
for _sv_name,_sv_asset,_sv_repeat in _surface_v2_targets:
 _sv_mat=M[_sv_name];_sv_dir=ROOT/'assets/material_refinement_v2'/_sv_asset
 for _sv_channel in ['basecolor','roughness','normal','height']:
  _sv_path=_sv_dir/(_sv_channel+'.png');assert _sv_path.is_file(),_sv_path
  _sv_node=_sv_mat.node_tree.nodes.get(_sv_channel);assert _sv_node is not None,(_sv_name,_sv_channel)
  _sv_node.image=bpy.data.images.load(str(_sv_path),check_existing=True)
  _sv_node.image.colorspace_settings.name='sRGB' if _sv_channel=='basecolor' else 'Non-Color'
  _sv_node.label='Original procedural v2 '+_sv_channel+'; inferred surface, not site scan'
  if _sv_asset.startswith('great_hall_floor_'):_sv_node.extension='EXTEND'
 _sv_mat['texture_repeat_m']=_sv_repeat;_sv_mat['texture_provenance']='Original procedural v2, source-informed color/material class; no photo pixels or measured reflectance claim'
 _sv_mat['physical_limit']='Height/normal are conservatively inferred; actual displacement disabled'
 _SURFACE_V2_ROWS.append(dict(material=_sv_name,asset=str(_sv_dir.relative_to(ROOT)),repeat_m=_sv_repeat))
scene['surface_material_refinement_v2']=json.dumps(_SURFACE_V2_ROWS)

if AGED:
 _sv_name='2017 aged limestone wall fields';_sv_dir=ROOT/'assets/material_refinement_v2/stone_field_aging_2017'
 _sv_mat=M['Exterior Indiana limestone'].copy();_sv_mat.name=_sv_name;M[_sv_name]=_sv_mat
 for _sv_channel in ['basecolor','roughness','normal','height']:
  _sv_node=_sv_mat.node_tree.nodes[_sv_channel]
  _sv_node.image=bpy.data.images.load(str(_sv_dir/(_sv_channel+'.png')),check_existing=True)
  _sv_node.image.colorspace_settings.name='sRGB' if _sv_channel=='basecolor' else 'Non-Color'
  _sv_node.label='Original imagegen field '+_sv_channel+'; support maps inferred, not surveyed'
 _sv_mat['texture_repeat_m']=4.0
 _sv_mat['texture_provenance']='Original text-only imagegen material plus disclosed periodicization; generated washing and 1 x .5 m course pattern are interpretive, not exact2017 condition'
 _sv_mat['physical_limit']='Unmeasured wall-field color and roughness; tiny inferred micrograin; no geometric damage or displacement'
 _sv_mat['placement_limit']='North planar shell fields only. Separate profiles, fluted columns, capitals and carved ornament retain unjointed material.'
 _SURFACE_V2_ROWS.append(dict(material=_sv_name,asset=str(_sv_dir.relative_to(ROOT)),repeat_m=4.0,scope='north planar facade fields only'))
 scene['surface_material_refinement_v2']=json.dumps(_SURFACE_V2_ROWS)
