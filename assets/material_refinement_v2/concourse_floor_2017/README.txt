2017 MAIN CONCOURSE FLOOR / ORIGINAL BOUNDED PBR CANDIDATE

Use as a separate material: Concourse 2017 worn mineral floor.
Scope: concourse qualified2017 unpatterned floor in the source-informed
masonry/floor group. Do not globally replace Weathered concrete, or apply this
to the Grand Hall, exterior concrete, passenger ramp, or other rooms.

The architect's visual tour p39 says the original concourse terrazzo had
deteriorated beyond repair and was replaced. This does not document a uniformly
bare-concrete floor in 2017. The surviving original terrazzo, exposed substrate,
deposits and dust proportions and damage positions remain unresolved.

This candidate supplies a restrained material class: neutral-warm worn mineral
binder, fine irregular aggregate, sparse millimetric dust and subtle short
abrasion variation. No broad cloudy white masks, new floor geometry, fractures,
wet patches, rubble, decorative restored bands, graffiti, or historic divider
layout have been invented. The 2010 photos are qualified context; aerials are
2017-published project imagery, not an exact May 2017 capture survey.

MAPS
basecolor.png: RGB8, sRGB; original authored albedo, no baked illumination
roughness.png: L8, linear
normal.png: RGB8, linear, tangent-space OpenGL +Y; strength 1.0
height.png: grayscale 16-bit unsigned PNG; linear data, sidecar only
orm.png: RGB8 linear, R=1 neutral AO; G=roughness; B=0 metallic

All maps are 3072 x 3072. Inferred 4 x 4 m seamless repeat, 1.302 mm/texel.
The 4 m period is an authoring scale, not a claimed historic floor module.
Height decode in metres: (uint16 / 65535 - 0.5) * 0.0004.
The actual relief is much smaller than that encoding range; see QA.
True displacement must remain disabled. No source photograph pixels are used.

INTEGRATION
1. Keep a distinct material with texture_repeat_m=4.0. Use REPEAT U/V.
2. The existing cw_face custom UVs are metric coordinates. build_station.py
   divides them by texture_repeat_m during mesh assembly. Do not divide twice.
3. For a saved scene the main floor already has world/4 UVs, so the new material
   can reuse them. Confirm that mapping after any topology repair.
4. Use sRGB only for basecolor; all other textures are Non-Color/linear data.
5. The support normal already encodes the conservative physical height scale.
   Use normal strength 1.0, not a large bump or displacement multiplier.
6. glTF: baseColorTexture=basecolor, normalTexture=normal, metallicRoughnessTexture
   =orm, metallicFactor=0, roughnessFactor=1. Height stays a sidecar.

integration_candidate.py contains optional definitions for strict one-batch
retargeting. It does nothing when imported. It has not been run in Blender.
The parent should integrate only after its shared topology/contact repair.
Re-render the actual fixed concourse_source_eye camera at corrected exposure.
The new albedo mean differs from inherited dark concrete; no measured color or
calibrated lighting match is claimed. Accept only after the fixed-camera check.

QA
qa/unlit_material_inspection.png: 4 m field, 0.625 m 1:1 detail, map thumbnails
qa/unlit_2x2_repeat.png: 8 m by 8 m unlit repeat, without overlaid seam lines
qa/original_project_before_after_unlit.png: old/new ORIGINAL project albedos
qa/encoding_and_seam_checks.json: PNG bit depth, map sizes, ORM, true relief,
normal slopes, wrap-neighbor statistics and macro-albedo contrast

Seam checking compares edge-neighbor differences with ordinary in-tile
neighbor differences. First/last pixel identity is not the periodicity test.
Source images are private study-only and absent from output maps and QA.

Reproduce: python assets/material_refinement_v2/concourse_floor_2017/prepare.py
Requires the existing NumPy, SciPy and Pillow; no Blender or imagegen call.
All preparation output stays in this new candidate directory. No live scripts
or previously completed material assets were edited.
