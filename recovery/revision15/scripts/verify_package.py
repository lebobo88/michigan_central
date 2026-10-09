"""Verify extracted checkpoint or ZIP. Reject traversal, symlinks and extra entries."""
import sys
sys.dont_write_bytecode = True
import argparse,hashlib,json,stat,zipfile
from pathlib import Path,PurePosixPath
from glb_io import digest,sha
MAX_TOTAL=64*1024*1024;MAX_FILE=16*1024*1024

def safe_name(name):
    p=PurePosixPath(name)
    if not name or '\\'in name or ':'in name or '\x00'in name or p.is_absolute() or any(x in ('','.','..') for x in name.split('/')) or p.as_posix()!=name or len(name)>1024:raise ValueError('Unsafe package path: '+repr(name))
    return p

def manifest_check(manifest):
    if manifest.get('schema')!=1 or manifest.get('blender_reconstruction')!='NOT YET VALIDATED':raise ValueError('Unexpected manifest contract')
    for name,rec in manifest['files'].items():
        safe_name(name)
        if name=='PACKAGE_MANIFEST.json' or rec['bytes']<0 or rec['bytes']>MAX_FILE or len(rec['sha256'])!=64:raise ValueError('Invalid manifest file entry')
    if sum(r['bytes'] for r in manifest['files'].values())>MAX_TOTAL:raise ValueError('Oversized manifest')

def verify_directory(root):
    root=Path(root)
    if root.is_symlink():raise ValueError('Package root symlink')
    files={}
    for path in root.rglob('*'):
        if path.is_symlink():raise ValueError('Package symlink')
        if path.is_file():name=path.relative_to(root).as_posix();safe_name(name);files[name]=path
    manifest=json.loads((root/'PACKAGE_MANIFEST.json').read_text());manifest_check(manifest)
    if set(files)!=set(manifest['files'])|{'PACKAGE_MANIFEST.json'}:raise ValueError('Missing or unexpected package entries')
    for name,rec in manifest['files'].items():
        if files[name].stat().st_size!=rec['bytes'] or digest(files[name])!=rec['sha256']:raise ValueError('Package hash mismatch: '+name)
    return {'passed':True,'files':len(files),'bytes':sum(p.stat().st_size for p in files.values()),'symlinks':False,'path_traversal':False,'blender_reconstruction':'NOT YET VALIDATED'}

def verify_zip(path):
    with zipfile.ZipFile(path) as z:
        info=z.infolist();names=[i.filename for i in info]
        if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP entry')
        if sum(i.file_size for i in info)>MAX_TOTAL:raise ValueError('Oversized ZIP content')
        for i in info:
            safe_name(i.filename);mode=i.external_attr>>16
            if i.is_dir() or stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0,stat.S_IFREG)) or i.flag_bits&1 or i.file_size>MAX_FILE:raise ValueError('Unsupported ZIP entry')
        if 'PACKAGE_MANIFEST.json'not in names:raise ValueError('No package manifest')
        manifest=json.loads(z.read('PACKAGE_MANIFEST.json'));manifest_check(manifest)
        if set(names)!=set(manifest['files'])|{'PACKAGE_MANIFEST.json'}:raise ValueError('ZIP entry set mismatch')
        for name,rec in manifest['files'].items():
            i=z.getinfo(name)
            if i.file_size!=rec['bytes']:raise ValueError('ZIP size mismatch')
            h=hashlib.sha256()
            with z.open(i) as f:
                for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
            if h.hexdigest()!=rec['sha256']:raise ValueError('ZIP hash mismatch: '+name)
        if z.testzip() is not None:raise ValueError('ZIP CRC error')
    return {'passed':True,'entries':len(names),'uncompressed_bytes':sum(i.file_size for i in info),'zip_bytes':Path(path).stat().st_size,'zip_sha256':digest(path),'entry_sizes_hashes_and_crc_verified':True,'symlinks':False,'path_traversal':False,'blender_reconstruction':'NOT YET VALIDATED'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('path',nargs='?',default=str(Path(__file__).resolve().parents[1]));a=ap.parse_args();path=Path(a.path);print(json.dumps(verify_directory(path) if path.is_dir() else verify_zip(path),indent=2))
