# Michigan Central: revision 15 recovery delta

**Packaged source/reference checkpoint; actual Blender reconstruction NOT YET VALIDATED.**

This small portable delta preserves the exact new west-concourse component sources and accepted references needed to reconstruct revision 15 on the **already saved revision 14 BLENDs**. It contains no full BLEND/GLB, texture library, source photograph, revision 16 work, old archive, or superseded integration attempt.

## What is included

- The pinned original study generator (SHA-256 `0ad7b90d58f96bdb6a488af62492604c0a6420a6de177141f5d8df278c6cd2a8`) and its evidence/qualification documents
- A portable replay that executes only its original `mesh`, `extrude`, `box`, `rounded`, `ring`, `bead`, and `add_detail` definitions, reusing the two exact-era materials already packed into R14
- All 48 (2017) and 166 (2026) accepted new meshes as compact reference POSITION/NORMAL/UV/TANGENT/index arrays, names, material fingerprints, node transforms, all-node local/world matrices and hierarchy, and per-object evaluated Blender matrices/bounds
- The four inherited 2026 UV/TANGENT baseline arrays, 1,578,360 raw bytes total, with POSITION/NORMAL/index/accessor/material guards; recovery needs no R14 GLB
- Accepted original integration manifests and source/check helpers, including both tiny candidate dependencies
- Two previously accepted actual-import portal screenshots. These document the sealed R15 checkpoint, not a newly reconstructed result
- Standard-library verification/tests and a reproducible ZIP builder

`original/` preserves historical scripts and reports as provenance. Their old absolute paths and original scene/archive references are intentionally unchanged. **Do not execute original entry-point scripts directly.** The supported portable entry point is `recover.py`; its dependency closure is documented in `DEPENDENCIES.json`.

## Required external inputs

1. Python 3.10 or later for package verification and orchestration. These steps need only the standard library
2. Blender **5.2.2 LTS**, with its bundled Python, NumPy, bmesh, mathutils and glTF importer/exporter. The sealed checkpoint used build `d13f752e3b9c` (2026-09-15). Other Blender versions fail the replay gate; another platform/build is not assumed to reproduce exact export arrays
3. The original, packed R14 BLEND for each requested era, matching these hashes exactly:

| Era | Original path/name | SHA-256 |
| --- | --- | --- |
| 2017 | `models/michigan_central_2017.blend` | `0dcdf687e35dd0026dfb8d7667fcadf079f708632707268fd9343539746cca2e` |
| 2026 | `models/michigan_central_2026.blend` | `453e90686ce0dcb72e3a2d20b644eff6dec3aa8a526354e4338b73d768054ba1` |

No isolated-study BLEND (73 MB / 31 MB), original GLB, external textures, or source photographs are required. Unmodified material images must remain packed in the supplied R14 BLENDs. Use fresh output directories outside the extracted package. Plan for several GB of free disk and sufficient RAM for full scenes; 2026 actual import/render previously approached 5 GB RSS. Run one era at a time. Each driver launches only one Blender child at a time, with two threads, and never renders.

## Verify without Blender

Run from the extracted package directory:

```sh
python -B scripts/verify_package.py .
python -B scripts/verify_references.py
python -B scripts/test_checkpoint.py
```

To verify an archive's entry names, no-symlink policy, declared sizes, SHA-256 and CRC:

```sh
python -B scripts/verify_package.py /path/to/Michigan-Central-R15-Recovery-Delta.zip
```

No command above opens or reconstructs a Blender scene. The tests include negative ZIP cases, source-definition dependency closure, a pure-Python geometry-emission test, and synthetic guarded preservation/rejection/no-op cases. They do not emulate Blender triangulation, UV storage, saving, export or import.

## Recover the editable source, then optionally the canonical full GLB

Replace example paths with your local paths. Outputs must not exist already. Never point an output at an R14/R15 source directory.

```sh
python -B recover.py --blender /path/to/blender --era 2017 --r14-blend /path/to/models/michigan_central_2017.blend --output /path/to/recovery-2017
python -B recover.py --blender /path/to/blender --era 2026 --r14-blend /path/to/models/michigan_central_2026.blend --output /path/to/recovery-2026
```

These source-only commands verify the package and R14 source hash, recreate original metric UVs before the exact original recentering operation, preserve world matrices when parenting, run per-detail evaluated matrix/bounds and closed-solid checks, save/reopen, compare retained-object signatures and repeat established source checks. They create a new `_recovered.blend`, logs, and reports. Source-only mode does not compare newly exported geometry/UV/index bytes with the compact GLB references; that stricter payload gate requires `--export`. A zero Blender exit alone is insufficient: the driver verifies the expected saved BLEND hash and passing, versioned source/placement reports. The exact inherited profiled-lintel object is the only removed object. Expected scene mesh totals are 742/2760.

For source plus full export and actual empty-scene import verification, use a **different fresh output directory** and add `--export`:

```sh
python -B recover.py --blender /path/to/blender --era 2017 --r14-blend /path/to/models/michigan_central_2017.blend --output /path/to/recovery-2017-full --export
python -B recover.py --blender /path/to/blender --era 2026 --r14-blend /path/to/models/michigan_central_2026.blend --output /path/to/recovery-2026-full --export
```

The export path uses the original export options and pinned zero-tangent helper, restores only the four guarded 2026 inherited UV/tangent payloads, compares all node names, hierarchy, local/world transforms, every primitive's POSITION/NORMAL/UV/TANGENT/index bytes and every material/sampler/embedded-image fingerprint against accepted references, and actually imports the GLB into an empty scene. The import completion report must identify the exact final GLB hash. Import checks cover exact mesh names (741/2759), group/marker counts, full bounds, era split, all 48/166 detail matrices/bounds, 18/25 public routes and nine west-passage probes. Only the render-only context ground is excluded from export, as in accepted R15. No automatic renders or Khronos executable download are included.

The 2026 raw pre-preservation GLB is retained alongside its new recovered copy for inspection. The preserved arrays are not an inherited-defect repair. No other candidate bytes may change during the preservation step; tangent handedness must already match. The input file is untouched. A guard failure aborts the operation, rather than matching nearby vertices or weakening checks.

For a separately created compatible candidate, standalone recovery and verification are also available:

```sh
python -B scripts/preserve_2026.py --input /path/to/candidate.glb --output /path/to/new-preserved.glb --report /path/to/preservation-report.json
python -B scripts/verify_glb.py --era 2026 --glb /path/to/new-preserved.glb --report /path/to/export-check.json
```

## Acceptance and stopping conditions

A nonzero exit means partial output is unaccepted. Keep the logs, diagnose the specific mismatch, and retry into another new directory. Do not overwrite an accepted scene or relax source hashes, geometry fingerprints, guard arrays, placement tolerances or source/import tests just to pass.

The original project encountered a placement failure from reading unevaluated library transforms. This replay does not load study libraries; it updates the view layer before reading world transforms and after parenting, and checks **every** detail's evaluated matrix and bounds before saving, after reopening and after actual import. Any future library-loading adaptation must assign `names.copy()` rather than a retained list to `bpy.data.libraries.load`, because Blender mutates the supplied list.

This package was prepared and checked without launching Blender. Original sealed R15 reports and screenshots remain historical acceptance evidence. `VALIDATION.json` explicitly distinguishes current pure-Python checks from the unrun reconstruction. New recovery reports only mark stages actually executed. A successful future source/export/import run still needs separate pixel review before claiming matched visual acceptance.

Regenerated BLEND hashes are **not** promised to be binary-identical. Metadata, save ordering or platform differences can alter a file hash. Exact R14 input identity, retained source-object signatures, new reference payloads, evaluated placements, material/image fingerprints and actual import checks are the recovery contract.

## Known limits retained from revision 15

Full-station fidelity remains WIP. North-pediment revision08 is not integrated. No unobserved west continuation or rooms are invented, no new image maps are added, and 2026 lower grilles are not copied into 2017. Dimensions, profiles, wear and 2017 persistence remain qualified by `original/study/EVIDENCE.md`.

The inherited exports remain globally strict-unclean: 2017 has 10,688 nonorthogonal tangent vertices, 5,876 collapsed-UV triangles and 1,370 degenerate triangles; 2026 has 28,486, 10,573 and 6,130 respectively. Categories can overlap; counts are unique primitive data, not multiplied by instances. The accepted new details pass strict numerical checks. Zero Khronos errors in the old reports do not certify inherited numerical defects as repaired. See the included inherited-defect report for the original scope and qualifications.

## Rebuild this small archive only

```sh
python -B build_archive.py --output /path/to/new-R15-Recovery-Delta.zip
```

This rechecks and archives the extracted package only. It does not rebuild or repack any station scene. ZIP timestamps and order are fixed for reproducibility. `PACKAGE_MANIFEST.json` lists every included payload's size and SHA-256; the ZIP's own SHA-256 is reported alongside it to avoid a self-referential hash.
