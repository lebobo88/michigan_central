"""Colonnade-front decorated lunettes and deep reveals, photo-informed revision.
Historic north outer glass stays21ft wide. Vertical controls below are an explicit
compatible modeling trial, not a reconciliation of the54/62/65ft source conflict.
The selected side crown17.2m is inferred from near-half-round front mouths and
published11ft cartouches; the prior16.16m was only a formula-derived assumption.
"""
_HL_GROUP=GROUP;GROUP='03 GREAT HALL | three sail vaults and colonnades'
HALL_LUNETTE_CONTROLS=dict(front_sill_m=9.55,boundary_crown_m=17.20,north_front_width_m=8.0,north_front_rise_m=4.0,south_front_width_m=8.6,south_front_rise_m=3.75,south_rear_width_m=7.6,south_rear_rise_m=3.45,north_front_y_m=3.9,south_front_y_m=27.7,north_rear_y_m=.525,south_rear_y_m=31.15,cartouche_height_m=3.3528,status='Photo-informed compatible comparison trial; not surveyed')
HALL_LUNETTE_CONTROLS.update(globals().get('HALL_LUNETTE_PARAMETERS',{}))
_HC=HALL_LUNETTE_CONTROLS

def hl_solid_profile(points,y0,y1,m,name):
 # Closed extruded X/Z profile with distinct cap/side UVs and no collapsed corners.
 pp=[]
 for p in points:
  if not pp or math.dist(p,pp[-1])>1e-6:pp.append(p)
 if len(pp)>2 and math.dist(pp[0],pp[-1])<1e-6:pp.pop()
 if len(pp)<3:return
 if sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(pp,pp[1:]+pp[:1]))<0:pp.reverse()
 n=len(pp);vv=[(x,y,z) for y in [y0,y1] for x,z in pp]
 # X/Z counterclockwise points to-Y, hence the near cap follows the profile.
 ff=[tuple(range(n)),tuple(range(n*2-1,n-1,-1))];uu=[pp,list(reversed(pp))]
 for i in range(n):
  j=(i+1)%n;ff.append((i,j,j+n,i+n));l=math.dist(pp[i],pp[j]);uu.append([(0,y0),(l,y0),(l,y1),(0,y1)])
 addmesh(vv,ff,m,name,face_uv=uu)

def hl_front_field(xa,xb,cx,y,face,ww,rise,field_material):
 base=_HC['front_sill_m'];hx=(xb-xa)/2;mid=(xa+xb)/2;outer=_HC['boundary_crown_m']-base
 # Dense source-safe strips make a continuous closed field without Boolean holes.
 xs=sorted(set([xa+(xb-xa)*i/112 for i in range(113)]+[cx-ww/2,cx+ww/2]))
 for left,right in zip(xs,xs[1:]):
  if right-left<1e-5:continue
  def z(x):
   q=max(0,1-((x-mid)/hx)**2);q=0 if q<1e-10 else q
   top=base+outer*sqrt(q)
   bot=base+rise*sqrt(max(0,1-((x-cx)/(ww/2))**2)) if abs(x-cx)<ww/2 else base
   return min(bot,top),top
  b0,t0=z(left);b1,t1=z(right)
  hl_solid_profile([(left,b0),(right,b1),(right,t1),(left,t0)],y-.18,y+.18,field_material,'hall vertical decorated spandrel field')
 # Nested carved profiles return toward a deep opening; they never lie on glass.
 for off,thick,dep in ([(0,.12,.17)] if AGED and face<0 else [(0,.20,.30),(.23,.095,.23),(.39,.065,.19),(.53,.055,.15)]):
  arch(cx,y+face*(.12+dep/2),base,ww+2*off,rise+off,thick,dep,field_material if AGED and face<0 else PL,'hall nested plaster opening archivolts',64)
 # Outer rim follows the actual new boundary arch, not a decal on the sail tile.
 arch(mid,y+face*.07,base,xb-xa,outer,.15,.23,field_material if AGED and face<0 else PL,'hall decorated field outer rim',80)

def hl_reveal(cx,yfront,yrear,frontwidth,frontrise,rearwidth,rearspring,rearrise,face):
 base=_HC['front_sill_m'];n=80;v=[];u=[]
 for j in range(9):
  t=j/8;yy=yfront+(yrear-yfront)*t;ww=frontwidth+(rearwidth-frontwidth)*t;rr=frontrise+(rearrise-frontrise)*t;zz=base+(rearspring-base)*t
  for i in range(n+1):
   a=pi*i/n;v.append((cx+ww/2*cos(a),yy,zz+rr*sin(a)));u.append((a*(ww/2+rr)/2,abs(yrear-yfront)*t))
 f=[]
 for j in range(8):
  for i in range(n):
   a=j*(n+1)+i;f.append((a+1,a,a+n+1,a+n+2) if face>0 else (a,a+1,a+n+2,a+n+1))
 addmesh(v,f,PL,'hall deep arched plaster reveal',uv=u)
 # The photographed lower alcove has a coffered flat ceiling behind the beam.
 # Only side fields outside the glass opening are closed here.
 for side in [-1,1]:
  aa=cx+side*frontwidth/2;bb=cx+side*rearwidth/2
  if rearspring-base>1e-5:
   # Close only the triangular spring-level return above the cornice. A solid
   # floor-height wall here would wrongly bury the freestanding north columns.
   v0=[(aa,yfront,base),(bb,yrear,rearspring),(bb,yrear,base)]
   vv=v0+[(x+side*.20,y,z) for x,y,z in v0]
   ff=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
   if side>0:ff=[tuple(reversed(f)) for f in ff]
   addmesh(vv,ff,PL,'hall north reveal triangular spring infill')

def hl_south_glazing(cx,y,width,rise):
 base=_HC['front_sill_m'];n=64;v=[(cx-width/2,y,base),(cx+width/2,y,base)]+[(cx+width/2*cos(pi*i/n),y,base+rise*sin(pi*i/n)) for i in range(1,n)]
 addmesh(v,[tuple(range(len(v)))],'Glass clear','south hall rear elliptical clerestory glazing')
 arch(cx,y-.025,base,width,rise,.095,.16,'Window cast iron','south hall rear clerestory frame',64)
 box((cx,y-.025,base+.025),(width,.16,.06),'Window cast iron','south hall rear clerestory sill')
 for i in range(1,13):
  dx=-width/2+width*i/13;h=rise*sqrt(max(0,1-(dx/(width/2))**2));box((cx+dx,y-.035,base+h/2),(.047,.13,h),'Window cast iron','south hall rear clerestory mullions')
 for h in [.75,1.50,2.25,3.0]:
  if h>=rise:continue
  span=width*sqrt(max(0,1-(h/rise)**2));box((cx,y-.04,base+h),(span,.13,.045),'Window cast iron','south hall rear clerestory transoms')

HALL_CARTOUCHE_METADATA=[]
HALL_CARTOUCHE_COVERAGE=[]
for xa,xb,cx in [(-31.8,-10,-20),(-10,10,0),(10,31.8,20)]:
 for side in ['north','south']:
  face=1 if side=='north' else -1;front=_HC[side+'_front_y_m'];rear=_HC[side+'_rear_y_m'];ww=_HC[side+'_front_width_m'];rise=_HC[side+'_front_rise_m']
  hl_front_field(xa,xb,cx,front,face,ww,rise,'Mixed 2017 hall backing' if AGED and side=='south' else HALL_WALL_PLASTER)
  if side=='north':rw=6.4008;rs=1.3+12.192-rw/2;rr=rw/2
  else:rw=_HC['south_rear_width_m'];rs=_HC['front_sill_m'];rr=_HC['south_rear_rise_m'];hl_south_glazing(cx,rear-.08,rw,rr)
  hl_reveal(cx,front,rear,ww,rise,rw,rs,rr,face)
  if not AGED:
   # North border sits just inside the existing facade glass; south joins its new rear frame.
   hall_window_tracery(cx,-.43 if side=='north' else rear-.125,rs,rw,rr,face)
  # Hidden aisle crown closure slopes down to the outer envelope; it is behind
  # the vertical decorated front rather than an exposed strip before that wall.
  vv=[];fu=[];n=80
  for yy,height in [(front,_HC['boundary_crown_m']),(rear,15.55)]:
   for i in range(n+1):
    t=pi*i/n;vv.append(((xa+xb)/2+(xb-xa)/2*cos(t),yy,_HC['front_sill_m']+(height-_HC['front_sill_m'])*sin(t)))
  ff=[(i,i+1,n+2+i,n+1+i) for i in range(n)];fu=[[(i,0),(i+1,0),(i+1,abs(rear-front)),(i,abs(rear-front))] for i in range(n)]
  addmesh(vv,ff,PL,'hall concealed aisle crown closure',face_uv=fu)
  # South back wall is a distinct plane behind the reveal. Lower alcove/core
  # walls are caller-owned and remain in their documented historical locations.
  if side=='south':
   xs=sorted(set([xa+(xb-xa)*i/80 for i in range(81)]+[cx-rw/2,cx+rw/2]))
   for _hl_left,_hl_right in zip(xs,xs[1:]):
    def bottom(x):return rs+rr*sqrt(max(0,1-((x-cx)/(rw/2))**2)) if abs(x-cx)<rw/2 else rs
    hl_solid_profile([(_hl_left,bottom(_hl_left)),(_hl_right,bottom(_hl_right)),(_hl_right,15.7),(_hl_left,15.7)],rear-.16,rear+.18,HALL_WALL_PLASTER,'south hall rear upper backing wall')
  if AGED:
   state='retained modeled' if side=='north' and cx==0 else 'documented absence' if side=='south' and cx in [0,20] else 'unobserved full extent; omitted'
   HALL_CARTOUCHE_COVERAGE.append(dict(side=side,center_x_m=cx,state=state,source='Historic Detroit May2017 pre_p6/pre_p16',note='Partly visible is not evidence of partial loss'))
  if not AGED or (side=='north' and cx==0):
   bottom=_HC['front_sill_m']+rise+.15
   HALL_CARTOUCHE_METADATA.append(hall_cartouche(cx,front+face*.20,bottom,_HC['cartouche_height_m'],face,PL))
scene['hall_lunette_controls']=json.dumps(_HC)
scene['hall_cartouche_metadata']=json.dumps(HALL_CARTOUCHE_METADATA)
scene['hall_cartouche_coverage']=json.dumps(HALL_CARTOUCHE_COVERAGE)
HALL_LUNETTE_CAMERAS={'hall_south_lunette':((0,9.0,8.5),(0,27.7,12.5),28),'hall_north_lunette':((0,23.0,8.5),(0,3.9,12.6),28),'hall_southeast_bay_ground':((-20,9.0,1.7),(-20,27.7,8.2),25),'hall_north_bay_ground':((0,23.0,1.7),(0,3.9,8.2),25)}
GROUP=_HL_GROUP
