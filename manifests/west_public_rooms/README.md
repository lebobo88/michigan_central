# West ground-floor public rooms

## Scope and status

This is an original, evidence-led architectural module for the historic men's reading room, historic café, restaurant, and a partial former lunch-counter shell. It is separate from the northeast women's room now called The Study. It is not a surveyed digital twin, a complete dated interior inventory, or a claim of photorealistic completion.

The 2026 scene carries forward the public architectural fabric photographed in 2023–24. No finished NoMad hotel, undocumented restaurant fit-out, operational equipment, furniture inventory, or exact 2026 construction state is invented. A separate Blender check confirms that the 2017 execution adds no west-room geometry because no matching exact-2017 room-condition photographs were isolated.

## Deliverable

- `scripts/west_public_rooms.py`, executed in the main batch-building namespace before finalization
- `evidence.json`, room extents, sources, coordinate assumptions and exclusions
- `qa/geometry.json`, authoritative isolated verification, including 2017 omission
- `qa/*.png`, low-resolution Cycles geometry/material review views
- `qa/isolated_west_rooms.blend`, isolated diagnostic scene with explicitly named QA-only facade proxies
- `qa_isolated.py` and `qa_verify.py`, repeatable verification harnesses
- `west_window_trace.csv`, the original-plan gap count and approximate normalized window centers

The diagnostic scene is not a replacement for the integrated station model. Its proxy facade is only for testing room apertures and daylight; it must not be merged into the main scene.

## Modeled architectural fabric

### Reading room and historic café

The rooms retain separate extents with three actual rectangular timber-cased openings through the intervening partition. The wall fields and pilasters have explicit metric UVs with vertical grain, while rails, lintels and cornices have horizontal grain. Pale stone skirting, profiled bases and upper cornices, raised panel moldings, interpretive ram-head/volute/acanthus capital relief, and small palmette friezes follow visible material and motif classes.

The ceilings contain 49 original square/octagonal relief coffers, layered perimeter profiles, octagonal sloping/fluted annuli, egg-and-dart-scale beads, floral rosettes, crossing bosses and interpreted pendant corbels. Counts, dimensions, relief depths and fine carvings are photo-proportioned rather than traced measured fabrication profiles.

The floor uses the project's original generated walnut-herringbone material, independently adjusted for a conserved finish. The narrow rose-marble strip beneath the reading/café partition follows the visible condition in photo p62. Warm opal pendants use original geometry. Current furniture and wayfinding/electrical inventories are omitted.

### Restaurant and partial former lunch counter

The restaurant uses two internal pier lines and four internal pier rows proportioned from the 1914 plan, creating alternating long/short and wide/narrow bays rather than a fictitious uniform grid. The interior has square plaster piers, pale stone bases, scored plaster sail vaults, concentric and staggered radial score joints, and scored arch faces/soffits. It does not use Guastavino tile.

The gray floor represents the unfinished substrate visible in p49/p50, without claiming that this is the final 2026 floor finish. A partial shell extends east into the former lunch-counter zone (approximately X24.7–36.16), with no original counter, kitchen equipment, or present tenant interior. The full extent of changes to the historic restaurant/lunch-counter partition remains uncertain. The module retains two plan-proportioned passages and explicitly does not claim the whole photographed vista has been dimensionally recovered.

## Shared geometry interface

Axes are metres: +X west, +Y south, +Z up. Room dimensions are normalized to the existing project envelope and raster plan; approximate values must not be treated as as-built measurements.

- Inner reading/café wall starts at X36.16, outside the hall wall's X36.1092 west face
- Hall-to-reading portal: Y10.1, width 2.4 m, clear height 3.65 m
- Hall-to-café portal: Y22.2, width 2.4 m, clear height 3.65 m
- Café/corridor and corridor/restaurant cuts: X44.1, width 3.0 m, clear height 3.6 m, at Y23.5 and Y28.85
- Both corridor doors were recalibrated from the initial X42.5 approximation to X44.1 so the route passes between the plan-based restaurant piers
- Three reading/café openings: centerX38.87/44.13/49.39, width3.48m, headZ5.12m, partitionY15.4
- East restaurant passages toward lunch-counter shell: centerY33.8/46.1, width 2.4 m, clear height 3.7 m
- Shared north windows remain at X39.719/44.069/48.419, facadeY4.4, width2.4384m, bottomZ1.0m, topZ7.2484m
- `WEST_FACADE_WINDOWS` accepts `(centerY, width, bottom, absoluteTop)` tuples from the core. The module creates only matching interior liners and trims, never new window glazing
- All shell glass, stone facade holes, hall wall cuts, and corridor walls/door leaves remain owned by the main/secondary modules
- `GROUP` is restored, and `WEST_ROOM_CAMERAS` plus `WEST_ROOM_METADATA` are provided

The corrected original-plan west schedule has three reading-room windows, two café windows, one service-corridor window, and six restaurant windows. An earlier five-restaurant-window count was corrected after inspecting a taller annotated crop. The chosen positions are bounds-normalized estimates, approximately ±0.3 m, and do not establish contemporary window alterations.

## Evidence inspected

- 1914 ground-floor plan, `research/visual/floor_plan_1914.jpg`; the main hall's233×104ft dimensions provide the project scale anchor
- [p59, historic café and corridor connection](https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p59)
- [p60, Feb12,2024 reading room/café](https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p60)
- [p62, both rooms, marble threshold and timber detailing](https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p62)
- [p66, reading-room coffer detail](https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p66)
- [Detail38, walnut entablature and pilasters](https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior-detail#p38)
- [Detail39, carved capital motifs and grain direction](https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior-detail#p39)
- [p49, May2024 restaurant east-looking view](https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p49)
- [p50, Aug2023 restaurant northwest-looking view](https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p50)
- [p51, restaurant ceiling and irregular bay rhythm](https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p51)
- [Detail43, scored-plaster vault/arch junctions](https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior-detail#p43)

These photographs are credited to Helmut Ziewers / HistoricDetroit.org. They are copyrighted study references. They are not embedded, projected, loaded as textures, or redistributed with the model. Do not package `study_only/` or the broader research photograph folders in user deliverable archives.

## Geometric verification

Blender 5.2.2, CPU, two render threads. The final isolated geometry run records:

- 322,769 module vertices, 195,616 faces, 113 named batches
- Zero nonfinite vertices, zero zero-area polygons, all UV values finite
- Fifteen clear route/width probes, including all three reading/café apertures, both hall portals, both corridor doors and both restaurant/lunch-counter passages
- Correct sampled outward normals for the floor, coffer underside, sail-vault underside and timber panel
- `GROUP` restoration passes
- Zero research/study photographs loaded as material assets
- 2017 omission test passes with zero new batches/vertices

This is not a complete manifold/watertightness certification: architectural liners, plaster scoring, and some relief leaves intentionally contain thin open surfaces. Named solid architectural boxes use explicit outward normals; curve-like pieces use appropriate smooth shading during finalization. Scene-wide overlaps, source completeness, finished lighting and final delivery quality still require integrated QA.

For a lightweight preview, small carving/scoring batches can be omitted by their descriptive names (relief beads, rosette petals, capital acanthus, palmette frieze, flute ribs, score joints). The delivered detailed module keeps them.
