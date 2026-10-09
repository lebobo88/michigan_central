"""Restore ONLY four approved inherited UV/tangent payloads into a NEW GLB copy.
No R14 GLB required. POSITION/NORMAL/index/material/TANGENT.w guards are mandatory.
"""
import sys
sys.dont_write_bytecode = True
import argparse,json,shutil,hashlib
from pathlib import Path
from glb_io import GLB,sha,digest,canonical,BLOCK
PKG=Path(__file__).resolve().parents[1]
def complement(path,intervals):
    h=hashlib.sha256();cursor=0
    with Path(path).open('rb') as f:
        for lo,hi in intervals+[(Path(path).stat().st_size,Path(path).stat().st_size)]:
            left=lo-cursor;f.seek(cursor)
            while left:b=f.read(min(left,BLOCK));h.update(b);left-=len(b)
            cursor=hi
    return h.hexdigest()
def recover(source,destination,report_path=None):
    source=Path(source);destination=Path(destination)
    if destination.exists() or destination.is_symlink() or source.resolve()==destination.resolve():raise ValueError('Destination must be a new file')
    if report_path and (Path(report_path).exists() or Path(report_path).is_symlink() or Path(report_path).resolve() in (source.resolve(),destination.resolve())):raise ValueError('Report must be a separate new file')
    ref=json.loads((PKG/'references/inherited_2026.json').read_text());blob=(PKG/'references/inherited_2026.bin').read_bytes()
    if sha(blob)!=ref['binary_sha256']:raise ValueError('Recovery binary hash mismatch')
    g=GLB(source);patches=[];guard_rows=[]
    for rec in ref['objects']:
        mi,p=g.primitive(rec['mesh'])
        if sha(canonical(g.material(p['material'])))!=rec['material_fingerprint_sha256']:raise ValueError('Material semantic mismatch: '+rec['mesh'])
        for label,expected in rec['guards'].items():
            ai=p['indices'] if label=='indices' else p['attributes'][label]
            if g.descriptor(ai)!=expected['accessor'] or sha(g.array(ai))!=expected['sha256']:raise ValueError('Vertex identity mismatch '+rec['mesh']+' '+label)
        for label,expected in rec['restore'].items():
            ai=p['attributes'][label];layout=g.layout(ai);before=g.array(ai);after=blob[expected['offset']:expected['offset']+expected['bytes']]
            if sha(after)!=expected['sha256'] or g.descriptor(ai)!=expected['accessor'] or len(before)!=len(after):raise ValueError('Restoration shape/hash mismatch')
            consumers=[(i,j,k) for i,m in enumerate(g.doc['meshes']) for j,q in enumerate(m['primitives']) for k,v in q['attributes'].items() if v==ai]
            if consumers!=[(mi,0,label)]:raise ValueError('Accessor shared outside target')
            width=8 if label=='TEXCOORD_0' else 12;stride=layout['row_bytes']
            for i in range(layout['count']):
                a=before[i*stride:(i+1)*stride];b=after[i*stride:(i+1)*stride]
                if label=='TANGENT' and a[12:]!=b[12:]:raise ValueError('Tangent handedness differs')
                if a[:width]!=b[:width]:patches.append((layout['start']+i*layout['stride'],a[:width],b[:width],ai))
        guard_rows.append({'mesh':rec['mesh'],'position_normal_index_material_and_handedness_guards_passed':True})
    patches.sort();intervals=[(offset,offset+len(before)) for offset,before,after,ai in patches]
    if any(a[1]>b[0] for a,b in zip(intervals,intervals[1:])):raise ValueError('Overlapping patches')
    # No alias via another accessor may overlap a modified byte, even if indices differ.
    import bisect
    ends=[b for a,b in intervals]
    for ai in range(len(g.doc.get('accessors',[]))):
        d=g.layout(ai);lo=d['start'];hi=lo+(d['count']-1)*d['stride']+d['row_bytes'];j=bisect.bisect_right(ends,lo)
        while j<len(intervals) and intervals[j][0]<hi:
            p=patches[j]
            if p[3]!=ai:
                first=max(0,(p[0]-lo-d['row_bytes'])//d['stride']);last=min(d['count'],(p[0]+len(p[1])-lo)//d['stride']+2)
                if any(max(p[0],lo+k*d['stride'])<min(p[0]+len(p[1]),lo+k*d['stride']+d['row_bytes']) for k in range(first,last)):raise ValueError('Aliased accessor patch')
            j+=1
    before_hash=digest(source);unchanged=complement(source,intervals)
    with source.open('rb') as src,destination.open('xb') as dst:shutil.copyfileobj(src,dst,BLOCK)
    with destination.open('r+b') as f:
        for off,before,after,ai in patches:
            f.seek(off)
            if f.read(len(before))!=before:raise ValueError('Input changed while preparing')
            f.seek(off);f.write(after)
    if digest(source)!=before_hash or complement(destination,intervals)!=unchanged:raise ValueError('Unapproved bytes changed')
    out=GLB(destination)
    for rec in ref['objects']:
        _,p=out.primitive(rec['mesh'])
        for label,x in rec['restore'].items():
            if sha(out.array(p['attributes'][label]))!=x['sha256']:raise ValueError('Post-recovery hash mismatch')
    report={'passed':True,'input_sha256':before_hash,'output_sha256':digest(destination),'new_output_file':str(destination),'changed_ranges':len(patches),'changed_bytes':sum(sum(a!=b for a,b in zip(old,new)) for _,old,new,_ in patches),'nonallowed_bytes_sha256':unchanged,'all_nonallowed_bytes_unchanged':True,'guards':guard_rows,'baseline_defects_not_repaired':True}
    if report_path:
        with Path(report_path).open('x') as f:f.write(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--output',required=True);ap.add_argument('--report');a=ap.parse_args();print(json.dumps(recover(a.input,a.output,a.report),indent=2))
