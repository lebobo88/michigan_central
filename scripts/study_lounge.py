"""The Study at Michigan Central: photographed 2025-completed public lounge in 2026.
Executed in build_station.py's batch context. Current era only; restores GROUP.
Source photos are study-only and never loaded into scene materials.
Net shell is plan-proportioned, not surveyed. Shared north/east openings remain core-owned.
"""
# HNS reports a nominal28-foot coffered ceiling; no measured Z datum or
# beam-soffit/coffer-field reference is supplied. Interpret the published height
# above the modeled finished floor, placing the upper plaster field at8.6344m.
STUDY_CEILING_HEIGHT_M=28*.3048
STUDY_BOUNDS=(-52.10,-36.16,4.95,20.40,.10,.10+STUDY_CEILING_HEIGHT_M)
STUDY_EAST_WINDOW_CENTERS=[9.98,13.94,17.94]
STUDY_EAST_BLIND_NICHE_CENTER=5.94
STUDY_CAMERAS={
 'study_lounge':((-44.05,19.58,1.85),(-44.0,6.1,3.7),23),
 'study_lounge_reverse':((-49.3,6.15,1.90),(-42.0,18.4,3.55),23),
 'study_lounge_detail':((-40.0,16.6,1.72),(-44.15,12.9,1.98),34),
 'study_lounge_northeast':((-37.35,18.85,1.82),(-47.7,7.2,3.52),24),
}
STUDY_SOURCES={
 'primary':'https://www.mergearchitects.com/projects/michigan-central-the-study/',
 'placement':'https://www.neumannsmith.com/wp-content/uploads/2025/09/vision_scope2.jpg',
 'published_ceiling_height':'https://www.neumannsmith.com/michigan-central-station-interior-fit-out/',
 'blind_niche_photo':'https://historicdetroit.org/galleries/michigan-central-station-post-renovation-interior',
 'built_photos':['01','02','03','06','10','11','13','14','15','16','17','18','19','20'],
 'design_documents':['04','05','07','08','09','12'],
 'outside_room':['21','22'],
}

def study_xy(x,y,c=(0,0),angle=0):
 return (c[0]+x*cos(angle)-y*sin(angle),c[1]+x*sin(angle)+y*cos(angle))

def study_prism(points,z0,z1,material,name,c=(0,0),angle=0):
 xy=[study_xy(x,y,c,angle) for x,y in points];n=len(xy)
 vv=[(x,y,z) for z in [z0,z1] for x,y in xy]
 ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 addmesh(vv,ff,material,name)

def study_rectpoly(w,d,r=.08,n=8):
 out=[];r=min(r,w/2,d/2)
 for cx,cy,a in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,pi/2),(-w/2+r,-d/2+r,pi),(w/2-r,-d/2+r,3*pi/2)]:
  out.extend((cx+r*cos(a+i*pi/(2*n)),cy+r*sin(a+i*pi/(2*n))) for i in range(n+1))
 return out

def study_block(c,w,d,z0,z1,material,name,r=.01,angle=0):
 study_prism(study_rectpoly(w,d,r),z0,z1,material,name,c,angle)

def study_cushion(c,w,d,z,h,material,name,r=.15,angle=0):
 # Beveled mesh surfaces remain exportable without procedural shader dependencies.
 vv=[];ff=[];profiles=[(.93,.93,0),(1,1,h*.23),(1,1,h*.70),(.93,.93,h)]
 for sx,sy,dz in profiles:
  for x,y in study_rectpoly(w*sx,d*sy,min(r,w*.28,d*.28),10):
   xx,yy=study_xy(x,y,c,angle);vv.append((xx,yy,z+dz))
 n=len(vv)//len(profiles)
 for j in range(len(profiles)-1):
  for i in range(n):ff.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 ff.extend([tuple(range(n-1,-1,-1)),tuple(range((len(profiles)-1)*n,len(vv)))])
 addmesh(vv,ff,material,name)

def study_arcback(c,rx,ry,z0,z1,thick,material,name,angle=0,tilt=.06,start=-.17,end=pi+.17):
 vv=[];n=36
 for dz in [0,z1-z0]:
  for offset in [0,-thick]:
   for i in range(n+1):
    a=start+(end-start)*i/n;x=(rx+offset)*cos(a);y=(ry+offset)*sin(a)+tilt*dz/(z1-z0)
    xx,yy=study_xy(x,y,c,angle);vv.append((xx,yy,z0+dz))
 s=n+1;ff=[]
 for i in range(n):ff.extend([(i,i+1,2*s+i+1,2*s+i),(s+i,3*s+i,3*s+i+1,s+i+1),(i,s+i,s+i+1,i+1),(2*s+i,2*s+i+1,3*s+i+1,3*s+i)])
 ff.extend([(0,2*s,3*s,s),(n,s+n,3*s+n,2*s+n)])
 addmesh(vv,ff,material,name)

def study_chair(x,y,angle=0,kind='desk'):
 c=(x,y);z=.10
 if kind=='stool':w=.51;d=.47;seat=.79;back=1.09;material='Study green leather';leg=.013
 elif kind=='lounge':w=.80;d=.81;seat=.46;back=1.10;material='Study wine wool';leg=.016
 elif kind=='tub':w=.87;d=.83;seat=.44;back=.82;material='Study tan leather';leg=.013
 else:w=.52;d=.51;seat=.48;back=.88;material='Study bluegray wool';leg=.013
 if kind=='tub':
  study_block(c,w,d,z+.045,z+seat,material,'Study tan lounge chair upholstered base',.37,angle)
 else:
  for dx in [-w*.35,w*.35]:
   for dy in [-d*.31,d*.31]:
    p=study_xy(dx*1.18,dy*1.30,c,angle);q=study_xy(dx,dy,c,angle)
    beam((p[0],p[1],z+.025),(q[0],q[1],z+seat),leg,'Study black steel','Study slender chair legs',8)
  if kind=='stool':
   for dx in [-w*.35,w*.35]:
    p=study_xy(dx,-d*.4,c,angle);q=study_xy(dx,d*.4,c,angle);beam((*p,z+.27),(*q,z+.27),.010,'Study black steel','Study stool foot rails',8)
   p=study_xy(-w*.35,-d*.4,c,angle);q=study_xy(w*.35,-d*.4,c,angle);beam((*p,z+.27),(*q,z+.27),.010,'Study black steel','Study stool foot rails',8)
 study_cushion(c,w,d,z+seat-.09,.12,material,'Study upholstery '+kind+' seat',.20,angle)
 if kind=='stool':
  for dx in [-w*.35,w*.35]:
   p=study_xy(dx,d*.2,c,angle);beam((*p,z+seat),(*p,z+back-.16),.011,'Study black steel','Study stool back uprights',8)
  study_arcback(c,w*.51,d*.45,z+back-.20,z+back,.07,material,'Study upholstery green curved stool backs',angle,.0)
 else:
  study_arcback(c,w*.51,d*.44,z+seat-.015,z+back,.065 if kind=='desk' else .11,material,'Study upholstery '+kind+' sculpted back',angle,.12 if kind=='lounge' else .035)


def study_brass_top(c,w,d,z,name,angle=0,r=.04):
 study_block(c,w,d,z-.065,z-.006,'Study brass',name+' brass rim',r,angle)
 study_block(c,w-.033,d-.033,z-.008,z+.004,'Study furniture oak',name+' oak surface',max(.01,r-.02),angle)

def study_square_ring(c,half,r,z0,z1,material,name,n=80):
 # Square outer ring around a real open circular hole. No texture-only aperture.
 vv=[]
 for z in [z0,z1]:
  for out in [False,True]:
   for i in range(n):
    a=2*pi*i/n;rad=half/max(abs(cos(a)),abs(sin(a))) if out else r
    vv.append((c[0]+rad*cos(a),c[1]+rad*sin(a),z))
 ff=[]
 for i in range(n):
  j=(i+1)%n;ff.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
 addmesh(vv,ff,material,name)

def study_leaf(p,tip,width,material,name):
 p=Vector(p);tip=Vector(tip);d=tip-p;side=d.cross(Vector((0,0,1)))
 if side.length<.01:side=Vector((1,0,0))
 side.normalize();mid=p+d*.46;ridge=mid+Vector((0,0,width*.18))
 vv=[tuple(p),tuple(mid+side*width*.5),tuple(tip),tuple(mid-side*width*.5),tuple(ridge)]
 addmesh(vv,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],material,name)

def study_palm(x,y,h,seed):
 rr=random.Random(seed);z=.95
 drift=Vector((rr.uniform(-.20,.20),rr.uniform(-.20,.20),h-z));base=Vector((x,y,z));crown=base+drift
 beam(base,crown,.031,'Study palm stem','Study palm trunks',10)
 for zz in [z+.15+i*.27 for i in range(int((h-z)/.27))]:
  t=(zz-z)/(h-z);cx=x+drift.x*t;cy=y+drift.y*t;lathe((cx,cy,zz),[(.032,0),(.034,.012),(.032,.021)],'Study palm pale ring','Study palm trunk rings',10)
 for frond in range(9):
  a=frond*2*pi/9+rr.random()*.31;length=rr.uniform(1.25,1.9);rise=rr.uniform(.2,1.1);pts=[]
  for j in range(13):
   t=j/12;pts.append(crown+Vector((cos(a)*length*t,sin(a)*length*t,rise*sin(pi*t*.8)-.30*t*t)))
  for j in range(12):beam(pts[j],pts[j+1],.009*(1-j/17),'Study palm stem','Study palm frond ribs',5)
  for j in range(2,12):
   t=j/12;p=pts[j];wid=.43*sin(pi*t)**.6
   for s in [-1,1]:
    tip=p+Vector((s*-sin(a)*wid+cos(a)*.23,s*cos(a)*wid+sin(a)*.23,-.04-.13*t))
    study_leaf(p,tip,.054,'Study leaf '+str((j+frond)%3),'Study palm individual leaflets')

def study_vine_planter(x,y,seed):
 rr=random.Random(seed);study_block((x,y),.47,.47,.10,1.12,'Study furniture oak','Study freestanding square vine planters',.018)
 study_block((x,y),.41,.41,1.112,1.125,'Study moss','Study planter soil and moss',.012)
 for dx in [-.17,0,.17]:
  for dy in [-.14,.14]:beam((x+dx,y+dy,1.14),(x+dx,y+dy,STUDY_BOUNDS[5]-.23),.006,'Study black steel','Study ceiling suspended plant trellis wires',5)
 box((x,y,STUDY_BOUNDS[5]-.23),(.48,.38,.035),'Study black steel','Study trellis ceiling plate')
 for i in range(800):
  zz=rr.uniform(1.12,2.7) if i<390 else rr.uniform(2.7,6.33);spread=.24 if zz<2.7 else .18;aa=rr.uniform(0,2*pi);xx=x+rr.uniform(0,spread)*cos(aa);yy=y+rr.uniform(0,spread)*sin(aa)
  le=rr.uniform(.16,.28) if zz<2.7 else rr.uniform(.07,.16)
  study_leaf((xx,yy,zz),(xx+le*cos(aa),yy+le*sin(aa),zz-le*.55),le*.68,'Study leaf '+str(i%3),'Study climbing vine individual leaves')


def study_bar(cx,cy):
 half=1.92;cell=half*2/3;z=1.20
 for i in [-1,0,1]:
  for j in [-1,0,1]:
   c=(cx+i*cell,cy+j*cell)
   if i==0 and j==0:
    study_square_ring(c,cell/2,.65,z-.075,z-.003,'Study brass','Study central bar real circular well brass')
    study_square_ring(c,cell/2-.012,.66,z-.001,z+.008,'Study furniture oak','Study central bar real circular well oak')
    lathe((cx,cy,.12),[(.66,0),(.66,z-.13),(.65,z-.13),(.65,0)],'Study furniture oak','Study central bar inner circular well',72)
   elif abs(i)==1 and abs(j)==1:
    study_square_ring(c,cell/2,.22,z-.075,z-.003,'Study brass','Study bar planter opening brass')
    study_square_ring(c,cell/2-.012,.23,z-.001,z+.008,'Study furniture oak','Study bar planter opening oak')
    lathe((c[0],c[1],z-.032),[(.215,0),(.215,.025)],'Study moss','Study palm moss circular inserts',32)
    # Scalloped concave outer corner supports distinguish the bespoke module.
    poly=[(-.53,-.53),(.53,-.53),(.53,0)]+[(.53+.53*cos(-pi/2-k*pi/24),.53+.53*sin(-pi/2-k*pi/24)) for k in range(1,13)]+[(-.53,.53)]
    poly=[(u*i,v*j) for u,v in poly]
    if i*j<0:poly.reverse()
    study_prism(poly,.12,z-.075,'Study furniture oak','Study bar concave scalloped oak supports',c)
    for k in range(2):study_palm(c[0]+(k-.5)*.11,c[1]+(k-.5)*.11,4.75+((i+j+k+4)%3)*.31,130+i*9+j*3+k)
   else:study_brass_top(c,cell,cell,z+.002,'Study central bar rectangular module')
 for s in [-1,1]:
  for off in [-.80,0,.80]:
   study_chair(cx+off,cy+s*(half+.32),0 if s>0 else pi,'stool')
   study_chair(cx+s*(half+.32),cy+off,-pi/2 if s>0 else pi/2,'stool')
 # Continuous full-height brass corner straps and middle-panel bases.
 for side in [-1,1]:
  for axis in [0,1]:
   cc=(cx+side*1.72,cy) if axis==0 else (cx,cy+side*1.72)
   study_block(cc,.65,2.30,.12,z-.075,'Study furniture oak','Study bar lower oak modular pedestals',.02,0 if axis==0 else pi/2)
 for dx in [-half,half]:
  for dy in [-half,half]:box((cx+dx,cy+dy,(z+.12)/2),(.033,.033,z-.12),'Study brass','Study bar full height brass straps')


def study_table(cx,cy,angle=0,count=6):
 c=(cx,cy);w=3.05;d=.92;z=.86
 study_block(c,w,d,z-.065,z,'Study furniture oak','Study modular desk rounded oak tabletop',.22,angle)
 for u in [-.55,.55]:
  cc=study_xy(u,0,c,angle);study_block(cc,.43,.78,.11,z-.055,'Study furniture oak','Study modular desk oak panel bases',.015,angle)
  p=study_xy(u-.225,0,c,angle);study_block(p,.035,d,z,z+.004,'Study brass','Study modular desk inlaid brass routes',.002,angle)
  p=study_xy(u,0,c,angle);study_block(p,.44,.035,z,z+.004,'Study brass','Study modular desk inlaid brass routes',.002,angle)
 for v in [-1,1]:
  for u in ([-1.02,0,1.02] if count==6 else [-.95,.95]):
   p=study_xy(u,v*.79,c,angle);study_chair(*p,angle+(0 if v>0 else pi),'desk')


def study_low_modules(cx,cy,angle=0):
 # One installed multi-height arrangement, never every alternate study13..17 at once.
 c=(cx,cy)
 for i,(u,v,h) in enumerate([(-.64,-.65,.46),(.64,-.65,.46),(-.64,.65,.76),(.64,.65,.76)]):
  cc=study_xy(u,v,c,angle);study_block(cc,1.27,1.28,.10,h+.10,'Study furniture oak','Study adaptable stepped oak seating modules',.055,angle)
  p=study_xy(u-.30,v,c,angle);study_block(p,.035,1.28,h+.10,h+.108,'Study brass','Study low module brass inlay',.002,angle)
  p=study_xy(u-.30,v-.655,c,angle);study_block(p,.035,.023,.11,h+.10,'Study brass','Study low module vertical brass strap',.002,angle)
  if i<2:study_cushion(cc,1.13,1.04,h+.11,.085,'Study bluegray wool','Study upholstery movable curved floor cushions',.40,angle)
 for u in [-.60,.60]:
  p=study_xy(u,1.64,c,angle);study_chair(*p,angle,'desk')


def study_coffee(cx,cy,angle=0):
 c=(cx,cy);study_block(c,1.8,.49,.48,.535,'Study furniture oak','Study low slender rectangular oak coffee tables',.02,angle)
 for u in [-.78,.78]:
  for v in [-.18,.18]:
   p=study_xy(u,v,c,angle);q=study_xy(u*.91,v*.94,c,angle);beam((*p,.10),(*q,.49),.025,'Study furniture oak','Study coffee table tapered legs',6)

def study_rug(cx,cy,w,d,angle=0,colors=('Study rug blue','Study rug green')):
 for i,col in enumerate(colors):
  p=study_xy((i-.5)*w/2,0,(cx,cy),angle);study_block(p,w/2,d,.107,.122,col,'Study woven color block rugs',.004,angle)
 for side in [-1,1]:
  p=study_xy(0,side*(d/2-.016),(cx,cy),angle);study_block(p,w,.03,.123,.126,'Study rug border','Study rug dark bound edges',.002,angle)

def study_sofa(cx,cy,angle=0,material='Study bluegray wool'):
 c=(cx,cy)
 study_cushion(c,3.30,1.30,.16,.38,material,'Study upholstery rounded sofa plinth',.59,angle)
 for u in [-.70,.06,.81]:
  p=study_xy(u,-.22,c,angle);study_cushion(p,.73,.64,.50,.09,material,'Study upholstery sofa individual seats',.14,angle)
  p=study_xy(u,.24,c,angle);study_cushion(p,.76,.25,.56,.43,material,'Study upholstery sofa raised back cushions',.12,angle)


def study_wall_panel(u0,u1,plane,axis,inward):
 # Slim finish placed on the room side only, with window/door intervals omitted by caller.
 def pt(u,z,off=0):return (u,plane+inward*off,z) if axis=='y' else (plane+inward*off,u,z)
 def bx(u,z,w,h,depth,m,name,off=0):box(pt(u,z,off),(w,depth,h) if axis=='y' else (depth,w,h),m,name)
 n=max(1,round((u1-u0)/.95));width=(u1-u0)/n
 bx((u0+u1)/2,1.56,u1-u0,2.37,.052,'Study panel walnut','Study historical dark timber dado',.055)
 for z,w,h in [(.35,.09,.12),(2.63,.12,.12),(2.74,.16,.08),(2.91,.19,.07)]:
  bx((u0+u1)/2,z,u1-u0,h,w,'Study panel walnut','Study timber dado layered crown rails',.12)
 bx((u0+u1)/2,.22,u1-u0,.25,.07,'Warm Mankato column stone','Study pale stone skirting',.09)
 for i in range(n):
  u=u0+(i+.5)*width
  bx(u,1.48,width-.18,1.87,.035,'Study panel walnut','Study raised timber field panels',.102)
  for delta in [-(width-.14)/2,(width-.14)/2]:bx(u+delta,1.48,.029,2.00,.024,'Study panel highlight','Study field panel molded edges',.135)
  for z in [.48,2.48]:bx(u,z,width-.14,.029,.024,'Study panel highlight','Study field panel molded edges',.135)
  for delta in [-width/2,width/2]:
   bx(u+delta,1.50,.10,2.13,.09,'Study panel walnut','Study timber panel pilasters',.145)
   bx(u+delta,2.55,.15,.12,.13,'Study panel walnut','Study timber pilaster capitals',.17)
 for i in range(int((u1-u0)/.17)):
  u=u0+.09+i*.17
  for s in [-1,1]:beam(pt(u-.058,2.815,.18),pt(u+.058,2.815+s*.042,.18),.006,'Study panel highlight','Study simplified interlace frieze',5)

def study_intervals(lo,hi,openings):
 c=lo;out=[]
 for u,w in sorted(openings):
  if u-w/2>c:out.append((c,u-w/2))
  c=max(c,u+w/2)
 if c<hi:out.append((c,hi))
 return out

def build_study_lounge():
 global GROUP
 if AGED:return
 saved_group=GROUP;GROUP='07 THE STUDY | documented public lounge completed2025'
 x0,x1,y0,y1,floor,ceil=STUDY_BOUNDS;cx=(x0+x1)/2;cy=(y0+y1)/2
 # Every image is original procedural artwork. No research directory is referenced by shaders.
 ap=ROOT/'manifests/study_lounge/assets'
 def mapped(name,file,rough=.66,metal=0,scale=1.1):
  m=mat(name,(.25,.18,.11),rough,metal);p=m.node_tree.nodes.get('Principled BSDF');tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ap/(file+'_color.png')),check_existing=True);m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
  rp=ap/(file+'_rough.png')
  if rp.exists():
   t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(rp),check_existing=True);t.image.colorspace_settings.name='Non-Color';m.node_tree.links.new(t.outputs['Color'],p.inputs['Roughness'])
  m['texture_repeat_m']=scale;m['texture_provenance']='Original deterministic procedural pattern, not a photographic scan';return m
 for name,file,rough,scale in [('Study cream ashlar','cream_stone',.8,4.0),('Study furniture oak','oak',.4,1.20),('Study panel walnut','panel_walnut',.43,1.35),('Study bluegray wool','bluegray',.90,.15),('Study wine wool','wine',.89,.15),('Study tan leather','tan',.45,.18),('Study green leather','green',.43,.18),('Study rug blue','rug_blue',.97,.20),('Study rug green','rug_green',.97,.20),('Study rug gray','rug_gray',.98,.20),('Study rug brown','rug_brown',.98,.20)]:mapped(name,file,rough,scale=scale)
 for name,color,rough,metal in [('Study brass',(.54,.37,.12),.29,.8),('Study black steel',(.018,.022,.018),.30,.6),('Study moss',(.085,.14,.029),.97,0),('Study leaf 0',(.025,.10,.025),.57,0),('Study leaf 1',(.040,.16,.035),.57,0),('Study leaf 2',(.075,.20,.043),.57,0),('Study palm stem',(.19,.29,.12),.68,0),('Study palm pale ring',(.48,.50,.35),.75,0),('Study panel highlight',(.071,.043,.026),.45,0),('Study rug border',(.014,.021,.033),.95,0),('Study curtain',(.66,.59,.46),.96,0)]:mat(name,color,rough,metal)
 fm=M['Historic walnut herringbone'].copy();fm.name='Study scaled walnut parquet';fm['texture_repeat_m']=1.2;M[fm.name]=fm
 box((cx,cy,.01),(x1-x0,y1-y0,.18),'Study scaled walnut parquet','Study restored walnut herringbone floor')
 for x in [x0+.23,x1-.23]:box((x,cy,.105),(.46,y1-y0,.025),'Warm Mankato column stone','Study pale stone floor perimeter')
 for y in [y0+.23,y1-.23]:box((cx,y,.105),(x1-x0-.92,.46,.025),'Warm Mankato column stone','Study pale stone floor perimeter')
 # South partition relocated from old provisional Y23.0 to photo/plan-supported Y20.4.
 wall_y_portals(y1+.075,x0,x1,ceil,[(cx,1.88,2.62)],'Study cream ashlar','Study south wall with actual double door',.15)
 wall_x_portals(x1-.025,y0,y1,ceil,[(16.2,2.4,3.65)],'Study cream ashlar','Study west finish with hall portal',.06)
 # Thin interior facing stones, preserving the core's real six arched exterior apertures.
 nx=[-48.419,-44.069,-39.719];ny=STUDY_EAST_WINDOW_CENTERS
 for xx in nx:wall_with_arch(xx,y0-.025,4.35,ceil,2.4384,6.2484,base=1.0,matname='Study cream ashlar',depth=.06)
 for aa,bb in [(x0,nx[0]-2.175),(nx[-1]+2.175,x1)]:box(((aa+bb)/2,y0-.025,ceil/2),(bb-aa,.06,ceil),'Study cream ashlar','Study north end facing stone')
 for lo,hi in study_intervals(x0,x1,[(v,2.56) for v in nx]):study_wall_panel(lo,hi,y0,'y',1)
 for lo,hi in study_intervals(y0,y1,[(v,2.56) for v in ny]+[(STUDY_EAST_BLIND_NICHE_CENTER,2.32)]):study_wall_panel(lo,hi,x0,'x',1)
 for lo,hi in study_intervals(x0,x1,[(cx,2.06)]):study_wall_panel(lo,hi,y1,'y',-1)
 for lo,hi in study_intervals(y0,y1,[(16.2,2.58)]):study_wall_panel(lo,hi,x1,'x',-1)
 # East wall substrate is core-owned; a thin pierced interior ashlar finish preserves its apertures.
 swap_before=globals().get('SWAP_XY',False);globals()['SWAP_XY']=True
 # Variable registered center spacing: narrow arched strips plus solid intervals
 # avoid old equal-bay gaps and keep the facing strictly inside the fixed room bounds.
 for yy in ny:wall_with_arch(yy,x0-.025,2.4784,ceil,2.4384,6.2484,base=1.0,matname='Study cream ashlar',depth=.06)
 globals()['SWAP_XY']=swap_before
 for lo,hi in study_intervals(y0,y1,[(yy,2.4784) for yy in ny]):
  box((x0-.025,(lo+hi)/2,ceil/2),(.06,hi-lo,ceil),'Study cream ashlar','Study east registered pier facing stone')
 for xx in nx:
  arch(xx,y0+.06,6.0292,2.3384,1.1692,.20,.12,'Warm Mankato column stone','Study north inner arch reveal',32)
  for s in [-1,1]:box((xx+s*1.273,y0+.06,3.48),(.10,.12,5.0),'Warm Mankato column stone','Study north inner window jamb')
  box((xx,y0+.055,.66),(2.43,.09,.64),'Study panel walnut','Study beneath window radiator enclosures')
 for yy in ny:
  arch(yy,x0+.075,6.0292,2.3384,1.1692,.20,.12,'Warm Mankato column stone','Study east inner arch reveal',32,'side')
  for s in [-1,1]:box((x0+.075,yy+s*1.273,3.48),(.12,.10,5.0),'Warm Mankato column stone','Study east inner window jamb')
  box((x0+.075,yy,.66),(.09,2.43,.64),'Study panel walnut','Study beneath window radiator enclosures')
 # post_p68 shows a SOLID blind arched bay north of the three east windows.
 # Retain the core's solid backing: this is an ashlar field with shallow raised
 # trim, never a fourth glazed aperture. Its northern side is partly in the
 # retained north return; clip the visible field and arch to that room boundary.
 nc=STUDY_EAST_BLIND_NICHE_CENTER;nr=1.16;ns=7.2484-nr;nlo=max(y0+.015,nc-nr)
 nt=math.acos((nlo-nc)/nr)
 niche_outline=[(x0+.014,nlo,1.0),(x0+.014,nc+nr,1.0),(x0+.014,nc+nr,ns)]
 niche_outline.extend((x0+.014,nc+nr*cos(nt*i/40),ns+nr*sin(nt*i/40)) for i in range(1,41))
 addmesh(niche_outline,[tuple(range(len(niche_outline)))],'Study cream ashlar','Study solid blind arched niche ashlar field')
 nv=[];nf=[];nn=40
 for xp in [x0+.040,x0+.105]:
  for rr in [nr,nr+.11]:
   nv.extend((xp,max(nlo,nc+rr*cos(nt*i/nn)),ns+rr*sin(nt*i/nn)) for i in range(nn+1))
 st=nn+1
 for i in range(nn):nf.extend([(i,i+1,st+i+1,st+i),(2*st+i,3*st+i,3*st+i+1,2*st+i+1),(i,2*st+i,2*st+i+1,i+1),(st+i,st+i+1,3*st+i+1,3*st+i)])
 nf.extend([(0,st,3*st,2*st),(nn,2*st+nn,3*st+nn,st+nn)])
 addmesh(nv,nf,'Warm Mankato column stone','Study blind niche shallow arch molding')
 box((x0+.075,nc+nr+.05,(1.0+ns)/2),(.12,.10,ns-1.0),'Warm Mankato column stone','Study blind niche visible stone jamb')
 box((x0+.080,(nlo+nc+nr)/2,.64),(.09,nc+nr-nlo,.70),'Study panel walnut','Study blind niche plain low timber plinth')
 # Tie-back pleated curtains beside each opening, made as original mesh fabric.
 for axis,centers,plane,half,sill,top in [('y',nx,y0+.15,1.219,1.0,6.85),('x',ny,x0+.15,1.219,1.0,6.85)]:
  for cc in centers:
   for s in [-1,1]:
    vv=[];ff=[];rows=24;cols=10
    for iz in range(rows+1):
     t=iz/rows;z=sill+(top-sill)*t;gather=.13+.16*abs(t-.30)
     for j in range(cols+1):
      u=cc+s*(half-.06-j/cols*gather);off=.022*cos(j*pi*2)
      vv.append((u,plane+off,z) if axis=='y' else (plane+off,u,z))
    for iz in range(rows):
     for j in range(cols):k=iz*(cols+1)+j;ff.append((k,k+1,k+cols+2,k+cols+1))
    addmesh(vv,ff,'Study curtain','Study gathered sheer window curtain meshes')
 # South double-door leaves visible in photos; adjoining hidden service rooms are omitted.
 for s in [-1,1]:
  dc=cx+s*.46;box((dc,y1-.05,1.36),(.90,.08,2.50),'Study panel walnut','Study south double doors timber stiles')
  box((dc,y1-.103,1.51),(.63,.008,1.65),'Glass tower dark','Study south door glazed upper panels')
  for z in [.70,1.09,1.48,1.87,2.29]:box((dc,y1-.12,z),(.66,.035,.033),'Study panel walnut','Study door glazing subdivisions')
  box((dc,y1-.15,1.03),(.81,.035,.040),'Study black steel','Study south door panic bars')
 # Ceiling matches final photograph's fine parallel joists under three broader transverse beams.
 box((cx,cy,ceil+.075),(x1-x0,y1-y0,.15),'Decorative plaster','Study light plaster ceiling fields')
 for i in range(24):
  xx=x0+.3+i*(x1-x0-.6)/23;box((xx,cy,ceil-.105),(.14,y1-y0,.21),'Study panel walnut','Study ceiling narrow parallel timber joists')
  for delta in [-.085,.085]:box((xx+delta,cy,ceil-.042),(.040,y1-y0,.084),'Study panel walnut','Study ceiling fine joist molding')
 for yy in [y0+.24,y0+5.15,y0+10.30,y1-.24]:
  box((cx,yy,ceil-.30),(x1-x0,.36,.60),'Study panel walnut','Study broad transverse timber ceiling beams')
  for xx in [x0+.2,x1-.2]:
   for zz,w,d in [(ceil-.64,.39,.57),(ceil-.78,.27,.40),(ceil-.90,.19,.30)]:box((xx,yy,zz),(w,d,.14),'Study panel walnut','Study stepped carved bracket approximations')
 for xx in [x0+.18,x1-.18]:box((xx,cy,ceil-.26),(.35,y1-y0,.52),'Study panel walnut','Study perimeter ceiling beams')
 for ix,xx in enumerate([x0+2.15,x0+6.0,x0+9.85,x0+13.7]):
  for iy,yy in enumerate([y0+2.55,y0+7.68,y0+12.85]):
   drop=.70 if iy%2 else .90;beam((xx,yy,ceil-.04),(xx,yy,ceil-drop),.015,'Dark bronze','Study original-style pendant rods',8)
   lathe((xx,yy,ceil-drop-.43),[(.01,0),(.12,.035),(.19,.14),(.205,.27),(.16,.39),(.075,.45)],'Warm lamp glass','Study opal globe pendant lamps',24)
   lathe((xx,yy,ceil-drop+.01),[(.09,0),(.10,.04),(.13,.045),(.13,.070)],'Study brass','Study pendant brass caps',24)
 # Actual photographed installed furniture palette and circulation, positioned at inferred scale.
 study_bar(cx-.12,cy+.05)
 study_rug(x1-2.6,y0+7.9,3.4,3.7,pi/2,('Study rug blue','Study rug green'));study_sofa(x1-2.6,y0+7.9,pi/2)
 study_coffee(x1-3.8,y0+7.9,pi/2)
 study_rug(cx+1.3,y0+2.50,3.80,2.30,0,('Study rug gray','Study rug brown'));study_sofa(cx+1.3,y0+2.20,0,'Study wine wool');study_coffee(cx+1.3,y0+3.3)
 for yy in [y0+6.25,y0+10.75]:
  xx=x0+2.72;study_rug(xx,yy,3.15,3.65,0,('Study rug blue','Study rug green'));study_coffee(xx,yy,pi/2)
  for off in [-1,1]:
   study_chair(xx-.84,yy+off*1.03,pi/2,'lounge');study_chair(xx+.84,yy+off*.93,-pi/2,'tub')
 study_table(x1-2.7,y0+2.70,0,6)
 study_table(x1-2.7,y0+4.85,0,6)
 study_table(cx+2.2,y1-2.7,0,6)
 study_table(x0+2.65,y1-2.7,0,6)
 study_low_modules(x0+2.60,y0+2.15,pi/2)
 study_low_modules(x0+2.58,y1-6.0,pi/2)
 # Wall-hung climbing plants: photographed on both glazed elevations and opposite back wall.
 for i,xx in enumerate([x0+.55,-46.03,-41.68,x1-.60]):study_vine_planter(xx,y0+.53,400+i)
 for i,yy in enumerate([7.96,11.96,15.94,y1-.65]):study_vine_planter(x0+.49,yy,500+i)
 for i,xx in enumerate([x0+2.0,x0+5.4,x1-5.4,x1-1.0]):study_vine_planter(xx,y1-.51,600+i)
 # Photograph-backed wall wash is implemented with small area lights, not a bright texture strip.
 for axis,u0,u1,plane,inward in [('y',x0,x1,y1,-1),('x',y0,y1,x1,-1)]:
  for i in range(5):
   u=u0+(i+.5)*(u1-u0)/5;ld=bpy.data.lights.new('Study concealed dado uplight','AREA');ld.energy=36;ld.color=(1,.70,.39);ld.shape='RECTANGLE';ld.size=2.7;ld.size_y=.15
   ob=bpy.data.objects.new('Study concealed dado uplight',ld);scene.collection.objects.link(ob);ob.location=(u,plane+inward*.17,2.95) if axis=='y' else (plane+inward*.17,u,2.95);ob.rotation_euler=(pi,0,0 if axis=='y' else pi/2)
 scene['study_coverage']='The Study: 2025-completed photographed public lounge; plan-proportioned room, furniture configuration interprets 2026 published built photos. Hidden service spaces omitted.'
 GROUP=saved_group

build_study_lounge()
