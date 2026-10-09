"""Targeted integrated public-space centerline probes; not a navigation or safety certificate."""
import bpy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from artifact_provenance import file_sha256
from mathutils import Vector
r=Path(__file__).resolve().parents[1];era=sys.argv[sys.argv.index('--')+1];s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
checks=[
 ('hall_to_ticket_low_clearance',(0,29.6,.35),(0,34.0,.35)),
 ('north_entry_low_clearance',(0,-1.1,.35),(0,1.0,.35)),
 ('north_entry_standing',(0,-1.1,1.7),(0,1.0,1.7)),
 ('hall_to_ticket',(0,29.6,1.70),(0,34.0,1.70)),
 ('ticket_to_arcade',(-4.5,40.0,1.70),(-37.8,40.0,1.70)),
 ('arcade_to_elevators',(-37.8,40.0,1.70),(-43.4,40.0,1.70)),
 ('elevators_to_east_entrance',(-44.0,40.07,1.70),(-53.3,40.07,1.70)),
 ('elevators_to_exit_passage',(-44.05,51.3,1.70),(-44.05,60.0,1.70)),
 ('concourse_to_exit_ramp',(-28.2,62.8,1.70),(-31.2,62.8,1.70)),
 ('ramp_to_wide_exit_vestibule',(-43.8,62.8,1.70),(-47.0,62.8,1.70)),
 ('concourse_to_passenger_ramp',(0,74.0,1.4),(0,78.3,1.4)),
]
if s.get('concourse_wall_metadata'):
 controls=json.loads(s['concourse_wall_metadata'])['controls'];width=controls['width_m'];cy=controls['center_y_m'];ny=cy-controls['depth_m']/2
 checks += [('concourse_to_west_portal',(width/2-1.2,cy,1.7),(width/2+1.2,cy,1.7))]
 for i in range(controls['long_bays']):
  x=-width/2+(i+.5)*width/controls['long_bays']
  if abs(x)>controls['ticket_half_opening_m']:checks.append(('concourse_north_arcade_bay_'+str(i+1),(x,ny+1,1.7),(x,ny-.7,1.7)))
if era=='2026':checks += [
 ('hall_to_study',(-34.3,16.2,1.7),(-37.3,16.2,1.7)),
 ('hall_to_west_reading',(34.3,10.1,1.7),(37.3,10.1,1.7)),
 ('cafe_to_west_corridor',(44.1,23.0,1.7),(44.1,24.15,1.7)),
 ('west_corridor_to_restaurant',(44.1,28.2,1.7),(44.1,29.5,1.7)),
 ('lobby_to_shop',(6.9,40.6,1.6),(9.2,40.6,1.6)),
 ('lobby_to_neighbor',(-10.3,46.05,1.6),(-12.6,46.05,1.6)),
 ('arcade_to_yellow_light',(-34.13,42.5,1.6),(-34.13,44.3,1.6)),
]
rows=[]
for label,a,b in checks:
 origin=Vector(a);end=Vector(b);direction=(end-origin).normalized();distance=(end-origin).length;hits=[];offset=0.
 for attempt in range(30):
  hit,loc,n,idx,obj,matrix=s.ray_cast(dg,origin+direction*offset,direction,distance=distance-offset)
  if not hit:break
  d=(loc-origin).length
  if d<offset-.001:break
  name=obj.name.lower();mats=[m.name.lower() for m in obj.data.materials if m]
  doorway=any(x in name for x in ['door','entrance','entry','portal','screen','frame','end door','exit-ramp connection','west concourse connection'])
  glass=any('glass' in x for x in mats)
  allowed=(doorway and (glass or any(x in name for x in ['division','glazing','door leaves','doorway','door wall','frame','portal','screen']))) or name in ['end door leaves','2026 north entrance panel lower rails'] or name.startswith('2017 north entry closed corrugated shutter ')
  if any(t in name for t in ['masonry','wall sections','unobserved continuation closure','brick piers','brick sill walls','structural wall','north facade continuous stone piers']):allowed=False
  hits.append(dict(object=obj.name,distance_m=round(d,4),classification='documented door/screen part, may be closed' if allowed else 'potential unexpected obstruction'))
  offset=d+.025
  if offset>=distance:break
 rows.append(dict(connection=label,from_m=a,to_m=b,hits=hits,status='clear or only documented door parts' if not any(q['classification'].startswith('potential') for q in hits) else 'REVIEW'))
out=dict(source_blend_sha256=file_sha256(bpy.data.filepath),era=era,checks=rows,limitations=['Centerlines only; does not check accessible widths, headroom, egress code, stair compliance, or every room','Declared door/screen parts may intentionally be closed','Each REVIEW requires visual/geometry classification rather than automatic deletion'])
(r/'manifests'/f'public_interface_checks_{era}.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
