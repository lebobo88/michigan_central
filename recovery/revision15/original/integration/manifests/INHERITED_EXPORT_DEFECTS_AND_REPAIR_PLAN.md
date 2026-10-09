# Inherited full-export defects and separate repair plan

Status: corrected revision15 concourse integration is sealed as a bounded WIP checkpoint. Source, per-detail placement, actual full-GLB import and eight matched render views passed. New details are strict-zero and all retained inherited payloads are byte-identical to revision14. The inherited full-export defects below are NOT repaired; revision15 is not globally strict-clean or a dependable finished asset. Earlier attempt01 hashes and placement passes are superseded evidence only.

## Exact baseline counts

Counts below are per unique GLB primitive data, not multiplied by scene instances. Reports list node names and instance counts. A triangle may appear in both degenerate-geometry and collapsed-UV counts.

### 2017
- Baseline full GLB SHA256: e501bccc93a36211f3a10466ce75151e62f73fc92cff2fcbd5c431697dbd9f8b
- 102 affected mesh names; 113 affected primitives
- Issue rows by category: {'nonorthogonal tangent': 108, 'collapsed UV triangle': 10, 'degenerate triangle': 2}
- Affected element counts: {'nonorthogonal tangent': 10688, 'collapsed UV triangle': 5876, 'degenerate triangle': 1370}
- Tangent severity counts: {'near_threshold_roundoff_range_vertices': 7602, 'substantial_over_0_0002_vertices': 3086, 'substantial_on_nondegenerate_triangles': 3086, 'substantial_on_nondegenerate_valid_uv_triangles': 20, 'substantial_only_on_degenerate_triangles': 0}
- Strict thresholds: |N dot T| > 1e-4; geometry double-area < 1e-10 square metres; UV double-area < 1e-12. The optional 0.0002 severity boundary is diagnostic classification, not a relaxed acceptance threshold.

### 2026
- Baseline full GLB SHA256: 3a58625a4f5055ef2bb50e9bfe272f591fa07ee2f59039081a140f6e588bb711
- 199 affected mesh names; 228 affected primitives
- Issue rows by category: {'nonorthogonal tangent': 223, 'collapsed UV triangle': 17, 'degenerate triangle': 6}
- Affected element counts: {'nonorthogonal tangent': 28486, 'collapsed UV triangle': 10573, 'degenerate triangle': 6130}
- Tangent severity counts: {'near_threshold_roundoff_range_vertices': 21820, 'substantial_over_0_0002_vertices': 6666, 'substantial_on_nondegenerate_triangles': 4813, 'substantial_on_nondegenerate_valid_uv_triangles': 1649, 'substantial_only_on_degenerate_triangles': 1853}
- Strict thresholds: |N dot T| > 1e-4; geometry double-area < 1e-10 square metres; UV double-area < 1e-12. The optional 0.0002 severity boundary is diagnostic classification, not a relaxed acceptance threshold.

## Source-to-export evidence and limitations

- Frozen revision 14 source reports have zero degenerate polygons and zero collapsed UV triangles. These do NOT establish that every exported defect originated in a modifier: validate_scene.py checks polygon area; check_uv_area.py explicitly skips source loop triangles whose area is below 1e-12. A valid-area quad or n-gon can contain a degenerate triangulation that both diagnostics miss.
- The current build_station.py, west_public_rooms.py and tower_facade_v2.py are byte-identical to frozen revision 14 copies. Integration snapshots report zero changed inherited objects. Source modifier inventories were recorded from the actual saved revision 15 sources and can therefore describe retained revision 14 chains.
- Both full exports use export_apply=True. Modifier-generated geometry/UVs and exporter triangulation therefore participate in the final data even when original source vertices are unchanged.
- Installed Blender 5.2.2 glTF exporter evidence: io_scene_gltf2/blender/exp/primitive_extract.py lines 1462 and 1529 independently round normals and tangents; io/com/constants.py line 160 sets ROUNDING_DIGIT=4. This is a demonstrated mechanism for threshold-level normal/tangent nonorthogonality. It does not explain |N dot T| values near 1 or justify relaxing the test.

## Prioritized separate cleanup plan

### 1. Rosette/petal topology and normal-mapped shading, 2026 only

Highest-confidence source-topology explanation. west_public_rooms.py: 210-220 emits three coincident vertices at t=0 (width and depth zero), and the t=1 row collapses at stored float32 precision. It keeps endpoint quads. Export triangulation can therefore produce a zero-area half-triangle while the full source quad still has positive area. These objects have no modifiers in the actual saved-scene inventory. The defect is not correctly described as bevel-created.

- West plaster rosette twelve original radial leaves: 2352 degenerate and 2352 collapsed-UV triangles; 1960 substantial tangent vertices, 980 on valid-UV nondegenerate triangles; max |N dot T|=0.383873619
- West plaster rosette inner curled petals: 1176 degenerate and 1176 collapsed-UV triangles; 1176 substantial tangent vertices, 588 on valid-UV nondegenerate triangles; max |N dot T|=0.409541671
- West ceiling crossing small floral relief: 480 degenerate and 480 collapsed-UV triangles; tangent deviations are only near-threshold roundoff
- All use portable normal-mapped plaster. Degenerate faces contribute no surface area, but shared affected vertices on real adjacent triangles can distort local shading. The actual appearance requires a bounded close render; numerical severity is not proof of a visible defect in every view.
- Proposed fix in a separate revision: replace collapsed endpoint rows with one vertex and explicit nondegenerate triangle fans, retain the interior shape and metric UV scale, regenerate outward normals/tangents after topology/UV validation. Do not just overwrite tangent vectors to hide degenerate topology.

### 2. Bevel-evaluated tower, wood and stone families

- tower deep cornice profiled modillions, both eras: 1368 degenerate triangles; 1958 collapsed-UV triangles; 134 substantial tangent vertices, 20 touching valid-UV nondegenerate triangles; max |N dot T|=1.0; 1368 geometric degenerates have exact zero area. Nonzero geometry with collapsed UV totals only 0.0000776563 square metres. Actual retained chain is BEVEL then TRIANGULATE. The generator stacks five profile blocks (tower_facade_v2.py: 230-235); source-versus-evaluated triangle comparison is needed to identify bevel contact/sliver origin exactly.
- West entablature carved palmette frieze, 2026: 752 geometric-degenerate triangles, 645 collapsed UVs; 394 substantial tangent vertices, 43 on valid-UV nondegenerate triangles, 285 only on degenerate triangles. Actual chain BEVEL then TRIANGULATE. The generic builder applies bevel by the name token entablature to this thin open ornamental relief. That rule is a specific candidate cause, but no modifier-toggle experiment has yet proved causality.
- forecourt balustrade continuous stone plinth, 2026: 12 collapsed UV triangles; 18 substantial tangent vertices on nondegenerate valid-UV triangles; max |N dot T|=0.652225137. Actual chain BEVEL then TRIANGULATE. The source is an explicit slab/ribbon triangulation in north_plaza.py; inspect side/bevel UV interpolation before changing authored geometry.
- Proposed fix sequence: collect raw loop-triangle metrics, evaluate one modifier stage at a time, compare exact face/UV ancestry, and only then adjust close-contact bevels or remove accidental name-driven bevels on open relief. Preserve silhouettes/materials. Recompute tangents after geometric/UV defects are removed. Normal-mapped terracotta, walnut and stone make these more appearance-sensitive than glass tangents.

### 3. Glass thickness UVs and fanlight endpoint, both eras

- Glass clear has 3916 collapsed-UV triangles in 2017 and 3948 in 2026. All are geometrically nondegenerate. The affected original surfaces receive SOLIDIFY; most also receive TRIANGULATE. Copied planar UVs on new thickness side faces are the leading explanation, strongly consistent with the 8 mm side extent in exported coordinates. A raw-versus-evaluated probe is still needed to certify each face ancestry.
- Some glass side-face tangents have |N dot T| near 1, but these materials do not have normalTexture. This lowers tangent-specific visual risk. Invalid UVs can still be a portability or future-texturing defect, and one should not infer that unrelated glass cloudiness is caused by these unused tangent attributes.
- Separate end wall fanlight glazing has 2 degenerate and 2 collapsed-UV triangles per era; it has only TRIANGULATE. build_station.py: 553 repeats the starting arc endpoint at i=40 when constructing the n-gon. Exact endpoint duplication at stored precision is a plausible and source-specific explanation; deduplicate the boundary before triangulation in a future revision.
- Proposed fix: deliberately unwrap SOLIDIFY rim faces or author a closed UV-valid pane. Preserve 8 mm thickness and authored normals. Remove duplicate fanlight boundary endpoints before triangulation. Do not blanket-recompute glass normals.

Exact glass object names and collapsed-UV triangle counts (both eras unless marked 2026):
- east exit door arched transoms glazing: 258
- east main entrance arched transom glazing: 86
- east southern wood windows glazing: 430
- north monumental window glazing: 258
- north secondary arched window glazing: 344
- north wing wood window glazing: 516
- side wood arched window glazing: 1634
- south hall rear elliptical clerestory glazing: 390
- Passenger ramp restored glazed roof: 16 (2026)
- Carriage 2025 observed roof-lantern sloped glazing: 16 (2026)
- end wall fanlight glazing: 2; different material, Glass tower blue; counted separately from Glass clear

### 4. Near-threshold exporter precision

- 7602 vertices in 2017 and 21820 in 2026 satisfy 1e-4 < |N dot T| <=2e-4. These are low-magnitude deviations consistent with the verified independent four-decimal rounding stage. They remain strict failures and were not repaired in revision 15.
- The inherited concourse cornice dentils have east 71, north 268, south 529, west 64 affected vertices in each era. Max dots range 0.000117543–0.000128839.
- A future precision-only export pass could Gram-Schmidt-orthogonalize verified tiny tangent deviations against unchanged normals, normalize, preserve handedness, and prove only intended tangent XYZ bytes changed. First fix severe topology/UV/tangent defects; do not apply the west-dentil-only study repair globally.

## Exact-no-regression preservation recovery already performed

Corrected-placement attempt02 2026 re-export produced tiny UV changes on four inherited primitives despite unchanged source snapshots and POSITION/NORMAL/index data. Max float32 UV ULP differences were 2 for forecourt plinth, 8 for bluegray sofa, 2 for wine sofa, 2 for palmettes. These sizes are consistent with floating interpolation roundoff; the exact exporter/evaluation nondeterminism was not isolated. The strict test was not relaxed.

The recovery restored only exact revision 14 UV and tangent XYZ arrays for those four identities after verifying accessor layouts, unshared accessor ownership, POSITION/NORMAL/index bytes, material definitions, samplers and embedded-channel bytes. It preserved tangent handedness. 7,358 bytes changed; all bytes outside 6,817 permitted per-vertex spans have the same complement hash. Failed pre-recovery audit remains saved. Reverse/replay of the recorded byte patches reconstructs both exact hashes, proving reproducibility without another export.

- Pre-recovery 2026 SHA256: 54e2a3d215f1cabd04885399f5e43f4c0cf2a76f8db4b93cb65fbf84a0cd3f9c
- Final 2026 SHA256: c1801cde3f864e851863c5b16c121cc7228725940465a5ae424fc4260adb669e
- Current 2017 SHA256 (no payload recovery): 58594a65c501a45493fd9fe97fb75f4fce014efe8cd6f50b275c5bb4e2e596e1
- Final inherited data equals baseline exactly; all 48/166 new meshes have zero strict errors. Retained baseline defects and count severities remain exactly as above.
- Post-recovery 2026 Khronos: 0 errors, 0 warnings, 1531 informational messages, untruncated. Schema conformance is not a claim of globally defect-free geometry.

## Probe and acceptance specification for a separately authorized repair

For the exact names above, record raw source polygons and loop triangles (including those currently skipped), object transforms, custom split normals, UVs and full modifier parameters. Then record evaluated triangles before/after each modifier and at the final export stage. Match faces by spatial/UV provenance rather than only indices after topology-changing modifiers.

Gate each repair on: finite attributes; positive nondegenerate triangle area; noncollapsed UVs; valid tangent length, orthogonality and handedness at the unchanged strict thresholds; material/channel identity; source and export silhouette/bounds; actual imported close renders under matched light. Keep full-station interface, era, floor and protected-artifact checks. A future severe-defect repair needs its own authorized revision and must not retroactively relabel revision 15 as globally clean.

## Reusable artifacts

- scripts/audit_export_geometry.py: read-only strict per-primitive analyzer and exact baseline-delta comparator
- scripts/restore_inherited_export_payloads.py: guarded, hash-pinned preservation recovery; default dry run and explicit --apply
- manifests/baseline_full_geometry_2017.json and 2026.json: every primitive, attribute hashes, affected vertex/triangle counts, areas, UV metrics, material normal-map status and source node references
- manifests/revision15_full_geometry_2017.json and 2026.json: final strict-zero/new-detail and inherited nonregression results
- manifests/revision15_full_geometry_2026_pre_recovery.json: preserved failed evidence with ULP and vector deltas
- manifests/inherited_export_payload_recovery_2026.json: all before/after patch bytes and byte-scope proof
- manifests/recovery_replay_verification_2026.json: deterministic reverse/replay proof
- manifests/audit_export_geometry_selftests.json: six diagnostic gate tests
- manifests/source_modifier_inventory_2017.json and 2026.json: actual saved-scene retained modifier chains
- manifests/khronos_2026_post_payload_recovery.json: complete conformance validation for final 2026 hash

Re-run example (replace ERA with 2017 or 2026):
python scripts/audit_export_geometry.py --glb ../../exports/revision15/michigan_central_ERA.glb --era ERA --output manifests/revision15_full_geometry_ERA.json --baseline-report manifests/baseline_full_geometry_ERA.json --allowlist-report ../concourse_portal_refinement/revision01/qa_ERA.json
Run from manifests/revision15_concourse_integration. No Blender or rendering is invoked.
