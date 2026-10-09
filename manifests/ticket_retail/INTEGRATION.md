# Ticket-lobby retail module

Original geometry authored 6 October 2026. This is a qualified reconstruction of public-facing evidence, not a measured current suite model. Do not distribute source photographs or third-party graphics.

## Integrate

1. Execute `scripts/ticket_retail.py` in the same shared batching namespace as other fit-out modules, after `current_fitouts.py` / `study_lounge.py` and before `FINISH BATCHED GEOMETRY`. It uses `box`, `beam`, `lathe`, `addmesh`, `mat`, `M`, `B`, `scene`, and the imported math/Blender helpers. It restores `GROUP` using `finally`; 2017 emits no geometry or lights.
2. Within the current-era camera additions, add `cams.update(globals().get('TICKET_RETAIL_CAMERAS',{}))`.
3. Preserve `scene['ticket_retail_evidence']`, which is emitted by the module. Optionally copy that dictionary into the general coverage manifest.
4. The module creates only original geometry and solid PBR materials, alongside existing stone/marble maps. It requires no new texture files. Main UV batching gives all meshes finite metric UVs.

## Core-owned cuts and removals, 2026 only

### The Shop, west plane X+8.10

Replace the simple solid west wall only inside Y34.25..46.95, Z0..4.22. Keep existing solid wall above Z4.22 as the blind clock-niche backing. The module supplies the lower 12.70m central documented frontage cluster, with its cornice projecting to Y34.09..47.11.

Equivalent core call for the remaining wall:

    wall_x_portals(8.1,31.7,50.7,9,[(40.60,12.70,4.22)],PL,'ticket-lobby west wall around retail frontage',depth=.6)

Remove the older current-era stub batches:
- ticket office walnut frontage
- ticket counter window
- recreated clock face
- clock minute hand
- clock hour hand

Keep the lobby chandeliers from the same `if not AGED` block.

The module's central open entry is Y40.60±0.75, floor≈Z0.13 to Z3.03. Four ticket-window bays flank it. Their number is the central reconstructed cluster, not a claim about all historic ticket positions. The visible fixture vignette occupies X8.50..13.60, Y37.95..43.25, ceiling Z3.16. Its siting behind the central entry is interpretive; the owner's single corner image does not establish the complete shop arrangement.

The main wall's front face is X7.80. The module's blind-arch moulding sits around X7.735 and is therefore visible in front of that retained wall. The clock and current THE SHOP lettering are fully replaced by the module.

### Neighbor, east plane X−11.89

The HNS raster shell gives the ticket lobby an asymmetric east edge. Do not move this doorway to the obsolete X−8.10 east wall. Register the core east lobby envelope and arcade interface to X−11.89.

Remove/replace the east wall fragment Y43.36..48.52, Z0..6.75. The module supplies that stone fragment to Z6.75. Keep core backing above that level. The actual entrance is centered Y46.05; structural aperture≈2.38m wide, top Z3.15. Timber jambs reduce the clear entry to≈2.02m wide; the lower transom rail gives a clear opening below≈Z2.59.

Do not leave a solid X−8.1 wall in front of the replacement. Preserve the arcade main portal to the north and concourse route to the south. Keep the core arcade south wall at Y43.36; the module's bounded floor/fixture fragment extends only X−15.85..−11.89, Y44.73..47.38 approximately. Nothing here establishes a complete tenant suite.

Two open door leaves project about0.94m west into the lobby. That projection is photographed and intentional. The actual sign is NEIGHBOR x FOLK. The visible PANTRY label is reproduced as simple original font geometry; product branding and wall art are omitted.

## Collections

- 21 THE SHOP: restored stone/window/clock central frontage
- 22 THE SHOP: qualified 2024 single-view fixture vignette, not complete2026 as-built
- 23 NEIGHBOR: 2026 doorway and short photographic view fragment
- 24 RETAIL LIGHTS: two illustrative fill lights; these are not a lighting/MEP survey

## Verification

Run isolated QA with:

    /workspace/scratch/253ae098be12/3d-tools/bin/blender -b -t 2 --python scripts/qa_ticket_retail.py

It instantiates only this module and a temporary diagnostic floor/lighting rig, never the station. It checks finite vertices/UVs, material/UV coverage, zero degenerate polygons, no reference photos loaded, GROUP restoration, and the2017 no-op. Three640×48012-sample CPU previews are written under `qa/ticket_retail/`; do not mistake the neutral background or diagnostic floor for proposed station fabric.

Full-scene doorway sightlines, adjacent stone seams, and the main wall cuts require core integration review. Isolated previews are not that review.
