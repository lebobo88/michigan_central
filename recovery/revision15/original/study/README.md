# Michigan Central west concourse portal detail study

A bounded, source-supported revision after station checkpoint 14. Both-era station models and all five checkpoint 14 archives are unchanged. This study is separate from the north-pediment work and does not complete the station.

## What improved
- Small-side terracotta features: stepped heads, shallow curved crowns, centered keys and the blind north feature's inset frame/sill
- Main retained metal portal: rounded opaque-panel borders, small attachment heads and layered lower rails
- Restored 2026 variant only: physical inset diamond grilles in the lower side panels

The inherited 2+8+2 glazing hierarchy, clear main passage, floor layout and wall controls are preserved. 2017 retains stripped lower framing and no restored grille or new glass. Exact dimensions, 2017 persistence, material wear and fine profiles remain qualified in EVIDENCE.md.

## Models and real rendered views
- concourse_west_portal_2017_STUDY.blend / .glb
- concourse_west_portal_2026_STUDY.blend / .glb
- import_2017_detail_oblique.png and import_2026_detail_oblique.png: final exported GLBs actually imported and rendered in Blender
- import_2017_small_crown.png and import_2026_small_crown.png: close views of the same actual GLB imports
- 2017_west_portal.png and 2026_west_portal.png: broader isolated original-study render context
- baseline_2026_west_portal.png: matched lighting/camera baseline before the added detail

Research photographs are not included in these models. No image generation was used. Existing legitimate authored material assets were reused. Neutral gray through-views are omitted context, not assertions about room finishes.

## Verification records
- qa_2017.json / qa_2026.json: new solid topology, finite explicit UVs, standing-height passage checks and strict GLB position/normal/UV/tangent validity
- khronos_2017.json / khronos_2026.json: 0 errors, 0 warnings; complete, untruncated reports
- import_qa_2017.json / import_qa_2026.json: all expected meshes actually imported, with source GLB hashes and actual render paths
- tangent_precision_2017.json / tangent_precision_2026.json: tightly bounded inherited-dentil exporter rounding correction, with a byte-scope proof
- integration_helper_qa.json: exact replacement and repeat-application guard tested against isolated original west components
- protected_artifact_recheck.json: two full source BLENDs and five revision14 archives remain byte-identical
- PIXEL_REVIEW.json: explicit final image inspection, distinctions and remaining limitations

The component helper apply_component.py never saves or overwrites a scene. It only appends the new detail meshes and replaces the exact old rectangular small-feature lintel object. Full-scene integration is pending; follow NEXT_INTEGRATION.md.

## Reproduction
Use the project Blender 5.2.2 installation. Run build_study.py with --era 2017 or --era 2026 for original-study renders and exports; --baseline renders the original context. verify_import.py takes 2017 or 2026 after the Blender -- separator and imports the actual GLB before rendering. The scripts intentionally use the existing immutable source file hashes and refuse a mismatched source. No full scene is regenerated or saved.

Source appearance remains simplified. Cloudy inherited overlight response, the plain dark small-door leaf/reveal seam, regularized fine relief, exact source wear and the unregistered west continuation remain unresolved. These are actual mesh renders of a useful component refinement, not a complete photoreal or surveyed reconstruction.
