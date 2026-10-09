# Michigan Central Station — current state

A photorealistic recreation project for Michigan Central Station in Corktown,
Detroit, Michigan, with scenes for the 2017 historical condition and the restored
2026 condition. Photorealism is the project goal; the supplied checkpoints remain
an incomplete architectural and material study.

Assembled October 8, 2026 from all six supplied archives. This folder is the
self-contained repository root for the supplied work.

## What is current

**Revision 14 is the latest supplied full, editable scene checkpoint.** Its five
archive parts have been merged, with identical shared files stored once. The
original scenes, exports, textures, scripts, renders, and evidence are unchanged.

**Revision 15 is supplied as a recovery delta, not a rebuilt scene.** It is
preserved intact in `recovery/revision15/`. Its reconstruction has not been run
here. Do not label the Revision 14 BLENDs or GLBs as Revision 15.

## Clone and restore scene files

Three large scene files are stored as 8 MiB Git LFS chunks because direct uploads
repeatedly failed with connection resets. The supplied files remain byte-identical;
the restore command verifies every chunk and the complete file hash. Git LFS is
required to download both ordinary assets and chunks.

```powershell
git clone https://github.com/lebobo88/michigan_central.git
cd michigan_central
python -B tools/restore_scene_files.py
python -B tools/verify_current_state.py
```

The restored files are ignored by Git; their versioned source is
`storage/scene_chunks/` with the mapping in `storage/scene_chunks.json`. Existing
scene files are verified without overwriting them. Before accepting later edits
to these three files, update their chunk payloads and hashes explicitly.

## Open the project

| Location | Contents |
| --- | --- |
| `models/michigan_central_2026.blend` | Packed editable restored-condition scene |
| `models/michigan_central_2017.blend` | Packed editable historical-condition scene |
| `exports/michigan_central_2026.glb` | Full restored-condition interchange model |
| `exports/michigan_central_2017.glb` | Full historical-condition interchange model |
| `exports/*_compact_review.glb` | Smaller review models for both eras |
| `assets/` | Original material maps, component assets, environment, provenance |
| `scripts/` | Supplied Revision 14 modeling, material, export, and QA pipeline |
| `renders/revision14/` | 18 supplied render images and review records |
| `manifests/` | Coverage, evidence, source gaps, validation, and assembly inventory |
| `models/studies/` | Separate unaligned 2017 southern study |
| `recovery/revision15/` | Portable recovery driver, references, tests, historical evidence |
| `docs/packages/` | All five original Revision 14 package manifests |

Packed BLENDs embed used textures; full GLBs embed materials. Open the saved
scenes to review the supplied checkpoint. The unaligned southern study must not
be treated as registered station geometry. Units are meters in a local station
frame, not a georeferenced survey.

See [the preserved Revision 14 README](docs/revision14/README.md),
[recovery notes](READ_FIRST_RECOVERY_WIP.txt), and
[review notes](REVIEW_NOTES.txt) for modeling scope, appearance, and limitations.
Paths in the preserved Revision 14 README refer to this repository root.

## Verification

From this folder, using Python 3.10 or later:

```powershell
python -B tools/verify_current_state.py
python -B recovery/revision15/scripts/verify_package.py recovery/revision15
```

Run the remaining portable recovery checks from their package directory:

```powershell
Push-Location recovery/revision15
python -B scripts/verify_references.py
python -B scripts/test_checkpoint.py
Pop-Location
```

The assembly inventory records every extracted file's SHA-256, size, and archive
origin. Verification also checks each original R14 package manifest. These checks
verify packaging and references; they do not establish new Blender or visual
acceptance. Subsequent intentional edits will change inventory hashes.

## Recover Revision 15

Follow [the portable recovery README](recovery/revision15/README.md). It requires
the specified Blender 5.2.2 runtime and exact R14 input BLENDs; both supplied
BLEND hashes were checked during consolidation. Use fresh output directories
such as `work/recovery-2026/`. The historical scripts in the recovery package's
`original/` directory retain old paths and are provenance, not supported entry
points. The supported entry point is `recovery/revision15/recover.py`.

The generic R14 builder is a supplied modeling pipeline, not a substitute for
the R15 recovery driver. Preserve these saved checkpoints before rebuilding.

## Repository setup

Git LFS attributes cover the binary scene, texture, render, and reference assets.
Git LFS must be installed on machines that clone or publish this project. This
folder contains about 2.33 GB of extracted payloads; account for that asset volume
when choosing repository hosting. The original ZIP archives remain unchanged in
the parent folder and are not needed to open this assembled project.

```powershell
git lfs install --local
git add .
git commit -m "Import Michigan Central current state: R14 scenes and R15 recovery"
```

Public repository: https://github.com/lebobo88/michigan_central

Scratch recovery outputs under `work/` are ignored. New accepted checkpoints should be explicitly promoted
with their evidence and validation records.

## Known scope and rights

Full-station fidelity remains WIP. Fine carving, material realism, site controls,
and unobserved private/service interiors remain qualified or missing. Inherited
export geometry/UV/tangent defects are documented in the R15 recovery package.
Source/reference verification does not certify those defects as repaired.

Existing asset provenance and license records are retained. The supplied package
documents authored geometry/maps and CC0 Poly Haven lighting. Research images and
architect PDFs are excluded from the supplied archives. No blanket new license
is assigned by this consolidation.
