"""Original cast-iron arch-border interpretation, restored Grand Hall only.
Photographs show circular rosettes and foliate scrolls around the recessed glazing.
Motif count/profile here are authored approximations, never an exact ironwork scan.
"""
def hall_window_tracery(cx,y,z,width,rise,face=1,material='Window cast iron'):
 def path(pts,r=.014,n=8):
  pp=[Vector(q) for q in pts];closed=(pp[0]-pp[-1]).length<1e-7;vv=[];uv=[];length=0
  for j,p in enumerate(pp):
   if j:length+=(p-pp[j-1]).length
   prev=pp[j-1] if j else pp[-2] if closed else pp[0];nxt=pp[j+1] if j+1<len(pp) else pp[1] if closed else pp[-1]
   tangent=(nxt-prev).normalized();u=tangent.cross(Vector((0,1,0))).normalized();v=tangent.cross(u).normalized()
   for k in range(n+1):
    a=2*pi*k/n;vv.append(tuple(p+r*(u*cos(a)+v*sin(a))));uv.append((length,r*a))
  ff=[];fu=[]
  for j in range(len(pp)-1):
   for k in range(n):
    a=j*(n+1)+k;f=(a,a+1,a+n+2,a+n+1);ff.append(f);fu.append([uv[i] for i in f])
  if not closed:
   for f in [tuple(range(n-1,-1,-1)),tuple((len(pp)-1)*(n+1)+k for k in range(n))]:
    ff.append(f);fu.append([(r*cos(2*pi*(i%(n+1))/n),r*sin(2*pi*(i%(n+1))/n)) for i in f])
  addmesh(vv,ff,material,'hall restored iron foliate arch border',face_uv=fu)
 def at(t,offset=0):return Vector((cx+(width/2-offset)*cos(t),y,z+(rise-offset)*sin(t)))
 for off in [.035,.305]:path([at(pi*i/96,off) for i in range(97)],.018,10)
 count=15
 for k in range(count):
  t=.045+(pi-.09)*k/(count-1);c=at(t,.165);rad=.115
  path([c+Vector((rad*cos(a),0,rad*sin(a))) for a in [2*pi*i/36 for i in range(37)]],.014)
  path([c+Vector((.068*cos(a),face*.006,.068*sin(a))) for a in [2*pi*i/24 for i in range(25)]],.009,6)
  for j in range(8):
   a=2*pi*j/8;path([c+Vector((rr*cos(a),face*.008,rr*sin(a))) for rr in [.01,.04,.075,.105]],.010,6)
 for k in range(count-1):
  t0=.045+(pi-.09)*k/(count-1);t1=.045+(pi-.09)*(k+1)/(count-1);tm=(t0+t1)/2;c=at(tm,.16)
  tan=Vector((-width/2*sin(tm),0,rise*cos(tm))).normalized();rad=Vector((cos(tm),0,sin(tm)))
  for sign in [-1,1]:
   points=[]
   for j in range(37):
    u=j/36;ang=sign*(.2+u*5.8);rr=.11*(1-.72*u)
    points.append(c+tan*(sign*.11+rr*cos(ang))+rad*(rr*sin(ang))+Vector((0,face*.004,0)))
   path(points,.013,8)
   # Pointed leaf loop and stem; independent authored motif, not traced source pixels.
   o=c+tan*(sign*.21)
   pts=[o+tan*(sign*.13*sin(pi*u))+rad*(.075*sin(2*pi*u)) for u in [j/20 for j in range(21)]]
   path(pts,.012,8)
 return dict(material_class='Cast-iron circular/foliate border',motifs=count,exact_motif_inventory='unverified; authored approximation',era='2026 restored appearance only')
