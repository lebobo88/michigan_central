# Michigan Central Station — two-period reconstruction

Status: active work in progress. This is an evidence-led, original architectural reconstruction, not an as-built BIM, survey, archival replica, or completed photoreal digital twin.

## Files

- `models/michigan_central_2017.blend`: editable historical-condition scene
- `models/michigan_central_2026.blend`: editable restored-public-architecture scene
- `exports/*.glb`: embedded-material interchange files; cameras/lights intentionally omitted
- `exports/*_preview_lod.glb`: lighter review assets with 512 px textures and micro-detail omitted
- `assets/textures/`, `assets/material_refinement_v2/`, and the landscape/component asset folders: original PBR maps with physical-scale and provenance records
- `assets/environment/`: verified CC0 Poly Haven environment illumination and source/license record
- `renders/`: actual Cycles CPU renders, with camera/era in each filename
- `scripts/`: deterministic Blender geometry, material, rendering and validation pipeline
- `manifests/`: dimensions, modeled-space coverage, provenance, validation and known limitations

All units are meters. Local +X points station west, +Y station south, +Z upward. Origin is the center of the front hall façade at ground datum. This is a station-relative frame, not a georeferenced Detroit survey.

## Historical basis

Original Railway Age Gazette, January 9,1914, pages 73–81, supplies dimensioned original floor plans. These define the major shell and adjacency, not every contemporary as-built detail. Tower plan dimensions:342 ft frontage,54 ft-deep central strip,54 × 108 ft end pavilions. Office floor spacing 12 ft6 in. Original sources disagree between 230 and 232 ft tower height and between written and drawn overall terminal dimensions; the geometry ledger keeps those conflicts visible.

Dated May/June 2017 photographs guide the abandoned-state differences. In particular, replacement tower windows were already present by 2017; the building is not portrayed as a wholly windowless ruin. Main-hall chandeliers and entrance canopy are absent in 2017. Interior plaster loss, stains, rubble and graffiti strokes are interpretive original distributions rather than copied site scans or exact historical marks.

The restored scene carries visible 2023/24 architectural fabric forward into 2026. Current sources confirm later occupants and changes, but do not provide complete floor plans. Yellow Light and The Study use completed2025 architect photographs and published HNS scope plans. Mezz, private tenant suites, youth-club spaces and hotel-construction areas remain documented coverage gaps. The planned 2027 NoMad hotel is not modeled as a finished 2026 hotel.

The Great Hall roof uses three sail vaults, confirmed by the project engineer’s 2026 article. Selected dome apex is 62 ft, from the architect’s visual tour. Owner sources also describe 54 and 65 ft heights. Possible differing reference points remain unproven; these are not presented as reconciled survey values. The current side-boundary crown17.2m is a photo-compatible modeling trial: the earlier16.16m came only from an assumed surface formula and left insufficient wall for the documented11ft cartouches. Decorated vertical lunettes now sit above the colonnades, with deep reveals to rear glazing. A blended elliptical sail surface retains the62ft central apex. The inferred copper-roof ridge22.0m clears this upper shell by a checked visualization margin; the original76ft roof-height assertion remains separately unresolved.

## Modeled / omitted

The current pipeline models the exterior shell and I-plan tower façades; Great Hall, Ticket Lobby, East Arcade, Concourse, six-door elevator lobby, observed upper passenger ramp and bridge, partial east-exit ramp and west carriage-house exterior. The restored scene additionally contains The Study in the northeast former women’s waiting room, Yellow Light’s visible customer fit-out and shell, detailed west men’s reading room/café woodwork, historic restaurant/lunch-counter shells, and a west tiled corridor with a preserved stair fragment. Individual modules have local geometry tests; targeted full-scene interface, UV, material-transfer and matching-camera checks are recorded per checkpoint; broader physical/detail fidelity remains in progress.

The 2026 public fit-outs use raster-registered published drawings, not contemporary measured CAD. The Study’s nominal28-foot ceiling comes from HNS; its exact coffer-field versus beam-soffit datum is uncertain. Yellow Light’s hidden service furnishings are omitted. The restaurant floor remains the observed unfinished gray substrate. No current dining/hotel operation is implied.

Unknown private tower partitions, shafts, basement systems and tenant furnishings remain explicit gaps in the per-space completeness matrix. No finished hotel is invented. Historical west façade openings are carried forward with a clear qualification. The east-south eight-aperture sequence is supported by the1914 plan and a datedAugust2025 photograph; an earlier seven-bay axon count was schematic. Final HNS north-window controls distinguish actual glazing from a blind arched niche. The southern platform/undercroft remains a material modeling gap:2017 photographs show the uncovered old structure, while a2025 structural-engineering account reports a replacement concrete deck with parking below. Bounds and vertical interfaces are under research. The1914 train-shed roof was demolished in2000 and is excluded from both eras. The restored north landscape follows observed forecourt/road/park topology from designer drawings and built photographs. Tree inventory, dimensions, benches, paths and grades remain photo-fit approximations. That 2023 park arrangement is disabled for 2017. A separate bounded historical paved forecourt, paired beds, flagpole and divided frontage-road reconstruction is included using period-published imagery; exact grading and the full park remain unresolved. The HDRI is generic illumination/reflection with a neutralized camera horizon.

## Materials

Materials combine original procedural maps and actual image-generated original Mankato, rose-marble, walnut and restrained aged limestone-field swatches. The north 2017 field material uses course-related washing only on planar walls; curved profiles and ornament have separate unjointed materials. The latest restored rose floor and 2017 dust/scuff derivative are original procedural refinements. None is a scan of the station. Generated color does not establish measured reflectance; auxiliary PBR maps are conservatively inferred and documented. Height maps are supplied but true displacement is disabled in the review scenes. Geometry carries major relief. Fine chipped edges, carved capital detail and textile/wood accuracy vary by component. GLB uses standard PBR channels and physical clear-glass thickness; Blender source is the appearance reference.

Copyrighted reference photographs and contemporary architect PDFs are for private study only and must be excluded from distributed deliverables. They are not embedded in scene textures. The original 1914 drawings are public-domain research references; all modeled geometry is original.

## Rebuild

Use Blender 5.2.2 LTS or a compatible version. The installed cloud wrapper is recorded by the surrounding tool environment and is not a dependency on the user’s computer.

1. Extract matching-checkpoint scene/source/material archives into the same project folder. Packed BLEND files and embedded GLBs open independently; the procedural rebuild needs the supplied assets and scripts together.
2. Run `python scripts/prepare_project.py` to create output folders. The supplied maps are already prepared. Do not replace the generated originals or regenerate only a subset of materials and assume the checkpoint appearance is unchanged.
3. Run Blender in background with `--python scripts/build_station.py -- --era 2017 --no-render`, then repeat with era 2026. The builder writes packed sources and full GLBs. Use `--no-export` only for development; its metadata explicitly marks any earlier export as potentially stale.
4. Additional fixed-camera images use `scripts/render_review_checkpoint.py`; set a new `STATION_REVIEW_DIR` so earlier PNGs remain immutable. Other camera helpers are also supplied.
5. Run source checks (`validate_scene.py`, `check_uv_area.py`, `check_public_interfaces.py`, `check_floor_overlaps.py`, `check_hall_roof_clearance.py`, `check_era_conditions.py`, `inventory_packed_materials.py`, `check_field_material_scope.py`, `check_exterior_plinth_contact.py`, `check_north_upper_contacts.py`, `check_concourse_floor_material.py`, `check_glass_shells.py`, `check_lobby_interfaces.py`) on each saved source. Export optional LOD/compact variants, run uncapped `validate_khronos.cjs`, import-check with `check_glb_roundtrip.py`, then run `validate_assets.py`.
6. Use `checkpoint_review_status.py` only after the actual images and checks finish. It binds both eras and export variants to saved-source hashes. Review PNGs visually; technical checks cannot do this step.

Python material-generation helpers use NumPy, Pillow and SciPy. Component provenance identifies the generator and required original inputs. Real imagegen originals are supplied as authored assets; mathematical regeneration does not recreate those images. The packed material inventory records the exact image payloads present in each source.

The full GLBs include explicit tangent bases, named room nodes and coverage-marker metadata. Each new full export writes a source/export hash lineage; no-export development builds explicitly mark that earlier GLBs may be stale. Immutable recovery packages remain tied to their own checkpoint hashes. Triangulation modifiers retain editable source geometry while making curved cap tangent mapping portable. Legacy normal channels are regenerated from their authored heights with OpenGL +Y orientation.

Outputs are rendered and inspected during development. Passing glTF structure tests does not establish architectural accuracy, every-room coverage, water-tightness or photorealism. See current validation records for checks actually run.

## Review lighting and export stability

Named render helpers apply an interior-only fill-light preset. Exterior renders use world/sun illumination so auxiliary emitters do not appear through the facade glass. These are photographic exposure aids, not measured fixture photometry. The editable scene stores the original interior fill energies. Current review exposure is 1.6 for the enclosed2017 Grand Hall,0.8/0.6 for2017/2026 lift-lobby cameras, and0.4 for other cameras; matched camera positions do not imply identical exposure. Image sidecars record the actual values and helper hashes.

A recorded export postprocess repairs zero tangent vectors on a small carved-frieze batch, using incident triangle UV derivatives where stable and an explicit orthogonal fallback otherwise. It does not change positions, normals, UVs, topology or materials. Full untruncated Khronos reports are the validation authority; capped diagnostic reports are superseded.

The 90 COVERAGE collection contains named visible viewport markers for unobserved areas. Those markers also export as metadata nodes. They are not invented room meshes.

Optional compact GLB processing uses the installed open-source glTF Transform core/extensions/functions and Khronos glTF Validator packages. Set STATION_NODE_MODULES to their node_modules directory when running the supplied .cjs helpers outside the original cloud workspace. These Node tools are not needed to open the packed Blender or GLB files.

## Revision14 recovery checkpoint

The HNS plan-traced lift lobby has two splayed banks of three lifts, retained lateral restroom door mouths and an open west branch. Exact door widths, elevations, complete2017 loss mapping and restroom interiors remain unresolved. The main lobby follows the arcade’s local0.13m modeling datum; its southern connector interpolates to the unmeasured ramp trial. This closes modeling discontinuities without claiming surveyed grades or accessibility compliance.

Source-palette regression identified25 material/era entries that formerly lost procedural color in GLB. The current image-channel replacements preserve authored palettes, scalar PBR factors and restrained normal detail; they are not exact bakes of object-generated noise. Full embedded-channel byte identity and per-export semantic reports are provided. Compact processing uses keepSolidTextures=true to retain authored near-flat normal maps. Schema validity alone is insufficient.

Fourteen exterior capital ornaments use one shared mesh; profiled arch bands, restrained exterior keystones and the mixed opaque/glazed entry canopy are integrated. Carving remains stylized, fabrication dimensions/counts are qualified, and2017 retains only bounded canopy anchor hardware. Closed glass boxes no longer receive redundant thickness shells; open panes retain8mm thickness. Clear-glass roughness0.008 is a source-comparison trial, not measured optics.

Recovery is split into five parts. The2017 full-scene ZIP includes its packed BLEND and full GLB. The2026 packed-source ZIP and separate full-GLB ZIP are separate independently usable formats, split to remain below the per-file limit. Review-model and materials/builder ZIPs are shared. All are explicitly incomplete WIP; exact file lists, hashes and counterpart names are in each package manifest. Earlier checkpoint files remain valid for their own recorded state.
