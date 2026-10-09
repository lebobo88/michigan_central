"""Bounded concourse masonry/end-portal/terrazzo replacement in B namespace.

Execute after the legacy SOUTH CONCOURSE batches; the source-informed roof is
never read, regenerated or deleted. Assets are original analytic PBR maps.
Public dimension controls are inherited, not a survey. No full2026 fit-out or
exact2017 damage map is claimed. See manifests/concourse_walls_detail/.
"""
import math as _cw_math
from copy import deepcopy as _cw_copy
_CW_SAVED_GROUP=GROUP
_CW_OLD_GROUP='05 CONCOURSE | restored glazing and structural roof'
_CW_GROUP='05 CONCOURSE | source-informed masonry and floor'
_CW_OLD_NAMES=('concourse floor','concourse brick sill walls','concourse brick piers','concourse brick parapet',
 'concourse original grid window','concourse window mullions','concourse window transoms','concourse west end wall',
 'concourse east wall sections','east-exit portal header','ticket lobby concourse portal lintel',
 'passenger ramp upper parapet','ramp opening flank masonry')
CONCOURSE_WALL_DEFAULTS={
 'width_m':58.9788,'depth_m':23.7744,'center_y_m':63.4,'wall_head_m':10.,'wall_depth_m':1.,'floor_top_m':.14,
 'long_bays':8,'long_pier_width_m':1.40,'north_arcade_clear_height_m':7.90,
 'south_window_sill_m':2.80,'south_window_head_m':8.40,
 'ticket_half_opening_m':7.37235,'passenger_half_opening_m':11.5824,'ramp_flank_outer_m':14.7447,
 'ramp_low_header_bottom_m':4.70,'ramp_upper_header_bottom_m':8.80,
 'east_exit_y0_m':59.4,'east_exit_y1_m':66.2,'east_exit_head_m':4.80,
 'west_portal_width_m':5.00,'west_portal_head_m':7.65,'west_screen_major_offset_fraction':.32,'west_screen_major_width_m':.16,'west_screen_minor_width_m':.035,'west_screen_panes_by_zone':[2,8,2],'west_side_door_offset_m':8.15,
 'west_side_door_width_m':1.08,'west_side_door_head_m':2.28,
 'pilaster_projection_m':.13,'panel_border_width_m':.075,'panel_border_projection_m':.030,
 'dado_head_m':.97,'frieze_bottom_m':8.66,'frieze_top_m':9.13,
 'cornice_bottom_m':9.48,'dentil_pitch_m':.29,'dentil_width_m':.135,'dentil_height_m':.17,
 'west_vestibule_depth_m':3.65,'north_circulation_back_y_m':49.0,'north_circulation_east_limit_x_m':-28.50,'north_circulation_2026_west_limit_x_m':24.70,
 'floor_long_band_offsets_m':[-7.75,0,7.75],'floor_band_width_m':.34,'floor_spine_width_m':.70,
 'floor_chamfer_m':.27,'include_bounded_north_circulation':True,'include_bounded_west_vestibule':True,
}
CONCOURSE_WALL_CONTROLS=_cw_copy(CONCOURSE_WALL_DEFAULTS)
CONCOURSE_WALL_CONTROLS.update(globals().get('CONCOURSE_WALL_CONTROL_OVERRIDES',{}))

def cw_pbr(name,asset):
 if name not in M:
  pbr(name,'concourse_walls_detail/'+asset,1.36)
  M[name]['texture_provenance']='Original deterministic procedural image; no source photograph sampled, projected or included'
 return name

def cw_materials():
 e=str(ERA)
 mats={'brick':cw_pbr('Concourse Flemish buff masonry '+e,'flemish_buff_'+e),
  'frieze':cw_pbr('Concourse herringbone frieze '+e,'herringbone_buff_'+e),
  'terra':cw_pbr('Concourse terracotta dressings '+e,'terracotta_'+e)}
 if not AGED:
  mats['floor']=cw_pbr('Concourse warm restored terrazzo','terrazzo_warm')
  mats['band']=cw_pbr('Concourse bluegray terrazzo bands','terrazzo_bluegray')
 else:mats['floor']=mats['band']='Weathered concrete'
 name='Concourse retained portal metal '+e
 if name not in M:mat(name,(.16,.093,.049) if AGED else (.041,.048,.043),.82 if AGED else .38,.34 if AGED else .68)
 mats['metal']=name
 # Avoid legacy Glass clear automatic SOLIDIFY; these panes are already solid.
 name='Concourse restored portal glass'
 if not AGED and name not in M:mat(name,(.79,.85,.88),.10,0,.92)
 mats['glass']=name
 return mats

def cw_face(points,material,name):
 # Face-local projection is explicitly metric; no Generated texture coordinates.
 a,b,c=points[:3];ab=[b[i]-a[i] for i in range(3)];ac=[c[i]-a[i] for i in range(3)]
 n=(ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0])
 ax=max(range(3),key=lambda j:abs(n[j]));ids=([1,2] if ax==0 else [0,2] if ax==1 else [0,1])
 uv=[(p[ids[0]],p[ids[1]]) for p in points]
 # Source-visible gauged west lintel has predominantly upright bricks, gently
 # splayed toward its central keystone. This is analytic UV orientation, not a
 # photograph projection or a recovered brick-by-brick inventory.
 if name=='concourse west retained masonry portal wall' and 'Flemish' in material and ax==0:
  cc=CONCOURSE_WALL_CONTROLS;mid=cc['center_y_m'];pw=cc['west_portal_width_m']
  if min(p[2] for p in points)>=cc['west_portal_head_m']-1e-7 and max(p[2] for p in points)<=8.66+1e-7 and max(abs(p[1]-mid) for p in points)<=pw/2+1e-7:
   uv=[(p[2]+abs(p[1]-mid)*.095,p[1]) for p in points]
 addmesh(points,[tuple(range(len(points)))],material,name,face_uv=[uv])

def cw_cube(c,s,material,name):
 x,y,z=c;hx,hy,hz=[v/2 for v in s]
 v=[(x+dx*hx,y+dy*hy,z+dz*hz) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 for f in [(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]:cw_face([v[i] for i in f],material,name)

def cw_unique(values):return sorted(set(round(float(x),8) for x in values))

def cw_relief_wall(label,axis,plane,sign,us,zs,front_depth,back_depth,cell):
 """Watertight stitched rectilinear wall with holes and variable relief depth.
 Cell returns (extra inward projection,front material), or None for an opening.
 Coplanar shared cell walls are omitted; no stacked panel decals or filled portals.
 """
 us=cw_unique(us);zs=cw_unique(zs);cells={}
 for i,(a,b) in enumerate(zip(us,us[1:])):
  for j,(lo,hi) in enumerate(zip(zs,zs[1:])):
   v=cell((a+b)/2,(lo+hi)/2)
   if v is not None:cells[i,j]=(front_depth+v[0],v[1])
 def P(u,d,z):return (plane+sign*d,u,z) if axis=='x' else (u,plane+sign*d,z)
 def emit(coords,m,normal):
  pts=[P(*q) for q in coords]
  a,b,c=pts[:3];ab=[b[k]-a[k] for k in range(3)];ac=[c[k]-a[k] for k in range(3)]
  n=(ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0])
  target=(normal[1]*sign,normal[0],normal[2]) if axis=='x' else (normal[0],normal[1]*sign,normal[2])
  if sum(x*y for x,y in zip(n,target))<0:pts.reverse()
  cw_face(pts,m,label)
 for (i,j),(d,m) in cells.items():
  a,b=us[i:i+2];lo,hi=zs[j:j+2]
  emit([(a,d,lo),(b,d,lo),(b,d,hi),(a,d,hi)],m,(0,1,0))
  emit([(a,-back_depth,lo),(b,-back_depth,lo),(b,-back_depth,hi),(a,-back_depth,hi)],m,(0,-1,0))
  for di,dj in [(-1,0),(1,0),(0,-1),(0,1)]:
   neighbour=cells.get((i+di,j+dj));nd=neighbour[0] if neighbour else -back_depth
   if nd>=d-1e-9:continue
   if di:
    u=a if di<0 else b
    emit([(u,nd,lo),(u,d,lo),(u,d,hi),(u,nd,hi)],m,(di,0,0))
   else:
    z=lo if dj<0 else hi
    emit([(a,nd,z),(b,nd,z),(b,d,z),(a,d,z)],m,(0,0,dj))
 return {'u':us,'z':zs,'occupied_cells':len(cells)}

def cw_wall_grid(u0,u1,holes,pilasters,panels,c):
 us=[u0,u1];zs=[c['floor_top_m'],c['dado_head_m'],1.11,1.23,7.99,8.13,8.32,
  c['frieze_bottom_m'],c['frieze_top_m'],9.22,c['cornice_bottom_m'],9.61,9.72,9.85,c['wall_head_m']]
 for a,b,lo,hi in holes:us.extend([a,b]);zs.extend([lo,hi])
 for p,w in pilasters:
  for d in [-w/2-.18,-w/2,-w/2+.12,w/2-.12,w/2,w/2+.18]:us.append(p+d)
 for a,b in panels:
  us.extend([a,a+c['panel_border_width_m'],b-c['panel_border_width_m'],b])
 us=[max(u0,min(u1,u)) for u in us];zs=[max(c['floor_top_m'],min(c['wall_head_m'],z)) for z in zs]
 return cw_unique(us),cw_unique(zs)

def cw_masonry_cell(u,z,holes,pilasters,panels,c,m):
 if any(a-1e-7<u<b+1e-7 and lo-1e-7<z<hi+1e-7 for a,b,lo,hi in holes):return None
 material=m['brick'];d=0.
 if z<c['dado_head_m']:material=m['terra'];d=.015
 elif z<1.11:material=m['terra'];d=.04
 for p,w in pilasters:
  if abs(u-p)<w/2:
   d=max(d,c['pilaster_projection_m'])
   if z<1.23 or z>8.13:material=m['terra']
  if abs(u-p)<w/2+.18:
   if 1.11<z<1.23:d=max(d,.19);material=m['terra']
   if 7.99<z<8.13:d=max(d,.18);material=m['terra']
   if 8.13<z<8.32:d=max(d,.245);material=m['terra']
 if 1.23<z<7.99:
  for a,b in panels:
   if a<u<b and (u<a+c['panel_border_width_m'] or u>b-c['panel_border_width_m']):d=max(d,c['panel_border_projection_m']);material=m['terra']
 if c['frieze_bottom_m']<z<c['frieze_top_m']:material=m['frieze']
 if c['frieze_top_m']<z<9.22 or 8.32<z<c['frieze_bottom_m']:material=m['terra'];d=max(d,.025)
 if z>c['cornice_bottom_m']:
  material=m['terra'];d=max(d,.09 if z<9.61 else .20 if z<9.72 else .275 if z<9.85 else .22)
 return d,material

def cw_dentils(label,axis,plane,sign,u0,u1,c,m):
 # Small individually authored projecting teeth beneath the retained masonry cap.
 n=int((u1-u0)/c['dentil_pitch_m']);pitch=(u1-u0)/n
 for i in range(n):
  u=u0+(i+.5)*pitch;d=plane+sign*(c['wall_depth_m']/2+.10)
  center=(d,u,9.37) if axis=='x' else (u,d,9.37)
  size=(.24,c['dentil_width_m'],c['dentil_height_m']) if axis=='x' else (c['dentil_width_m'],.24,c['dentil_height_m'])
  cw_cube(center,size,m['terra'],label+' regularized cornice dentil teeth')

def cw_roundel(label,axis,plane,sign,u,z,material,r=.22):
 # Original simplified concentric medallion, not a copied decorative design.
 # Radius/profile and distribution remain explicitly photo-proportioned.
 def P(uu,dd,zz):return (plane+sign*dd,uu,zz) if axis=='x' else (uu,plane+sign*dd,zz)
 profile=[(0.,.10),(r*.72,.10),(r*.72,.14),(r,.14),(r,.02),(0.,.02)]
 n=32
 for (ra,da),(rb,db) in zip(profile,profile[1:]):
  for i in range(n):
   a=2*_cw_math.pi*i/n;b=2*_cw_math.pi*(i+1)/n
   pts=[P(u+ra*_cw_math.cos(a),da,z+ra*_cw_math.sin(a)),P(u+rb*_cw_math.cos(a),db,z+rb*_cw_math.sin(a)),P(u+rb*_cw_math.cos(b),db,z+rb*_cw_math.sin(b)),P(u+ra*_cw_math.cos(b),da,z+ra*_cw_math.sin(b))]
   if ra==0:pts=pts[:3]
   if rb==0:pts=[pts[0],pts[1],pts[3]]
   # yz->x / xz->y handedness changes between these projections.
   if (axis=='x' and sign<0) or (axis=='y' and sign>0):pts.reverse()
   # Small curved relief at large station coordinates needs explicit triangles:
   # float32 quad normals can differ enough from MikkTSpace triangle tangents
   # to fail strict orthogonality. Triangles share the same authored profile.
   if len(pts)==4:
    for tri in [(0,1,2),(0,2,3)]:cw_face([pts[i] for i in tri],material,label+' original concentric frieze medallions')
   else:cw_face(pts,material,label+' original concentric frieze medallions')

def cw_keystone(x,cy,material):
 poly=[(cy-.19,7.65),(cy+.19,7.65),(cy+.29,8.56),(cy-.29,8.56)]
 v=[(xx,y,z) for xx in [x-.64,x-.485] for y,z in poly]
 for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:cw_face([v[i] for i in f],material,'concourse west plain photo-relative terracotta keystone')


def cw_screen(label,axis,plane,sign,u0,u1,z0,z1,m,main=False):
 """Source-readable retained metal grid;2017 contains NO glazing or new leaves."""
 w=u1-u0;mid=(u0+u1)/2
 us=[u0,u0+.10,u1-.10,u1];zs=[z0,z0+.10,z1-.10,z1]
 if main:
  lower=2.55;transom=3.64;plate=4.66
  controls=CONCOURSE_WALL_CONTROLS
  major_offset=w*controls['west_screen_major_offset_fraction'];major_half=controls['west_screen_major_width_m']/2
  minor_half=controls['west_screen_minor_width_m']/2
  major_positions=[mid-major_offset,mid+major_offset]
  for v in major_positions:us.extend([v-major_half,v+major_half])
  # post_p48 shows2 +8 +2 panes, with two larger continuous mullions.
  # Pane counts are independently inspected, while metric section sizes remain
  # source-proportioned. The same retained hierarchy is qualified for2017.
  clear_zones=[(u0+.10,major_positions[0]-major_half),(major_positions[0]+major_half,major_positions[1]-major_half),(major_positions[1]+major_half,u1-.10)]
  minor_positions=[]
  for (a,b),count in zip(clear_zones,controls['west_screen_panes_by_zone']):
   for i in range(1,count):minor_positions.append(a+(b-a)*i/count)
  for u in minor_positions:us.extend([u-minor_half,u+minor_half])
  for zz in [lower,transom,plate]:zs.extend([zz-.075,zz+.075])
  zs.extend([6.10-.027,6.10+.027,transom+.14,transom+.19,plate-.19,plate-.14])
  for u in [u0+.18,u0+.23,mid-major_offset-.09,mid-major_offset-.04,mid+major_offset+.04,mid+major_offset+.09,u1-.23,u1-.18]:us.append(u)
 else:
  lower=z0;transom=z0+(z1-z0)*.35;plate=transom
  for i in range(1,8):
   u=u0+w*i/8;us.extend([u-.03,u+.03])
  for i in range(1,5):
   z=z0+(z1-z0)*i/5;zs.extend([z-.028,z+.028])
 def cell(u,z):
  edge=u<u0+.10 or u>u1-.10 or z<z0+.10 or z>z1-.10
  if main:
   # Central lower passage remains open in both eras. Restoration side panels
   # are seen in post48;2010 corroborates sparse framework, not a2017 pane map.
   side=abs(u-mid)>major_offset
   lowerframe=any(abs(u-p)<major_half for p in major_positions)
   horizontal=any(abs(z-t)<.075 for t in [lower,transom,plate])
   if z<lower-.075:
    if not side:return None
    solid=edge or lowerframe or not AGED
   elif transom+.075<z<plate-.075:solid=True
   else:
    solid=edge or horizontal or lowerframe or any(abs(u-p)<minor_half for p in minor_positions) or (z>plate and abs(z-6.10)<.027)
  else:solid=edge or any(abs(u-(u0+w*i/8))<.03 for i in range(1,8)) or any(abs(z-(z0+(z1-z0)*i/5))<.028 for i in range(1,5))
  if solid:
   relief=.075
   if main and transom+.075<z<plate-.075:
    relief=.066
    if abs(z-(transom+.165))<.025 or abs(z-(plate-.165))<.025 or any(abs(u-p)<.025 for p in [u0+.205,mid-major_offset-.065,mid+major_offset+.065,u1-.205]):relief=.092
   if main and lowerframe:relief=max(relief,.105)
   return relief,m['metal']
  if AGED:return None
  return .004,m['glass']
 return cw_relief_wall(label,axis,plane,sign,us,zs,0,.075,cell)

def cw_floor(c,m):
 """Single partitioned floor skin: flush bands, no coplanar overlays."""
 x0=-c['width_m']/2;x1=-x0;y0=c['center_y_m']-c['depth_m']/2;y1=c['center_y_m']+c['depth_m']/2;z=c['floor_top_m']
 if AGED:
  cw_cube((0,c['center_y_m'],z-.12),(c['width_m'],c['depth_m'],.24),m['floor'],'concourse qualified2017 unpatterned floor');return
 xs=[x0+i*(x1-x0)/c['long_bays'] for i in range(c['long_bays']+1)]
 ys=[y0]+[c['center_y_m']+d for d in c['floor_long_band_offsets_m']]+[y1]
 tops=[]
 def top(poly,material):
  tops.append(poly);cw_face([(x,y,z) for x,y in poly],material,'concourse restored flush terrazzo field' if material==m['floor'] else 'concourse restored flush terrazzo bands')
 for ia,(xa,xb) in enumerate(zip(xs,xs[1:])):
  for ja,(ya,yb) in enumerate(zip(ys,ys[1:])):
   border=c['floor_band_width_m']/2
   xlo=xa+border;xhi=xb-border
   ylo=ya+(c['floor_spine_width_m']/2 if abs(ya-c['center_y_m'])<1e-6 else border)
   yhi=yb-(c['floor_spine_width_m']/2 if abs(yb-c['center_y_m'])<1e-6 else border)
   d=c['floor_chamfer_m']
   inner=[(xlo+d,ylo),(xhi-d,ylo),(xhi,ylo+d),(xhi,yhi-d),(xhi-d,yhi),(xlo+d,yhi),(xlo,yhi-d),(xlo,ylo+d)]
   outer=[(xa+d,ya),(xb-d,ya),(xb,ya+d),(xb,yb-d),(xb-d,yb),(xa+d,yb),(xa,yb-d),(xa,ya+d)]
   top(inner,m['floor'])
   for k in range(8):top([outer[k],outer[(k+1)%8],inner[(k+1)%8],inner[k]],m['band'])
   for k,corner in [(7,(xa,ya)),(1,(xb,ya)),(3,(xb,yb)),(5,(xa,yb))]:top([outer[k],corner,outer[(k+1)%8]],m['band'])
 # Bottom tessellation mirrors the top and the outer sides close only boundary
 # edges. Adjacent material patches share geometry, never duplicate top faces.
 edges={}
 for poly in tops:
  cw_face([(x,y,z-.24) for x,y in reversed(poly)],m['floor'],'concourse floor slab underside')
  for a,b in zip(poly,poly[1:]+poly[:1]):
   key=tuple(sorted((tuple(round(q,7) for q in a),tuple(round(q,7) for q in b))))
   edges.setdefault(key,[]).append((a,b))
 for uses in edges.values():
  if len(uses)==1:
   a,b=uses[0];cw_face([(a[0],a[1],z),(a[0],a[1],z-.24),(b[0],b[1],z-.24),(b[0],b[1],z)],m['floor'],'concourse floor slab perimeter edge')

def cw_build(c):
 global GROUP
 if set(c)-set(CONCOURSE_WALL_DEFAULTS):raise ValueError('Unknown wall controls')
 if bool(AGED)!=(str(ERA)=='2017'):raise ValueError('ERA and AGED disagree')
 if globals().get('SWAP_XY',False):raise ValueError('Station-global axes required')
 GROUP=_CW_GROUP;m=cw_materials();w=c['width_m'];d=c['depth_m'];cy=c['center_y_m'];x0=-w/2;x1=w/2;y0=cy-d/2;y1=cy+d/2;floor=c['floor_top_m'];bay=w/c['long_bays'];wallreport={}
 cw_floor(c,m)
 for north,plane,sign in [(True,y0,1),(False,y1,-1)]:
  holes=[];pillars=[];panels=[];screens=[]
  for j in range(c['long_bays']):
   a=x0+j*bay;b=a+bay;mid=(a+b)/2
   if north and abs(mid)<8:
    holes.append((a,b,floor,8.80));continue
   if not north and abs(mid)<15:continue
   left=a+c['long_pier_width_m']/2;right=b-c['long_pier_width_m']/2
   holes.append((left,right,floor if north else c['south_window_sill_m'],c['north_arcade_clear_height_m'] if north else c['south_window_head_m']))
   if not north:screens.append((left,right,c['south_window_sill_m'],c['south_window_head_m']))
   panels.append((a+.22,b-.22))
  if not north:
   ph=c['passenger_half_opening_m'];outer=c['ramp_flank_outer_m']
   holes.extend([(-ph,ph,floor,c['ramp_upper_header_bottom_m']),(-outer,-ph,c['ramp_low_header_bottom_m'],c['ramp_upper_header_bottom_m']),(ph,outer,c['ramp_low_header_bottom_m'],c['ramp_upper_header_bottom_m'])])
  for i in range(c['long_bays']+1):
   p=x0+i*bay
   if north and abs(p)<c['ticket_half_opening_m']-.01:continue
   if not north and abs(p)<c['ramp_flank_outer_m']-.01:continue
   if x0+.5<p<x1-.5:pillars.append((p,c['long_pier_width_m']))
  us,zs=cw_wall_grid(x0,x1,holes,pillars,panels,c)
  label='concourse north open arcade masonry' if north else 'concourse south retained window and ramp masonry'
  wallreport['north' if north else 'south']=cw_relief_wall(label,'y',plane,sign,us,zs,.5,.5,lambda u,z:cw_masonry_cell(u,z,holes,pillars,panels,c,m))
  cw_dentils(label,'y',plane,sign,x0,x1,c,m)
  for j in range(c['long_bays']):
   u=x0+(j+.5)*bay
   if not north and abs(u)<15:continue
   cw_roundel(label,'y',plane+sign*.5,sign,u,8.90,m['terra'])
  for a,b,lo,hi in screens:cw_screen('concourse south retained metal window grid','y',plane,sign,a,b,lo,hi,m)
 # West wall: source-visible portal assembly, left small doorway and right blind
 # former doorway/recess. Direction looking west: image-left is station south.
 pw=c['west_portal_width_m'];po=c['west_side_door_offset_m'];sw=c['west_side_door_width_m']
 holes=[(cy-pw/2,cy+pw/2,floor,c['west_portal_head_m']),(cy+po-sw/2,cy+po+sw/2,floor,c['west_side_door_head_m'])]
 pillars=[(cy-pw/2-1.05,1.10),(cy+pw/2+1.05,1.10),(y0+.75,.95),(y1-.75,.95)]
 panels=[(y0+1.5,cy-pw/2-1.75),(cy+pw/2+1.75,y1-1.5)]
 us,zs=cw_wall_grid(y0,y1,holes,pillars,panels,c)
 wallreport['west']=cw_relief_wall('concourse west retained masonry portal wall','x',x1,-1,us,zs,.5,.5,lambda u,z:cw_masonry_cell(u,z,holes,pillars,panels,c,m))
 cw_screen('concourse west retained portal screen and open center','x',x1-.065,-1,cy-pw/2,cy+pw/2,floor,c['west_portal_head_m'],m,True)
 cw_dentils('concourse west end','x',x1,-1,y0,y1,c,m)
 cw_roundel('concourse west end','x',x1-.5,-1,cy,8.91,m['terra'],.24)
 cw_keystone(x1,cy,m['terra'])
 # Both small side features have visible terracotta jambs, cap and shallow
 # pediment. The north feature remains blind rather than inventing a new room.
 for side in [-1,1]:
  u=cy+side*po;lo=floor;top=c['west_side_door_head_m'];plane=x1-.57
  for off in [-sw/2-.13,sw/2+.13]:cw_cube((plane,u+off,(lo+top)/2),(.22,.26,top-lo),m['terra'],'concourse west small opening terracotta jambs')
  for zz,ww,hh,depth in [(top+.10,sw+.52,.20,.24),(top+.28,sw+.74,.15,.34)]:cw_cube((plane-.035,u,zz),(depth,ww,hh),m['terra'],'concourse west small opening profiled lintel')
  if side<0:cw_cube((x1-.522,u,1.29),(.035,sw,1.84),m['terra'],'concourse west observed blind north side feature')
  elif not AGED:cw_cube((x1-.03,u,1.25),(.10,sw-.09,2.22),m['metal'],'concourse west restored small side door leaf')
 # East outlet keeps the exact old public aperture, with wall-head dressing.
 holes=[(c['east_exit_y0_m'],c['east_exit_y1_m'],floor,c['east_exit_head_m'])]
 pillars=[(c['east_exit_y0_m']-.7,1.10),(c['east_exit_y1_m']+.7,1.10)]
 panels=[(y0+.4,c['east_exit_y0_m']-1.35),(c['east_exit_y1_m']+1.35,y1-.4)]
 us,zs=cw_wall_grid(y0,y1,holes,pillars,panels,c)
 wallreport['east']=cw_relief_wall('concourse east masonry with preserved exit portal','x',x0,1,us,zs,.5,.5,lambda u,z:cw_masonry_cell(u,z,holes,pillars,panels,c,m))
 cw_dentils('concourse east end','x',x0,1,y0,y1,c,m)
 # Shallow circulation shell covers new north arcade views; the central lobby
 # remains open. No fit-out, new tenants or hidden room functions are invented.
 if c['include_bounded_north_circulation']:
  ya=c['north_circulation_back_y_m'];yb=y0
  for a,b in [(c['north_circulation_east_limit_x_m'],-11.89),(8.1,x1 if AGED else c['north_circulation_2026_west_limit_x_m'])]:
   cw_cube(((a+b)/2,(ya+yb)/2,.04),(b-a,yb-ya,.20),m['floor'],'concourse north inferred circulation floor outside lobby')
   cw_cube(((a+b)/2,ya-.13,3.95),(b-a,.26,7.62),'Decorative plaster','concourse north unobserved continuation closure')
   cw_cube(((a+b)/2,(ya+yb)/2,7.92),(b-a,yb-ya,.20),'Decorative plaster','concourse north inferred circulation ceiling')
  if not AGED:
   # Reuse the existing former lunch-counter shell, leaving only its inherited
   #6.28cm floor gap to the concourse bridged at that shell's0.10m datum.
   xa=c['north_circulation_2026_west_limit_x_m'];ya_lunch=51.45
   cw_cube(((xa+x1)/2,(ya_lunch+y0)/2,.02),(x1-xa,y0-ya_lunch,.16),m['floor'],'concourse former lunch counter small inherited floor gap')
  # Explicitly close the0.8128m inherited gap between lobby and concourse slab,
  # rather than covering the existing ticket-lobby floor with another surface.
  cw_cube(((-11.89+8.1)/2,(50.7+yb)/2,.04),(19.99,yb-50.7,.20),m['floor'],'concourse ticket interface gap floor')
 if c['include_bounded_west_vestibule']:
  xa=x1+.5;xb=xa+c['west_vestibule_depth_m'];half=pw/2+.5
  cw_cube(((x1+xb)/2,cy,.04),(xb-x1,half*2,.20),m['floor'],'concourse west short plan-supported vestibule floor')
  for y in [cy-half,cy+half]:cw_cube(((xa+xb)/2,y,3.92),(xb-xa,.22,7.56),m['brick'],'concourse west short plan-supported vestibule side walls')
  cw_cube(((xa+xb)/2,cy,7.80),(xb-xa,half*2,.20),'Decorative plaster','concourse west short vestibule ceiling with open far continuation')
 return wallreport

if any(k[0]==_CW_GROUP for k in B):raise ValueError('Concourse walls component already emitted; refuse duplicate integration')
_cw_removed=[]
for _k in list(B):
 if _k[0]==_CW_OLD_GROUP and _k[2] in _CW_OLD_NAMES:_cw_removed.append(_k[2]);del B[_k]
_cw_wallreport=cw_build(CONCOURSE_WALL_CONTROLS)
# Share coincident vertices within each authored material batch. Face-corner UVs
# remain independent at seams; no unused control vertices survive this pass.
for _key,(_vv,_ff,_uv) in list(B.items()):
 if _key[0]!=_CW_GROUP:continue
 _lookup={};_out=[];_remap={}
 for _i,_p in enumerate(_vv):
  _q=tuple(round(v,8) for v in _p)
  if _q not in _lookup:_lookup[_q]=len(_out);_out.append(_q)
  _remap[_i]=_lookup[_q]
 B[_key]=[_out,[tuple(_remap[i] for i in f) for f in _ff],_uv]
_cw_vertices=[v for k,(vv,ff,uu) in B.items() if k[0]==_CW_GROUP for v in vv]
CONCOURSE_WALL_METADATA={
 'era':str(ERA),'controls':_cw_copy(CONCOURSE_WALL_CONTROLS),'group':_CW_GROUP,
 'status':'Evidence-led component reconstruction; inherited metric envelope, photo-relative moldings and floor-band layout; not surveyed as-built',
 'evidence':{'primary':'Railway Age Gazette1914p77: light brick Flemish bond, terracotta panel strips/pilaster caps/bases, west cab entrance',
  'west_screen_count':'Restored post_p48 independently inspected at native1300x867:2side +8center +2side panes; two thicker continuous mullions; sizes approximate',
  'retained_west_shell':'Original1914 plan and HistoricDetroit pre_p20(2010) establish opening and retained metal topology; cannot fix exact2017 condition',
  'restored_geometry':'HistoricDetroit post_p39/post_p48(undated restored), post_p41(August2023), detail_p32(August2023)',
  '2017_condition':'May2017 pre_p27 supports brick/terracotta material character only; exact west-door identity and whole-room damage map unconfirmed'},
 'period_limits':['2017 no restored floor pattern, no added glazing, no modern main door leaves; retained historic grid is a qualified persistence assumption',
  '2026 carries restoration-shell and August2023 floor character forward; does not establish exact October2026 fit-out',
  'All unobserved rooms, services and actual west vestibule-to-carriage alignment remain unresolved; far vestibule end intentionally open',
  'North circulation rear closures are plain extent boundaries for unobserved rooms, not claimed historical partitions',
  'Concentric medallions and upright/splayed lintel UVs are original simplified relief, not exact ornament copies',
  'Floor grid/band widths/chamfers are conservative photo-relative controls, not an exact recovered setting-out drawing'],
 'preserved_interfaces':{'ticket_center_open_x_m':[-7.37235,7.37235],'east_exit_y_m':[59.4,66.2],
  'passenger_center_clear_x_m':[-11.5824,11.5824],'roof':'No roof geometry/material batch is read or replaced',
  'carriage_enclosure_x_m':[52.6288,72.136],'west_vestibule_unobserved_beyond_x_m':CONCOURSE_WALL_CONTROLS['width_m']/2+.5+CONCOURSE_WALL_CONTROLS['west_vestibule_depth_m']},
 'replacement':{'exact_legacy_names':list(_CW_OLD_NAMES),'removed_names':sorted(set(_cw_removed)),
  'bounds_m':[[min(v[i] for v in _cw_vertices),max(v[i] for v in _cw_vertices)] for i in range(3)]},
 'original_assets':'assets/textures/concourse_walls_detail; original deterministic textures, no copyrighted pixels',
 'wall_grids':_cw_wallreport,
}
CONCOURSE_WALL_CAMERAS={
 'concourse_source_eye':{'location':(-23.0,63.4,1.70),'target':(29.3,63.4,5.0),'lens_mm':23},
 'concourse_walls_west':{'location':(-20.,63.25,2.1),'target':(29.35,63.4,4.5),'lens_mm':24},
 'concourse_west_portal':{'location':(16.5,63.4,3.6),'target':(29.45,63.4,4.6),'lens_mm':26},
 'concourse_wall_material':{'location':(20.4,58.4,2.2),'target':(21.8,51.6,3.25),'lens_mm':36},
 'concourse_floor_bands':{'location':(-20.,64.,4.4),'target':(-9.,63.4,.14),'lens_mm':37},
}
CONCOURSE_WALL_UNRESOLVED_CONTINUATIONS=[
 {'id':'west_vestibule_to_carriage','location_m':(CONCOURSE_WALL_CONTROLS['width_m']/2+.5+CONCOURSE_WALL_CONTROLS['west_vestibule_depth_m'],63.4,1.7),'direction':'+X','marker_type':'metadata only; no opaque plane','reason':'Plan establishes vestibule adjacency but its remaining current registration/door fit-out is unresolved'},
 {'id':'north_arcade_side_rooms','plane_y_m':CONCOURSE_WALL_CONTROLS['north_circulation_back_y_m'],'x_spans_m':[(-28.50,-11.89),(8.1,29.4894 if AGED else 24.70)],'marker_type':'plain bounded shell closure','reason':'Existing2026 lunch-counter shell reused forX24.70..29.4894 with onlyY51.45..51.5128 floor gap bridged; no hidden tenant rooms or furnishings reconstructed; rear closure minY48.74 is beyond documented Neighbor frontageY48.52; complete suite boundary unknown'},
 {'id':'yellow_light_rear_registration_notch','x_span_m':[-29.4894,-28.50],'y_span_m':[48.52,51.88],'marker_type':'metadata only; new circulation shell omitted in this strip','reason':'Avoid Yellow Light HNS rear service envelopeX-33.57..-28.63,Y48.52..51.88; its overlap with the inherited concourse datum is a0.3-0.6m registration uncertainty, not an exact shared wall'}]
CONCOURSE_WALL_METADATA['unresolved_continuations']=_cw_copy(CONCOURSE_WALL_UNRESOLVED_CONTINUATIONS)
# Directly compatible with build_station.py cams.update: no hidden adapter.
CONCOURSE_WALL_CAMERAS={name:(v['location'],v['target'],v['lens_mm']) for name,v in CONCOURSE_WALL_CAMERAS.items()}
GROUP=_CW_SAVED_GROUP
