# Bounded pre-restoration north forecourt module

## What is modeled

Original geometry for a broad paved apron; two elongated low-shrub beds with exposed soil; pale station-facing balustrades and rounded outer returns; a central paved approach with shallow side lobes, flagpole and simplified thin fence/gate; station-side sidewalk; two bounded asphalt frontage-road strips separated by a narrow paved, streetlit median.

The bed footprints are independent photo-fit controls. They were not inherited from the 2026 module. The plant inventory is deliberately low shrubs only, without trees or modern flower-pot additions in these beds. All plants are independently authored polygon geometry, shared through four Mesh datablocks. No particles, external vegetation assets, photograph cards or geometry extraction are used.

## Temporal and dimensional limits

The main sources are Dandelion Air / Aleksey Bochkovsky photographs in a creator presentation linked by a Pix4D showcase published 15 September 2017. The individual photograph capture dates are not stated. "2017" is the project model's period label, not proof that every detail was photographed in that calendar year.

Actual image pixels inspected: `research/south_structure/presentation_ref_12.jpg` and `_13.jpg`. These two different views establish topology; smaller duplicate versions were not treated as independent evidence. The model uses the project’s 105.2576 m overall station-width reference for loose proportional fitting, but the photographs are not certified orthophotos. No exact site dimensions, curb radii, road widths, survey datum, slopes or elevations were available. Every site coordinate here remains editable and approximate.

The undated Historic Detroit view north from the station (`#p10`, photographer Bob Laperriere) was inspected for corroboration and to understand what lies outside this module. Its filename is not capture-date evidence. The crescent island, boulevard, wider park lawns/paths/trees and outer street junctions are intentionally absent, with five named metadata/viewport coverage markers documenting the limits.

## Explicit gaps and approximations

- No precise complete 2017 park reconstruction
- No modern circular lawn, modern park planting or post-2023 park topology
- No certified lane counts, traffic directions, pavement markings, parking-bay inventory or complete side-junction geometry
- Faint angled apron markings are visible in a reference, but their complete layout and purpose are not known, so no full marking plan is invented
- Shrub species/count/placement, baluster and pier counts, fencing gauge, lamp manufacturer/shape, flag folds, flagpole and lamp heights are approximations
- Surface cracks, paving joints and material weathering are original interpretive details, not traced damage maps
- Flat local levels are for the reconstruction only, not grading, drainage or accessibility certification
- No private interiors or unseen surrounding blocks are added

## Sources

1. Creator presentation: https://spark.adobe.com/page/OMI5cVvEGgqxk/
2. Dated publication link: https://community.pix4d.com/t/michigan-central-station-by-aleksey-bochkovsky-dandelion-air/3356
3. Undated context only: https://historicdetroit.org/galleries/michigan-central-station-pre-restoration-exterior#p10

All source photographs retain their creators' rights and remain reference-only. No reference image, screenshot, PDF or downloaded photogrammetry mesh is redistributed or loaded into a model material.

## Integration contract

1. Execute `scripts/north_forecourt_2017.py` with `execute_component` before core batch finalization. It requires the existing `B`, `M`, `mat`, `pbr`, `addmesh`, `box`, `lathe`, `beam`, `scene`, `ROOT`, `ERA` and math helpers
2. Call `forecourt_2017_post_finalize(collections, room_nodes)` after batch finalization to place shared shrubs and coverage-marker empties
3. Merge `FORECOURT_2017_CAMERAS` into the camera registry
4. Export the module's `export_group` and `export_coverage_marker` empties alongside its mesh objects
5. Replace the main script's old statement that all 2017 north grounds remain unmodeled with this narrower bounded-forecourt / broader-park distinction

No main build file was edited by this module's author. `GROUP` is restored; CLI argument names are not overwritten. For `ERA != '2017'`, no materials, batches, images, scene objects, instances or cameras are emitted. The post-finalizer is idempotent and a no-op in other eras.

## Assets and checks

- Four original 512 px procedural PBR surface sets plus independently drawn US flag pattern in `assets/forecourt_2017/textures`
- Read-only reuse of the project's original `limestone_2017` and `north_plaza/np_asphalt` materials
- Reproducible texture generation script in `assets/forecourt_2017/prepare_textures.py`
- Isolated non-render test harness in `assets/forecourt_2017/qa/qa_forecourt.py`
- Binary GLB accessor checker in `assets/forecourt_2017/qa/check_glb_accessors.py`

The QA harness checks finite vertices, normals and UVs; triangle areas; noncollapsed UVs; GROUP and CLI argument preservation; era guard; shared-mesh reuse; post-finalizer idempotence; actual GLB import; geometry bounds; and preservation of era/space/coverage metadata. Separate binary accessor checking examines exported attributes and tangent bases. No render or photorealism claim follows from passing these checks.

## Isolated QA result

Geometry and binary GLB checks passed with 173 mesh objects, 45 unique meshes, 63,863 unique vertices, 82,092 unique triangles, and 132 shrubs sharing four original meshes. There are zero nonfinite attributes, degenerate triangles, collapsed UV triangles, nonunit normals or invalid tangent bases. Actual Blender GLB import retained the five coverage markers, era/space metadata, material assignments and expected metric bounds. The 2026 no-op guard, GROUP and CLI-argument preservation, and post-finalizer idempotence passed. Two authorized isolated previews were subsequently rendered and inspected; whole-station integration remains a separate check.

An additional exported-top-face area test confirms that the apron partition totals 2,923.5200 m² and the bounded road/median partition totals 3,328.0000 m², matching their bounded rectangles. The median-tip arc subdivision was conformed to remove a 0.0236 m² numerical gap before this checkpoint. This is a coverage/area consistency check, not a full arbitrary polygon-intersection proof.

## Visual review

The overhead and oblique PNGs in the QA directory were inspected. The paired-bed/central-lobe arrangement, station-facing rails, low exposed-soil shrubs, flagpole/gate, sidewalk and divided-road median read as intended, with no unexpected visible holes or stray plants. The oblique is a close view and crops part of a bounded road corner. Neutral background is only a rendering backdrop. The exact reviewed camera overrides were copied into the module registry and the isolated non-render checks were rerun; the GLB hash remained unchanged. No whole-station, as-built or photorealism claim is made.
