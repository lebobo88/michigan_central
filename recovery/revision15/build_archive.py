#!/usr/bin/env python3
"""Reproducibly archive this sealed, verified checkpoint; never operates on scenes."""
import sys
sys.dont_write_bytecode = True
import argparse,json,stat,sys,zipfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'scripts'))
from verify_package import verify_directory,verify_zip

def build(output):
    verify_directory(ROOT);output=Path(output).resolve()
    if output.exists() or ROOT in output.parents:raise ValueError('Archive output must be new and outside this package')
    with zipfile.ZipFile(output,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(ROOT.rglob('*')):
            if not p.is_file():continue
            name=p.relative_to(ROOT).as_posix();i=zipfile.ZipInfo(name,date_time=(2026,10,7,0,0,0));i.create_system=3;i.external_attr=(stat.S_IFREG|0o644)<<16;i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return verify_zip(output)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--report');a=p.parse_args();r=build(a.output)
    if a.report:
        with Path(a.report).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r,indent=2))
