"""Restore large scene files from versioned, Git LFS tracked chunks."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def within(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Unsafe path: ' + name)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, default=ROOT,
                        help='Optional separate directory for reconstruction verification')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'storage/scene_chunks.json').read_text(encoding='utf-8'))
    for record in manifest['files']:
        target = within(args.output_root, record['path'])
        if target.exists():
            if target.stat().st_size != record['bytes'] or digest(target) != record['sha256']:
                raise SystemExit('Existing scene differs; refusing to overwrite: ' + str(target))
            print('Verified existing scene: ' + record['path'], flush=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + '.restore.tmp')
        if temporary.exists():
            raise SystemExit('Incomplete restore file already exists: ' + str(temporary))
        h = hashlib.sha256()
        size = 0
        try:
            with temporary.open('xb') as out:
                for chunk in record['chunks']:
                    source = within(ROOT, chunk['path'])
                    payload = source.read_bytes()
                    if len(payload) != chunk['bytes'] or hashlib.sha256(payload).hexdigest() != chunk['sha256']:
                        raise ValueError('Chunk mismatch; ensure Git LFS downloaded it: ' + chunk['path'])
                    out.write(payload)
                    h.update(payload)
                    size += len(payload)
            if size != record['bytes'] or h.hexdigest() != record['sha256']:
                raise ValueError('Restored file hash mismatch: ' + record['path'])
            if target.exists():
                raise ValueError('Scene appeared during restore; refusing to overwrite')
            temporary.rename(target)
        except BaseException:
            if temporary.exists():
                temporary.unlink()
            raise
        print('Restored and verified: ' + record['path'], flush=True)


if __name__ == '__main__':
    main()
