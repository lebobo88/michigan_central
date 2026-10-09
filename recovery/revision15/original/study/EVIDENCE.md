# West concourse detail study, revision 01

## Baseline finding
NEXT_SOURCE_SUPPORTED_PASSES.md item 2 is stale as an initial-build instruction. Revision14 already contains the west overlight and open central passage, open north arcade, Flemish-bond brick with terracotta strips, and flush blue-gray restored floor bands. The frozen builder's concourse_walls_detail.py and the live component are byte-identical (SHA256 b956052145283eec459289b5c48b61f7ad893603d0c7b14da7df8678e6d711f1). The actual source BLEND hashes match revision14. This study appends only west-wall and floor context directly from those files; it does not rebuild or save either full source.

## Chosen visible refinements
- Replaced the two rectangular-only small-opening lintels with stepped cornice profiles, a low curved crown and centered tapering key
- Added an inset terracotta border/sill over the north blind feature; it remains blind
- Refined the main portal's three opaque panel border fields with rounded corners and regularized small attachment heads
- Added three shallow rails above the established central passage, preserving its opening
- 2026 only: physical diagonal-bar grille inserts in the two lower flanking solid panels. Existing opaque backing remains; no unseen room or doorway is created

The frozen roof, north arcade, public interfaces, floor layout and separate north-pediment study are outside the refinement. Main floor context is cropped at X18 in these isolated files only. Through-views terminate in omitted context; no private interior is reconstructed. Render lighting is neutral diagnostic daylight, not a match to a dated photographic exposure.

## Source observations and limits
Primary restored detail: Historic Detroit, west end of Main Concourse, post_p48. Local study reference: research/interior/concourse_walls_qa/study_only/post_p48.jpg. https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p48
The image visibly supports shallow segmental crowns on both small west features, layered projecting cornices, centered key blocks, a blind framed north feature, rounded main-panel borders and lower inset grilles. Its capture date is not given in the supplied caption. Treat it as a restored-fabric baseline carried forward to 2026, not proof of October2026 fit-out.

Historic west-end corroboration: Historic Detroit pre_p20, explicitly 2010, research/interior/concourse_roof_2017_qa/study_only/pre_p20.jpg. https://historicdetroit.org/galleries/michigan-central-station-pre-restoration-interior#p20
It corroborates the west small-opening forms and retained main opaque-band/frame hierarchy. Their persistence into2017 is qualified. This study does not copy its graffiti, floor debris, clock, broken panes or individual damage locations into2017.

May2017 material/profile corroboration: Historic Detroit pre_p27, research/interior/study_only/pre_p27.jpg. https://historicdetroit.org/galleries/michigan-central-station-pre-restoration-interior#p27
Its caption dates a Main Concourse doorway to May2017. The curved crown and stepped terracotta profile are visible, but this doorway's exact identity is not established. It corroborates a material/profile family; it does not authorize copying a specific door leaf or damage map onto the west side features.

All portal metric dimensions, crown rise/radius, relief depths, grille pitch/bar thickness, border widths and attachment counts are photo-relative authored reconstruction controls, not measured values. The existing5m main opening and7.65m head are inherited qualified controls. The2+8+2 grid and basic surfaces remain unchanged.2017 retains its inherited unglazed/stripped lower framework, and receives no restored lower grilles.

## Materials and rights
All original inherited revision14 materials are reused. No new image maps or image generation are used. The material maps remain authored/procedural approximations, not recovered material or damage maps. No source photograph is loaded, projected, sampled, packed, exported or delivered with these models. Research references remain copyrighted study-only evidence.

## Acceptance limits
This is an isolated source-supported component refinement. It is neither the complete station nor a photoreal/as-built certification. Tiny details remain regularized, photograph-only dimensions uncertain, and the onward west circulation registration unresolved. Full integrated architectural sightline/interface review is still needed before applying this study to a new coordinated station revision.

## Export precision and actual-import checks
The initial GLB export omitted inherited objects whose original group parent was outside the isolated scene. Final isolated GLBs explicitly include all study meshes after detaching those inherited group parents while preserving each object’s world transform. An intermediate normal-recomputation trial produced incorrect cloudy/ribbed glass shading and was rejected. Final context retains the original frozen-source custom normals and modifiers; the frozen full scenes remain unchanged. A strict tangent check identified four-decimal exporter rounding on 64 vertices of inherited west cornice dentils in each era: maximum normal–tangent dot 0.0001176. A bounded repair orthogonalizes only those tangent XYZ components (max vector change 0.0001181), preserves handedness, and proves every other byte unchanged. Final strict and Khronos checks are recorded separately; no validation thresholds were relaxed. New detail geometry did not require this repair.

## Pixel-review cautions
The rounded panel fields, shallow molding relief and lower physical grilles are visibly supported by the primary restored photograph. The inherited overlight renders cloudy against omitted context, unlike the clear photographed through-view. The small south doorway retains a plain recessed solid restored door leaf, without the source's detailed hardware/infill; it reads very dark in the close view. A narrow stepped dark reveal edge in that doorway is inherited context and remains a full-scene review item. These studies do not certify exact restored door state, glazing appearance or photographic material realism. Independent pixel review found no blocking fault in the added details and confirmed that the central passage remains open and the north small feature remains blind.
