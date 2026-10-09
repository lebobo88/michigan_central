"""West ground-floor public rooms, restored 2023/24 fabric carried into 2026.

Executes in build_station.py before batch finalization; no shared facade glazing.
Axes +X west/+Y south/+Z up, metres. Plans are raster-scaled, not a survey.
No exact 2017 condition is asserted and no 2026 NoMad fit-out is invented.
Source photographs are study-only and NEVER become materials or packaged assets.
"""
_west_previous_group = GROUP
WEST_ROOM_BOUNDS = {'reading': [36.16,52.10,4.95,15.4,.10,8.82],
                    'cafe': [36.16,52.10,15.4,23.5,.10,8.82],
                    'restaurant': [36.16,52.10,28.85,51.45,.10,7.62]}
WEST_ROOM_CAMERAS = {
 'mens_room':((38.2,13.25,1.72),(47.7,6.45,4.28),23),
 'west_reading_reverse':((50.6,6.8,1.78),(39.65,15.0,4.05),23),
 'historic_cafe':((37.5,19.35,1.76),(50.8,19.45,4.05),22),
 'west_reading_cafe':((48.8,21.6,1.70),(42.0,9.15,4.28),22),
 'west_woodwork_detail':((43.2,18.25,2.0),(41.82,15.2,4.35),33),
 'west_ceiling_detail':((44.2,9.2,4.0),(44.2,10.1,8.62),26),
 'restaurant':((38.15,30.1,1.76),(46.4,47.75,4.55),22),
 'restaurant_reverse':((50.7,49.8,1.76),(40.6,31.4,4.15),22),
 'restaurant_vault_detail':((41.65,37.5,3.0),(43.6,40.7,7.0),28),
}
WEST_ROOM_METADATA = {
 'status':'Interpretive restoration-baseline architecture; NOT a surveyed or complete 2026 interior',
 'era_policy':'Restored public fabric built only in 2026 scene from 2023/24 photographs; exact 2017 omitted',
 'source_plan':'research/visual/floor_plan_1914.jpg; 233 x 104 ft hall scale anchor',
 'room_bounds_m':WEST_ROOM_BOUNDS,
 'calibrated_corridor_connection':'Both corridor doors centered X44.1, between plan-derived restaurant piers; approximate, not surveyed',
 'precision':'Room partitions and grid generally +/-0.3 m raster estimates; heights/photo proportions less certain',
 'shared_hall_portals':[{'center_y':10.1,'width':2.4,'height':3.65},{'center_y':22.2,'width':2.4,'height':3.65}],
 'corridor_portals':[{'plane_y':23.5,'center_x':44.1,'width':3.,'height':3.6},{'plane_y':28.85,'center_x':44.1,'width':3.,'height':3.6}],
 'restaurant_east_connections':'Two 2.4 m clear, plan-proportioned plan-based openings to former lunch-counter zone; continuation outside this module unresolved',
 'omitted':['Exact 2017 loss/decay','Unknown 2026 construction changes','NoMad finished hotel','Restaurant final flooring','Extent of2024 removal of historic restaurant/lunch-counter partition','Furniture and operational fittings not documented'],
 'sources':['https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p59',
            'https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p60',
            'https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p62',
            'https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p66',
            'https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior-detail#p38',
            'https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior-detail#p39',
            'https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior#p49',
            'https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior-detail#p43']}


def west_material(name,color,rough=.45,metal=0,grain=False):
 m=mat(name,color,rough,metal);m['texture_repeat_m']=1.;m['provenance']='Original procedural material, photographic material class only; no image projection'
 nt=m.node_tree;p=nt.nodes.get('Principled BSDF');tc=nt.nodes.new('ShaderNodeTexCoord');mp=nt.nodes.new('ShaderNodeVectorMath');mp.operation='MULTIPLY';mp.inputs[1].default_value=(18,.36,1) if grain else (2.2,2.2,2.2)
 nt.links.new(tc.outputs['UV'],mp.inputs[0]);no=nt.nodes.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=3.8 if grain else 8;no.inputs['Detail'].default_value=3.;no.inputs['Roughness'].default_value=.65;nt.links.new(mp.outputs[0],no.inputs['Vector'])
 ramp=nt.nodes.new('ShaderNodeValToRGB');spread=.32 if grain else .055
 for e,f in zip(ramp.color_ramp.elements,[1-spread,1+spread]):e.color=(*[min(.99,c*f) for c in color],1)
 nt.links.new(no.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
 bu=nt.nodes.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.14 if grain else .1;bu.inputs['Distance'].default_value=.0012 if grain else .0007;nt.links.new(no.outputs['Fac'],bu.inputs['Height']);nt.links.new(bu.outputs['Normal'],p.inputs['Normal'])
 if grain:
  # Original image-channel equivalent preserves authored grain in GLB as well as Blender.
  for channel in ['basecolor','roughness','normal']:
   tex=nt.nodes.new('ShaderNodeTexImage');tex.name='West exportable '+channel;tex.image=bpy.data.images.load(str(ROOT/'assets/textures/original_walnut_longgrain'/(channel+'.png')),check_existing=True)
   if channel!='basecolor':tex.image.colorspace_settings.name='Non-Color'
   if channel=='basecolor':nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
   elif channel=='roughness':nt.links.new(tex.outputs['Color'],p.inputs['Roughness'])
   else:
    nm=nt.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.3;nt.links.new(tex.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],p.inputs['Normal'])
  p.inputs['Coat Weight'].default_value=.18;p.inputs['Coat Roughness'].default_value=.25
 return name


def west_block(c,s,material,name,grain=2):
 """Per-face metric UVs: u transverse, v along specified world grain axis."""
 x,y,z=c;dx,dy,dz=[v/2 for v in s];corners=[(x+a*dx,y+b*dy,z+d*dz) for a,b,d in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 fs=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)];vv=[];ff=[];uv=[]
 for face in fs:
  n=Vector(corners[face[1]])-Vector(corners[face[0]]);n=n.cross(Vector(corners[face[2]])-Vector(corners[face[0]]));normal=max(range(3),key=lambda i:abs(n[i]));va=grain if grain!=normal else next(i for i in range(3) if i!=normal);ua=next(i for i in range(3) if i not in [normal,va]);k=len(vv)
  for idx in face:vv.append(corners[idx]);uv.append((corners[idx][ua],corners[idx][va]))
  ff.append(tuple(range(k,k+4)))
 addmesh(vv,ff,material,name,uv)


def west_pt(u,p,z,axis='y'):
 return (p,u,z) if axis=='x' else (u,p,z)


def west_panel_box(u,p,z,w,d,h,material,name,axis='y',grain=2):
 west_block(west_pt(u,p,z,axis),(d,w,h) if axis=='x' else (w,d,h),material,name,grain)


def west_spans(a,b,holes):
 cursor=a
 for c,w in sorted((h[0],h[1]) for h in holes):
  lo=max(a,c-w/2);hi=min(b,c+w/2)
  if lo>cursor:yield cursor,lo
  cursor=max(cursor,hi)
 if cursor<b:yield cursor,b


def west_trimline(p,a,b,z,depth,height,material,name,axis='y',holes=()):
 for aa,bb in west_spans(a,b,holes):west_panel_box((aa+bb)/2,p,z,bb-aa,depth,height,material,name,axis,1 if axis=='x' else 0)


def west_rectframe(u,p,z,w,h,material,name,axis='y',depth=.10,bar=.045):
 for s in [-1,1]:west_panel_box(u+s*w/2,p,z,w=bar,d=depth,h=h,material=material,name=name,axis=axis)
 for s in [-1,1]:west_panel_box(u,p,z+s*h/2,w=w+bar,d=depth,h=bar,material=material,name=name,axis=axis,grain=1 if axis=='x' else 0)


def west_ellipse(c,r,material,name,n=12,rings=6):
 vv=[(c[0],c[1],c[2]-r[2])];ff=[]
 for j in range(1,rings):
  a=-pi/2+j*pi/rings
  for i in range(n):t=2*pi*i/n;vv.append((c[0]+r[0]*cos(a)*cos(t),c[1]+r[1]*cos(a)*sin(t),c[2]+r[2]*sin(a)))
 top=len(vv);vv.append((c[0],c[1],c[2]+r[2]))
 for i in range(n):ff.append((0,1+(i+1)%n,1+i));ff.append((top,1+(rings-2)*n+i,1+(rings-2)*n+(i+1)%n))
 for j in range(rings-2):
  for i in range(n):k=1+j*n+i;ff.append((k,1+j*n+(i+1)%n,1+(j+1)*n+(i+1)%n,k+n))
 addmesh(vv,ff,material,name)


def west_leaf(u,p,z,w,h,material,name,axis='y',sign=1):
 # Original ten-lobed relief silhouette, raised midrib; motif class only.
 contour=[(0,0),(-.18,.16),(-.50,.28),(-.34,.46),(-.48,.62),(-.25,.69),(-.30,.85),(0,1),(.30,.85),(.25,.69),(.48,.62),(.34,.46),(.5,.28),(.18,.16)]
 vv=[west_pt(u+a*w,p,z+b*h,axis) for a,b in contour];vv.append(west_pt(u,p+sign*.035,z+h*.53,axis));ff=[(i,(i+1)%len(contour),len(contour)) for i in range(len(contour))]
 if (axis=='y' and sign<0) or (axis=='x' and sign>0):ff=[tuple(reversed(f)) for f in ff]
 # Stable local metric UVs avoid world-coordinate precision cancellation in tiny carved relief.
 uv=[((a+.5)*w,b*h) for a,b in contour]+[(.5*w,.53*h)]
 addmesh(vv,ff,material,name,uv)


def west_pilaster(u,p,z0=.10,axis='y',sign=1,width=.54,top=5.40):
 material=WEST_WOOD;face=p+sign*.13
 west_panel_box(u,p,(z0+top)/2,width,.22,top-z0,material,'West walnut pilaster vertical grained shaft',axis)
 west_panel_box(u,p+sign*.04,z0+.18,width+.10,.30,.36,'Warm Mankato column stone','West pale stone pilaster plinth',axis)
 for z,w,d,h in [(z0+.42,width+.14,.34,.11),(z0+.53,width+.08,.28,.10),(z0+.62,width+.02,.24,.07),(4.72,width+.05,.28,.07),(5.24,width+.19,.35,.10),(5.34,width+.27,.38,.08)]:west_panel_box(u,p+sign*.03,z,w,d,h,material,'West walnut pilaster stepped base and capital abacus',axis)
 west_rectframe(u,face+sign*.008,2.73,width-.14,3.87,material,'West walnut pilaster recessed shaft panel moldings',axis,.045,.029)
 for j in range(5):west_leaf(u+(j-2)*width*.155,face+sign*.026,4.72,width*.15,.30,material,'West carved capital acanthus flutes',axis,sign)
 for s in [-1,1]:
  hu=u+s*width*.39;hp=face+sign*.095
  c=west_pt(hu,hp,5.09,axis);r=(.095,.068,.14) if axis=='y' else (.068,.095,.14);west_ellipse(c,r,material,'West carved ram-head corner bosses',10,5)
  c=west_pt(hu,hp+sign*.049,5.02,axis);r=(.065,.067,.071) if axis=='y' else (.067,.065,.071);west_ellipse(c,r,material,'West carved ram-head muzzles',8,4)
  pts=[]
  for j in range(19):
   t=j/18*2.5*pi;r=.098*(1-j/22);pts.append(west_pt(hu+s*r*cos(t),hp+sign*.018,5.18+r*sin(t),axis))
  for aa,bb in zip(pts,pts[1:]):beam(aa,bb,.012,material,'West carved capital curled horns and volutes',5)
 west_leaf(u,face+sign*.04,4.95,width*.30,.36,material,'West carved capital central palmette',axis,sign)


def west_wood_entablature(p,a,b,axis='y',sign=1,holes=()):
 for z,d,h in [(5.37,.21,.065),(5.45,.25,.085),(5.56,.22,.12),(5.67,.29,.055),(5.75,.23,.09),(5.84,.32,.075),(5.94,.38,.075)]:west_trimline(p+sign*d*.40,a,b,z,d,h,WEST_WOOD,'West walnut layered entablature cornice',axis,holes)
 for aa,bb in west_spans(a,b,holes):
  count=max(1,int((bb-aa)/.24))
  for j in range(count):
   u=aa+(j+.5)*(bb-aa)/count;west_leaf(u,p+sign*.165,5.49,.155,.14,WEST_WOOD,'West entablature carved palmette frieze',axis,sign)


def west_wall_panels(p,a,b,axis='y',sign=1,portals=(),windows=()):
 """Thin independent interior finish over shared wall; holes are real geometry."""
 holes=[(c,w) for c,w,*rest in portals]+[(c,w) for c,w,*rest in windows]
 for aa,bb in west_spans(a,b,holes):
  west_panel_box((aa+bb)/2,p,2.90,bb-aa,.055,5.60,WEST_WOOD,'West walnut wall fields vertical grain',axis)
  west_panel_box((aa+bb)/2,p+sign*.025,.29,bb-aa,.105,.38,'Warm Mankato column stone','West pale stone wall skirting',axis)
  n=max(1,round((bb-aa)/2.7))
  for j in range(n):
   u=aa+(j+.5)*(bb-aa)/n;ww=(bb-aa)/n-.21
   if ww>.35:
    west_rectframe(u,p+sign*.060,2.85,ww,4.14,WEST_WOOD,'West walnut raised rectangular panel frames',axis,.038,.032)
  if bb-aa>.70:
   for u in [aa+.23,bb-.23]:west_pilaster(u,p+sign*.065,axis=axis,sign=sign,width=.38)
 for c,w,top in portals:
  west_panel_box(c,p,(top+5.70)/2,w,.055,5.70-top,WEST_WOOD,'West walnut true-door opening headers',axis)
  west_rectframe(c,p+sign*.067,(top+5.18)/2,max(.30,w-.23),5.18-top-.22,WEST_WOOD,'West walnut overdoor raised panel',axis,.05,.032)
 for c,w,bottom,top in windows:
  west_panel_box(c,p,(.1+bottom)/2,w,.065,bottom-.1,WEST_WOOD,'West walnut under-window solid panel',axis)
  west_panel_box(c,p+sign*.03,.28,w,.10,.36,'Warm Mankato column stone','West under-window pale stone skirting',axis)
 for z,d,h in [(.60,.12,.10),(.69,.085,.04),(5.22,.09,.06)]:west_trimline(p+sign*.055,a,b,z,d,h,WEST_WOOD,'West walnut wall rails horizontal grain',axis,holes)
 west_wood_entablature(p,a,b,axis,sign,[(c,w) for c,w,*_ in windows])


def west_doorcase(u,p,width,top,axis='y',sign=1):
 for off in [0,.075,.15]:
  ww=width+.15+off*2
  for s in [-1,1]:west_panel_box(u+s*ww/2,p+sign*(.05+off*.28),(top+.10)/2,.075,.13+off*.3,top-.10,WEST_WOOD,'West room layered timber door jambs',axis)
  west_panel_box(u,p+sign*(.05+off*.28),top+.03+off,ww+.08,.13+off*.3,.075,WEST_WOOD,'West room layered timber door lintels',axis,1 if axis=='x' else 0)
 west_panel_box(u,p+sign*.12,top+.28,width+.80,.33,.10,WEST_WOOD,'West room doorcase projecting cornice',axis,1 if axis=='x' else 0)
 # Open aperture intentionally retained. Core/secondary module owns operational door leaves.
 for s in [-1,1]:
  for j in range(3):west_panel_box(u+s*(width/2+.29),p+sign*(.13+j*.018),top-.22+j*.13,.10+j*.02,.17+j*.025,.14,WEST_WOOD,'West doorcase carved bracket profiles',axis)


def west_arch_liner(p,a,b,windows,axis='y',sign=1):
 """Interior plaster only. Shared outer stone wall and glazing remain core-owned."""
 for aa,bb in west_spans(a,b,[(c,w) for c,w,*_ in windows]):west_panel_box((aa+bb)/2,p,7.37,bb-aa,.055,2.94,WEST_CREAM,'West upper plaster wall between arched windows',axis)
 for c,w,bot,top in windows:
  r=w/2;spring=top-r;vv=[];ff=[];n=32
  for j in range(n+1):
   u=-r+2*r*j/n;zz=spring+sqrt(max(0,r*r-u*u));vv.extend([west_pt(c+u,p,zz,axis),west_pt(c+u,p,8.84,axis)])
  for j in range(n):ff.append((2*j,2*j+1,2*j+3,2*j+2) if ((axis=='y')==(sign>0)) else (2*j+2,2*j+3,2*j+1,2*j))
  addmesh(vv,ff,WEST_CREAM,'West upper plaster true arched window heads')
  for off,thick in [(.045,.052),(.12,.035),(.19,.040)]:arch(c,p+sign*.07,spring,w+off*2,r+off,thick,.075,WEST_CREAM,'West arched window interior plaster archivolt',32,'side' if axis=='x' else 'front')
  # Reveals and sills avoid placing glazing or bars over the shared facade window.
  for s in [-1,1]:west_panel_box(c+s*(r+.05),p+sign*.06,(bot+spring)/2,.10,.19,spring-bot,WEST_WOOD,'West window interior timber jamb trims',axis)
  west_panel_box(c,p+sign*.10,bot-.035,w+.17,.29,.10,WEST_WOOD,'West window projecting timber sills',axis,1 if axis=='x' else 0)


def west_polygon_ring(cx,cy,outer,inner,z,thick,material,name,n=8,angle=pi/8,sy=1.):
 vv=[]
 for zz in [z-thick/2,z+thick/2]:
  for r in [outer,inner]:
   for j in range(n):t=angle+2*pi*j/n;vv.append((cx+r*cos(t),cy+r*sin(t)*sy,zz))
 ff=[]
 for j in range(n):
  k=(j+1)%n;ff.extend([(j,n+j,n+k,k),(2*n+j,2*n+k,3*n+k,3*n+j),(j,k,2*n+k,2*n+j),(n+j,3*n+j,3*n+k,n+k)])
 addmesh(vv,ff,material,name)


def west_petal(cx,cy,z,angle,length,width,material,name):
 # Smoothly raised original radial plaster ornament, underside normals face room.
 vv=[];segments=8
 for j in range(segments+1):
  t=j/segments;rr=.035+length*t;ww=width*sin(pi*t)**.65;depth=.045*sin(pi*t)
  for side in [-1,0,1]:
   u=rr;v=side*ww;vv.append((cx+u*cos(angle)-v*sin(angle),cy+u*sin(angle)+v*cos(angle),z-depth*(1 if side==0 else .20)))
 ff=[]
 for j in range(segments):
  for k in range(2):i=j*3+k;ff.append((i,i+1,i+4,i+3))
 addmesh(vv,ff,material,name)


def west_rosette(cx,cy,z,r=.32):
 lathe((cx,cy,z-.042),[(.002,0),(.07,0),(.12,.025),(.16,.052),(r*.67,.080),(r*.76,.115)],WEST_CREAM,'West plaster rosette layered central boss',24)
 for j in range(12):west_petal(cx,cy,z+.055,2*pi*j/12,r,r*.16,WEST_CREAM,'West plaster rosette twelve original radial leaves')
 for j in range(6):west_petal(cx,cy,z+.017,2*pi*j/6+pi/12,r*.53,r*.13,WEST_CREAM,'West plaster rosette inner curled petals')


def west_coffer(cx,cy,w,d):
 # Deep real nested squares and octagons, fluted sloping annulus, relief rosette.
 sy=d/w;r=w*.385
 for off,zz,bar in [(0,8.47,.08),(.075,8.52,.045),(.125,8.575,.039)]:
  ww=w-.16-off*2;dd=d-.16-off*2
  for s in [-1,1]:west_block((cx+s*ww/2,cy,zz),(bar,dd+bar,.075),WEST_CREAM,'West ceiling coffer inset stepped square moldings');west_block((cx,cy+s*dd/2,zz),(ww+bar,bar,.075),WEST_CREAM,'West ceiling coffer inset stepped square moldings')
 for outer,inner,zz,thick in [(r,r-.050,8.56,.070),(r-.055,r-.085,8.60,.055),(r*.52,r*.46,8.66,.065)]:west_polygon_ring(cx,cy,outer,inner,zz,thick,WEST_CREAM,'West ceiling octagonal coffer profiles',8,pi/8,sy)
 # Sloping octagonal shell with lower outer rim and deeper central well.
 vv=[]
 for rr,zz in [(r-.085,8.605),(r*.52,8.68)]:
  for j in range(8):a=pi/8+j*pi/4;vv.append((cx+rr*cos(a),cy+rr*sin(a)*sy,zz))
 addmesh(vv,[(j,8+j,8+(j+1)%8,(j+1)%8) for j in range(8)],WEST_CREAM,'West ceiling fluted octagonal sloping coffers')
 for side in range(8):
  a0=pi/8+side*pi/4;a1=a0+pi/4
  for k in range(1,7):
   t=k/7;px=(1-t)*cos(a0)+t*cos(a1);py=(1-t)*sin(a0)+t*sin(a1)
   beam((cx+(r-.095)*px,cy+(r-.095)*py*sy,8.593),(cx+r*.55*px,cy+r*.55*py*sy,8.658),.012,WEST_CREAM,'West coffer radial flute ribs',5)
  for k in range(1,5):
   t=k/5;px=(1-t)*cos(a0)+t*cos(a1);py=(1-t)*sin(a0)+t*sin(a1)
   cc=(cx+(r-.035)*px,cy+(r-.035)*py*sy,8.515)
   west_ellipse(cc,(.022,.025,.035),WEST_CREAM,'West coffer egg and dart relief beads',6,3)
 west_rosette(cx,cy,8.49,min(w,d)*.175)


def west_ceiling(x0,x1,y0,y1,nx,ny):
 west_block(((x0+x1)/2,(y0+y1)/2,8.92),(x1-x0,y1-y0,.18),WEST_CREAM,'West cream plaster ceiling substrate')
 marginx=.85;marginy=.85;xa=x0+marginx;xb=x1-marginx;ya=y0+marginy;yb=y1-marginy;cw=(xb-xa)/nx;cd=(yb-ya)/ny
 for i in range(nx):
  for j in range(ny):west_coffer(xa+(i+.5)*cw,ya+(j+.5)*cd,cw,cd)
 for i in range(nx+1):west_block((xa+i*cw,(ya+yb)/2,8.39),(.12,yb-ya+.12,.15),WEST_CREAM,'West ceiling coffering main ribs')
 for j in range(ny+1):west_block(((xa+xb)/2,ya+j*cd,8.39),(xb-xa+.12,.12,.15),WEST_CREAM,'West ceiling coffering cross ribs')
 for i in range(nx+1):
  for j in range(ny+1):
   xx=xa+i*cw;yy=ya+j*cd;west_block((xx,yy,8.29),(.25,.25,.095),WEST_CREAM,'West ceiling coffer crossing square floral bosses')
   if 0<i<nx and 0<j<ny:
    for k in range(4):west_petal(xx,yy,8.265,k*pi/2,.10,.05,WEST_CREAM,'West ceiling crossing small floral relief')
 for p,a,b,axis,sign in [(x0, y0,y1,'x',1),(x1,y0,y1,'x',-1),(y0,x0,x1,'y',1),(y1,x0,x1,'y',-1)]:
  for step,(off,zz,h) in enumerate([(.12,8.20,.10),(.22,8.29,.075),(.37,8.37,.08),(.49,8.45,.06),(.57,8.52,.07)]):west_trimline(p+sign*off,a,b,zz,.16+step*.08,h,WEST_CREAM,'West plaster perimeter cornice stepped profiles',axis)
  west_trimline(p+sign*.08,a,b,7.62,.038,.030,WEST_CREAM,'West upper wall fine plaster dado profile',axis)
  for u in [a+(b-a)*.25,a+(b-a)*.75]:
   for j in range(4):west_panel_box(u,p+sign*(.22+j*.07),8.05+j*.055,.24-j*.025,.20+j*.04,.12,WEST_CREAM,'West ceiling perimeter pendant corbel blocks',axis)


def west_pendant(x,y,ceiling,bottom,kind='West'):
 beam((x,y,ceiling),(x,y,bottom+.52),.018,WEST_BRONZE,kind+' dark pendant stems',10)
 lathe((x,y,ceiling-.10),[(.16,0),(.19,.04),(.16,.095),(.08,.12)],WEST_BRONZE,kind+' pendant ceiling roses',20)
 lathe((x,y,bottom),[(.015,0),(.13,.025),(.225,.15),(.26,.30),(.24,.43),(.16,.52),(.08,.54)],WEST_OPAL,kind+' opal pear pendant globe',28)
 lathe((x,y,bottom+.48),[(.145,0),(.175,.05),(.175,.09),(.10,.13)],WEST_BRONZE,kind+' pendant stepped metal caps',24)


def west_sailz(x,y,hx,hy,spring=4.78,rise=2.6):return spring+rise*sqrt(max(0,1-.5*((x/hx)**2+(y/hy)**2)))


def west_sail(cx,cy,hx,hy):
 n=22;vv=[];uv=[]
 for j in range(n+1):
  for i in range(n+1):xx=-hx+2*hx*i/n;yy=-hy+2*hy*j/n;vv.append((cx+xx,cy+yy,west_sailz(xx,yy,hx,hy)));uv.append((cx+xx,cy+yy))
 ff=[]
 for j in range(n):
  for i in range(n):k=j*(n+1)+i;ff.append((k,k+n+1,k+n+2,k+1))
 addmesh(vv,ff,WEST_CREAM,'West restaurant scored plaster sail vaults',uv)
 def line(points):
  # Ribbon follows actual curved underside. Very shallow gray score, not tile.
  verts=[];faces=[];prev=None
  for xx,yy in points:
   if abs(xx)>hx-.018 or abs(yy)>hy-.018:
    prev=None;continue
   rr=sqrt((xx/hx)**2+(yy/hy)**2);dr=.0019
   if rr<.01:continue
   z=west_sailz(xx,yy,hx,hy)-.005
   k=len(verts);verts.extend([(cx+xx-dr*xx/rr,cy+yy-dr*yy/rr,z),(cx+xx+dr*xx/rr,cy+yy+dr*yy/rr,z)])
   if prev is not None:faces.append((prev,k,k+1,prev+1))
   prev=k
  if faces:addmesh(verts,faces,WEST_SCORE,'West restaurant incised concentric plaster scoring')
 for r in [.14,.31,.48,.65,.82,.99,1.16,1.33]:line([(hx*r*cos(2*pi*k/80),hy*r*sin(2*pi*k/80)) for k in range(81)])
 for band,(r0,r1) in enumerate(zip([.14,.31,.48,.65,.82,.99,1.16],[.31,.48,.65,.82,.99,1.16,1.33])):
  count=8+band*4
  for j in range(count):
   a=2*pi*(j+(.5 if band%2 else 0))/count;xx0=hx*r0*cos(a);yy0=hy*r0*sin(a);xx1=hx*r1*cos(a);yy1=hy*r1*sin(a)
   if max(abs(xx0),abs(xx1))>hx-.025 or max(abs(yy0),abs(yy1))>hy-.025:continue
   vv=[]
   for k in range(7):
    t=k/6;xx=xx0*(1-t)+xx1*t;yy=yy0*(1-t)+yy1*t;z=west_sailz(xx,yy,hx,hy)-.005
    vv.extend([(cx+xx-.003*sin(a),cy+yy+.003*cos(a),z),(cx+xx+.003*sin(a),cy+yy-.003*cos(a),z)])
   addmesh(vv,[(2*k,2*k+2,2*k+3,2*k+1) for k in range(6)],WEST_SCORE,'West restaurant staggered radial plaster score joints')


def west_arch_scores(cx,p,z,width,rise,thick=.26,depth=.84,axis='y'):
 r=width/2
 for j in range(1,15):
  a=pi*j/15
  for side in [-1,1]:
   pp=p+side*(depth/2+.002)
   beam(west_pt(cx+r*cos(a),pp,z+rise*sin(a),axis),west_pt(cx+(r+thick)*cos(a),pp,z+(rise+thick)*sin(a),axis),.0032,WEST_SCORE,'West restaurant arch face incised voussoir joints',4)
  u=cx+(r-.003)*cos(a);zz=z+(rise-.003)*sin(a)
  beam(west_pt(u,p-depth/2,zz,axis),west_pt(u,p+depth/2,zz,axis),.0032,WEST_SCORE,'West restaurant arch soffit transverse scored joints',4)


def west_restaurant_window_liner(windows):
 p=52.085;a=28.85;b=51.45;h=7.62
 holes=[(c,w) for c,w,*_ in windows]
 for aa,bb in west_spans(a,b,holes):
  west_panel_box((aa+bb)/2,p,(.10+h)/2,bb-aa,.06,h-.10,WEST_CREAM,'West restaurant outer wall cream plaster liner','x')
  west_panel_box((aa+bb)/2,p-.035,.30,bb-aa,.085,.40,'Warm Mankato column stone','West restaurant outer wall stone skirting','x')
  for zz in [1.96+i*.45 for i in range(10)]:west_panel_box((aa+bb)/2,p-.033,zz,bb-aa,.004,.004,WEST_SCORE,'West restaurant outer wall shallow scored courses','x')
 for c,w,bot,top in windows:
  r=w/2;sp=top-r
  west_panel_box(c,p,(.1+bot)/2,w,.06,bot-.1,WEST_CREAM,'West restaurant under-window plaster liner','x')
  west_panel_box(c,p-.035,.30,w,.085,.40,'Warm Mankato column stone','West restaurant window stone skirting','x')
  vv=[];ff=[];n=32
  for j in range(n+1):
   u=-r+2*r*j/n;zz=sp+sqrt(max(0,r*r-u*u));vv.extend([west_pt(c+u,p,zz,'x'),west_pt(c+u,p,h,'x')])
  for j in range(n):ff.append((2*j,2*j+1,2*j+3,2*j+2))
  addmesh(vv,ff,WEST_CREAM,'West restaurant genuine arched plaster window heads')
  arch(c,p-.035,sp,w+.07,r+.035,.07,.09,WEST_CREAM,'West restaurant window plaster archivolts',30,'side')
  for sign in [-1,1]:west_panel_box(c+sign*(r+.035),p-.025,(bot+sp)/2,.08,.11,sp-bot,WEST_CREAM,'West restaurant plaster window jambs','x')
  west_panel_box(c,p-.10,bot-.02,w+.16,.30,.085,'Warm Mankato column stone','West restaurant stone window sills','x',grain=1)


def west_pier(x,y,width=.84):
 label='West restaurant square piers' if width>.8 else 'West restaurant narrow boundary pilasters'
 west_block((x,y,2.48),(width,.84,4.76),WEST_CREAM,label)
 west_block((x,y,.30),(width+.07,.91,.40),'Warm Mankato column stone','West restaurant stone pier plinths')
 for z,extra,h in [(.53,.07,.07),(1.87,.04,.07),(1.97,.07,.10),(4.66,.05,.08)]:west_block((x,y,z),(width+extra,.84+extra,h),WEST_CREAM,'West restaurant square pier impost moldings')
 for zz in [2.24+i*.42 for i in range(6)]:
  for p,u,axis,span in [(x+width/2+.002,y,'x',.84),(x-width/2-.002,y,'x',.84),(y+.422,x,'y',width),(y-.422,x,'y',width)]:
   west_panel_box(u,p,zz,span,.004,.0045,WEST_SCORE,'West restaurant incised ashlar pier courses',axis)
   west_panel_box(u+(.13 if int(zz/.42)%2 else -.18),p,zz+.21,.0045,.004,.416,WEST_SCORE,'West restaurant staggered vertical pier scores',axis)



if not AGED:
 WEST_WOOD=west_material('West restored carved walnut',(.041,.018,.0075),.30,grain=True)
 WEST_CREAM=west_material('West restored warm ivory plaster',(.73,.70,.625),.62)
 WEST_SCORE=west_material('West shallow plaster score shadow',(.38,.365,.325),.78)
 WEST_BRONZE=west_material('West patinated pendant bronze',(.11,.075,.033),.32,.72)
 WEST_OPAL=mat('West warm opaline glass',(.96,.84,.61),.23,0,.08,2.2).name
 WEST_SLAB=west_material('West restaurant observed unfinished slab',(.205,.224,.226),.86)
 # Keep image-generated ORIGINAL floor texture, tame its inferred micro-normal.
 WEST_FLOOR='West conserved walnut herringbone';mf=M['Historic walnut herringbone'].copy();mf.name=WEST_FLOOR;M[WEST_FLOOR]=mf
 for nd in mf.node_tree.nodes:
  if nd.type=='NORMAL_MAP':nd.inputs['Strength'].default_value=.10
 pp=mf.node_tree.nodes.get('Principled BSDF')
 for link in list(pp.inputs['Roughness'].links):mf.node_tree.links.remove(link)
 pp.inputs['Roughness'].default_value=.28;pp.inputs['Coat Weight'].default_value=.10;mf['texture_repeat_m']=1.40
 x0=36.16;x1=52.10;read_y0=4.95;partition=15.4;cafe_y1=23.5
 GROUP='08 WEST READING ROOM AND HISTORIC CAFE | 2023-24 restored fabric baseline'
 west_block(((x0+x1)/2,(read_y0+cafe_y1)/2,.025),(x1-x0,cafe_y1-read_y0,.15),WEST_FLOOR,'West original herringbone reading and cafe floor',grain=1)
 west_block(((x0+x1)/2,partition,.103),(x1-x0,.88,.013),'Rose Tennessee marble','West reading cafe rose-marble threshold strip',grain=0)
 # Hall east wall: finish begins safely west of the core hall wall face X36.1092.
 hall_portals=[(10.1,2.4,3.65),(22.2,2.4,3.65)]
 west_wall_panels(36.225,4.95,23.5,'x',1,hall_portals)
 west_panel_box((4.95+23.5)/2,36.195,7.41,23.5-4.95,.07,2.94,WEST_CREAM,'West reading cafe east upper plaster',axis='x')
 for yy,ww,hh in hall_portals:west_doorcase(yy,36.29,ww,hh,'x',1)
 northwins=[(39.719,2.4384,1.,7.2484),(44.069,2.4384,1.,7.2484),(48.419,2.4384,1.,7.2484)]
 west_wall_panels(4.975,x0,x1,'y',1,windows=northwins);west_arch_liner(4.970,x0,x1,northwins,'y',1)
 # Plan-proportioned twelve-window west schedule; core owns the actual facade cuts.
 # Lead can supply WEST_FACADE_WINDOWS=[(centerY,width,bottom,top),...] before exec.
 defaultwins=[(yy,2.4384,1.,7.2484) for yy in [6.84,10.34,13.69,17.81,21.55,26.26,30.79,34.45,38.18,41.98,45.71,49.45]]
 facade_wins=globals().get('WEST_FACADE_WINDOWS',defaultwins)
 westwins=[win for win in facade_wins if win[0]-win[1]/2>=read_y0-.1 and win[0]+win[1]/2<=cafe_y1+.1]
 west_wall_panels(52.075,read_y0,cafe_y1,'x',-1,windows=westwins);west_arch_liner(52.09,read_y0,cafe_y1,westwins,'x',-1)
 WEST_ROOM_METADATA['west_window_centers_m']=[w[0] for w in westwins];WEST_ROOM_METADATA['west_windows_source']='Core-supplied schedule or twelve original-plan gaps normalized to agreed approximate room bounds'
 # Three broad rectangular apertures between the two HISTORIC rooms.
 partition_holes=[(38.87,3.48,5.12),(44.13,3.48,5.12),(49.39,3.48,5.12)]
 wall_y_portals(partition,x0,x1,8.84,partition_holes,WEST_CREAM,'West real three-opening reading cafe partition',.54)
 for sign in [-1,1]:
  p=partition+sign*.29
  west_wall_panels(p,x0,x1,'y',sign,partition_holes)
  for c,w,top in partition_holes:
   for s in [-1,1]:west_pilaster(c+s*(w/2+.19),p+sign*.095,axis='y',sign=sign,width=.43)
   # Full-depth timber reveals, not a facade pasted onto solid partition.
   for s in [-1,1]:west_block((c+s*w/2,partition,2.63),(.072,.65,4.98),WEST_WOOD,'West broad opening vertical timber-cased reveals')
   west_block((c,partition,5.145),(w+.07,.65,.10),WEST_WOOD,'West broad opening horizontal timber-cased soffits',grain=0)
 # South cafe wall finish leaves corridor passage clear; secondary module owns wall/door.
 south_portals=[(44.1,3.0,3.60)]
 west_wall_panels(23.345,x0,x1,'y',-1,south_portals)
 west_doorcase(44.1,23.31,3.0,3.60,'y',-1)
 west_panel_box((x0+x1)/2,23.39,7.405,x1-x0,.15,2.99,WEST_CREAM,'West cafe upper wall above connecting corridor')
 west_ceiling(x0,x1,read_y0,partition,7,4);west_ceiling(x0,x1,partition,cafe_y1,7,3)
 for yy in [8.0,12.1]:
  for xx in [39.3,44.1,48.9]:west_pendant(xx,yy,8.48,6.32)
 for xx in [39.3,44.1,48.9]:
  for yy in [17.35,21.30]:west_pendant(xx,yy,8.48,6.32)

 GROUP='09 WEST HISTORIC RESTAURANT | scored plaster shell, 2026 finish unresolved'
 y0=28.85;y1=51.45
 west_block(((x0+x1)/2,(y0+y1)/2,.01),(x1-x0,y1-y0,.18),WEST_SLAB,'West restaurant documented unfinished floor substrate')
 # Preserve documented adjacency to former lunch-counter room via two true portals.
 rest_portals=[(33.8,2.4,3.7),(46.1,2.4,3.7)]
 wall_x_portals(x0+.09,y0,y1,7.62,rest_portals,WEST_CREAM,'West restaurant inner wall with lunch-counter portals',.18)
 for aa,bb in west_spans(y0,y1,rest_portals):
  west_panel_box((aa+bb)/2,x0+.195,.30,bb-aa,.055,.40,'Warm Mankato column stone','West restaurant perimeter stone skirting',axis='x')
 for yy in [y0,y1]:
  if yy==y0:
   # Secondary corridor wall is solid only around its 3 m real opening below5.55.
   west_block(((x0+x1)/2,yy,6.59),(x1-x0,.23,2.07),WEST_CREAM,'West restaurant upper wall over corridor')
   for aa,bb in west_spans(x0,x1,[(44.1,3.0)]):west_panel_box((aa+bb)/2,yy+.14,.30,bb-aa,.08,.40,'Warm Mankato column stone','West restaurant north stone skirting')
  else:
   wall_y_portals(yy,x0,x1,7.62,[(44.13,3.1,3.6)],WEST_CREAM,'West restaurant south opening toward concourse',.26)
   for aa,bb in west_spans(x0,x1,[(44.13,3.1)]):west_panel_box((aa+bb)/2,yy-.16,.30,bb-aa,.08,.40,'Warm Mankato column stone','West restaurant south stone skirting')
 # Outer west wall is core-owned; no opaque duplicate wall and no fabricated window decals.
 # Interior plaster follows the same plan-calibrated core window list; no new glazing.
 restwins=[win for win in facade_wins if win[0]-win[1]/2>=y0 and win[0]+win[1]/2<=y1]
 west_restaurant_window_liner(restwins)
 WEST_ROOM_METADATA['restaurant_west_window_centers_m']=[w[0] for w in restwins]
 for yy in [y0,y1]:west_doorcase(44.1 if yy==y0 else 44.13,yy+(.15 if yy==y0 else -.16),3. if yy==y0 else 3.1,3.60,'y',1 if yy==y0 else -1)
 gx=[36.61,42.32,45.89,51.65]
 gy=[29.28,32.14,38.31,41.82,47.91,51.02]
 WEST_ROOM_METADATA['restaurant_grid_m']={'x':gx,'y':gy,'basis':'2 internal pier lines x4 internal rows proportioned from enlarged1914 raster; alternating bay widths, unsurveyed'}
 for xx in gx:
  for yy in gy:west_pier(xx,yy,.50 if yy in [gy[0],gy[-1]] and xx in gx[1:-1] else .84)
 for i in range(3):
  for j in range(5):
   cx=(gx[i]+gx[i+1])/2;cy=(gy[j]+gy[j+1])/2;hx=(gx[i+1]-gx[i])/2;hy=(gy[j+1]-gy[j])/2
   west_sail(cx,cy,hx,hy)
   if (i+j)%2==0:west_pendant(cx,cy,7.31,5.90,'West restaurant')
 # Repeated plaster arches supporting and separating the sail bays.
 for yy in gy:
  for i in range(3):
   width=gx[i+1]-gx[i]-.84;arch((gx[i+1]+gx[i])/2,yy,4.58,width,1.88,.26,.84,WEST_CREAM,'West restaurant transverse scored-plaster arch',30);west_arch_scores((gx[i+1]+gx[i])/2,yy,4.58,width,1.88)
 for xx in gx:
  for j in range(5):
   width=gy[j+1]-gy[j]-.84;arch((gy[j+1]+gy[j])/2,xx,4.58,width,1.88,.26,.84,WEST_CREAM,'West restaurant longitudinal scored-plaster arch',30,'side');west_arch_scores((gy[j+1]+gy[j])/2,xx,4.58,width,1.88,axis='x')
 # Partial publicly visible former lunch-counter continuation. Historic extent only;
 # the original lunch counter, appliances and current tenant fit-out are not inferred.
 GROUP='09B FORMER LUNCH COUNTER | partial documented open shell, current use unresolved'
 lx0=24.70;lx1=36.16;ly0=31.72;ly1=51.45
 west_block(((lx0+lx1)/2,(ly0+ly1)/2,.01),(lx1-lx0,ly1-ly0,.18),WEST_SLAB,'Former lunch counter observed shell floor continuation')
 # North limit abuts the existing hall rear wall; no invented opening into it.
 west_block(((lx0+lx1)/2,ly0,3.81),(lx1-lx0,.18,7.62),WEST_CREAM,'Former lunch counter north hall boundary')
 # Exact former ticket-office connections remain open at the east limit; no sealed
 # wall is fabricated from an unseen arrangement. The partial ceiling is intentional.
 lx=[24.97,30.72,36.61]
 for xx in lx[:-1]:
  for yy in gy[1:]:west_pier(xx,yy)
 for i in range(2):
  for j in range(1,5):
   cx=(lx[i]+lx[i+1])/2;cy=(gy[j]+gy[j+1])/2;hx=(lx[i+1]-lx[i])/2;hy=(gy[j+1]-gy[j])/2
   west_sail(cx,cy,hx,hy)
   if (i+j)%2==0:west_pendant(cx,cy,7.31,5.90,'Former lunch counter')
 for yy in gy[1:]:
  for i in range(2):arch((lx[i+1]+lx[i])/2,yy,4.58,lx[i+1]-lx[i]-.84,1.88,.26,.84,WEST_CREAM,'Former lunch counter transverse plaster arch',30);west_arch_scores((lx[i+1]+lx[i])/2,yy,4.58,lx[i+1]-lx[i]-.84,1.88)
 for xx in lx[:-1]:
  for j in range(1,5):arch((gy[j+1]+gy[j])/2,xx,4.58,gy[j+1]-gy[j]-.84,1.88,.26,.84,WEST_CREAM,'Former lunch counter longitudinal plaster arch',30,'side');west_arch_scores((gy[j+1]+gy[j])/2,xx,4.58,gy[j+1]-gy[j]-.84,1.88,axis='x')
 WEST_ROOM_METADATA['partial_lunch_counter']={'extent_m':[lx0,lx1,ly0,ly1,.10,7.62],'basis':'1914 plan adjacency and p49 east-looking vista; partial architectural shell, no old counter or current tenant fit-out','limits':'Narrow north ceiling strip and further east office/service connections unresolved; photograph does not establish complete present partition inventory'}
 WEST_ROOM_METADATA['restaurant_east_portals_m']=rest_portals
 WEST_ROOM_CAMERAS['restaurant_lunch_counter']=((50.5,33.8,1.76),(26.4,33.8,4.0),23)
 scene['west_public_room_evidence']=json.dumps(WEST_ROOM_METADATA)
scene['west_public_room_evidence']=json.dumps(WEST_ROOM_METADATA)
GROUP = _west_previous_group
