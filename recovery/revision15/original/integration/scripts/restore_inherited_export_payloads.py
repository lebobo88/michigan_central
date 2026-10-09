"""Exact baseline restoration for four verified inherited2026 export primitives.

Default is a read-only dry run. --apply is the explicitly authorized preservation
operation; it touches only revision15's2026 full GLB and its owned lineage.
This does not repair any baseline geometric, UV, or tangent defect.
"""
import argparse
import copy
import hashlib
import json
import struct
from pathlib import Path

import numpy as np

OWNED = Path(__file__).resolve().parents[1]
ROOT = OWNED.parents[1]
BASELINE = ROOT / "exports/michigan_central_2026.glb"
TARGET = ROOT / "exports/revision15/michigan_central_2026.glb"
EXPECTED_BASELINE = "3a58625a4f5055ef2bb50e9bfe272f591fa07ee2f59039081a140f6e588bb711"
EXPECTED_BEFORE = "54e2a3d215f1cabd04885399f5e43f4c0cf2a76f8db4b93cb65fbf84a0cd3f9c"
NAMES = ["forecourt balustrade continuous stone plinth", "Study upholstery rounded sofa plinth",
         "Study upholstery rounded sofa plinth.001", "West entablature carved palmette frieze"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


class GLB:
    def __init__(self, path, mutable=False):
        self.path = path
        self.data = bytearray(path.read_bytes()) if mutable else path.read_bytes()
        offset = 12
        while offset < len(self.data):
            size, kind = struct.unpack_from("<II", self.data, offset)
            if kind == 0x4E4F534A:
                self.doc = json.loads(self.data[offset+8:offset+8+size])
            elif kind == 0x004E4942:
                self.start = offset+8
            offset += 8+size

    def array(self, index):
        a = self.doc["accessors"][index]
        assert "sparse" not in a and not a.get("normalized", False)
        v = self.doc["bufferViews"][a["bufferView"]]
        assert v.get("buffer", 0) == 0
        width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]]
        dtype = np.dtype({5126: "<f4", 5125: "<u4", 5123: "<u2", 5121: "u1"}[a["componentType"]])
        return np.ndarray((a["count"], width), dtype=dtype, buffer=self.data,
                          offset=self.start+v.get("byteOffset", 0)+a.get("byteOffset", 0),
                          strides=(v.get("byteStride", width*dtype.itemsize), dtype.itemsize))

    def material(self, index):
        def texture(index):
            t = copy.deepcopy(self.doc["textures"][index])
            assert "source" in t, "No compressed-only texture restoration"
            im = self.doc["images"][t.pop("source")]
            assert "uri" not in im and "bufferView" in im
            view = self.doc["bufferViews"][im["bufferView"]]
            base = self.start+view.get("byteOffset", 0)
            t["embedded_image"] = {"sha256": sha(self.data[base:base+view["byteLength"]]), "mimeType": im.get("mimeType")}
            if "sampler" in t:
                t["sampler"] = self.doc["samplers"][t["sampler"]]
            return t
        def walk(item, key=""):
            if isinstance(item, list):
                return [walk(v) for v in item]
            if not isinstance(item, dict):
                return item
            result = {k: walk(v, k) for k, v in item.items()}
            if key.lower().endswith("texture") and "index" in result:
                result["resolved_texture"] = texture(result.pop("index"))
            return result
        return walk(self.doc["materials"][index])

    def primitive(self, name):
        found = [(i, m) for i, m in enumerate(self.doc["meshes"]) if m.get("name") == name]
        assert len(found) == 1, (name, "Mesh identity must be unambiguous")
        index, mesh = found[0]
        assert len(mesh["primitives"]) == 1, (name, "Exactly one primitive expected")
        return index, mesh["primitives"][0]


def complement_digest(data, intervals):
    h = hashlib.sha256()
    cursor = 0
    for lo, hi in intervals:
        h.update(memoryview(data)[cursor:lo])
        cursor = hi
    h.update(memoryview(data)[cursor:])
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    b, c = GLB(BASELINE), GLB(TARGET, mutable=True)
    assert sha(b.data) == EXPECTED_BASELINE
    assert sha(c.data) == EXPECTED_BEFORE, "Only the reviewed pre-recovery export is authorized"
    integration = json.loads((OWNED / "manifests/integration_2026.json").read_text())
    assert integration["changed_original_objects"] == []
    report = {"operation": "Restore exact baseline UV and tangent XYZ only on four verified unchanged inherited primitives",
              "attempt": "attempt02_corrected_placement",
              "baseline": str(BASELINE.relative_to(ROOT)), "target": str(TARGET.relative_to(ROOT)),
              "baseline_sha256": EXPECTED_BASELINE, "before_sha256": EXPECTED_BEFORE,
              "baseline_defects_not_repaired": True, "new_detail_untouched": True,
              "source_blends_untouched": True, "rows": [], "patches": [], "applied": False}
    for name in NAMES:
        bi, bp = b.primitive(name)
        ci, cp = c.primitive(name)
        assert bp.get("mode", 4) == cp.get("mode", 4) == 4
        assert b.material(bp["material"]) == c.material(cp["material"]), (name, "Material semantic change")
        row = {"mesh": name, "baseline_mesh_index": bi, "candidate_mesh_index": ci, "primitive_index": 0,
               "material": c.doc["materials"][cp["material"]]["name"], "material_semantics_identical": True,
               "preserved_array_hashes": {}, "restored_attributes": {}}
        for label in ("POSITION", "NORMAL", "indices"):
            ba = b.array(bp[label] if label == "indices" else bp["attributes"][label])
            ca = c.array(cp[label] if label == "indices" else cp["attributes"][label])
            assert ba.dtype == ca.dtype and ba.shape == ca.shape
            assert ba.tobytes() == ca.tobytes(), (name, label, "Inherited vertex order/content differs")
            row["preserved_array_hashes"][label] = sha(ca.tobytes())
        for label in ("TEXCOORD_0", "TANGENT"):
            bai, cai = bp["attributes"][label], cp["attributes"][label]
            ba, ca = b.array(bai), c.array(cai)
            bd, cd = b.doc["accessors"][bai], c.doc["accessors"][cai]
            bv, cv = b.doc["bufferViews"][bd["bufferView"]], c.doc["bufferViews"][cd["bufferView"]]
            assert ba.dtype == ca.dtype == np.dtype("<f4") and ba.shape == ca.shape
            assert {k: v for k, v in bd.items() if k not in ("bufferView", "byteOffset")} == {k: v for k, v in cd.items() if k not in ("bufferView", "byteOffset")}
            assert ba.strides == ca.strides, (name, label, "Accessor layout differs")
            consumers = [(mi, pi, at) for mi, mesh in enumerate(c.doc["meshes"]) for pi, prim in enumerate(mesh["primitives"])
                         for at, ai in prim["attributes"].items() if ai == cai]
            assert consumers == [(ci, 0, label)], (name, label, "Accessor is shared outside target")
            width = 2 if label == "TEXCOORD_0" else 3
            if label == "TANGENT":
                assert ba[:, 3].tobytes() == ca[:, 3].tobytes(), "Handedness must remain byte-identical"
            changed = np.flatnonzero(np.any(ba[:, :width] != ca[:, :width], axis=1))
            start = c.start+cv.get("byteOffset", 0)+cd.get("byteOffset", 0)
            for vi in changed:
                offset = start+int(vi)*ca.strides[0]
                before = bytes(c.data[offset:offset+width*4])
                after = ba[vi, :width].tobytes()
                report["patches"].append({"offset": offset, "before_hex": before.hex(), "after_hex": after.hex(),
                                          "mesh": name, "attribute": label, "vertex": int(vi)})
            row["restored_attributes"][label] = {"changed_vertices": len(changed), "baseline_sha256": sha(ba.tobytes()), "before_sha256": sha(ca.tobytes())}
        report["rows"].append(row)
    patches = sorted(report["patches"], key=lambda p: p["offset"])
    intervals = [(p["offset"], p["offset"]+len(bytes.fromhex(p["before_hex"]))) for p in patches]
    assert all(a[1] <= z[0] for a, z in zip(intervals, intervals[1:])), "Patch ranges overlap"
    unaffected_before = complement_digest(c.data, intervals)
    changed_byte_count = 0
    for p in patches:
        before, after = bytes.fromhex(p["before_hex"]), bytes.fromhex(p["after_hex"])
        lo = p["offset"]
        assert bytes(c.data[lo:lo+len(before)]) == before
        changed_byte_count += sum(x != y for x, y in zip(before, after))
        c.data[lo:lo+len(before)] = after
    assert complement_digest(c.data, intervals) == unaffected_before
    for row in report["rows"]:
        _, prim = c.primitive(row["mesh"])
        for label, expected in row["preserved_array_hashes"].items():
            index = prim[label] if label == "indices" else prim["attributes"][label]
            assert sha(c.array(index).tobytes()) == expected
        for label, desc in row["restored_attributes"].items():
            assert sha(c.array(prim["attributes"][label]).tobytes()) == desc["baseline_sha256"]
    report.update(after_sha256=sha(c.data), byte_length_unchanged=len(c.data) == TARGET.stat().st_size,
                  changed_bytes=changed_byte_count, allowed_intervals=len(intervals),
                  all_nonallowed_bytes_sha256=unaffected_before,
                  only_allowed_uv_and_tangent_xyz_bytes_changed=True,
                  positions_normals_indices_materials_images_json_and_tangent_handedness_unchanged=True,
                  script_sha256=sha(Path(__file__).read_bytes()))
    report_path = OWNED / "manifests/inherited_export_payload_recovery_2026.json"
    if args.apply:
        assert sha(TARGET.read_bytes()) == EXPECTED_BEFORE, "Target changed during preparation"
        temporary = TARGET.with_suffix(".glb.recovery_tmp")
        assert not temporary.exists()
        temporary.write_bytes(c.data)
        assert sha(temporary.read_bytes()) == report["after_sha256"]
        temporary.replace(TARGET)
        report["applied"] = True
        lineage_path = OWNED / "manifests/export_lineage_2026.json"
        lineage = json.loads(lineage_path.read_text())
        assert lineage["glb_sha256"] == EXPECTED_BEFORE
        lineage["glb_sha256"] = report["after_sha256"]
        lineage["preservation_recovery"] = {k: v for k, v in report.items() if k not in ("patches", "rows")}
        lineage["preservation_recovery"]["report"] = str(report_path.relative_to(ROOT))
        lineage["full_numerical_strict_status"] = "Pending post-recovery delta audit; inherited defects retained exactly, not repaired"
        lineage_path.write_text(json.dumps(lineage, indent=2)+"\n")
    report_path.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("patches", "rows")}, indent=2))


if __name__ == "__main__":
    main()
