# Southern platform and undercroft component

Status: **detached 2017 local study only; global integration is blocked**. The 2026 generator is parameterized, but it emits no geometry until current placement controls exist. This is an architectural study component, not an as-built survey or a completed southern reconstruction.

## Files

- `scripts/south_structure.py`: era-separated generator, preserving the caller's `GROUP`
- `manifests/south_structure/placement_controls.json`: default global controls; both eras are deliberately blocked
- `manifests/south_structure/local_2017_controls.json`: documented, editable parameters for the detached study
- `models/studies/michigan_central_2017_south_core_LOCAL_STUDY.blend`: editable local study with its used original images packed
- `qa/south_structure/detached_2017_core.png`: the one inspected 640 × 480 preview
- `manifests/south_structure/isolated_qa.json`: actual finite-coordinate, UV-area and degeneracy checks
- `manifests/south_structure/evidence_and_unknowns.json`: source ledger, coverage and integration limitations

## What the 2017 study represents

The approximate 570 × 340 ft cargo core described by MDOT is modeled as a **bounded subset**, using local X center 0, northern core edge Y0 and deck surface Z0. The metric values 173.736 × 103.632 m are unit conversions from approximate published dimensions. They do not imply millimeter accuracy.

The six clearly visible platform strips in the 2017 aerial crop are regularized using the original 19 ft platform width and 40 ft pitch. This is a photo-informed interpretation, not an exact strip-by-strip survey. The south cargo facade has 30 shutter bays, built-up exterior steel columns, a riveted edge girder, exposed terra-cotta headers and original broken-parapet detail. Weeds follow the observed banded distribution, but individual plants and damage locations are invented original arrangements.

The local cargo floor is selected at Z−4.8 m. Together with the provisional slab and edge beam, this provides approximately 3.9–4.25 m of clear height. That is consistent with MDOT's 12–14 ft range. **It does not establish any relationship to the station's hall floor.** Slab depth, platform height, damage pattern and individual facade dimensions remain editable, range-labeled interpretations.

The 1914 Bush train-shed roof was demolished in 2000. It is absent from both era generators. The original shed was approximately 1,104 ft long, with some platforms extending to 1,400 ft. Neither that full length nor the separate 100 ft West Vernor bridge is represented by this cargo-core subset.

## What is not established

- Cargo-core global X offset and exact northern Y alignment
- Hall-floor-to-cargo-floor or track-deck elevation
- The full old track inventory, southern active freight corridor, and platform extensions
- North cargo facade/awning bay positions, private rooms, utilities, complete interior support grid, and former stair/elevator openings
- Current concrete-deck perimeter, support locations, slab thickness and deck elevation
- A completed 2026 park, landscaping, private parking layout or open connection to the station

The registered original plan places the northern viaduct column line around Y104–108 m in the existing hall-relative frame. Its printed dimension chain and pixel ratios disagree. The 77 ft 10 in dimension starts at the outer south wall of the smoking/baggage-room row. The 262 ft dimension begins at the north side-wing front, not at the projecting hall front. Neither the previous Y103.58 calculation nor a precise replacement Y107.98 is adopted as a validated global coordinate.

## Ramp interface

The original passenger ramp goes **down beneath** the track structure into a 40 ft wide, 8 ft high subway; passengers then used stairs up to the platforms. Its floor must not simply be connected to the top of the deck. A 2024 onsite report states that the old platform tunnels are sealed. The existing upper-ramp room's Y87.8 end is provisional.

No new cuts to `build_station.py` or `secondary_spaces.py` are justified at this checkpoint. Once a global datum and verified interface are chosen, the lower ramp length, floor Z, roof alignment and sealed end condition must be reconciled together.

## Integration

Execute `south_structure.py` before the main batched geometry is materialized. It reads `placement_controls.json`; blocked entries only add explicit scene metadata and emit no meshes. No global geometry has been enabled by this work.

The module exposes:

- `SOUTH_STRUCTURE_CAMERAS`
- `SOUTH_STRUCTURE_SPACES`
- `SOUTH_STRUCTURE_EVIDENCE_PROPERTIES`

The main camera dictionary may merge `SOUTH_STRUCTURE_CAMERAS`. The module writes its evidence status to `scene['south_structure_evidence']` and restores `GROUP` even when validation fails.

For the detached study only, set `SOUTH_STRUCTURE_CONTROL_PATH` to `local_2017_controls.json` before executing the module. Do not use that override in a production station build: the coordinate frame is deliberately unrelated to the station.

## QA result and visual inspection

The detached study has 51 mesh batches, 30,980 vertices and 18,117 polygons. Its 37,626 triangulated faces had no degenerate geometry and no collapsed UV triangles. All coordinates and UVs were finite, every mesh had material and UV assignments, used image files were packed, and no study photograph was loaded. Default 2017 and 2026 controls correctly emitted no geometry and preserved `GROUP`.

The one 640 px preview was inspected. It clearly shows an uncovered, six-band platform subset and cargo-core massing. The shutter/rivet detail is small at whole-core scale, and the near-regular pattern is an acknowledged schematic limitation. This is suitable for a detached evidence/modeling checkpoint, not a final photorealistic station view. These checks do not establish complete southern coverage, exact historical condition, full-scene intersections or contemporary architectural accuracy.

## Rights

All geometry and material use is original. Existing project-authored PBR maps are reused. Copyrighted contemporary images were studied only and are excluded from Blender and distributed files. No public photogrammetry mesh was downloaded or extracted. The public creator thumbnail is only a reference, never an asset source.
