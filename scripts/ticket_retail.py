"""Ticket-lobby retail evidence module for build_station.py's batching namespace.
Original mesh geometry only. Source photographs are NOT loaded or redistributed.
2026 only: The Shop's documented frontage and qualified single-view merchandise
vignette; Neighbor's photographed west-facing entrance and bounded view fragment.
No complete suite or hidden back-of-house is asserted. See ticket_retail_evidence.json.
"""
TICKET_RETAIL_CAMERAS = {
 'ticket_shop_front':((-3.6,40.6,1.78),(8.04,40.6,3.55),27),
 'ticket_shop_detail':((5.40,43.05,1.72),(8.4,40.4,2.05),23),
 'ticket_shop_vignette':((8.90,42.25,1.70),(12.0,39.1,1.75),22),
 'ticket_neighbor_front':((-5.60,46.30,1.72),(-12.8,46.1,2.10),31),
 'ticket_neighbor_threshold':((-9.80,45.60,1.68),(-13.5,46.3,1.73),28),
}
TICKET_RETAIL_METADATA = {
 'period':'2026 public-use interpretation using 2024-2026 documented views',
 'shop':{'front_plane_x':8.10,'front_y':[34.25,46.95],'entry_y':40.60,
         'photographed_vignette_bounds':[8.50,13.65,37.95,43.25],
         'fitout_date':'Owner photo upload December 2024; current continuation unverified',
         'scope':'Central entrance, four visible ticket-window bays, clock; one photographed fixture corner, re-sited interpretively behind entrance',
         'omitted':'Complete ticket-office shell, private rooms, copied wall-art graphics, unseen fixtures'},
 'neighbor':{'front_plane_x':-11.89,'front_y':[43.36,48.52],'entry_y':46.05,
             'photographed_view_bounds':[-15.75,-11.89,44.75,47.35],
             'fitout_date':'Official entrance image filename January 21 2026',
             'scope':'West-facing doorway, paired stone pilasters, open timber doors, labeled transom, visible pegboard shelf/counter, pendant and plants',
             'omitted':'Complete suite footprint, all hidden rooms, 2024 Latent proposal furniture',
             'registration':'HNS raster shell position; original pixel x714 y700..769; +/-0.3-0.6m; doorway Y photo-proportioned'},
 'no_2017_fitout':True,
 'copyright':'Original geometric approximations and font lettering only. No source pixels or third-party graphics.',
 'dimensions':'All fixture dimensions photo-proportioned, not measured or current as-built documentation',
}


def _build_ticket_retail():
 global GROUP
 _saved_group=GROUP
 try:
  # Solid PBR values and existing authored maps survive interchange export.
  specs=[('TR pale birch',(.64,.56,.42),.54,0),('TR translucent rib panel',(.68,.68,.59),.41,0),
   ('TR charcoal ceiling',(.022,.030,.039),.82,0),('TR light gray concrete',(.40,.385,.34),.80,0),
   ('TR warm cream',(.83,.77,.63),.56,0),('TR amber cane',(.38,.205,.057),.59,0),
   ('TR muted terracotta',(.51,.16,.075),.72,0),('TR sage package',(.16,.30,.19),.62,0),
   ('TR mustard package',(.77,.48,.045),.63,0),('TR teal package',(.015,.40,.38),.56,0),
   ('TR cobalt package',(.019,.065,.37),.52,0),('TR coral package',(.62,.07,.048),.57,0),
   ('TR white package',(.85,.85,.77),.68,0),('TR bronze label',(.54,.36,.12),.32,.67),
   ('TR clock porcelain',(.87,.83,.69),.31,0),('TR plant pot',(.025,.028,.025),.57,.1)]
  for n,c,r,metal in specs:
   if n not in M:mat(n,c,r,metal)
  if 'TR neutral lamp' not in M:mat('TR neutral lamp',(1,.91,.75),.3,0,0,5)
  if 'TR exit red' not in M:mat('TR exit red',(1,.025,.005),.3,0,0,3)
  pale='TR pale birch';metal='Dark bronze';stone='Warm Mankato column stone';plaster='Decorative plaster'

  def space(prefix,front,cy,direction):
   # direction+1: west shop; direction-1: east Neighbor. u=screen right,
   # v=distance behind threshold; positive z=up. This transform is right-handed.
   def P(u,v,z):return (front+direction*v,cy-direction*u,z)
   def bx(c,s,m,n):box(P(*c),(s[1],s[0],s[2]),m,prefix+' '+n)
   def bm(p,q,r,m,n,segments=8):beam(P(*p),P(*q),r,m,prefix+' '+n,segments)
   def am(v,f,m,n,uv=None):addmesh([P(*p) for p in v],f,m,prefix+' '+n,uv)
   def lt(c,profile,m,n,segments=32):lathe(P(*c),profile,m,prefix+' '+n,segments)
   def textmesh(txt,loc,size,m,n,spacing=1):
    cu=bpy.data.curves.new('temporary retail font','FONT');cu.body=txt;cu.size=size;cu.align_x='CENTER';cu.space_character=spacing;cu.extrude=.0007;cu.resolution_u=3
    ob=bpy.data.objects.new('temporary retail font',cu);scene.collection.objects.link(ob)
    deps=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(deps);me=ev.to_mesh()
    vv=[P(loc[0]+p.co.x,loc[1]-p.co.z,loc[2]+p.co.y) for p in me.vertices];ff=[tuple(p.vertices) for p in me.polygons]
    addmesh(vv,ff,m,prefix+' '+n);ev.to_mesh_clear();bpy.data.objects.remove(ob,do_unlink=True);bpy.data.curves.remove(cu)
   def disk(u,v,z,r,m,n,segments=48):
    vv=[(u,v,z)]+[(u+r*cos(2*pi*j/segments),v,z+r*sin(2*pi*j/segments)) for j in range(segments)]
    am(vv,[(0,j+1,(j+1)%segments+1) for j in range(segments)],m,n)
   def circle(u,v,z,r,t,m,n,segments=64):
    # A shallow annular extrusion in the frontage plane, all faces nondegenerate.
    vv=[(u+rr*cos(2*pi*j/segments),vv,z+rr*sin(2*pi*j/segments)) for vv in [v,v+.024] for rr in [r-t/2,r+t/2] for j in range(segments)]
    ff=[];k=segments
    for j in range(k):
     q=(j+1)%k;ff.extend([(j,q,k+q,k+j),(2*k+j,3*k+j,3*k+q,2*k+q),(j,2*k+j,2*k+q,q),(k+j,k+q,3*k+q,3*k+j)])
    am(vv,ff,m,n)
   def profile_strip(u,w,profile,m,n):
    # Projecting horizontal molding with an explicit section in v,z.
    vv=[(u+side*w/2,v,z) for side in [-1,1] for v,z in profile];k=len(profile)
    ff=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
    am(vv,ff,m,n)
   def shelf(u,v,z,width,height,depth,levels=4,back=True):
    for du in [-width/2,width/2]:bx((u+du,v,z+height/2),(.05,depth,height),pale,'display shelving side panel')
    if back:bx((u,v+depth/2-.018,z+height/2),(width,.035,height),'TR translucent rib panel','display shelving back panel')
    for j in range(levels):bx((u,v,z+.10+j*(height-.20)/(levels-1)),(width,depth,.040),pale,'display shelving boards')
   def books(u,v,z,count=7):
    colors=['TR sage package','TR white package','TR coral package','TR teal package','Wood walnut']
    for j in range(count):
     h=.18+.035*(j%3);bx((u+(j-(count-1)/2)*.065,v,z+h/2),(.047,.145,h),colors[j%len(colors)],'unbranded book spines')
   def bottles(u,v,z,count=6):
    for j in range(count):
     lt((u+(j-(count-1)/2)*.12,v,z),[(.034,0),(.037,.018),(.037,.21),(.016,.24),(.016,.30)],'TR sage package','unbranded bottles',12)
     bx((u+(j-(count-1)/2)*.12,v-.038,z+.12),(.049,.004,.065),'TR warm cream','plain bottle labels')
   def plant(u,v,z,height=.95):
    lt((u,v,z),[(.16,0),(.20,.025),(.235,.28),(.225,.33)],'TR plant pot','black planter',24)
    for j in range(9):
     theta=j*2.399;top=z+.40+height*(.58+.04*(j%4));uu=u+.22*cos(theta);vv=v+.22*sin(theta)
     bm((u,v,z+.25),(uu,vv,top),.009,'Foliage','plant stems',5)
     for k in range(3):
      za=top-.13*k;scale=.16+.035*((j+k)%3);angle=theta+k*.8
      a=(uu,vv,za);b=(uu+scale*cos(angle),vv+scale*sin(angle),za+.11);c=(uu+scale*.40*cos(angle)-.065*sin(angle),vv+scale*.40*sin(angle)+.065*cos(angle),za+.05);d=(uu+scale*.40*cos(angle)+.065*sin(angle),vv+scale*.40*sin(angle)-.065*cos(angle),za+.05)
      am([a,c,b,d],[(0,1,2,3)],'Foliage','broad plant leaves')
   return P,bx,bm,am,lt,textmesh,disk,circle,profile_strip,shelf,books,bottles,plant

  GROUP='21 THE SHOP | documented frontage and qualified 2024 view fragment'
  P,bx,bm,am,lt,txt,disk,circle,molding,shelf,books,bottles,plant=space('The Shop',8.10,40.60,1)
  # Only the documented central frontage cluster is replaced. Wider historic
  # service-window counts and exact fixture spacing remain outside this module.
  # Apertures: central1.50m entrance, four1.25m ticket windows, 2.10m centers.
  front_min,front_max=-6.35,6.35
  windows=[-4.85,-2.65,2.65,4.85]
  apertures=[(u,1.25,.94,2.89) for u in windows]+[(0,1.50,.13,3.03)]
  cursor=front_min
  for u,w,zlo,zhi in sorted(apertures):
   left,right=u-w/2,u+w/2
   if left>cursor:bx(((cursor+left)/2,0,1.76),(left-cursor,.42,3.52),plaster,'historic pale stone frontage piers')
   if zlo>.13:bx((u,0,(zlo+.13)/2),(w,.42,zlo-.13),stone,'ticket counter stone dado')
   bx((u,0,(zhi+3.52)/2),(w,.42,3.52-zhi),plaster,'historic frontage lintel infill')
   cursor=right
  if cursor<front_max:bx(((cursor+front_max)/2,0,1.76),(front_max-cursor,.42,3.52),plaster,'historic frontage piers')
  # End/piers have profile-scaled pilasters, not a fabricated retail wall.
  for u in [-5.72,-3.75,-1.31,1.31,3.75,5.72]:
   bx((u,-.255,1.96),(.22,.18,2.92),stone,'flat frontage pilaster shafts')
   for zz,ww,dd,hh in [(.33,.34,.24,.20),(.47,.29,.22,.10),(3.31,.33,.24,.12),(3.42,.39,.29,.08)]:bx((u,-.27,zz),(ww,dd,hh),stone,'frontage pilaster base and capital')
  molding(0,12.8,[(-.25,3.49),(-.39,3.49),(-.39,3.56),(-.45,3.59),(-.45,3.69),(-.23,3.69)],stone,'continuous ticket entablature lower molding')
  bx((0,-.24,3.85),(12.85,.48,.32),plaster,'continuous pale stone name fascia')
  molding(0,13.02,[(-.20,4.01),(-.44,4.01),(-.45,4.07),(-.53,4.11),(-.53,4.22),(-.16,4.22)],stone,'projecting ticket cornice')
  txt('THE SHOP',(0,-.492,3.795),.20,metal,'current simple THE SHOP letters',1.24)
  for u in [-2.1,2.1]:disk(u,-.49,3.90,.043,metal,'fascia round dark fixing',16)
  # Service windows: visible dark border, open grille and rose marble shelf.
  for u in windows:
   for du in [-.65,.65]:bx((u+du,-.24,1.94),(.09,.13,2.00),metal,'ticket-window metal frame')
   for zz in [1.00,2.88]:bx((u,-.24,zz),(1.38,.13,.085),metal,'ticket-window horizontal frame')
   bx((u,-.38,.96),(1.70,.62,.12),'Rose Tennessee marble','rose-marble ticket counter')
   # Single-plane open quatrefoil lattice, original mathematical geometry.
   for col in range(7):
    for row in range(10):
     uu=u-.51+col*.17;zz=1.15+row*.17
     count=20;vv=[]
     for rr in [.070,.053]:
      for j in range(count):
       a=2*pi*j/count;r=rr*(1+.19*cos(4*a));vv.append((uu+r*cos(a),-.305,zz+r*sin(a)))
     am(vv,[(j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count)],metal,'open ornamental ticket grille')
   for du in [-.76,.76]:
    bx((u+du,-.16,1.97),(.07,.07,2.08),stone,'ticket aperture stone bead')
   bx((u,-.16,3.035),(1.60,.07,.085),stone,'ticket aperture lintel bead')
  # Central opening and threshold remain passable, no dark fake-glass closure.
  for u in [-.79,.79]:bx((u,-.04,1.58),(.10,.36,2.92),stone,'central entrance reveal jamb')
  bx((0,.13,.15),(1.48,.66,.035),'Pale rose marble','central shop threshold')
  # Recreated clock: published housing size roughly8ft wide by6ft tall.
  cz=5.13
  bx((0,-.33,4.54),(1.92,.32,.65),'Wood walnut','clock lower timber housing')
  # Half-arched upper silhouette with original geometric outline.
  vv=[(-1.03,-.50,4.28),(1.03,-.50,4.28),(1.03,-.50,5.16)]
  vv += [(1.03*cos(pi*j/40),-.50,5.16+1.00*sin(pi*j/40)) for j in range(1,41)]
  am(vv,[tuple(range(len(vv)))],'Wood walnut','clock curved timber case silhouette')
  for u in [-1.08,1.08]:
   bx((u,-.34,4.77),(.11,.35,1.11),'Wood walnut','clock housing side post')
   molding(u,.20,[(-.18,4.18),(-.46,4.18),(-.46,4.30),(-.39,4.41),(-.18,4.41)],'Wood walnut','clock base feet')
  for u in [-1.15,1.15]:bx((u,-.35,5.35),(.14,.40,.16),'Wood walnut','clock side shoulder')
  circle(0,-.533,cz,.918,.062,'Wood walnut','clock outer timber ring')
  disk(0,-.549,cz,.861,'TR clock porcelain','clock pale dial')
  circle(0,-.563,cz,.749,.158,metal,'clock dark numeral annulus')
  for j in range(12):
   a=pi/2-j*2*pi/12;u=.744*cos(a);z=cz+.744*sin(a)
   disk(u,-.582,z,.080,'TR clock porcelain','clock numeral medallions',24)
   txt(str(12 if j==0 else j),(u,-.586,z-.038),.106,metal,'clock Arabic numeral geometry')
  for j in range(60):
   a=2*pi*j/60;r0=.613;r1=.638 if j%5 else .647
   bm((r0*cos(a),-.593,cz+r0*sin(a)),(r1*cos(a),-.593,cz+r1*sin(a)),.005,metal,'clock minute ticks',4)
  for a,r,w in [(pi/3,.54,.033),(pi*5/6,.39,.038)]:bm((0,-.608,cz),(r*cos(a),-.608,cz+r*sin(a)),w,metal,'clock hands illustrative static time',6)
  disk(0,-.646,cz,.052,metal,'clock hand hub',24)
  # Gentle stone blind arch behind clock, spans only evidenced center bay.
  for radius in [2.18,2.29,2.40]:
   for j in range(48):
    a=pi*j/48;b=pi*(j+1)/48
    bm((radius*cos(a),-.365,4.27+radius*sin(a)),(radius*cos(b),-.365,4.27+radius*sin(b)),.041,stone,'blind clock niche concentric archivolt',6)

  # Qualified merchandising vignette. Source image shows one corner only;
  # position and extent are representative behind the observed central entry.
  # No walls are added beyond the 5.1x5.3m illustrated patch.
  GROUP='22 THE SHOP | qualified photo-corner vignette, no full suite layout'
  bx((0,2.95,.10),(5.30,5.10,.12),'TR light gray concrete','limited vignette floor patch')
  bx((0,2.95,3.16),(5.30,5.10,.075),'TR charcoal ceiling','observed dark ceiling patch')
  # Ceilings and lighting geometry follow the photo material class, not a MEP plan.
  for u in [-2.0,-.8,.4,1.6]:bx((u,2.95,3.113),(.010,5.1,.007),metal,'dark ceiling panel joints')
  for v in [1.05,2.25,3.45,4.65]:bx((0,v,3.111),(5.30,.009,.008),metal,'ceiling cross joints')
  for u in [-1.23,1.03]:
   for v in [1.72,4.02]:
    bm((u,v,3.10),(u,v,2.72),.005,metal,'linear pendant suspension')
   bx((u,2.88,2.70),(.075,2.36,.075),'TR charcoal ceiling','linear pendant body')
   bx((u,2.88,2.657),(.054,2.31,.008),'TR neutral lamp','linear pendant diffuser')
  for u in [-2.35,2.35]:
   bx((u,2.95,2.99),(.034,4.40,.045),metal,'ceiling track')
   for v in [1.15,2.2,3.25,4.3]:
    bm((u,v,2.98),(u,v,2.84),.015,metal,'adjustable track light stalk')
    lt((u,v,2.76),[(.041,0),(.044,.075)],metal,'track light barrel',16)
    lt((u,v,2.754),[(.035,0),(.035,.004)],'TR neutral lamp','track light lens',16)
  # Documented back-wall surface patch only; source collage imagery is omitted.
  bx((0,5.19,1.62),(5.30,.035,3.0),'TR warm cream','observed back-wall fragment without copied art')
  # Two visible rear display modules with subtly ribbed translucent infills.
  for u in [-1.45,.35]:
   shelf(u,4.91,.15,1.48,2.58,.34,4,True)
   for j in range(56):bx((u-.70+j*.0255,5.068,1.45),(.004,.010,2.48),'TR warm cream','subtle vertical translucent panel ribs')
   for zz in [.34,.95,1.66]:books(u,4.78,zz,9)
  # A perpendicular pale shelf fragment creates the photo's documented corner.
  # Generic packages substitute products, with no reproduced branding or artwork.
  for zz in [.26,.85,1.45,2.04]:
   bx((2.45,4.05,zz),(.38,1.63,.043),pale,'right corner shelf boards')
   for j in range(5):bx((2.36,3.44+j*.26,zz+.14),(.18,.20,.25),['TR teal package','TR white package','TR coral package'][j%3],'unbranded right shelf packages')
  for v in [3.21,4.89]:bx((2.45,v,1.45),(.38,.065,2.70),pale,'right corner shelf uprights')
  # Historic wall collage intentionally omitted; plain backing is only a marker
  # for the observed occupied surface, never a substitute invented graphic.
  bx((2.635,4.10,1.64),(.028,1.95,2.80),'TR warm cream','unresolved wall-art surface plain backing')
  # Central two-sided merchandising table/bookcase pair observed in owner image.
  for u in [-.80,.80]:
   for du in [-.67,.67]:bx((u+du,2.40,.68),(.065,1.15,1.10),pale,'central display table ends')
   bx((u,2.40,1.24),(1.42,1.20,.045),pale,'central merchandise table top')
   for zz in [.18,.67]:bx((u,2.40,zz),(1.37,1.13,.044),pale,'central merchandise table shelf')
   for zz in [.20,.69]:
    books(u,2.04,zz,10)
   for j in range(3):bx((u-.36+j*.33,2.29,1.30+j*.021),(.25,.32,.095),['TR sage package','TR white package','TR coral package'][j],'generic stacked merchandise')
  # Hanging garment rack, with simple original T-shirt silhouettes.
  bm((-1.22,4.02,.18),(-1.22,4.02,1.80),.019,metal,'garment rail standards')
  bm((.38,4.02,.18),(.38,4.02,1.80),.019,metal,'garment rail standards')
  bm((-1.22,4.02,1.80),(.38,4.02,1.80),.019,metal,'garment hanging rail')
  for j in range(6):
   u=-1.06+j*.23;garment_v=3.89+j*.033;c=['TR mustard package','TR white package','TR coral package','TR cobalt package'][j%4]
   am([(u-.13,garment_v,1.69),(u-.26,garment_v,1.54),(u-.18,garment_v,1.41),(u-.12,garment_v,1.48),(u-.12,garment_v,1.08),(u+.12,garment_v,1.08),(u+.12,garment_v,1.48),(u+.18,garment_v,1.41),(u+.26,garment_v,1.54),(u+.13,garment_v,1.69)],[(0,1,2,3,4,5,6,7,8,9)],c,'unbranded garment silhouette')
   bm((u-.13,4.01,1.70),(u,4.01,1.78),.004,metal,'clothes hangers',4);bm((u,4.01,1.78),(u+.13,4.01,1.70),.004,metal,'clothes hangers',4)

  GROUP='23 NEIGHBOR | 2026 photographed west-facing doorway and limited view'
  P,bx,bm,am,lt,txt,disk,circle,molding,shelf,books,bottles,plant=space('Neighbor',-11.89,46.05,-1)
  # Five-meter facade fragment extends from arcade south wall to concourse side.
  for u,w in [(-1.94,1.50),(1.83,1.28)]:bx((u,0,3.44),(w,.40,6.62),plaster,'documented front stone wall fragment')
  bx((0,0,4.95),(2.55,.40,3.60),plaster,'doorway overhead stone wall')
  for u in [-1.39,1.39,-2.22]:
   bx((u,-.26,3.59),(.40,.19,5.85),stone,'historic paired pilaster shafts')
   bx((u,-.27,.43),(.64,.31,.61),'Pale rose marble','pilaster stone plinths')
   molding(u,.66,[(-.12,.70),(-.43,.70),(-.46,.76),(-.44,.82),(-.30,.88),(-.38,.94),(-.38,1.03),(-.12,1.03)],stone,'pilaster torus and scotia profile')
   for zz,ww,hh in [(6.51,.53,.10),(6.63,.65,.13)]:bx((u,-.27,zz),(ww,.29,hh),stone,'pilaster capital molding')
  # Rectangular lintel with stepped architrave; photo shows no arch at this door.
  for zz,ww,dd,hh in [(3.38,2.64,.45,.15),(3.56,2.87,.49,.17),(3.70,3.02,.55,.11)]:bx((0,-.13,zz),(ww,dd,hh),stone,'door head stone architrave')
  for u in [-1.085,1.085]:bx((u,-.115,1.69),(.15,.15,3.10),'Wood walnut','dark timber outer doorway jamb')
  for zz in [2.64,3.15,3.23]:bx((0,-.12,zz),(2.27,.16,.105),'Wood walnut','dark timber transom rails')
  bx((0,-.13,2.91),(2.11,.075,.46),'Wood walnut','dark transom sign backing')
  bx((0,-.180,2.918),(1.92,.012,.233),'TR bronze label','simple brass-colored transom label')
  for zz in [2.809,3.026]:bx((0,-.190,zz),(1.88,.006,.009),metal,'transom label keyline')
  txt('NEIGHBOR x FOLK',(0,-.197,2.863),.131,metal,'original-font NEIGHBOR x FOLK lettering',1.14)
  # Two open leaves, each with the photograph's three narrow upper glazing slots,
  # dividing rail and lower timber panel. Open angle is photo-proportioned.
  def door_leaf(sign):
   hinge=sign*1.01;angle=math.radians(69);length=.98
   def D(t,v,z):return (hinge-sign*t*cos(angle)+v*sin(angle),-t*sin(angle)-sign*v*cos(angle),z)
   def db(c,s,m,n):
    u,v,z=c;du,dv,dz=[p/2 for p in s];vv=[D(u+a*du,v+b*dv,z+c*dz) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    am(vv,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m,n)
   for t in [.075,.905]:db((t,0,1.38),(.15,.060,2.48),'Wood walnut','open timber door stiles')
   for zz,hh in [(.21,.14),(.71,.20),(2.49,.17),(1.95,.06)]:db((length/2,0,zz),(length,.060,hh),'Wood walnut','open timber door cross rails')
   db((length/2,.018,.44),(.68,.022,.35),'Wood walnut','open door recessed lower panel')
   for t in [.36,.65]:db((t,0,1.60),(.028,.060,1.53),'Wood walnut','narrow glazed-slot vertical mullions')
   for t in [.245,.505,.765]:db((t,.012,1.59),(.22,.008,1.49),'Glass clear','open door clear glazing slots')
   bm(D(.83,-.07,1.14),D(.83,-.07,1.34),.013,metal,'door pull')
   for zz in [.39,1.38,2.31]:bm(D(0,0,zz),D(0,0,zz+.075),.017,metal,'door hinges',8)
  for sign in [-1,1]:door_leaf(sign)
  bx((0,.04,.145),(2.08,.60,.030),'Pale rose marble','stone entry threshold')
  # Visible view fragment only, not a closure defining the true room perimeter.
  bx((0,2.03,.10),(2.65,3.86,.10),'TR light gray concrete','doorway-view floor fragment')
  # Perforated pale timber merchandise counter visible immediately beyond door.
  # Front face uses actual circular holes, no copied photo/alpha mask.
  bx((.25,1.95,.20),(1.95,.68,.10),pale,'retail counter plinth')
  bx((.25,1.95,1.05),(2.04,.74,.06),pale,'retail counter top')
  for u in [-.76,1.26]:bx((u,1.95,.61),(.055,.71,.82),pale,'retail counter end panels')
  vv=[];ff=[];pitch=.095;n=12
  for iz in range(8):
   for ix in range(20):
    cu=-.70+(ix+.5)*pitch;cz=.24+(iz+.5)*pitch;start=len(vv)
    for mode in ['square','hole']:
     for j in range(n):
      a=2*pi*j/n;cs,sn=cos(a),sin(a);r=pitch/2/max(abs(cs),abs(sn)) if mode=='square' else .0105
      vv.append((cu+r*cs,1.57,cz+r*sn))
    for j in range(n):ff.append((start+j,start+(j+1)%n,start+n+(j+1)%n,start+n+j))
  am(vv,ff,pale,'visible pegboard counter face with true holes')
  # Source shows a rear-left labeled pantry shelf and right merchandise shelves.
  for u in [-.73,.86]:
   shelf(u,3.35,.15,1.31,2.37,.31,5,True)
   for zz in [.31,.83,1.36,1.87]:
    if u<0:bottles(u,3.26,zz,6)
    else:books(u,3.26,zz,8)
  bx((-.73,3.145,2.70),(1.24,.04,.24),metal,'PANTRY shelf header')
  txt('PANTRY',(-.73,3.119,2.635),.134,'TR warm cream','visible PANTRY label',1.3)
  # Counter merchandise: book stand, baskets and plain packaged goods.
  for j in range(4):bx((.28+j*.19,1.84,1.16),(.13,.18,.17),['TR white package','TR mustard package','TR sage package'][j%3],'unbranded counter gifts')
  books(-.36,1.88,1.08,5)
  for u,v,z,w in [(.24,1.41,.68,.43),(.75,1.42,.94,.34)]:
   for dz in [0,.045,.09]:
    for j in range(18):
     a=2*pi*j/18;b=2*pi*(j+1)/18
     bm((u+w/2*cos(a),v+.12*sin(a),z+dz),(u+w/2*cos(b),v+.12*sin(b),z+dz),.006,'TR amber cane','small open basket woven rings',5)
  # Wicker pendant silhouette with actual open rods, observed through threshold.
  for j in range(36):
   a=2*pi*j/36
   bm((-.44+.15*cos(a),2.31+.15*sin(a),2.92),(-.44+.34*cos(a),2.31+.34*sin(a),2.65),.006,'TR amber cane','basket pendant radial cane rods',5)
  for z,r in [(2.65,.34),(2.72,.29),(2.80,.23),(2.89,.17)]:
   for j in range(36):
    a=2*pi*j/36;b=2*pi*(j+1)/36
    bm((-.44+r*cos(a),2.31+r*sin(a),z),(-.44+r*cos(b),2.31+r*sin(b),z),.006,'TR amber cane','basket pendant horizontal cane rings',5)
  bm((-.44,2.31,2.95),(-.44,2.31,3.40),.008,metal,'basket pendant suspension')
  lt((-.44,2.31,2.70),[(.040,0),(.046,.055),(.035,.088)],'TR neutral lamp','pendant warm bulb',16)
  plant(-.89,.60,.17,.85);plant(.57,2.54,1.07,1.00)
  # Small photographed wall device and edge-lit EXIT sign, deliberately plain.
  bx((-1.82,-.23,2.78),(.13,.06,.17),'TR warm cream','plain wall sensor')
  bx((-2.42,-.37,2.85),(.43,.10,.30),'TR warm cream','exit sign body')
  txt('EXIT',(-2.42,-.429,2.755),.21,'TR exit red','EXIT lettering')

  # Collection-separated lights: illumination supports the visible fragments,
  # not an asserted electrical fixture survey. Parent can disable this collection.
  col=bpy.data.collections.get('24 RETAIL LIGHTS | illustrative photographic exposure')
  if col is None:col=bpy.data.collections.new('24 RETAIL LIGHTS | illustrative photographic exposure');scene.collection.children.link(col)
  for name,pos,power,size,color in [('Shop display bounce',(11.0,40.6,2.98),170,3.0,(1,.91,.76)),('Neighbor doorway bounce',(-13.8,46.05,3.0),100,2.0,(1,.78,.48))]:
   l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;l.color=color
   ob=bpy.data.objects.new(name,l);col.objects.link(ob);ob.location=pos;ob['evidence']='Illustrative fill to expose documented view fragment; not fixture photometry'
  scene['ticket_retail_evidence']=json.dumps(TICKET_RETAIL_METADATA)
 finally:
  GROUP=_saved_group

if not AGED:
 _build_ticket_retail()
