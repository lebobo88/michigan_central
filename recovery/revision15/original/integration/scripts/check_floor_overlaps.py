"""Broad coplanar floor-face overlap check; detail overlays and tiny tiles excluded."""
import bpy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from artifact_provenance import file_sha256
R=Path(__file__).resolve().parents[1];era=sys.argv[sys.argv.index('--')+1];faces=[];findings=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not any(k in o.name.lower() for k in ['floor','slab','grout bed']):continue
 for p in o.data.polygons:
  if p.normal.z<.9999 or len(p.vertices)!=4 or p.area<1:continue
  vs=[o.matrix_world@o.data.vertices[i].co for i in p.vertices];xs=[v.x for v in vs];ys=[v.y for v in vs];zs=[v.z for v in vs]
  if max(zs)-min(zs)>1e-5:continue
  xa,xb,ya,yb=min(xs),max(xs),min(ys),max(ys)
  if abs((xb-xa)*(yb-ya)-p.area)>p.area*.001:continue
  faces.append((o.name,p.index,round(sum(zs)/4,5),xa,xb,ya,yb))
for i,a in enumerate(faces):
 for b in faces[i+1:]:
  if a[2]!=b[2]:continue
  dx=min(a[4],b[4])-max(a[3],b[3]);dy=min(a[6],b[6])-max(a[5],b[5])
  if dx>.002 and dy>.002 and dx*dy>.05:findings.append(dict(a=a[0],b=b[0],z=a[2],overlap_m2=dx*dy))
report=dict(source_blend_sha256=file_sha256(bpy.data.filepath),era=era,broad_faces_checked=len(faces),overlaps=findings,limits='Targets broad horizontal rectangular floor faces only; decorative inlays and nonrectangular floors need separate visual review')
(R/'manifests'/f'floor_overlap_{era}.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
