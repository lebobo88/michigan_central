# Yellow Light integration: registered revision

- Execute `scripts/current_fitouts.py` in the shared builder context before mesh finalization. It restores `GROUP`, creates original materials and fixture lights, and emits2026 geometry only.
- Merge `FRONTEND_CAMERAS` into the main camera dictionary.
- South arcade wall and glass plane Y43.36: east entry cut X−34.13,width2.32m; west window cut X−30.165,width2.31m; both topZ4.30m. Module supplies their independently resized frames, glazing, sill infill and signage. Remove obsolete sample opaque storefronts here.
- Registered main shop shell: X−37.98..−28.63,Y43.36..48.52 (48.246m²). HNS scope-raster registration is approximate, uncertainty±0.3–0.6m, not a dimensioned contemporary survey. The published full lease area is59.458m²; raster areas are not forced to match it.
- Counter, niches and equipment retain their photo-derived widths. Their main assembly shifted west3.22m; rear fixtures moved0.50m deeper, increasing staff aisle depth. Additional east strip is unfurnished and has no invented internal partition. Menu lettering follows outer east wall. Plain ceiling margins and shell closures are explicitly provisional.
- Rear L service topology is known from HNS but remains UNFIT-OUT: roughly X−33.57..−28.63,Y48.52..51.88.
- Omit named batches `Yellow Light physical perforated ceiling panels` and `Yellow Light curved brass mesh screen wires` from the lightweight preview if needed. Keep them in high detail; edge rims and joint profiles can remain in preview.
- Original maps are in `manifests/current_fitouts/materials/`. The production builder packs them. Supplied height maps have physical displacement disabled at this LOD.
- CURRENT proof image: `qa/yellow_light_registered.png`; current isolated blend: `qa/yellow_light_isolated.blend`. Registered mesh QA:108meshes,487641vertices,369388polygons,zero degenerate/nonfinite data,allUVs. One640×460,8-sample check used2threads.
- PRE-REGISTRATION proof only: `qa/yellow_light_pre_registration.glb` and `qa/glb_pre_registration_report.json`. Those verify exporter/material compatibility with12embedded images and complete normals/UVs, but retain obsolete coordinates. The production lead must export the current module. Earlier PNGs are also explicitly pre-registration evidence.
- No copyrighted study photographs are scene assets.

See `yellow_light_evidence.json`, `qa/mesh_report.json`, and `qa/period_gate.json` for current results and provenance.
