"""Optional parent integration helper. DEFINITIONS ONLY; no scene is changed on import.

Not executed/tested in Blender during asset preparation. The parent must review
and integrate in its approved render window, then inspect the actual camera.
Call only for era 2017, after concourse geometry batches exist and before mesh
assembly. This changes exactly the main concourse floor batch's material key.
"""
from pathlib import Path

MATERIAL_NAME = "Concourse 2017 worn mineral floor"
TARGET_OBJECT = "concourse qualified2017 unpatterned floor"
TARGET_GROUP = "05 CONCOURSE | source-informed masonry and floor"

def make_concourse_floor_material(root, materials):
    import bpy
    if MATERIAL_NAME in materials:
        raise RuntimeError("Refuse to overwrite existing named candidate material")
    asset = Path(root) / "assets/material_refinement_v2/concourse_floor_2017"
    required = [asset / (name + ".png") for name in ("basecolor", "roughness", "normal", "height")]
    if not all(path.is_file() for path in required):
        raise FileNotFoundError("Incomplete concourse candidate PBR maps")
    source = materials["Weathered concrete"]
    material = source.copy()
    material.name = MATERIAL_NAME
    for channel in ("basecolor", "roughness", "normal", "height"):
        node = material.node_tree.nodes.get(channel)
        if node is None or node.type != "TEX_IMAGE":
            raise RuntimeError("Unexpected inherited material layout: " + channel)
        node.image = bpy.data.images.load(str(asset / (channel + ".png")), check_existing=True)
        node.image.colorspace_settings.name = "sRGB" if channel == "basecolor" else "Non-Color"
        node.extension = "REPEAT"
        node.interpolation = "Linear"
        node.label = "Original procedural concourse-only " + channel + "; physical values inferred"
    for node in material.node_tree.nodes:
        if node.type == "NORMAL_MAP":
            node.space = "TANGENT"
            node.inputs["Strength"].default_value = 1.0
        if node.type == "OUTPUT_MATERIAL" and node.inputs["Displacement"].is_linked:
            raise RuntimeError("Unexpected displacement connection; candidate requires displacement disabled")
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Metallic"].default_value = 0.0
    material["texture_repeat_m"] = 4.0
    material["texture_provenance"] = "Original procedural fine mineral/old-terrazzo interpretation; no source-image pixels"
    material["physical_limit"] = "Inferred 4 m repeat and conservative micrometre relief; no displacement; exact 2017 layer mix unresolved"
    material["placement_limit"] = "2017 main concourse floor only; leave every other Weathered concrete assignment unchanged"
    materials[MATERIAL_NAME] = material
    return material

def retarget_concourse_floor_batch(batches):
    old_key = (TARGET_GROUP, "Weathered concrete", TARGET_OBJECT)
    new_key = (TARGET_GROUP, MATERIAL_NAME, TARGET_OBJECT)
    if old_key not in batches:
        raise KeyError("Exact 2017 main-concourse floor batch not found; do not broaden the material scope")
    if new_key in batches:
        raise RuntimeError("Candidate batch is already present")
    batches[new_key] = batches.pop(old_key)
    return {"old_key": old_key, "new_key": new_key,
            "geometry_or_custom_uv_changed": False,
            "target_count": 1, "material_repeat_m": 4.0}

if AGED:
 make_concourse_floor_material(ROOT,M)
 scene['concourse_floor_material_refinement']=json.dumps(retarget_concourse_floor_batch(B))
