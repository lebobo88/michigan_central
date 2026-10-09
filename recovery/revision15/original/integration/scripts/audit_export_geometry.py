"""Read-only full-GLB precision/geometry audit and bounded revision comparison.

Never opens Blender or changes input artifacts. Writes only the explicit report.
Thresholds reproduce qa_concourse_roof_detail.validate_glb without weakening it.
Counts are unique primitive data, not multiplied by instancing; node references
and instance counts are included so the distinction remains visible.
"""
import argparse
import collections
import hashlib
import json
import math
import mmap
import struct
from pathlib import Path

import numpy as np

THRESHOLDS = {"normal_length_deviation": 1e-4, "tangent_length_deviation": 1e-4,
              "normal_tangent_abs_dot": 1e-4, "handedness_deviation": 1e-4,
              "geometry_double_area": 1e-10, "uv_double_area": 1e-12}


def digest(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def finite_float(value):
    value = float(value)
    return value if math.isfinite(value) else None


def bounds(arr):
    return [arr.min(axis=0).tolist(), arr.max(axis=0).tolist()] if len(arr) else None


def audit(path, era):
    path = Path(path)
    raw = path.read_bytes()
    assert raw[:4] == b"glTF" and struct.unpack_from("<I", raw, 4)[0] == 2
    doc = None
    binary = None
    offset = 12
    while offset < len(raw):
        size, kind = struct.unpack_from("<II", raw, offset)
        if kind == 0x4E4F534A:
            doc = json.loads(raw[offset + 8:offset + 8 + size])
        elif kind == 0x004E4942:
            binary = memoryview(raw)[offset + 8:offset + 8 + size]
        offset += 8 + size
    assert doc is not None and binary is not None
    types = {5126: "<f4", 5125: "<u4", 5123: "<u2", 5122: "<i2", 5121: "u1", 5120: "i1"}
    dims = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}

    def acc(index):
        item = doc["accessors"][index]
        assert "sparse" not in item, "Sparse data needs an explicit reader"
        assert not item.get("normalized", False), "Full-export audit expects unquantized attributes"
        view = doc["bufferViews"][item["bufferView"]]
        assert view.get("buffer", 0) == 0
        dtype = np.dtype(types[item["componentType"]])
        width = dims[item["type"]]
        return np.ndarray((item["count"], width), dtype=dtype, buffer=binary,
                          offset=view.get("byteOffset", 0) + item.get("byteOffset", 0),
                          strides=(view.get("byteStride", dtype.itemsize * width), dtype.itemsize))

    references = collections.defaultdict(list)
    for node in doc.get("nodes", []):
        if "mesh" in node:
            references[node["mesh"]].append(node.get("name", "unnamed node"))
    primitives = []
    occurrence = collections.Counter()
    issue_rows = collections.Counter()
    affected_counts = collections.Counter()
    for mesh_index, mesh in enumerate(doc.get("meshes", [])):
        name = mesh.get("name", f"unnamed mesh {mesh_index}")
        ordinal = occurrence[name]
        occurrence[name] += 1
        for primitive_index, prim in enumerate(mesh["primitives"]):
            attrs = prim["attributes"]
            material = doc.get("materials", [])[prim["material"]] if "material" in prim else {}
            row = {"mesh": name, "mesh_occurrence": ordinal, "mesh_index": mesh_index,
                   "primitive_index": primitive_index, "node_names": references[mesh_index],
                   "instance_count": len(references[mesh_index]),
                   "material": material.get("name"), "material_has_normal_texture": "normalTexture" in material,
                   "issues": {}, "metrics": {}}
            row["identity"] = json.dumps([name, ordinal, primitive_index, row["material"]], separators=(",", ":"))
            required = ("POSITION", "NORMAL", "TEXCOORD_0", "TANGENT")
            missing = [k for k in required if k not in attrs]
            if missing:
                row["issues"]["missing export attribute"] = {"count": len(missing), "attributes": missing}
                primitives.append(row)
                continue
            assert prim.get("mode", 4) == 4, "Only triangle primitives are in this contract"
            arrays = {k: acc(attrs[k]) for k in required}
            index_array = acc(prim["indices"]).reshape(-1) if "indices" in prim else np.arange(len(arrays["POSITION"]), dtype=np.uint32)
            idx = index_array.reshape(-1, 3)
            p, n, u, t = [arrays[k].astype(np.float64) for k in required]
            row["vertices"] = len(p)
            row["triangles"] = len(idx)
            row["attribute_sha256"] = {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in arrays.items()}
            row["indices_sha256"] = hashlib.sha256(index_array.tobytes()).hexdigest()
            row["referenced_vertices"] = int(len(np.unique(idx)))

            def vertex_issue(category, bad, metric=None):
                ids = np.flatnonzero(bad)
                if len(ids):
                    detail = {"count": len(ids), "kind": "vertices", "sample_indices": ids[:16].tolist(),
                              "unreferenced_affected_vertices": int(np.count_nonzero(~np.isin(ids, idx)))}
                    if metric is not None:
                        detail["max_deviation"] = finite_float(np.max(metric[ids]))
                    row["issues"][category] = detail

            nonfinite = ~np.isfinite(p).all(axis=1) | ~np.isfinite(n).all(axis=1) | ~np.isfinite(u).all(axis=1) | ~np.isfinite(t).all(axis=1)
            vertex_issue("nonfinite", nonfinite)
            normal_deviation = np.abs(np.linalg.norm(n, axis=1) - 1)
            tangent_deviation = np.abs(np.linalg.norm(t[:, :3], axis=1) - 1)
            tangent_dot = np.abs((n * t[:, :3]).sum(axis=1))
            handedness_deviation = np.abs(np.abs(t[:, 3]) - 1)
            for category, metric, threshold in [
                ("normal length", normal_deviation, THRESHOLDS["normal_length_deviation"]),
                ("tangent length", tangent_deviation, THRESHOLDS["tangent_length_deviation"]),
                ("nonorthogonal tangent", tangent_dot, THRESHOLDS["normal_tangent_abs_dot"]),
                ("invalid tangent handedness", handedness_deviation, THRESHOLDS["handedness_deviation"]),
            ]:
                vertex_issue(category, metric > threshold, metric)
            row["metrics"].update(max_normal_length_deviation=finite_float(normal_deviation.max()),
                                   max_tangent_length_deviation=finite_float(tangent_deviation.max()),
                                   max_abs_normal_tangent_dot=finite_float(tangent_dot.max()),
                                   max_handedness_deviation=finite_float(handedness_deviation.max()))
            a, b, c = p[idx[:, 0]], p[idx[:, 1]], p[idx[:, 2]]
            geometry_area2 = np.linalg.norm(np.cross(b-a, c-a), axis=1)
            edge_lengths = np.stack([np.linalg.norm(b-a, axis=1), np.linalg.norm(c-a, axis=1), np.linalg.norm(c-b, axis=1)], axis=1)
            a, b, c = u[idx[:, 0]], u[idx[:, 1]], u[idx[:, 2]]
            uv_area2 = np.abs((b[:, 0]-a[:, 0])*(c[:, 1]-a[:, 1]) - (b[:, 1]-a[:, 1])*(c[:, 0]-a[:, 0]))
            geometry_bad = geometry_area2 < THRESHOLDS["geometry_double_area"]
            uv_bad = uv_area2 < THRESHOLDS["uv_double_area"]
            if "nonorthogonal tangent" in row["issues"]:
                detail = row["issues"]["nonorthogonal tangent"]
                substantial = np.flatnonzero(tangent_dot > .0002)
                surface_vertices = np.unique(idx[~geometry_bad])
                valid_uv_surface_vertices = np.unique(idx[~geometry_bad & ~uv_bad])
                detail.update(near_threshold_roundoff_range_vertices=int(np.count_nonzero((tangent_dot > 1e-4) & (tangent_dot <= .0002))),
                              substantial_over_0_0002_vertices=len(substantial),
                              substantial_on_nondegenerate_triangles=int(np.count_nonzero(np.isin(substantial, surface_vertices))),
                              substantial_on_nondegenerate_valid_uv_triangles=int(np.count_nonzero(np.isin(substantial, valid_uv_surface_vertices))),
                              substantial_only_on_degenerate_triangles=int(np.count_nonzero(~np.isin(substantial, surface_vertices))))
            for category, bad in [("degenerate triangle", geometry_bad), ("collapsed UV triangle", uv_bad)]:
                ids = np.flatnonzero(bad)
                if len(ids):
                    row["issues"][category] = {
                        "count": len(ids), "kind": "triangles", "sample_indices": ids[:16].tolist(),
                        "affected_unique_vertices": int(len(np.unique(idx[ids]))),
                        "geometry_double_area_min": finite_float(geometry_area2[ids].min()),
                        "geometry_double_area_max": finite_float(geometry_area2[ids].max()),
                        "geometry_total_area_m2": finite_float(geometry_area2[ids].sum()/2),
                        "uv_double_area_min": finite_float(uv_area2[ids].min()),
                        "uv_double_area_max": finite_float(uv_area2[ids].max()),
                        "exact_zero_geometry_triangles": int(np.count_nonzero(geometry_area2[ids] == 0)),
                        "exact_zero_uv_triangles": int(np.count_nonzero(uv_area2[ids] == 0)),
                        "max_longest_edge_m": finite_float(edge_lengths[ids].max()),
                        "affected_local_position_bounds_m": bounds(p[np.unique(idx[ids])]),
                        "geometry_degenerate_and_uv_collapsed": int(np.count_nonzero(geometry_bad[ids] & uv_bad[ids])),
                        "uv_collapsed_but_geometry_nondegenerate": int(np.count_nonzero(~geometry_bad[ids] & uv_bad[ids])),
                    }
            row["metrics"].update(min_geometry_double_area=finite_float(geometry_area2.min()),
                                   min_uv_double_area=finite_float(uv_area2.min()),
                                   exact_zero_geometry_triangles=int(np.count_nonzero(geometry_area2 == 0)),
                                   exact_zero_uv_triangles=int(np.count_nonzero(uv_area2 == 0)))
            primitives.append(row)
    for row in primitives:
        for category, detail in row["issues"].items():
            issue_rows[category] += 1
            affected_counts[category] += detail["count"]
    affected = [row for row in primitives if row["issues"]]
    return {"file": str(path.resolve()), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
            "era": era, "thresholds": THRESHOLDS, "scope": "Read-only strict export diagnostics; inherited defects are not silently accepted as zero-error geometry",
            "count_basis": "Per unique exported mesh primitive; instance_count and node_names show multiplied appearances",
            "summary": {"mesh_count": len(doc.get("meshes", [])), "mesh_nodes": sum("mesh" in n for n in doc.get("nodes", [])),
                        "primitives": len(primitives), "vertices": sum(r.get("vertices", 0) for r in primitives),
                        "triangles": sum(r.get("triangles", 0) for r in primitives),
                        "affected_mesh_names": len({r["mesh"] for r in affected}), "affected_primitives": len(affected),
                        "issue_rows": dict(issue_rows), "affected_elements": dict(affected_counts),
                        "maximum_abs_normal_tangent_dot": max(r["metrics"].get("max_abs_normal_tangent_dot", 0) or 0 for r in primitives)},
            "primitives": primitives}


def compare(baseline, candidate, allowlist):
    old = {row["identity"]: row for row in baseline["primitives"]}
    new = {row["identity"]: row for row in candidate["primitives"]}
    expected_names = set(allowlist)
    replaced_name = "concourse west small opening profiled lintel"
    regressions = []
    new_issues = []
    changed_payloads = []
    for key, row in new.items():
        if row["mesh"] in expected_names:
            if row["issues"]:
                new_issues.append(row)
            continue
        if key not in old:
            regressions.append({"identity": key, "reason": "Unexpected inherited primitive identity"})
            continue
        previous = old[key]
        if row.get("attribute_sha256") != previous.get("attribute_sha256") or row.get("indices_sha256") != previous.get("indices_sha256"):
            changed_payloads.append(key)
        for category, detail in row["issues"].items():
            prior = previous["issues"].get(category)
            if prior is None:
                regressions.append({"identity": key, "category": category, "reason": "New inherited issue category", "candidate": detail})
                continue
            if detail["count"] > prior["count"]:
                regressions.append({"identity": key, "category": category, "reason": "Affected count increased", "baseline": prior["count"], "candidate": detail["count"]})
            for metric in ("max_deviation", "geometry_total_area_m2", "max_longest_edge_m", "uv_collapsed_but_geometry_nondegenerate",
                           "substantial_over_0_0002_vertices", "substantial_on_nondegenerate_triangles",
                           "substantial_on_nondegenerate_valid_uv_triangles"):
                if metric in detail and metric in prior and detail[metric] is not None and prior[metric] is not None:
                    tolerance = 1e-12 if isinstance(detail[metric], float) else 0
                    if detail[metric] > prior[metric] + tolerance:
                        regressions.append({"identity": key, "category": category, "reason": metric + " increased", "baseline": prior[metric], "candidate": detail[metric]})
    unexpected_missing = [k for k, row in old.items() if k not in new and row["mesh"] != replaced_name]
    candidate_names = {r["mesh"] for r in candidate["primitives"]}
    missing_new = sorted(expected_names - candidate_names)
    old_target_retained = replaced_name in candidate_names
    passed = not regressions and not new_issues and not unexpected_missing and not missing_new and not old_target_retained
    payload_deltas = compare_changed_payloads(baseline, candidate, changed_payloads) if changed_payloads else []
    return {"passed": passed, "baseline_sha256": baseline["sha256"], "candidate_sha256": candidate["sha256"],
            "strict_new_detail_zero_errors": not new_issues and not missing_new,
            "expected_new_meshes": len(expected_names), "missing_new_meshes": missing_new,
            "new_detail_issues": new_issues, "inherited_regressions": regressions,
            "unexpected_missing_inherited_primitives": unexpected_missing,
            "replaced_lintel_retained": old_target_retained,
            "inherited_changed_geometry_attribute_payloads": changed_payloads,
            "inherited_changed_payload_deltas": payload_deltas,
            "all_inherited_geometry_attribute_payloads_identical": not changed_payloads,
            "limits": "Compares exact inherited identities, failure categories/counts/severity and records payload changes. Appearance still needs actual import rendering; materials and transforms require separate QA."}


def compare_changed_payloads(baseline, candidate, changed_identities):
    """Read only the changed accessor ranges, without allocating both full GLBs."""
    def selected_arrays(report):
        wanted = set(changed_identities)
        rows = {r["identity"]: r for r in report["primitives"] if r["identity"] in wanted}
        result = {}
        with Path(report["file"]).open("rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as data:
            offset = 12
            while offset < len(data):
                size, kind = struct.unpack_from("<II", data, offset)
                if kind == 0x4E4F534A:
                    doc = json.loads(data[offset+8:offset+8+size])
                elif kind == 0x004E4942:
                    binary_start = offset+8
                offset += 8+size
            for key, row in rows.items():
                attrs = doc["meshes"][row["mesh_index"]]["primitives"][row["primitive_index"]]["attributes"]
                result[key] = {}
                for name, index in attrs.items():
                    if name not in row["attribute_sha256"]:
                        continue
                    item = doc["accessors"][index]
                    view = doc["bufferViews"][item["bufferView"]]
                    assert item["componentType"] == 5126
                    width = {"VEC2": 2, "VEC3": 3, "VEC4": 4}[item["type"]]
                    arr = np.ndarray((item["count"], width), dtype="<f4", buffer=data,
                                     offset=binary_start+view.get("byteOffset", 0)+item.get("byteOffset", 0),
                                     strides=(view.get("byteStride", width*4), 4))
                    result[key][name] = arr.copy()
                    del arr
        return result
    old = selected_arrays(baseline)
    new = selected_arrays(candidate)
    results = []
    for key in changed_identities:
        changes = {}
        for name, a in old[key].items():
            b = new[key][name]
            if a.shape != b.shape:
                changes[name] = {"shape_changed": [list(a.shape), list(b.shape)]}
                continue
            delta = b.astype(np.float64)-a.astype(np.float64)
            mask = np.any(delta != 0, axis=1)
            if np.any(mask):
                changes[name] = {"changed_vertices": int(np.count_nonzero(mask)),
                                 "changed_components": int(np.count_nonzero(delta)),
                                 "max_abs_component_delta": finite_float(np.max(np.abs(delta))),
                                 "max_vector_delta": finite_float(np.linalg.norm(delta, axis=1).max()),
                                 "sample_changed_vertex_indices": np.flatnonzero(mask)[:16].tolist()}
                if name == "TEXCOORD_0":
                    # Same-sign positive UVs dominate these inherited changes;
                    # use ordered IEEE-754 bit patterns for all finite signs.
                    def ordered(values):
                        bits = values.view(np.uint32).astype(np.int64)
                        return np.where(bits & 0x80000000, 0x80000000-(bits & 0x7fffffff), 0x80000000+bits)
                    ulps = np.abs(ordered(a)-ordered(b))
                    changes[name]["max_float32_ulp_delta"] = int(ulps.max())
                    changes[name]["changed_component_ulp_histogram"] = {str(int(k)): int(v) for k, v in zip(*np.unique(ulps[ulps > 0], return_counts=True))}
                if name == "TANGENT":
                    changes[name]["handedness_changes"] = int(np.count_nonzero(delta[:, 3]))
        results.append({"identity": key, "changed_attributes": changes})
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--glb", required=True)
    parser.add_argument("--era", required=True, choices=["2017", "2026"])
    parser.add_argument("--output", required=True)
    parser.add_argument("--baseline-report")
    parser.add_argument("--allowlist-report")
    args = parser.parse_args()
    report = audit(args.glb, args.era)
    if args.baseline_report:
        assert args.allowlist_report, "Comparison requires the exact study QA allowlist"
        baseline = json.loads(Path(args.baseline_report).read_text())
        allowlist = [r["name"] for r in json.loads(Path(args.allowlist_report).read_text())["new_geometry"]]
        report["comparison"] = compare(baseline, report, allowlist)
    output = Path(args.output).resolve()
    owned = Path(__file__).resolve().parents[1]
    assert output.is_relative_to(owned), "Write only under revision15_concourse_integration"
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"output": str(output), "sha256": report["sha256"], "summary": report["summary"],
                      "comparison_passed": report.get("comparison", {}).get("passed")}, indent=2))
    return 0 if report.get("comparison", {}).get("passed", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
