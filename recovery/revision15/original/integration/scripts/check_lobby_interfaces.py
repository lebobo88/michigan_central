"""Candidate raw-import alignment/contact/opening checks, not code compliance."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));from artifact_provenance import file_sha256
era=sys.argv[sys.argv.index('--')+1];s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();meta=json.loads(s['elevator_lobby_metadata']);c=meta['controls'];scale=c['scale_m_per_pixel'];xe=(555-c['east_face_x_pixel'])*scale
probes=[('arcade',(-39.0,40,1.7),(-44.5,40,1.7)),('east_entrance',(-44.5,40.07,1.7),(-53.,40.07,1.7)),('south_connector',(-44.1,50.2,1.7),(-44.1,59.3,1.7)),('north_approach',(-44.1,20.6,1.7),(-44.1,31.,1.7)),('west_restroom_gap',(-44.1,25.,1.7),(-41.6,25.,1.7)),('east_restroom_gap',(-44.1,25.,1.7),(-46.6,25.,1.7)),('west_north_branch',(-44.1,27.,1.7),(-40.5,27.,1.7))]
rows=[];fails=[]
for label,a,b in probes:
 origin=Vector(a);end=Vector(b);d=(end-origin).normalized();L=(end-origin).length;offset=0;hits=[]
 for _ in range(20):
  hit,pt,n,i,ob,mx=s.ray_cast(dg,origin+d*offset,d,distance=L-offset)
  if not hit:break
  dist=(pt-origin).length;name=ob.name.lower();allowed=('door' in name or 'portal' in name) and any(t in name for t in ['frame','division','glazing','door wall','sill and head','jambs'])
  hits.append(dict(object=ob.name,distance_m=dist,allowed_closed_door_part=allowed))
  if not allowed:fails.append([label,ob.name,'Unexpected opaque obstruction'])
  offset=dist+.02
  if offset>=L:break
 rows.append(dict(probe=label,from_m=a,to_m=b,hits=hits))
headers=[]
for y in [38.4,40.07,41.8]:
 a=Vector((xe+.6,y,5.15));hit,pt,n,i,ob,mx=s.ray_cast(dg,a,Vector((-1,0,0)),distance=1.)
 passed=hit and 'upper structural infill' in ob.name
 headers.append(dict(y=y,passed=passed,object=ob.name if hit else None))
 if not passed:fails.append(['upper entrance cap',y,'Source-supported header absent'])
cameras=[]
for ob in [o for o in s.objects if o.type=='CAMERA' and o.name.startswith('Camera elevator_lobby')]:
 p=ob.location;hit,pt,n,i,other,mx=s.ray_cast(dg,p,Vector((0,0,-1)),distance=3.);good=hit and 'floor' in other.name.lower() and pt.z<p.z
 cameras.append(dict(camera=ob.name,passed=good,first_downward_hit=other.name if hit else None,point=list(pt) if hit else None))
 if not good:fails.append(['Camera not above candidate floor',ob.name])
issues=[]  # Full source UV/geometry is tested independently by validate_scene/check_uv_area.
report=dict(era=era,source_blend_sha256=file_sha256(bpy.data.filepath),passed=not(fails or issues),source_code_current_sha256=hashlib.sha256((ROOT/'scripts/candidates/elevator_lobby_detail.py').read_bytes()).hexdigest(),opening_checks=rows,upper_entrance_cap=headers,camera_floor_containment=cameras,geometry_uv_issues=issues,failures=fails,scope='Actual saved full scene; intended route centerlines and visible cap/contact only; no accessibility/egress certification, no surveyed clearance claim')
(ROOT/f'manifests/lobby_interface_checks_{era}.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['era','passed','failures','geometry_uv_issues']},indent=2));assert report['passed']
