"""Original plaster cartouche relief, parametrically scaled to published11ft height.
This is a modeled ornamental approximation, not a carving scan. It is built in a
vertical X/Z plane; callers must supply a source-supported wall/front location.
No reference image is loaded. Existing builder material/mesh helpers are reused.
"""
def hall_cartouche(cx,front_y,bottom,height=3.3528,face=1,material='Decorative plaster'):
 before={k:len(v[0]) for k,v in B.items()}
 s=height/3.3528
 def pos(x,d,z):return (cx+x*s,front_y+face*d*s,bottom+z*s)
 def mesh(v,f,label):
  # Keep winding outward for either face orientation and planar metric UVs perface.
  w=[pos(*p) for p in v];ff=f if face==1 else [tuple(reversed(q)) for q in f]
  u=[]
  for q in f:
   pts=[Vector(v[i]) for i in q];n=(pts[1]-pts[0]).cross(pts[2]-pts[0]);axis=max(range(3),key=lambda i:abs(n[i]));axes=[i for i in range(3) if i!=axis]
   u.append([(v[i][axes[0]]*s,v[i][axes[1]]*s) for i in q])
  if face==-1:u=[list(reversed(q)) for q in u]
  addmesh(w,ff,material,'hall cartouche '+label,face_uv=u)
 def tube(points,r,label,segments=12):
  # Continuous swept cross-section, no per-segment caps or coincident disks.
  closed=(Vector(points[0])-Vector(points[-1])).length<1e-7
  pts=[Vector(p) for p in points];nv=segments+1;vv=[];uv=[];dist=0
  for j,p in enumerate(pts):
   if j:dist+=(p-pts[j-1]).length
   prev=pts[j-1] if j else pts[-2] if closed else pts[0]
   nxt=pts[j+1] if j+1<len(pts) else pts[1] if closed else pts[-1]
   tangent=(nxt-prev).normalized();u=tangent.cross(Vector((0,1,0))).normalized();v=tangent.cross(u).normalized()
   for k in range(nv):
    t=2*pi*k/segments;q=p+r*(u*cos(t)+v*sin(t));vv.append(tuple(q));uv.append((dist*s,t*r*s))
  ff=[];fu=[]
  for j in range(len(pts)-1):
   for k in range(segments):
    a=j*nv+k;f=(a,a+1,a+1+nv,a+nv);ff.append(f);fu.append([uv[i] for i in f])
  if not closed:
   for f in [tuple(range(segments-1,-1,-1)),tuple((len(pts)-1)*nv+k for k in range(segments))]:
    ff.append(f);fu.append([(r*s*cos(2*pi*(i%nv)/segments),r*s*sin(2*pi*(i%nv)/segments)) for i in f])
  if face==-1:ff=[tuple(reversed(f)) for f in ff];fu=[list(reversed(q)) for q in fu]
  addmesh([pos(*p) for p in vv],ff,material,'hall cartouche '+label+' foliate continuous sweep',face_uv=fu)
 def leaf(x,z,angle,length,width,depth=.18,label='foliate acanthus leaves'):
  # A pointed, ribbed leaf with continuous nonzero-area fan ends.
  v=[];rows=9;cols=7
  for j in range(rows):
   t=j/(rows-1);ww=width*(.035+.965*sin(pi*t)**.7)*(1+.13*sin(8*pi*t))
   for k in range(cols):
    u=-1+2*k/(cols-1);along=length*(t-.16);side=ww*u
    xx=x+along*sin(angle)+side*cos(angle);zz=z+along*cos(angle)-side*sin(angle)
    relief=depth+.060*sin(pi*t)*(1-u*u)+.014*cos(u*pi*3)*sin(pi*t)
    v.append((xx,relief,zz))
  f=[]
  for j in range(rows-1):
   for k in range(cols-1):a=j*cols+k;f.append((a,a+1,a+1+cols,a+cols))
  mesh(v,f,label)
  tube([(x+length*(t-.16)*sin(angle),depth+.063*sin(pi*t),z+length*(t-.16)*cos(angle)) for t in [i/12 for i in range(13)]],.014,'leaf midribs',6)
 # Central oval shield, mildly tapered at the lower end with a shallow convex face.
 n=72;v=[(0,.155,2.01)];radii=[.25,.56,.82,1.0]
 for r in radii:
  for k in range(n):
   a=2*pi*k/n;sh=.98+.10*sin(a)
   v.append((.60*r*cos(a)*sh,.155-.045*r*r,2.01+1.01*r*sin(a)))
 f=[(0,1+(k+1)%n,1+k) for k in range(n)]
 for j in range(len(radii)-1):
  for k in range(n):a=1+j*n+k;b=1+j*n+(k+1)%n;f.append((a,b,b+n,a+n))
 mesh(v,f,'convex oval shield')
 # Three distinct elliptical molding profiles, continuous actual relief.
 for radius,depth,r in [(1.015,.14,.055),(1.10,.105,.055),(1.21,.065,.045)]:
  pts=[]
  for k in range(n+1):
   a=2*pi*k/n;pts.append((.60*radius*cos(a)*(.98+.10*sin(a)),depth,2.01+1.01*radius*sin(a)))
  tube(pts,r,'layered oval moldings')
 # Flanking scrolling foliage and downward garlands, asymmetric leaves authored
 # deterministically to avoid a copied/scanned historic motif.
 for side in [-1,1]:
  pts=[]
  for k in range(38):
   t=k/37;ang=-.4+t*4.7;r=.34*(1-.76*t)
   pts.append((side*(.79+r*cos(ang)),.095+.065*t,2.07+r*1.9*sin(ang)))
  tube(pts,.055,'side volute scrolls')
  for j in range(9):
   z=.95+j*.235;x=side*(.70+.21*sin(j*pi/8));leaf(x,z,side*(.60+.24*sin(j)),.32,.115,.13+j*.006)
  # Spreading lower spray overlaps the window-arch crown, as in study photographs.
  tube([(side*(.30+t*1.0),.09,.96-.15*t) for t in [i/15 for i in range(16)]],.042,'lower garland stems')
  for j in range(6):
   x=side*(.36+.145*j);z=.91-.035*j;leaf(x,z,side*(1.00+.13*j),.34,.11,.14)
  # Small crest scroll and upright top leaves.
  tube([(side*(.34+.20*cos(t)),.13,3.08+.16*sin(t)) for t in [-pi*.55+i*pi*1.9/28 for i in range(29)]],.043,'crest scrolls')
  leaf(side*.15,3.06,side*.18,.295,.105,.17)
 leaf(0,3.025,0,.30,.12,.18,'central crest leaf')
 # Pendant keystone with corrugated front. Total localZ0..3.3528 preserves the
 # architect's documented height; absolute mounting datum remains caller-owned.
 outline=[(-.35,1.00),(.35,1.00),(.28,.68),(.245,.20),(.18,.045),(.09,.065),(0,0),(-.09,.065),(-.18,.045),(-.245,.20),(-.28,.68)]
 vv=[(x,d,z) for d in [.055,.175] for x,z in outline];q=len(outline)
 ff=[tuple(range(q-1,-1,-1)),tuple(range(q,q*2))]+[(i,(i+1)%q,(i+1)%q+q,i+q) for i in range(q)]
 mesh(vv,ff,'pendant keystone')
 for x in [-.18,0,.18]:
  tube([(x*(.78+.22*t),.186+.025*sin(pi*t),.15+.74*t) for t in [i/16 for i in range(17)]],.022,'pendant fluted ribs')
 # Normalize the authored relief's actual vertical envelope to the documented
 # overall height, rather than assuming a control-point extent equals mesh extent.
 refs=[(key,i) for key,data in B.items() if key[2].startswith('hall cartouche ') for i in range(before.get(key,0),len(data[0]))]
 zlo=min(B[k][0][i][2] for k,i in refs);zhi=max(B[k][0][i][2] for k,i in refs)
 for k,i in refs:
  x,y,z=B[k][0][i];B[k][0][i]=(x,y,bottom+(z-zlo)/(zhi-zlo)*height)
 return dict(height_m=height,max_width_m=2.95*s,placement=(cx,front_y,bottom),front_direction=face,
             evidence='Quinn Evans Visual Tour2024 p27: six11ft-tall cartouches; shape/relief authored from photographic appearance',
             status='photo-informed ornament approximation; no carving scan or exact mounting survey')
