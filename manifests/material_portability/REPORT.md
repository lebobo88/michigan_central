# Material portability audit and candidate fix

Status: candidate only. Live builder, source scenes, accepted assets, full exports, and stage13 recovery artifacts have not been modified. Isolated Blender raw-export/import validation is complete; integration into full station scenes is not yet authorized or performed.

## Confirmed defect

Inspected all 65 used materials in the 2017 full GLB and all 144 used materials in the 2026 full GLB. The actual JSON contains 9 affected 2017 and 16 affected 2026 material entries (19 unique names). Every affected entry has neither baseColorFactor nor baseColorTexture and therefore defaults to white. Every affected entry also omits the procedural bump. Roughness and metallic survive correctly as constants. No other unexplained default-white used material was found.

The packed inventories report no image nodes for these materials. Their packing checks pass because there are no texture payloads to pack; they do not prove material fidelity. Source sec_material() links Generated → Noise → ColorRamp into Principled Base Color and Bump into Normal. west_material() non-grain uses the same unsupported graph via scaled metric UV. Grain=True walnut already has accepted image channels and is excluded.

## Source palette and portable proposal

RGB is scene-linear, exactly as authored in the source calls. Mean is the midpoint of the symmetric ramp, not a measured scene-wide original-noise average. Roughness/metallic are unitless authored PBR controls, not measured site reflectance.

| Material | Used eras | Authored linear RGB | Roughness | Metallic | Existing UV repeat | Nominal noise scale |
|---|---|---|---:|---:|---:|---:|
| Secondary 2017 protective plywood | 2017 | 0.26, 0.14, 0.072 | 0.91 | 0 | 4 m | 0.4444 m |
| Secondary exposed ribbed substrate | 2017 | 0.26, 0.23, 0.18 | 0.95 | 0 | 4 m | 0.1667 m |
| Secondary iron rust | 2017 | 0.14, 0.071, 0.035 | 0.73 | 0.4 | 4 m | 0.1000 m |
| Secondary conservation grille | 2017, 2026 | 0.018, 0.02, 0.019 | 0.45 | 0.55 | 4 m | 0.2000 m |
| Secondary original abstract marking 1 | 2017, 2026 | 0.016, 0.14, 0.24 | 0.95 | 0 | 4 m | 0.4000 m |
| Secondary original abstract marking 2 | 2017, 2026 | 0.51, 0.35, 0.035 | 0.95 | 0 | 4 m | 0.4000 m |
| Secondary original abstract marking 3 | 2017, 2026 | 0.35, 0.06, 0.022 | 0.95 | 0 | 4 m | 0.4000 m |
| Secondary original abstract marking 4 | 2017, 2026 | 0.09, 0.11, 0.12 | 0.95 | 0 | 4 m | 0.4000 m |
| Secondary original abstract marking 5 | 2017, 2026 | 0.14, 0.22, 0.22 | 0.95 | 0 | 4 m | 0.4000 m |
| West restored warm ivory plaster | 2026 | 0.73, 0.7, 0.625 | 0.62 | 0 | 1 m | 0.0568 m |
| West patinated pendant bronze | 2026 | 0.11, 0.075, 0.033 | 0.32 | 0.72 | 1 m | 0.0568 m |
| West shallow plaster score shadow | 2026 | 0.38, 0.365, 0.325 | 0.78 | 0 | 1 m | 0.0568 m |
| West restaurant observed unfinished slab | 2026 | 0.205, 0.224, 0.226 | 0.86 | 0 | 1 m | 0.0568 m |
| Secondary brushed bronze | 2026 | 0.24, 0.14, 0.055 | 0.32 | 0.78 | 4 m | 0.1250 m |
| Secondary conserved iron | 2026 | 0.037, 0.046, 0.043 | 0.36 | 0.76 | 4 m | 0.1000 m |
| Secondary pale mineral grout | 2026 | 0.42, 0.45, 0.41 | 0.9 | 0 | 4 m | 0.4000 m |
| Secondary ivory hex tile | 2026 | 0.65, 0.66, 0.59 | 0.51 | 0 | 4 m | 0.1111 m |
| Secondary glazed white ceramic | 2026 | 0.72, 0.75, 0.71 | 0.19 | 0 | 4 m | 0.2667 m |
| Secondary preserved west stair iron | 2026 | 0.12, 0.092, 0.065 | 0.83 | 0.35 | 4 m | 0.1667 m |

## Maintainable narrow integration

Candidate helper scripts/candidates/material_portability.py reparses the actual source call arguments and fingerprints both material constructor functions. apply_candidate_materials() changes only the explicit affected-name allowlist, refuses existing image nodes, retains material names and disconnected original procedural nodes, preserves scalar roughness/metallic, loads and packs original sRGB color and Non-Color OpenGL normal maps. It does not edit geometry, UVs, accepted maps, source builder files, or files outside this candidate scope. Invoke it explicitly in a copied scene first; do not install by default until review.

19 original 512 × 512 base-color maps plus 25 era-specific normal maps total 4,680,848 bytes. The candidate palette image is informational and is not a shaded render. All generated linear means differ from nominal source means by less than 0.000023 per channel.

## Explicit physical and appearance assumptions

- Existing secondary MetricUV uses the core fallback of 4 m/repeat, even though old shaders use Generated coordinates. New 2D noise uses that existing 4 m repeat and the old nominal Noise Scale. This is a disclosed physical-scale reinterpretation, not preservation of per-object Generated placement
- West non-grain already uses metric UV with 1 m/repeat, then multiplies 2.2 and Noise Scale 8. Candidate nominal density is 17.6 per repeat
- Periodic, deterministic four-band spectral noise approximates source stochastic variation and preserves the source ColorRamp palette. It is not a bake or an exact Blender Noise match. Bands above 512px Nyquist are omitted, avoiding aliases
- Color is encoded in sRGB from the authored scene-linear controls. Metallic and roughness stay exact scalars; no fictitious roughness variation is added
- Normal height amplitude approximates original Bump Distance × Strength; old secondary distance is 18 mm for 2017 and 2 mm for 2026, both strength 0.15. West is 0.7 mm at strength 0.1. Resulting tangent perturbations are restrained (candidate maximum 4.6° for 2017 rust)
- Existing geometry supplies ribs, railings, tile shapes, joints, graffiti stroke arrangements, and panel divisions. No directional brushed finish, wood fibres, photographed rust patches, or damage is invented
- No reference photographs are sampled, projected, or packaged. These are original procedural controls only

## Regression and verification

- check_material_portability.py checks actual embedded GLB image pixels in linear light, multiplies baseColorFactor, compares source ramp mean, tests that authored variation remains, checks exact roughness/metallic, portable normal presence/validity, and primitive TEXCOORD_0
- It also rejects any other unreviewed used material that implicitly defaults white and checks expected affected-material presence in full-model runs
- Existing full exports correctly fail: 9/9 affected entries in 2017 and 16/16 in 2026. Those are expected failures proving the regression detects the current defect
- Eight Python tests pass, including default white, silent constant-color fallback, incorrect color-space encoding, factor multiplication, roughness drift, and dropped normals
- All candidate scripts compile
- qa_material_portability.py was run serially for both eras in Blender 5.2.2 LTS. Each actual raw GLB was exported without postprocessing and re-imported for neutral-light comparison. All 25 original shader / portable source / raw export material entries were inspected. Mesh positions/topology/UV fingerprints were unchanged by material-only application
- Both actual raw isolated GLBs pass the semantic source-color regression (9/9 in 2017, 16/16 in 2026). Both uncapped Khronos reports have zero errors, warnings, infos, and no truncation. All 50 embedded image payloads exactly match candidate source PNG bytes. The schema check and semantic check are independent

## Actual neutral comparison and remaining integration gate

Results are under neutral_test/. The 2017 raw GLB is about 2.2 MiB; the 2026 raw GLB is about 3.3 MiB. No full duplicate BLEND was saved.

Visual inspection: in each row the candidate source and its raw re-import have consistent material class, hue, texture pattern, metallic/roughness response and normal detail. Their positions differ within the neutral light rig, so the image is not a pixelwise matched-lighting error metric. Exact image payload matching and scalar tests establish portable channel fidelity separately.

The left original-graph column visibly differs in texture scale and bump, most noticeably on 2017 rust and conservation grille, and on the preserved 2026 stair iron. This is expected from replacing object-bounds Generated coordinates with the pre-existing metric UVs. The candidate grille is smoother than the original graph. These differences remain explicit limitations; the candidate is not an exact visual replacement of the old shader. Palette, authored material class, meaningful low-amplitude variation, and portable PBR are retained.

Next integration gate: explicitly approve the narrow material-only application in full station source copies or the rebuild hook, then export the real full GLBs, rerun the semantic regression plus uncapped validator, and review affected rooms. The existing station exports still have the original defect. No completed-station fidelity or full-scene validation is claimed by these isolated tests. The separate redundant Glass clear Solidify issue remains outside this candidate.
