"""Verify assembled payloads and all original Revision 14 package manifests."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    report = json.loads((ROOT / "manifests/consolidation.json").read_text(encoding="utf-8"))
    errors = []
    hashes = {}
    for record in report["files"]:
        path = ROOT / record["path"]
        if not path.is_file():
            errors.append(f"Missing: {record['path']}")
            continue
        sha = digest(path)
        hashes[record["path"]] = sha
        if path.stat().st_size != record["bytes"] or sha != record["sha256"]:
            errors.append(f"Changed: {record['path']}")
    manifest_entries = 0
    for path in sorted((ROOT / "docs/packages").glob("*.json")):
        package = json.loads(path.read_text(encoding="utf-8"))
        for record in package["files"]:
            relative = record["path"].split("/", 1)[1]
            if relative == "README.md":
                relative = "docs/revision14/README.md"
            if hashes.get(relative) != record["sha256"]:
                errors.append(f"Original package mismatch: {path.name}: {relative}")
            manifest_entries += 1
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"PASS: {len(hashes)} assembled payloads and {manifest_entries} original R14 manifest entries")
    print("R14 scene files and R15 recovery package retain their supplied bytes.")


if __name__ == "__main__":
    main()
