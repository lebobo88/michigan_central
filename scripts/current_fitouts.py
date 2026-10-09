"""2026 Yellow Light public bar zone. Original geometry and material maps.
Shared-context add-on for build_station.py. No 2017 fit-out is emitted.
See manifests/current_fitouts/yellow_light_evidence.json for source/uncertainty.
"""
FRONTEND_CAMERAS = globals().get('FRONTEND_CAMERAS', {})
CURRENT_FITOUT_METADATA = {
 'space':'Yellow Light Coffee & Donuts, observed customer/bar zone',
 'period':'Completed 2025; documented current2026 use',
 'footprint_m':{'x':[-37.98,-28.63],'y':[43.36,48.52]},
 'registration':'HNS undimensioned scope raster, X=(555-px)*0.074756; Y=(py-120)*0.074756; uncertainty +/-0.3-0.6m',
 'rear_service_unfit_out':{'x':[-33.57,-28.63],'y':[48.52,51.88]},
 'geometry_policy':'Photographed bar/niche widths preserved; translated west3.22m; extra east strip unfurnished; staff aisle deepened0.50m',
 'modeled_area_m2':48.246,'published_suite_area_m2':59.4579456,
 'unresolved':'No current measured suite plan; hidden suite remainder and back-of-house omitted',
 'storefront_portals':[{'x':-34.13,'width':2.32,'top':4.30,'y':43.36,'entry':True}, {'x':-30.165,'width':2.31,'top':4.30,'y':43.36,'entry':False}],
 'copyright':'Architect photos studied only, never embedded or projected',
 'lod_omit_mesh_name_contains':['physical perforated ceiling panels','curved brass mesh screen wires'],
 'lod_keep_mesh_name_contains':['screen rim edging','ceiling panel joints','dark plenum'],
}

def _build_documented_yellow_light():
 global GROUP
 saved_group=GROUP
 GROUP='20 YELLOW LIGHT | 2025 completed, observed 2026 public bar zone'
 x0,y0=-35.73,43.36
 rear_shift=0.0
 def P(u,v,z):return (x0+u,y0+v+rear_shift,z)
 def bx(c,s,m,n):box(P(*c),s,m,'Yellow Light '+n)
 def bm(p,q,r,m,n,segments=12):beam(P(*p),P(*q),r,m,'Yellow Light '+n,segments)
 def lt(c,profile,m,n,segments=48):lathe(P(*c),profile,m,'Yellow Light '+n,segments)
 def am(v,f,m,n,uv=None):addmesh([P(*p) for p in v],f,m,'Yellow Light '+n,uv)
 def pm(name,folder,repeat):
  m=mat(name,(.5,.5,.5));nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
  for ch in ['basecolor','roughness','normal','height']:
   tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'manifests/current_fitouts/materials'/folder/(ch+'.png')),check_existing=True);tex.label='Original mathematical texture; not a scan'
   if ch!='basecolor':tex.image.colorspace_settings.name='Non-Color'
   if ch=='basecolor':nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
   if ch=='roughness':nt.links.new(tex.outputs['Color'],p.inputs['Roughness'])
   if ch=='normal':
    nn=nt.nodes.new('ShaderNodeNormalMap');nn.inputs['Strength'].default_value=.27;nt.links.new(tex.outputs['Color'],nn.inputs['Color']);nt.links.new(nn.outputs['Normal'],p.inputs['Normal'])
  m['texture_repeat_m']=repeat;m['texture_provenance']='Original mathematical material authored for this reconstruction; image-observed material class only'
  return name
 pale=pm('YL pale veined solid-surface stone','yl_pale_counter',2.1)
 floor=pm('YL polished mottled concrete','yl_polished_concrete',3.2)
 ocher=pm('YL salvaged Mankato ocher segments','yl_salvaged_ocher',1.5)
 for name,c,r,met in [
  ('YL mustard yellow',(.70,.51,.008),.40,0),('YL mauve plaster',(.36,.235,.285),.77,0),('YL fluted dyed concrete',(.40,.325,.34),.70,0),('YL mauve joinery',(.43,.29,.34),.40,0),
  ('YL bronze perforated metal',(.30,.225,.15),.27,.79),('YL brass mesh',(.55,.38,.09),.28,.82),('YL stainless steel',(.52,.56,.57),.26,.92),('YL dark appliance',(.018,.019,.02),.29,.18),
  ('YL timber ledges',(.33,.175,.056),.34,0),('YL pastry baked',(.43,.20,.075),.77,0),('YL pastry glaze',(.75,.49,.29),.42,0),('YL white ceramic',(.87,.85,.79),.20,0),('YL colored packaging green',(.045,.30,.15),.52,0),('YL colored packaging coral',(.67,.095,.05),.50,0),('YL colored packaging cyan',(.035,.34,.47),.50,0)]:mat(name,c,r,met)
 mat('YL thin architectural glass',(.95,.975,1),.018,0,1)
 mat('YL yellow lamp',(1,.78,.055),.22,0,.12,2.2)
 mat('YL white downlight',(1,.84,.64),.25,0,0,8)
 mat('YL blue-white neon',(.34,.73,1),.22,0,0,5)
 mat('YL pink cabinet light',(1,.44,.58),.3,0,0,2.5)
 yellow='YL mustard yellow';mauve='YL mauve plaster';flute='YL fluted dyed concrete';metal='YL bronze perforated metal';black='YL dark appliance';steel='YL stainless steel'
 # Clockwise UV-compatible extruded horizontal outline with explicit top/bottom.
 def slab(poly,z0,z1,m,n):
  count=len(poly);v=[(u,v,z) for z in [z0,z1] for u,v in poly]
  f=[tuple(range(count-1,-1,-1)),tuple(range(count,count*2))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
  am(v,f,m,n)
 # HNS registered outer shell. Extra east strip is left entirely unfurnished.
 # Bar/niche fabrication-scale geometry is not stretched to fill this footprint.
 bx((2.425,2.58,.10),(9.35,5.16,.16),floor,'registered-shell polished concrete floor')
 for u in [-2.25,7.10]:bx((u,2.58,1.64),(.12,5.16,3.1),mauve,'side plaster walls approximate registered envelope')
 bx((2.425,5.10,1.64),(9.35,.12,3.1),mauve,'back niche wall backing registered envelope')
 for u in [-2.175,7.025]:bx((u,2.57,.20),(.045,5.08,.14),'YL mauve joinery','side skirting')
 bx((2.425,5.01,.20),(9.25,.035,.14),'YL mauve joinery','rear skirting')
 # Glazing planes are Y43.36. Historic arcade frontage wall is lead-owned.
 for ua,ub in [(-2.25,.44),(2.76,4.41),(6.72,7.10)]:
  bx(((ua+ub)/2,.30,1.30),(ub-ua,.13,2.35),mauve,'front pier mauve lining')
  bx(((ua+ub)/2,.30,3.40),(ub-ua,.13,1.85),yellow,'front pier yellow upper lining')
 bx((2.425,.54,4.37),(9.35,1.08,.14),yellow,'raised yellow front ceiling')
 bx((2.425,1.13,3.77),(9.35,.12,1.2),yellow,'raised ceiling rear upstand')
 # Plain closures beyond the photographed perforated-field extent are provisional.
 bx((-1.10,3.15,3.20),(2.30,4.02,.04),metal,'plain ceiling closure over unresolved east strip')
 bx((3.55,4.87,3.20),(7.10,.58,.04),metal,'rear ceiling closure at registered shell')
 # Original circular field of yellow floor strips, clipped to an ellipse.
 # Photos establish strips, not a dimensioned installation drawing.
 for j in range(26):
  u=1.0+j*.175;dx=(u-3.1)/2.72
  if abs(dx)>=1:continue
  extent=1.11*sqrt(1-dx*dx);vmin=2.05-extent;vmax=2.05+extent
  am([(u-.0435,vmin,.18015),(u+.0435,vmin,.18015),(u+.0435,vmax,.18015),(u-.0435,vmax,.18015)],[(0,1,2,3)],yellow,'painted yellow floor sun strips')
 # Counter bar: HNS identifies salvaged half-round Mankato sections.
 def half_column(u,v,z,profile):
  count=33;vv=[(u+r*cos(pi+pi*i/32),v+r*sin(pi+pi*i/32),z+h) for r,h in profile for i in range(count)];ff=[]
  for j in range(len(profile)-1):
   for i in range(count-1):k=j*count+i;ff.append((k,k+1,k+1+count,k+count))
   ff.append((j*count,(j+1)*count,(j+2)*count-1,(j+1)*count-1))
  ff.extend([tuple(range(count-1,-1,-1)),tuple((len(profile)-1)*count+i for i in range(count))])
  am(vv,ff,ocher,'salvaged half-round column shafts')
 for u in [2.80,3.62,4.44,5.26,6.08]:
  half_column(u,2.62,.185,[(.38,0),(.401,.022),(.405,.12),(.402,.69),(.392,.75)])
 bx((4.40,2.57,1.026),(4.43,.86,.15),pale,'long counter solid stone top')
 bx((4.40,2.156,.91),(4.43,.035,.16),pale,'counter front apron')
 # Rounded eastern counter return; quarter-circle turns into the rear bench.
 poly=[(.50,4.60)]
 for i in range(41):
  t=pi+pi/2*i/40;poly.append((1.25+.75*cos(t),2.90+.75*sin(t)))
 poly += [(2.20,2.15),(2.20,3.01),(1.38,3.01),(1.38,4.60)]
 slab(poly,.20,1.10,pale,'rounded counter return shafts')
 # Glass-front merchandise cubby immediately after curved return.
 bx((2.40,2.51,.855),(.52,.64,.035),pale,'merchandise inset bottom')
 bx((2.40,2.181,.966),(.52,.008,.22),'YL thin architectural glass','counter merchandise display glazing')
 bx((2.40,2.51,1.108),(.52,.64,.009),'YL thin architectural glass','counter merchandise display lid')
 for i,c in enumerate([yellow,'YL mauve joinery',black]):
  bx((2.23+i*.16,2.49,.886),(.135,.31,.035),c,'folded merchandise without copied graphics')
 # Rear equipment/niche group translated0.50m deeper without stretching fixtures.
 rear_shift=.50
 # Back cabinets and shallow counter; exact utility connections intentionally absent.
 for u in [.55,2.0,2.59,3.18,3.77,4.36,6.48]:
  bx((u,4.20,.575),(.56,.54,.81),'YL mauve joinery','rear cabinet carcasses')
  bx((u,3.917,.57),(.54,.032,.76),'YL mauve joinery','cabinet fronts')
  bx((u+.17,3.89,.66),(.018,.025,.24),metal,'cabinet pull handles')
 bx((3.20,4.18,1.0),(3.53,.64,.065),pale,'rear bar worktop')
 # Three niche outlines: east merchandise arch; central broad yellow work niche;
 # west storage niche. Fluted front is an actual clipped corrugated surface.
 def limit(u):
  if .06<u<1.30:return 1.02+2.01*sqrt(max(0,1-(u/1.32)**2))
  if 1.60<u<4.78:
   return 1.08+1.98*sqrt(max(0,1-((u-3.16)/1.56)**2)) if u<3.16 else 3.06
  if 5.08<u<5.85:return 2.70
  if 6.04<u<6.93:return 2.72
  return .22
 count=560;v=[];f=[]
 for i in range(count+1):
  u=.04+6.92*i/count;yy=4.02-.024*cos(u*2*pi/.064);low=limit(u)
  v.extend([(u,yy,low),(u,yy,3.17)])
  if i:f.append((2*i-2,2*i,2*i+1,2*i-1))
 am(v,f,flute,'clipped hand-dyed fluted concrete wall')
 # Niche background shape and reveal: original geometry based on photo silhouette.
 outline=[(1.60,1.00),(4.78,1.00),(4.78,3.06),(3.16,3.06)]
 for i in range(1,49):
  t=pi/2+pi/2*i/48;outline.append((3.16+1.56*cos(t),1.08+1.98*sin(t)))
 vv=[(u,vv,z) for vv in [4.38,4.03] for u,z in outline];nn=len(outline)
 faces=[tuple(range(nn-1,-1,-1))]+[(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)]
 am(vv,faces,yellow,'main yellow quarter-arch niche lining')
 for u in [.67,6.48]:
  for z in [1.60,2.12]:bx((u,4.17,z),(1.02,.55,.038),'YL mauve joinery','merchandise niche shelves')
 bx((3.59,4.16,2.49),(2.24,.45,.035),yellow,'yellow display shelf')
 # Rear door closes the visible opening: no guessed room beyond.
 bx((5.47,4.45,1.45),(.74,.065,2.55),metal,'visible service door no hidden room')
 bx((5.47,4.41,1.90),(.31,.013,.41),'Glass tower dark','service door vision panel')
 bx((5.47,4.397,1.90),(.35,.02,.045),steel,'service door vision rail')
 bm((5.77,4.375,1.16),(5.77,4.375,1.42),.013,steel,'service door pull')
 # Coffee urns, brewer and frozen beverage machine. No manufacturer branding.
 for u in [1.97,2.41]:
  bx((u,4.02,1.10),(.37,.40,.07),black,'coffee urn bases')
  lt((u,4.12,1.13),[(.145,0),(.15,.08),(.147,.53),(.16,.55),(.16,.59),(.13,.61)],steel,'coffee urn shafts',40)
  lt((u,4.12,1.74),[(.13,0),(.15,.015),(.15,.055),(.07,.065)],black,'coffee urn lids',32)
  bm((u,3.93,1.38),(u,3.84,1.38),.023,black,'coffee taps')
  bm((u,3.88,1.38),(u,3.88,1.46),.011,metal,'tap levers')
  for du in [-.115,.115]:bm((u+du,4.10,1.11),(u+du,4.10,1.31),.025,black,'urn support legs')
 bx((2.17,4.28,1.84),(.88,.29,.82),steel,'two-station brewer rear cabinet')
 bx((2.17,4.24,2.28),(.97,.40,.12),steel,'brewer upper hood')
 for u in [1.97,2.41]:bx((u,4.074,2.04),(.18,.016,.16),black,'brewer controls')
 bx((2.98,4.05,1.58),(.56,.44,1.1),steel,'slush dispenser cabinet')
 # Front circular dispenser face lies in x-z plane; mesh normals explicit.
 for r,yy,material in [(.168,3.808,black),(.137,3.796,'YL pastry glaze')]:
  vv=[(2.98,yy,1.80)]+[(2.98+r*cos(2*pi*i/40),yy,1.80+r*sin(2*pi*i/40)) for i in range(40)]
  am(vv,[(0,i+1,(i+1)%40+1) for i in range(40)],material,'circular frozen beverage viewport')
 bm((2.98,3.77,1.56),(2.98,3.66,1.56),.025,steel,'dispenser spout')
 bx((2.98,3.75,1.18),(.48,.16,.05),steel,'dispenser drip tray')
 # Two-shelf glazed pastry case, pink light and original torus-like donuts.
 bx((3.92,4.09,1.055),(1.10,.52,.055),'YL mauve joinery','pastry display base')
 for z in [1.12,1.47,1.88]:bx((3.92,4.05,z),(1.10,.53,.034),'YL mauve joinery','pastry display horizontal frame')
 for u in [3.38,4.46]:
  for v0 in [3.805,4.295]:bx((u,v0,1.48),(.025,.025,.80),'YL mauve joinery','pastry display frame posts')
 bx((3.92,3.795,1.50),(1.045,.008,.73),'YL thin architectural glass','pastry display front glass')
 for u in [3.385,4.455]:bx((u,4.05,1.50),(.008,.47,.73),'YL thin architectural glass','pastry display side glass')
 for z in [1.48,1.85]:bx((3.92,4.18,z),(1.00,.14,.012),'YL pink cabinet light','pastry shelf light strips')
 def donut(u,v,z):
  vv=[];ff=[]
  for a in range(20):
   ta=2*pi*a/20
   for b in range(9):
    tb=2*pi*b/9;r=.054+.026*cos(tb);vv.append((u+r*cos(ta),v+r*sin(ta),z+.019*sin(tb)))
  for a in range(20):
   for b in range(9):ff.append((a*9+b,((a+1)%20)*9+b,((a+1)%20)*9+(b+1)%9,a*9+(b+1)%9))
  am(vv,ff,'YL pastry glaze','original donut geometry')
 for z in [1.164,1.514]:
  for i in range(6):
   for j in range(2):donut(3.49+i*.172,3.94+j*.19,z)
 bx((3.92,4.295,1.50),(1.06,.016,.74),'YL mauve joinery','pastry display pink rear wall')
 # Undercounter commercial cooling fronts.
 for u in [3.72,4.31]:
  bx((u,3.898,.59),(.54,.042,.73),steel,'undercounter refrigeration front')
  bx((u,3.868,.77),(.42,.015,.18),black,'refrigeration handle recess')
  bx((u,3.853,.85),(.40,.032,.025),steel,'refrigeration handle')
 # East open-front beverage cooler with original unbranded bottles and cans.
 bx((.54,4.10,.63),(.94,.67,.89),black,'beverage cooler cabinet')
 bx((.54,3.752,.63),(.84,.016,.67),'YL thin architectural glass','beverage cooler front glazing')
 for z in [.38,.64,.90]:bx((.54,3.98,z),(.84,.42,.020),steel,'beverage cooler shelves')
 for z in [.40,.66]:
  for i in range(7):
   c=['YL colored packaging green','YL colored packaging coral','YL colored packaging cyan','YL white ceramic'][i%4]
   lt((.18+i*.12,3.93,z),[(.040,0),(.04,.13),(.022,.16),(.022,.19)],c,'unbranded refrigerated drink',16)
 # Merchandise: generic packages and ceramic mugs, never photographic labels.
 for shelf in [1.63,2.15]:
  for i in range(6):
   u=.19+i*.16;bx((u,4.08,shelf+.12),(.12,.17,.23),black,'unbranded coffee retail bags')
   c=['YL colored packaging green',yellow,'YL colored packaging coral'][i%3]
   bx((u,3.988,shelf+.12),(.07,.003,.08),c,'generic colored package label')
 for i in range(7):
  u=2.70+i*.28
  lt((u,4.05,2.515),[(.048,0),(.048,.13),(.041,.134),(.041,.01)],black,'display mug shafts',24)
  # Small ring handle vertical in x-z.
  for j in range(14):
   t=2*pi*j/14;t2=2*pi*(j+1)/14
   bm((u+.058+.028*cos(t),4.05,2.578+.045*sin(t)),(u+.058+.028*cos(t2),4.05,2.578+.045*sin(t2)),.008,black,'mug handles',6)
 rear_shift=0.0
 # Counter espresso machine and original perforated cylindrical brass screens.
 bx((5.33,2.73,1.35),(1.12,.50,.50),black,'espresso machine body')
 bx((5.33,2.74,1.63),(1.08,.46,.04),steel,'espresso machine top')
 for u in [5.04,5.41]:
  bm((u,2.99,1.40),(u,3.14,1.38),.029,steel,'espresso portafilter arms')
  bm((u,3.14,1.38),(u+.10,3.22,1.38),.018,black,'espresso portafilter handles')
 for u in [4.85,5.81]:
  radius=.32;zlo=1.105;zhi=1.79;steps=82
  # Open-backed bronze mesh screen wraps about 260 degrees; actual holes remain.
  for k in range(steps+1):
   t=math.radians(140)+math.radians(260)*k/steps
   bm((u+radius*cos(t),2.53+radius*sin(t),zlo),(u+radius*cos(t),2.53+radius*sin(t),zhi),.0028,'YL brass mesh','curved brass mesh screen wires',4)
  for j in range(41):
   z=zlo+(zhi-zlo)*j/40
   for k in range(steps):
    t=math.radians(140)+math.radians(260)*k/steps;t2=math.radians(140)+math.radians(260)*(k+1)/steps
    bm((u+radius*cos(t),2.53+radius*sin(t),z),(u+radius*cos(t2),2.53+radius*sin(t2),z),.0028,'YL brass mesh','curved brass mesh screen wires',4)
  for z in [zlo,zhi]:
   for k in range(steps):
    t=math.radians(140)+math.radians(260)*k/steps;t2=math.radians(140)+math.radians(260)*(k+1)/steps
    bm((u+radius*cos(t),2.53+radius*sin(t),z),(u+radius*cos(t2),2.53+radius*sin(t2),z),.009,'YL brass mesh','screen rim edging',8)
 # POS hardware angled screen, no copied interface.
 bx((1.57,2.65,1.13),(.30,.21,.033),black,'POS base')
 bm((1.57,2.65,1.14),(1.57,2.70,1.31),.035,metal,'POS stand')
 am([(1.36,2.70,1.28),(1.79,2.70,1.28),(1.79,2.86,1.55),(1.36,2.86,1.55)],[(0,1,2,3)],black,'POS screen body')
 am([(1.39,2.696,1.30),(1.76,2.696,1.30),(1.76,2.83,1.52),(1.39,2.83,1.52)],[(0,1,2,3)],'YL colored packaging cyan','POS blank display')
 lt((1.77,2.30,1.103),[(.065,0),(.065,.025),(.06,.034)],black,'payment puck',24)
 # Perforated bronze ceiling: square repeat tessellation with real circular holes.
 # LOD pitch 60mm, hole diameter36mm; pitch not a field-survey measurement.
 vv=[];ff=[];n=16;pitch=.06;z=3.18
 for iy in range(53):
  cy=1.38+(iy+.5)*pitch
  for ix in range(115):
   cx=.05+(ix+.5)*pitch;start=len(vv)
   for zz in [z,z+.006]:
    for mode in ['outside','inside']:
     for k in range(n):
      t=2*pi*k/n;cs,sn=cos(t),sin(t);r=pitch/2/max(abs(cs),abs(sn)) if mode=='outside' else .018
      vv.append((cx+r*cs,cy+r*sn,zz))
   for k in range(n):
    q=(k+1)%n
    ff.extend([(start+k,start+n+k,start+n+q,start+q),(start+2*n+k,start+2*n+q,start+3*n+q,start+3*n+k),(start+n+k,start+3*n+k,start+3*n+q,start+n+q)])
 am(vv,ff,metal,'physical perforated ceiling panels')
 bx((3.50,2.96,3.24),(6.9,3.22,.015),black,'dark plenum behind perforated ceiling')
 for u in [.05,2.35,4.65,6.95]:bx((u,2.97,3.176),(.013,3.20,.014),metal,'ceiling panel joints')
 # Curved ceiling edge and yellow reveal over front aisle.
 for i in range(64):
  u=.05+6.90*(i+.5)/64;v0=1.24+.22*(1-cos(pi*u/6.9))
  bx((u,v0,3.20),(6.9/64+.003,.14,.16),metal,'curved ceiling bronze nosing')
 for u in [1,2.2,3.4,4.6,5.8]:
  for v0 in [1.88,3.20,4.25]:
   lt((u,v0,3.161),[(.052,0),(.052,.012)],'YL white downlight','recessed ceiling light apertures',24)
 # Yellow oblong wall lights with bronze central opaque strip.
 for u in [1.42,4.92,5.98]:
  # Capsule x-z plane; no borrowed fixture mesh.
  pts=[]
  for k in range(25):t=pi*k/24;pts.append((u+.11*cos(t),4.5,2.38+.11*sin(t)))
  for k in range(25):t=pi+pi*k/24;pts.append((u+.11*cos(t),4.5,2.04+.11*sin(t)))
  am(pts,[tuple(range(len(pts)))],'YL yellow lamp','capsule wall sconce glazing')
  bx((u,4.484,2.21),(.083,.034,.34),'YL brass mesh','sconce center shield')
 # Standing ledges now fit narrower registered openings, with entry clear.
 for ua,ub in [(.49,1.18),(2.02,2.71),(4.46,6.67)]:
  bx(((ua+ub)/2,.49,1.035),(ub-ua,.32,.072),'YL timber ledges','front standing ledges')
  for u in [ua+.035,ub-.035]:bx((u,.47,.61),(.065,.28,.83),'YL timber ledges','standing ledge supports')
 # Independently resized storefront frames; the counter is not rescaled.
 for center,width,door in [(1.60,2.32,True),(5.565,2.31,False)]:
  lo,hi=center-width/2,center+width/2;step=width/3
  for u in [lo,lo+step,lo+2*step,hi]:bx((u,0.0,2.27),(.047,.09,4.05),'Window cast iron','storefront vertical frames')
  for z0 in [2.61,4.27]:bx((center,0.0,z0),(width,.09,.065),'Window cast iron','storefront horizontal transoms')
  for k in range(3):
   ua=lo+k*step+.033;ub=lo+(k+1)*step-.033
   bx(((ua+ub)/2,.015,3.44),(ub-ua,.008,1.59),'YL thin architectural glass','storefront upper glass')
   isdoor=door and k==1;bottom=.18 if isdoor else .56
   bx(((ua+ub)/2,.015,(bottom+2.57)/2),(ub-ua,.008,2.57-bottom),'YL thin architectural glass','storefront door glass' if isdoor else 'storefront lower glass')
   bx(((ua+ub)/2,-.005,bottom),(ub-ua,.10,.048),'Window cast iron','storefront sill rails')
   if not isdoor:bx(((ua+ub)/2,.015,.335),(ub-ua,.17,.43),'Warm Mankato column stone','stone under glazing')
   if isdoor:
    bm((ub-.055,-.063,1.04),(ub-.055,-.063,1.34),.014,'Dark bronze','entry door pull')
    bx(((ua+ub)/2,-.025,.20),(ub-ua,.17,.035),metal,'entry threshold')
 # Typographic signage is original font geometry based on visible words.
 def text_mesh(txt,loc,size,m,name,rotation=(pi/2,0,0),align='CENTER',depth=.003):
  cu=bpy.data.curves.new('temporary YL text','FONT');cu.body=txt;cu.size=size;cu.align_x=align;cu.extrude=depth;cu.bevel_depth=.001;cu.resolution_u=4
  ob=bpy.data.objects.new('temporary YL text',cu);scene.collection.objects.link(ob);ob.location=P(*loc);ob.rotation_euler=rotation
  deps=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(deps);me=ev.to_mesh()
  matrix=ob.matrix_world;verts=[tuple(matrix@v.co) for v in me.vertices];faces=[tuple(p.vertices) for p in me.polygons]
  addmesh(verts,faces,m,'Yellow Light '+name);ev.to_mesh_clear();bpy.data.objects.remove(ob,do_unlink=True);bpy.data.curves.remove(cu)
 text_mesh('YELLOW LIGHT',(1.60,-.037,3.56),.202,'YL blue-white neon','front name sign')
 for center,width in [(1.60,2.32),(5.565,2.31)]:
  for k,word in enumerate(['COFFEE','BISCUITS','DONUTS']):text_mesh(word,(center-width/3+k*width/3,-.034,2.38),.085,black,'storefront product lettering')
 # East wall menu faces across the room; prices and current offerings omitted.
 text_mesh('YELLOW LIGHT',(-2.177,3.05,2.53),.20,yellow,'interior name lettering',(pi/2,0,pi/2))
 for word,v0 in [('DONUTS',2.06),('BISCUITS',2.88),('COFFEE',3.77)]:
  text_mesh(word,(-2.177,v0,2.17),.123,yellow,'menu category lettering',(pi/2,0,pi/2))
  for z0 in [1.22,1.37,1.52,1.67,1.82,1.97]:bx((-2.168,v0,z0),(.015,.69,.012),metal,'menu slotted rails no invented prices')
 # West wall simple round yellow brand motif (not a traced raster logo).
 rad=.36;vv=[(7.025,2.50,2.02)]+[(7.025,2.50+rad*cos(2*pi*i/64),2.02+rad*sin(2*pi*i/64)) for i in range(64)]
 am(vv,[(0,i+1,(i+1)%64+1) for i in range(64)],yellow,'simple round wall motif')
 bm((7.0,2.35,1.64),(7.0,2.66,2.40),.028,mauve,'diagonal cut in wall motif',8)
 # Fixture lights, collection-separated so they remain inspectable and adjustable.
 lighting=bpy.data.collections.get('20 YELLOW LIGHT | fixture lighting')
 if lighting is None:lighting=bpy.data.collections.new('20 YELLOW LIGHT | fixture lighting');scene.collection.children.link(lighting)
 for name,loc,power,size,color,rot in [
  ('bar indirect',(3.4,2.8,3.02),175,4.2,(1,.83,.65),(0,0,0)),
  ('yellow niche wash',(3.7,4.65,2.98),65,2.0,(1,.90,.58),(0,0,0)),
  ('front daylight',(3.5,.08,2.8),360,4.5,(.79,.88,1),(pi/2,0,0))]:
  data=bpy.data.lights.new('Yellow Light '+name,'AREA');data.energy=power;data.color=color;data.size=size;ob=bpy.data.objects.new('Yellow Light '+name,data);lighting.objects.link(ob);ob.location=P(*loc);ob.rotation_euler=rot
  ob['evidence']='Interpretive lighting intensity; photographed fixture and daylight class'
 GROUP=saved_group

if not AGED:
 _build_documented_yellow_light()
 FRONTEND_CAMERAS.update({
  'yellow_light':((-34.63,44.13,1.63),(-31.56,47.17,1.60),22),
  'yellow_light_counter':((-32.38,43.80,1.65),(-32.28,47.57,1.43),18),
  'yellow_light_reverse':((-29.28,44.52,1.64),(-34.48,46.57,1.70),23),
  'yellow_light_arcade':((-32.30,38.95,1.80),(-32.18,44.77,2.13),23),
 })
