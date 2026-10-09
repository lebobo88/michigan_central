# North landscape module integration

This is an independently modeled, source-led 2026 draft, not a surveyed as-built. Exact widths, radii, inventory, positions and local grades remain approximate. No OHM/ASLA reference pixels are loaded as assets. The current park is disabled for 2017.

## Before core batch finalization

After ordinary components and before `# FINISH BATCHED GEOMETRY`, add:

```python
execute_component('north_plaza.py')
```

## After the core B loop

After the main batch-to-object loop finishes, before scene save/export, add:

```python
north_plaza_post_finalize(collections, room_nodes)
```

This creates standard object transforms sharing 16 authored Mesh datablocks. It is idempotent per scene and is a no-op for 2017. Do not realize/rebatch the vegetation into global B. Regular GLB export selection already includes the meshes. Keep the core tangent-repair pass after GLB export.

## Cameras

Before the camera creation loop:

```python
cams.update(globals().get('NORTH_PLAZA_CAMERAS', {}))
```

Presets: `north_forecourt_detail`, `north_plaza_axis`, `north_park_aerial`, `north_park_path`.

## Remove the old illustrative site

In the SITE block of build_station.py, retain the initial four-piece `landscape context` ground loop. Its four rectangles deliberately preserve the south ramp opening using X +/-12.8m and Y74.5–88.7m. Change its material from `Lawn texture` to a neutral render-ground material, while keeping its name `landscape context` so existing export exclusion works.

Remove or disable the following site geometry, from `north axial approach` through the end of the context-tree/individual-leaf loop immediately before `# TERMINAL EXTERIOR`:

- `north axial approach`
- `cross paths`
- `station apron`
- `broad entry steps`
- `landscape benches` / `bench legs`
- `context tree trunks`, `context tree branches`, `context tree twigs`, `context individual leaves`

Keep the `terminal foundation datum` boxes under TERMINAL EXTERIOR, all exterior building geometry, existing south foundations and ramp cutouts. Do not replace the four ground pieces with a single solid plane.

For 2017, neutral ground may remain; this module contributes no current north landscape. A historical landscape fragment would require separate dated evidence.

## Assets and provenance

Only new paths are used:

- `assets/north_plaza/textures/`: seven deterministic original PBR sets, about34MB total
- `scripts/prepare_north_plaza_textures.py`: texture generator
- `manifests/north_plaza/texture_provenance.json`: original asset records
- `manifests/north_plaza/evidence_integration_uncertainty.json`: sources, rights, scope and uncertainty

The module reuses the existing original Indiana-limestone material for the stone balustrades. All plants are original seeded mesh geometry, not downloaded vegetation. The 2022/2026 legal ROW dimensions are not treated as asphalt pavement dimensions; NAD83/Detroit vertical survey values are not used as local Z0.

## Isolated QA

```sh
/workspace/scratch/253ae098be12/3d-tools/bin/blender -b -t 2 --python scripts/qa_north_plaza.py -- --render --glb
python scripts/check_north_plaza_glb.py
/workspace/scratch/253ae098be12/3d-tools/bin/blender -b -t 2 --python scripts/check_north_plaza_roundtrip.py
```

The first command creates only the isolated landscape, verifies actual mesh/UV data and the 2017/GROUP guards, exports GLB, applies the existing zero-tangent repair, and renders two bounded 1200px CPU previews. It never loads or renders the complete station. QA output lives in `qa/north_plaza/`; the isolated gray render plane is excluded from the GLB.

The code is intended for integration after the parent has reviewed the evidence/uncertainty manifest and isolated previews. It does not certify full-scene interfaces or final visual quality.
