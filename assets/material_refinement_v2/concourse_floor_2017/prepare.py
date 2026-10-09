"""Original bounded 2017 concourse material-class interpretation.

No reference images are opened by this generator. Source images were inspected
privately for material class only. No imagegen call, scan, BRDF measurement, or
exact historic damage map is claimed. No Blender dependency or scene editing.
"""
from pathlib import Path
import hashlib, json, math, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
QA = HERE / "qa"
QA.mkdir(exist_ok=True)
N = 3072
REPEAT_M = 4.0  # Inferred material authoring scale, not a measured floor bay.
MM_PER_TEXEL = 1000.0 * REPEAT_M / N
HEIGHT_FULL_RANGE_M = 0.0004
SEED = 201708030639
rng = np.random.default_rng(SEED)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save01(name, value):
    Image.fromarray(np.rint(np.clip(value, 0, 1) * 255).astype(np.uint8)).save(HERE / name)

def field(sigma_px):
    a = rng.standard_normal((N, N), dtype=np.float32)
    if sigma_px:
        a = gaussian_filter(a, sigma_px, mode="wrap")
    a -= np.mean(a)
    a /= max(float(np.std(a)), 1e-8)
    return np.clip(a, -3, 3)

def polygon_periodic(draw, points, fill):
    """Paint wrapped copies only where a small polygon crosses a tile edge."""
    x0, x1 = min(p[0] for p in points), max(p[0] for p in points)
    y0, y1 = min(p[1] for p in points), max(p[1] for p in points)
    ox = [0] + ([N] if x0 < 0 else []) + ([-N] if x1 >= N else [])
    oy = [0] + ([N] if y0 < 0 else []) + ([-N] if y1 >= N else [])
    for dx in ox:
        for dy in oy:
            draw.polygon([(x + dx, y + dy) for x, y in points], fill=fill)

print("Authoring original fine mineral aggregate; no study pixels read", flush=True)
# Small, irregular angular inclusions. The values are deliberately close to the
# binder after a dusty top-film, rather than clean high-contrast decorative chips.
index = Image.new("L", (N, N), 0)
relief = Image.new("L", (N, N), 128)
di, dh = ImageDraw.Draw(index), ImageDraw.Draw(relief)
PALETTE = np.array([
    [165.0, 163.0, 157.0],  # worn neutral-warm binder / fine mineral film
    [155.5, 155.0, 151.5],  # subdued dark gray inclusion
    [170.5, 169.0, 164.0],  # pale neutral inclusion
    [161.0, 158.5, 150.5],  # warm fine inclusion
    [168.5, 166.5, 160.5],
    [158.0, 158.5, 156.0],
    [173.0, 171.0, 166.0],
], dtype=np.float32)
GRAIN_COUNT = 195000
diameters_mm = np.clip(rng.lognormal(np.log(4.2), 0.40, GRAIN_COUNT), 1.7, 10.5)
for d_mm in diameters_mm:
    cx, cy = rng.uniform(0, N, 2)
    radius = d_mm / MM_PER_TEXEL / 2
    count = int(rng.integers(5, 8))
    angle = float(rng.uniform(0, 2 * np.pi))
    aspect = float(rng.uniform(0.60, 1.0))
    pts = []
    for k in range(count):
        a = angle + (k + rng.uniform(-0.10, 0.10)) * 2 * np.pi / count
        r = radius * float(rng.uniform(0.80, 1.06))
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r * aspect))
    color_id = int(rng.integers(1, len(PALETTE)))
    polygon_periodic(di, pts, color_id)
    # Slightly recessed/protruding inclusions; no raised pebble field.
    polygon_periodic(dh, pts, int(rng.integers(99, 153)))

idx = np.asarray(index)
coverage = float(np.mean(idx != 0))
color = PALETTE[idx]
color = gaussian_filter(color, (.38, .38, 0), mode="wrap")
grain_height = gaussian_filter((np.asarray(relief, np.float32) - 128) / 128, .48, mode="wrap")
grain_mask = gaussian_filter((idx > 0).astype(np.float32), .48, mode="wrap")
del index, relief, di, dh, idx

# Fine mineral binder grain and dust: no broad multi-octave cloud/fBm albedo.
# The 2 cm-scale contribution has only 0.65 code-value standard deviation;
# the 10 cm-scale contribution only 0.20 code value. These are inferred.
micro = field(.40)
fine_dust = field(.020 / (REPEAT_M / N))
quiet_dust = field(.10 / (REPEAT_M / N))
variation = .36 * micro + .65 * fine_dust + .20 * quiet_dust
color += variation[:, :, None]

# Sparse millimetric dark dust particles, not holes/fractures or baked shadows.
speck = Image.new("L", (N, N), 0)
ds = ImageDraw.Draw(speck)
for _ in range(2400):
    cx, cy = rng.uniform(0, N, 2)
    r = float(rng.uniform(.5, 1.5))
    pts = [(cx - r, cy), (cx, cy - r * .65), (cx + r, cy), (cx, cy + r)]
    polygon_periodic(ds, pts, int(rng.integers(75, 210)))
specks = gaussian_filter(np.asarray(speck, np.float32) / 255, .55, mode="wrap")
color -= specks[:, :, None] * np.array([9., 8.5, 7.5], np.float32)
del speck, ds

# A few short broad abrasion swipes. They primarily vary roughness, with tiny
# albedo lift from a disturbed dust film. No jagged or joined crack-like lines.
scuff = Image.new("L", (N, N), 0)
ds = ImageDraw.Draw(scuff)
SCUFF_COUNT = 62
for _ in range(SCUFF_COUNT):
    cx, cy = rng.uniform(0, N, 2)
    angle = float(rng.uniform(0, np.pi))
    half_len = float(rng.uniform(.035, .09)) / (REPEAT_M / N)
    half_width = float(rng.uniform(.002, .006)) / (REPEAT_M / N)
    dx, dy = math.cos(angle), math.sin(angle)
    pts = [(cx + s * half_len * dx + t * half_width * dy,
            cy + s * half_len * dy - t * half_width * dx)
           for s, t in [(-1, -1), (-1, 1), (1, 1), (1, -1)]]
    polygon_periodic(ds, pts, int(rng.integers(90, 230)))
scuffs = gaussian_filter(np.asarray(scuff, np.float32) / 255, 1.3, mode="wrap")
color += scuffs[:, :, None] * 1.6
del scuff, ds

# Conservative tactile relief. Full encoding range is 0.4 mm; actual signal is
# substantially smaller. Height is a sidecar only, not connected displacement.
height_m = (grain_height * .000100 + micro * .0000025
            - specks * .000034 + fine_dust * .0000008)
height_m -= np.mean(height_m)
h16 = np.rint(np.clip(height_m / HEIGHT_FULL_RANGE_M + .5, 0, 1) * 65535).astype(np.uint16)
Image.fromarray(h16).save(HERE / "height.png")
# Derive normals from the quantized 16-bit height actually delivered, so the
# decoder and normal map have a verifiable one-to-one scale relationship.
height_decoded = (h16.astype(np.float32) / 65535 - .5) * HEIGHT_FULL_RANGE_M
step_m = REPEAT_M / N
dx = (np.roll(height_decoded, -1, 1) - np.roll(height_decoded, 1, 1)) / (2 * step_m)
dy_image = (np.roll(height_decoded, -1, 0) - np.roll(height_decoded, 1, 0)) / (2 * step_m)
# Image row grows downward, UV-v grows upward. OpenGL +Y: +dH/d(image-row).
normal = np.stack([-dx, dy_image, np.ones_like(dx)], axis=2)
normal /= np.linalg.norm(normal, axis=2)[:, :, None]
roughness = np.clip(.866 - grain_mask * .035 + fine_dust * .008
                    + quiet_dust * .003 + micro * .005
                    + specks * .025 - scuffs * .025, .77, .94)
save01("basecolor.png", color / 255)
save01("roughness.png", roughness)
save01("normal.png", normal * .5 + .5)
orm = np.zeros((N, N, 3), np.uint8)
orm[:, :, 0] = 255
orm[:, :, 1] = np.rint(roughness * 255).astype(np.uint8)
Image.fromarray(orm).save(HERE / "orm.png")

print("Preparing unlit inspection sheets and encoding/seam checks", flush=True)
font_file = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font = ImageFont.truetype(font_file, 20)
small = ImageFont.truetype(font_file, 16)
title_font = ImageFont.truetype(font_file, 27)
base = Image.open(HERE / "basecolor.png").convert("RGB")
tile = base.resize((768, 768), Image.Resampling.LANCZOS)
sheet = Image.new("RGB", (1536, 1602), (34, 37, 40))
for y in range(2):
    for x in range(2):
        sheet.paste(tile, (x * 768, y * 768 + 66))
d = ImageDraw.Draw(sheet)
d.text((20, 10), "2017 concourse | original unlit 2 x 2 repeat", font=title_font, fill="white")
d.text((20, 42), "8 x 8 m inferred extent; original pixels only; no lights, shadows, or source photographs", font=small, fill=(210, 213, 217))
sheet.save(QA / "unlit_2x2_repeat.png")

board = Image.new("RGB", (1680, 1145), (34, 37, 40))
d = ImageDraw.Draw(board)
d.text((24, 14), "CONCOURSE FLOOR 2017 | restrained worn mineral / old-terrazzo study", font=title_font, fill="white")
d.text((24, 52), "Original procedural material class. Exact 2017 layer mix and damage positions remain unresolved.", font=small, fill=(214, 216, 220))
board.paste(base.resize((960, 960), Image.Resampling.LANCZOS), (24, 100))
d.text((24, 77), "4 x 4 m repeat / pale neutral-warm field", font=small, fill="white")
# Detail crops are 0.625 m square and shown at exactly 1:1 pixel scale.
board.paste(base.crop((720, 1100, 1200, 1580)), (1040, 100))
d.text((1040, 77), "0.625 m detail | 1:1 pixels", font=small, fill="white")
norm_im = Image.open(HERE / "normal.png").convert("RGB")
rough_im = Image.open(HERE / "roughness.png").convert("RGB")
board.paste(norm_im.resize((240, 240), Image.Resampling.LANCZOS), (1040, 650))
board.paste(rough_im.resize((240, 240), Image.Resampling.LANCZOS), (1310, 650))
d.text((1040, 620), "OpenGL +Y normal", font=small, fill="white")
d.text((1310, 620), "Linear roughness", font=small, fill="white")
for y, line in enumerate([
    "4 m repeat is inferred, not a historic floor module",
    "Fine aggregate: 1.7–10.5 mm authored diameters",
    "No large clouds, deep cracks, baked AO or wetness",
    "True displacement disabled; no geometry changed",
    "Full-scene lighting validation is still required",
]):
    d.text((1040, 925 + y * 27), line, font=small, fill=(216, 218, 221))
d.text((24, 1084), "Unlit texture inspection; numerical material properties and chip distribution are artistic inferences.", font=small, fill=(216, 218, 221))
board.save(QA / "unlit_material_inspection.png")

# Optional comparison uses the project's old ORIGINAL procedural asset, never
# copyrighted source-image pixels. It is not used to generate any new PBR map.
old_path = ROOT / "assets/textures/dust_concrete/basecolor.png"
comparison = Image.new("RGB", (1660, 900), (34, 37, 40))
dc = ImageDraw.Draw(comparison)
dc.text((20, 14), "Original project albedo comparison | unlit, same 4 m extent", font=title_font, fill="white")
dc.text((20, 59), "Inherited Weathered concrete", font=font, fill="white")
dc.text((845, 59), "New concourse-only material class", font=font, fill="white")
comparison.paste(Image.open(old_path).convert("RGB").resize((790, 790), Image.Resampling.LANCZOS), (20, 92))
comparison.paste(base.resize((790, 790), Image.Resampling.LANCZOS), (845, 92))
comparison.save(QA / "original_project_before_after_unlit.png")

def png_header(path):
    raw = path.read_bytes()
    w, h, bits, color_type = struct.unpack(">IIBB", raw[16:26])
    return {"size": [w, h], "bit_depth": bits, "png_color_type": color_type}

def seam_metrics(a):
    a = a.astype(np.float32)
    metrics = {}
    for axis, label in [(1, "u"), (0, "v")]:
        differences = np.abs(np.diff(a, axis=axis))
        edge = np.abs(np.take(a, 0, axis=axis) - np.take(a, -1, axis=axis))
        inside = float(np.mean(differences))
        metrics[label] = {
            "wrap_neighbor_mean_abs_delta": float(np.mean(edge)),
            "interior_neighbor_mean_abs_delta": inside,
            "wrap_to_interior_ratio": float(np.mean(edge)) / max(inside, 1e-8),
            "wrap_neighbor_p99_abs_delta": float(np.percentile(edge, 99)),
            "pass_ratio_below_1_5": bool(float(np.mean(edge)) / max(inside, 1e-8) < 1.5),
        }
    return metrics

maps = {name: np.asarray(Image.open(HERE / (name + ".png")))
        for name in ["basecolor", "roughness", "normal", "height", "orm"]}
qa = {
    "status": "Texture-only QA; not a Blender render or final full-scene approval",
    "periodic_construction": "Wrapped polygon copies, wrap-mode filters, and wrapped normal derivatives",
    "edge_note": "Periodic texels are adjacent samples; exact first/last edge equality is neither required nor expected. Seam deltas are compared with ordinary neighbor deltas.",
    "encoding": {name: png_header(HERE / (name + ".png")) for name in maps},
    "seams": {name: seam_metrics(value) for name, value in maps.items()},
    "orm": {"occlusion_all_255": bool(np.all(maps["orm"][:, :, 0] == 255)),
            "roughness_matches_exactly": bool(np.array_equal(maps["orm"][:, :, 1], maps["roughness"])),
            "metallic_all_zero": bool(np.all(maps["orm"][:, :, 2] == 0))},
    "height_actual_mm": {"min": float(height_decoded.min() * 1000),
                         "max": float(height_decoded.max() * 1000),
                         "peak_to_peak": float(np.ptp(height_decoded) * 1000),
                         "full_encoding_range": HEIGHT_FULL_RANGE_M * 1000},
    "normal": {"orientation": "OpenGL +Y; x=-dH/dU; y=+dH/dImageRow (image rows run opposite UV v)",
               "strength": 1.0,
               "unquantized_slope_degrees_max": float(np.degrees(np.arccos(np.clip(normal[:, :, 2].min(), 0, 1)))),
               "unquantized_slope_degrees_p99": float(np.percentile(np.degrees(np.arctan(np.sqrt(dx * dx + dy_image * dy_image))), 99)),
               "blue_all_255": bool(np.all(maps["normal"][:, :, 2] == 255)),
               "derived_from_delivered_height": True},
    "albedo_srgb_code": {"mean_rgb": maps["basecolor"].mean((0, 1)).tolist(),
                         "std_rgb": maps["basecolor"].std((0, 1)).tolist(),
                         "min_rgb": maps["basecolor"].min((0, 1)).tolist(),
                         "max_rgb": maps["basecolor"].max((0, 1)).tolist()},
    "roughness_actual": {"min": float(maps["roughness"].min() / 255),
                         "max": float(maps["roughness"].max() / 255),
                         "mean": float(maps["roughness"].mean() / 255)},
    "aggregate_coverage_fraction": coverage,
    "aggregate_count": GRAIN_COUNT,
    "scuff_count": SCUFF_COUNT,
}
luma = maps["basecolor"].astype(np.float32).mean(axis=2)
macro = gaussian_filter(luma, .10 / step_m, mode="wrap")
qa["macro_albedo_control"] = {
    "low_pass_sigma_m": .10,
    "low_pass_std_srgb_code": float(np.std(macro)),
    "low_pass_peak_to_peak_srgb_code": float(np.ptp(macro)),
    "explanation": "Large-area albedo contrast is intentionally sub-code-value; microaggregate and roughness carry surface character instead of white cloud masks.",
}
qa["all_encoding_checks_pass"] = bool(
    all(v["size"] == [N, N] for v in qa["encoding"].values())
    and qa["encoding"]["height"]["bit_depth"] == 16
    and all(qa["encoding"][name]["bit_depth"] == 8 for name in ["basecolor", "roughness", "normal", "orm"])
    and all(qa["orm"].values())
    and all(axis["pass_ratio_below_1_5"] for item in qa["seams"].values() for axis in item.values())
)
(QA / "encoding_and_seam_checks.json").write_text(json.dumps(qa, indent=2))
assert qa["all_encoding_checks_pass"], "Inspect seam or encoding failure"

source_rows = [
    {"id": "architect_visual_tour_p39", "date_strength": "2024 reopening architect publication, retrospective floor history",
     "url": "https://cdn.prod.website-files.com/6240e0408c8f1a116a84978a/665b5ce09fd63562d30a4708_Michigan%20Central%20Station_Visual%20Tour.pdf",
     "local": "research/quinn_evans_visual_tour_2024.txt",
     "observation": "Original concourse terrazzo deteriorated beyond repair and was replaced, with radiant heating in the replacement.",
     "limit": "Does not establish the surviving terrazzo/substrate/dust proportions or damage locations in 2017."},
    {"id": "historic_detroit_pre_p20", "date_strength": "Caption says 2010; context only, not a 2017 condition map",
     "url": "https://historicdetroit.org/galleries/michigan-central-station-pre-restoration-interior#p20",
     "local": "research/interior/concourse_roof_2017_qa/study_only/pre_p20.jpg",
     "observation": "Pale warm mineral-looking floor with deposits, fragments, wet areas and faint divisions.",
     "limit": "2010 objects, wetness, color and exact damage are not transferred into a 2017 material."},
    {"id": "historic_detroit_pre_p4", "date_strength": "Caption: July 5, 2010; context only",
     "url": "https://historicdetroit.org/galleries/michigan-central-station-pre-restoration-interior#p4",
     "local": "research/interior/concourse_roof_2017_qa/study_only/pre_p4.jpg",
     "observation": "Worn, marked floor with faint divisions and localized deposits; material is not a uniformly clean cloud-patterned surface.",
     "limit": "Does not determine May 2017 joint, graffiti, material-layer or damage inventory."},
    {"id": "dandelion_2017_published_project", "date_strength": "Project published August 3, 2017; individual aerial capture dates unspecified",
     "url": "https://spark.adobe.com/page/OMI5cVvEGgqxk/",
     "publication_source": "https://sketchfab.com/3d-models/michigan-central-station-17921c30b4134bf598b0cac817f00f1d",
     "local": ["research/south_structure/presentation_ref_10.jpg", "research/south_structure/presentation_ref_13.jpg"],
     "observation": "Broad pale lower floor under dense open truss shadows; warm light appears amber in the color aerial.",
     "limit": "Shadows and resolution prevent a calibrated albedo, layer mix or detailed condition reconstruction. Amber is not baked into albedo."},
]
provenance = {
    "material": "Concourse 2017 worn mineral floor",
    "asset_id": "concourse_floor_2017",
    "origin": "Original deterministic procedural authoring; no imagegen used; no third-party pixels sampled, copied, projected, or redistributed",
    "generator": "prepare.py", "generator_sha256": sha(Path(__file__)), "seed": SEED,
    "integration_target": "2017 main concourse floor only; separate material, never a global Weathered concrete replacement",
    "pixels": [N, N], "physical_repeat_m": [REPEAT_M, REPEAT_M], "periodic": True,
    "physical_scale_status": "Inferred 4 m repeat and particle/relief/roughness values; not measured site material or historic floor module",
    "mm_per_texel": MM_PER_TEXEL,
    "basecolor_encoding": "8-bit RGB sRGB; authored albedo without baked lighting/AO",
    "roughness_encoding": "8-bit grayscale linear data",
    "normal_encoding": "8-bit RGB, OpenGL +Y tangent space, linear data",
    "height_encoding": {"bit_depth": 16, "type": "grayscale unsigned PNG", "full_range_m": HEIGHT_FULL_RANGE_M,
                        "decode_m": "(uint16/65535 - 0.5) * 0.0004", "actual_peak_to_peak_m": float(np.ptp(height_decoded)),
                        "inferred": True, "true_displacement_enabled": False},
    "orm_encoding": "8-bit RGB linear; R=255 neutral occlusion, G=roughness, B=0 dielectric metallic",
    "gltf": {"baseColorTexture": "basecolor.png", "normalTexture": "normal.png", "normalTexture_scale": 1.0,
             "metallicRoughnessTexture": "orm.png", "metallicFactor": 0.0, "roughnessFactor": 1.0,
             "occlusionTexture": "orm.png (optional, entirely neutral)", "height": "Sidecar only, not core glTF displacement",
             "sampler": "REPEAT U/V; mipmaps and anisotropic filtering recommended"},
    "sources": source_rows,
    "limitations": [
        "Original source-informed material-class interpretation, not a survey, calibrated reflectance, photogrammetry or exact 2017 damage map.",
        "A uniformly bare-concrete concourse is not established by the evidence. The original material was terrazzo; its exact 2017 surviving mix with exposed substrate, deposits and dust remains unresolved.",
        "Fine aggregate population, color, scuff positions, roughness and microscopic relief are inferred appearance controls.",
        "No cracks, historic divider layout, decorative restored bands, graffiti, rubble or wetness are fabricated in this repeated material.",
        "The 4 m period is a practical authored repeat, not a claimed terrazzo panel size or historic module.",
        "Source photographs remain private study-only. QA images contain only the new original material and, in one comparison, the project's original procedural dust_concrete asset.",
        "New albedo has a different mean from the inherited dark concrete. It is not a calibrated exposure compensation; assess it in the actual fixed-camera scene after topology/contact repair.",
        "No Blender render, scene mutation or live build-script change was performed while preparing these assets.",
    ],
    "output_sha256": {name + ".png": sha(HERE / (name + ".png")) for name in maps},
    "comparison_only_original_asset": {"path": str(old_path.relative_to(ROOT)), "sha256": sha(old_path)},
    "qa": "qa/encoding_and_seam_checks.json",
}
(HERE / "provenance.json").write_text(json.dumps(provenance, indent=2))
(HERE / "physical_scale.json").write_text(json.dumps({
    "authoring_extent_m": [REPEAT_M, REPEAT_M], "scale_status": "inferred",
    "texel_size_mm": MM_PER_TEXEL, "grain_diameter_authored_mm": [1.7, 10.5],
    "grain_diameter_authored_median_mm": float(np.median(diameters_mm)),
    "scuff_length_authored_m": [.07, .18], "scuff_width_authored_m": [.004, .012],
    "normal_height_decode": provenance["height_encoding"],
    "normal_strength_recommended": 1.0, "true_displacement": "disabled",
    "floor_uv": "u=world.x/4; v=world.y/4 on horizontal faces; periodic offsets allowed",
    "existing_uv_note": "The current cw_face supplies metric coordinates, and build_station.py divides by material.texture_repeat_m. Set that property to 4.0; do not divide twice.",
}, indent=2))
print(json.dumps({"status": "done", "output": str(HERE), "aggregate_coverage": coverage,
                  "albedo_mean": qa["albedo_srgb_code"]["mean_rgb"],
                  "macro_std": qa["macro_albedo_control"]["low_pass_std_srgb_code"],
                  "height_peak_to_peak_mm": qa["height_actual_mm"]["peak_to_peak"],
                  "roughness": qa["roughness_actual"],
                  "all_encoding_checks_pass": qa["all_encoding_checks_pass"]}, indent=2), flush=True)
