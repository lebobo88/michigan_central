2017 GRAND HALL FLOOR / BOUNDED FOLLOW-UP

New, isolated full-room atlas only. No completed v2 maps or live assets changed.
Use this directory for 2017 Grand Hall floor assembly, retaining room UVs:
u=world.x/71.0184+0.5; v=world.y/31.6992. Clamp to edge. Do not tile.

The original unlit atlas already included faint joints and perimeter grit.
This derivative adds restrained dust-film variation, sparse short scuffs,
partial dull rose-gray marble visibility and uneven fine edge deposits.
The exact existing joint mask and all original 16-bit height pixels are preserved.
Normal relief is conservatively decoded to 0.072 mm peak-to-peak, not rubble.
No new cracks, major damage, restored bench footprints or floor geometry added.

Maps: basecolor sRGB; roughness linear; normal OpenGL +Y; inferred height16;
orm contains occlusion=1, roughness in G and metallic=0. Height is a sidecar,
not core glTF displacement. Provenance and input/output hashes are recorded.

QA: qa/floor_2017_before_after_unlit.png and qa/floor_2017_physical_aspect.png.
No Blender render was performed for this follow-up. Correct the hall exposure,
then compare the material in the final scene before increasing contrast.
Evidence: May 2017 Historic Detroit pre_p16 and pre_p6, linked in provenance.
This is an original material-class interpretation, not a surveyed damage map.
No reference-photo pixels are included. All numerical PBR values are inferred.

Reproduce with the project NumPy/Pillow/SciPy interpreter and this prepare.py.
