# Revision 15 concourse-only integration checkpoint

This is a bounded integration of the verified west-concourse detail study. It does not complete the station, certify photorealism, or resolve inherited full-GLB numerical defects. North-pediment revision08 remains separate.

## Scope

- Two new full source scenes: models/checkpoints/revision15/michigan_central_2017.blend and michigan_central_2026.blend
- One canonical full GLB per era under exports/revision15; no preview/compact variants or archive repacks
- Exactly 48/166 new detail meshes; exactly one inherited profiled-lintel object replaced in each era
- Rounded metal-panel borders, layered head rails, shallow terracotta crowns/keys and the blind feature frame; lower diamond grilles only in 2026
- No new west continuation or undocumented rooms, no image generation, no new maps

Every retained inherited object keeps its original geometry, UVs, transform and material assignment. The source mesh counts are 742/2760; canonical exports contain 741/2759 mesh nodes, excluding the documented render-only context ground.

## Separate acceptance gates

1. Saved-source checks: public routes, floor overlaps, era state, source polygon/UV diagnostics, original-object preservation, packed materials, and new closed-solid topology
2. Per-detail placement: every appended object compared with its approved isolated study, using evaluated world matrices and evaluated world-space bounds before saving, after reopening, and after actual GLB import
3. Export preservation: every retained inherited POSITION/NORMAL/TEXCOORD/TANGENT/index payload matches revision14. All new detail primitives pass strict numerical checks
4. Material preservation: every used material definition, sampler and embedded image payload is unchanged; semantic palette/PBR checks run on the final hashed exports
5. Actual import: full GLB imported into an empty scene, all node/group/coverage counts, world bounds, era split, 18/25 public routes and nine unqualified west-passage probes checked
6. Matched pixels: source and actual-import source-eye/portal-close renders under the same original scene lighting

Khronos conformance is checked separately. A clean Khronos result is not a claim that the inherited numerical defects are fixed.

## Important unresolved export defects

The full exports retain the documented baseline failures. Counts are unique primitive data, not multiplied by instances; categories may overlap:
- 2017: 10,688 nonorthogonal tangent vertices, 5,876 collapsed-UV triangles, 1,370 degenerate triangles
- 2026: 28,486 nonorthogonal tangent vertices, 10,573 collapsed-UV triangles, 6,130 degenerate triangles

Some are substantial, including normal-mapped surfaces. See manifests/INHERITED_EXPORT_DEFECTS_AND_REPAIR_PLAN.md for exact affected objects, severity, source/export diagnosis and a separate targeted repair plan. These exports remain WIP and should not be described as globally strict-clean or dependable finished assets.

## Rejected first attempt

The first integration read library-appended transforms before a dependency-graph update. New pieces landed at the origin even though counts/UVs and passage probes passed. Actual full-scene pixel review caught it. Its reports/logs/scripts are labeled superseded in attempt01_superseded; images are under renders/revision15_concourse/attempt01_misplaced_details. No rejected first-attempt model is a delivery candidate.

The corrected helper updates the view layer before reading transforms. The per-detail matrix/bounds gate is now mandatory at source, reopened-source and import stages. An unrelated four-primitive UV/tangent re-export drift is restored byte-for-byte from revision14 under a recorded, constrained preservation script. This restoration is separate from fixing inherited defects.

## Evidence and files

- Manifests and final hashes: checkpoint_manifest.json and manifests/*
- Matched renders: renders/revision15_concourse/source_ERA_VIEW.png and import_ERA_VIEW.png
- Frozen input verification includes revision14 source scenes, exports, five archives and the separate north-pediment revision08 artifacts
- Full source/API and GLB files are written only to their revision15 paths; original scenes/archives are never overwritten

Model dimensions, detail profiles, 2017 persistence and damage state remain qualified by the isolated study's EVIDENCE.md. The inherited pale 2017 floor, simplified wear/glass response, sculptural approximations and unregistered onward circulation remain visible fidelity limits.
