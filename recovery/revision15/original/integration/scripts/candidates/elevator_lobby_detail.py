"""Opt-in tapered six-lift lobby candidate, with source-controlled XY and explicit limits.
No work runs on import. HNS pixels are approximate controls, not an as-built survey.
Call build_elevator_lobby_candidate(globals(), controls) after secondary_spaces.py.
The function replaces only GROUP10 meshes and its named camera/space record.
"""
import math
import random

DEFAULT_ELEVATOR_CONTROLS = {
    'revision': 'EL-01-registered-trial',
    'scale_m_per_pixel': 0.07475621052631579,
    'north_y_pixel': 499, 'south_y_pixel': 801,
    'east_face_x_pixel': 1164.5,
    'north_bank_pixels': [[1127,511],[1104,614]],
    'south_bank_pixels': [[1104,700],[1127,801]],
    'north_door_center_y_pixels': [545,573,600],
    'south_door_center_y_pixels': [709,740,766],
    'door_width_m': 1.30,
    'floor_z_m': .13, 'ceiling_z_m': 5.75,
    'door_top_m': 4.10, 'leaf_top_m': 3.24,
    'portal_width_m': 1.80, 'portal_center_x_pixel': 1145,
    'east_entry_y_pixels': [630,682],
    'north_approach_limit_y_m': 20.40,
    'south_approach_limit_y_m': 59.40,
    'status': 'Independent XY topology review complete; door glyph centers ±3–5px, not surveyed jambs; isolated candidate',
    'uncertainty_xy_m': [.3,.6],
    'z_status': 'Inherited visual-proportion trial, no elevation calibration',
}


def build_elevator_lobby_candidate(g, controls=None):
    c=dict(DEFAULT_ELEVATOR_CONTROLS);c.update(controls or {})
    old_group=g['GROUP']; B=g['B']; M=g['M']; aged=g['AGED']; era=g['ERA']
    removed=[k for k in B if k[0].startswith('10 EAST ELEVATOR LOBBY')]
    if not removed: raise ValueError('Expected existing group10 lobby batches before replacement')
    for k in removed: del B[k]
    g['GROUP']='10 EAST ELEVATOR LOBBY | HNS tapered six-lift plan, qualified vertical detail'
    add=g['addmesh']; box=g['box']; beam=g['beam']; lamp=g['sec_lamp']
    stone='Warm Mankato column stone'; plaster=g['PL']; bronze=g['SEC_BRONZE']; iron=g['SEC_IRON']
    if aged:
        stone='Elevator lobby retained pale cladding interpretation'
        if stone not in M:
            m=M['Exterior Indiana limestone'].copy();m.name=stone;M[stone]=m
            m['texture_provenance']='Original pale mineral surface reused for surviving lobby cladding color class; stone species and exact wear unverified'
            m['placement_limit']='Local elevator-lobby retained cladding only; not an exterior-wall or exact loss map'
        plaster='Elevator lobby 2017 residual pale plaster'
        if plaster not in M:g['pbr'](plaster,'plaster_restored',4)
        M[plaster]['texture_provenance']='Original pale plaster surface with separate source-class loss interpretation; exact 2017 loss polygons unknown'
    sf=g['SEC_FLOOR']; ply=g['SEC_PLY']; dark=g['SEC_DARK']; substrate=g['SEC_SUBSTRATE']
    s=c['scale_m_per_pixel']; zf=c['floor_z_m']; H=c['ceiling_z_m']; top=c['door_top_m']; leaf=c['leaf_top_m']
    def xy(p): return ((555-p[0])*s,(p[1]-120)*s)
    def yy(p): return (p-120)*s
    xe=xy([c['east_face_x_pixel'],120])[0]; yn=yy(c['north_y_pixel']); ys=yy(c['south_y_pixel'])
    north=[xy(p) for p in c['north_bank_pixels']]; south=[xy(p) for p in c['south_bank_pixels']]
    xc=xy([c['portal_center_x_pixel'],120])[0]; pw=c['portal_width_m']
    entry=[yy(p) for p in c['east_entry_y_pixels']]
    def uv_for(v,f):
        # Per-face orthonormal metric charts; no degenerate box cap projections.
        a,b,d=[v[i] for i in f[:3]]
        u=[b[i]-a[i] for i in range(3)]; ul=math.sqrt(sum(t*t for t in u));u=[t/ul for t in u]
        q=[d[i]-a[i] for i in range(3)];n=(u[1]*q[2]-u[2]*q[1],u[2]*q[0]-u[0]*q[2],u[0]*q[1]-u[1]*q[0]);nl=math.sqrt(sum(t*t for t in n));n=[t/nl for t in n]
        w=(n[1]*u[2]-n[2]*u[1],n[2]*u[0]-n[0]*u[2],n[0]*u[1]-n[1]*u[0])
        return [(sum((v[j][i]-a[i])*u[i] for i in range(3)),sum((v[j][i]-a[i])*w[i] for i in range(3))) for j in f]
    def emit(v,f,mat,name): add(v,f,mat,name,face_uv=[uv_for(v,p) for p in f])
    def basis(a,b):
        t=(b[0]-a[0],b[1]-a[1]);L=math.hypot(*t);t=(t[0]/L,t[1]/L);return t,(-t[1],t[0]),L
    def point(a,b,u,d,z):
        t,n,L=basis(a,b);return (a[0]+t[0]*u+n[0]*d,a[1]+t[1]*u+n[1]*d,z)
    def panel(a,b,u0,u1,z0,z1,mat,name,depth=.18,offset=0):
        if u1-u0<1e-6 or z1-z0<1e-6:return
        v=[point(a,b,u,d,z) for u,d,z in [(u0,offset-depth,z0),(u1,offset-depth,z0),(u1,offset,z0),(u0,offset,z0),(u0,offset-depth,z1),(u1,offset-depth,z1),(u1,offset,z1),(u0,offset,z1)]]
        emit(v,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],mat,name)
    def wall(a,b,z0,z1,mat,name,depth=.22,offset=0):panel(a,b,0,basis(a,b)[2],z0,z1,mat,name,depth,offset)
    def slab(poly,zt,thick,mat,name):
        # Supplied room cells are convex and CCW; fan tessellation is explicit.
        area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1]))
        if area<0:poly=list(reversed(poly))
        n=len(poly);v=[(x,y,z) for z in [zt-thick,zt] for x,y in poly]
        f=[(0,i+1,i) for i in range(1,n-1)]+[(n,n+i,n+i+1) for i in range(1,n-1)]
        f += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        # Floors use world XY so all cells/borders have consistent metric grain.
        u=[[(v[j][0],v[j][1]) for j in p] if max(v[j][2] for j in p)-min(v[j][2] for j in p)<1e-8 else uv_for(v,p) for p in f]
        add(v,f,mat,name,face_uv=u)
    # Whole concourse map is reused as an original mineral-dust CLASS in this
    # separate lobby material. This is not a photographed surface or a source
    # assertion that the two historical floors had identical material.
    if aged:
        sf='Elevator lobby 2017 original mineral dust'
        if sf not in M:
            src=M.get('Concourse 2017 worn mineral floor')
            if src is None:src=M['Weathered concrete']
            m=src.copy();m.name=sf;M[sf]=m
            m['provenance']='Original mineral dust interpretation reused on a distinct lobby material; no dated floor texture scan'
            m['placement_limit']='East elevator lobby original mineral-dust material class only; no verified substrate composition'
    # Three convex cells reproduce the splayed footprint without a giant box.
    cells=[[(xe,yn),(north[0][0],yn),north[1],(xe,north[1][1])],
           [(xe,north[1][1]),north[1],south[0],(xe,south[0][1])],
           [(xe,south[0][1]),south[0],south[1],(xe,ys)]]
    for idx,p in enumerate(cells):
        slab(p,zf,.16,sf,'Elevator lobby tapered principal floor')
        slab(p,H+.18,.18,plaster,'Elevator lobby tapered flat ceiling')
    # Inlaid, narrow pale stone bands, embedded only a millimetre above finish.
    if not aged:
        for a,b in [(north[0],north[1]),(south[0],south[1]),((xe,yn),(xe,ys))]:
            t,n,L=basis(a,b); interior=1 if a[0]!=xe else -1
            poly=[point(a,b,u,interior*d,0)[:2] for u,d in [(0,.14),(L,.14),(L,.48),(0,.48)]]
            slab(poly,zf+.001,.015,'Pale rose marble','Elevator lobby source-informed perimeter inlay')
    # East wall, interrupted at the actual entrance, is separate from the facade.
    for ya,yb in [(yn,entry[0]),(entry[1],ys)]:
        a,b=(xe,yb),(xe,ya)  # interior normal +X
        wall(a,b,zf,H,stone,'Elevator lobby east boundary masonry')
        L=basis(a,b)[2]
        for zz in [.82,1.68,2.54,3.40,4.26,5.12]:
            panel(a,b,0,L,zz,zz+.005,'Distress umber' if aged else 'Pale rose marble','Elevator lobby restrained large-stone joints',.005,.002)
        for u in [1.6+k*2.2 for k in range(int(L/2.2))]:panel(a,b,u,u+.004,zf,H-.55,'Distress umber' if aged else 'Pale rose marble','Elevator lobby vertical stone joints',.005,.002)
    # The east entrance is lower than the lobby ceiling: a real stone header
    # closes the interval above the vestibule. Do not conceal a missing cap
    # by adding decorative cornice alone.
    box((xe,sum(entry)/2,(4.70+H)/2),(.22,entry[1]-entry[0],H-4.70),stone,'Elevator east entrance upper structural infill')
    # Continuous east and end-wall plaster profiles match the source's wrap.
    for a,b in [((xe,ys),(xe,yn)),((xe,yn),(north[0][0],yn)),((south[1][0],ys),(xe,ys))]:
        for zz,dep,hh in [(H-.31,.12,.09),(H-.21,.21,.10),(H-.11,.32,.11)]:wall(a,b,zz,zz+hh,plaster,'Elevator lobby returned perimeter plaster cornice',dep,dep-.03)
    door_records=[]
    def bank(a,b,py_centers,label):
        t,n,L=basis(a,b); centers=[(yy(v)-a[1])/t[1] for v in py_centers]; dw=c['door_width_m']
        cursor=0.
        for i,u in enumerate(centers):
            lo,hi=u-dw/2,u+dw/2
            if lo<0 or hi>L:raise ValueError(('Door outside registered bank',label,i,lo,hi,L))
            panel(a,b,cursor,lo,zf,H,stone,'Elevator lobby splayed bank masonry')
            panel(a,b,lo,hi,top,H,stone,'Elevator lobby lift-head stone infill')
            panel(a,b,lo,hi,zf,top,'Dark void','Elevator lobby shallow lift recess, no shaft modeled',.06,-.16)
            for q in [lo-.13,hi+.13]:
                panel(a,b,q-.09,q+.09,zf,H-.37,stone,'Elevator lobby slim stone door pilasters',.20,.10)
                for zz,ww,hh in [(zf,.33,.21),(.34,.26,.1),(H-.54,.29,.08),(H-.40,.38,.10)]:panel(a,b,q-ww/2,q+ww/2,zz,zz+hh,stone,'Elevator lobby door pilaster profiles',.24,.13)
            panel(a,b,lo,hi,zf,leaf,ply if aged else bronze,'2017 boarded lift-face interpretation' if aged else 'Restored elevator bronze door leaves',.075,-.06)
            if not aged:
                # Restored divided metal leaves and radial transom motif. The
                # dated2017 plywood does not justify copying this subdivision.
                panel(a,b,u-.01,u+.01,zf,leaf,'Dark bronze','Elevator lobby lift central seam',.02,-.022)
                for center in [u-dw/4,u+dw/4]:
                    for zz in [.40,1.37,2.25,3.00]:panel(a,b,center-dw*.25+.08,center+dw*.25-.08,zz,zz+.017,'Dark bronze','Elevator lobby shallow lift panel rails',.012,-.019)
                panel(a,b,lo,hi,leaf+.07,top,'Dark bronze','Elevator lobby historic transom backing',.04,-.015)
                for k in range(15):
                    th=math.pi*k/14
                    p=point(a,b,u+.47*math.cos(th),.016,leaf+.18+.38*math.sin(th));q=point(a,b,u+.52*math.cos(th),.016,leaf+.18+.42*math.sin(th))
                    beam(p,q,.007,bronze,'Elevator lobby original radial transom motif',5)
            else:
                panel(a,b,lo,hi,leaf+.07,top,'Dark void','2017 open upper elevator transom interpretation',.035,-.05)
            if not aged:
                panel(a,b,hi+.25,hi+.42,1.23,1.54,'Dark bronze','Elevator lobby small call plate',.08,.13)
            door_records.append(dict(bank=label,index=i+1,center_xy_m=list(point(a,b,u,0,0)[:2]),clear_width_trial_m=dw,source_center_y_pixel=py_centers[i]))
            cursor=hi
        panel(a,b,cursor,L,zf,H,stone,'Elevator lobby splayed bank masonry')
        # Continuous layered cornice follows the splay; no floating ends.
        for zz,dep,hh in [(H-.31,.12,.09),(H-.21,.21,.10),(H-.11,.32,.11)]:wall(a,b,zz,zz+hh,plaster,'Elevator lobby splayed plaster cornice',dep,dep-.03)
    bank(*north,c['north_door_center_y_pixels'],'north')
    bank(*south,c['south_door_center_y_pixels'],'south')
    # The north threshold band is not proven to be steps. The .08m floor is
    # only a shared modeling datum and must not imply a surveyed level route.
    wall((north[0][0],yn),north[0],zf,H,stone,'Elevator lobby north taper shoulder')
    # Close short end shoulders between the angled-bank endpoints and portals.
    for y,xw,reverse,label in [(yn,north[0][0],True,'north approach'),(ys,south[1][0],False,'south approach')]:
        for xa,xb in [(xe,xc-pw/2),(xc+pw/2,xw)]:
            box(((xa+xb)/2,y,(zf+H)/2),(max(0,xb-xa),.24,H-zf),stone,'Elevator lobby '+label+' side masonry')
        box((xc,y,(3.88+H)/2),(pw,.24,H-3.88),stone,'Elevator lobby '+label+' lintel')
        g['sec_frame'](xc,y,zf,pw,3.80,'y','Dark bronze','Elevator lobby '+label+' portal',False,.62,2)
    # Corridor-to-arcade transition lies outside the old arcade's fixed extent.
    xw=north[1][0]; ya=36.63;yb=43.36
    slab([(xw,ya),(-39.5,ya),(-39.5,yb),(xw,yb)],zf,.16,sf,'Elevator lobby to arcade transition floor')
    slab([(xw,ya),(-39.5,ya),(-39.5,yb),(xw,yb)],5.96,.22,plaster,'Elevator lobby arcade transition ceiling')
    for yy0 in [ya,yb]:box(((xw-39.5)/2,yy0,2.9),(-39.5-xw,.22,5.8),stone,'Elevator lobby arcade transition cheek')
    # Main east entrance shell; the external door/head control stays fixed.
    a,b=entry
    slab([(-52.1,a),(xe,a),(xe,b),(-52.1,b)],.07,.12,sf,'Elevator lobby east entrance vestibule floor')
    slab([(-52.1,a),(xe,a),(xe,b),(-52.1,b)],4.80,.18,plaster,'Elevator lobby east entrance vestibule ceiling')
    for y in entry:box(((-52.1+xe)/2,y,2.35),(xe+52.1,.22,4.7),stone,'Elevator lobby entrance vestibule side wall')
    g['sec_frame'](sum(entry)/2,-52.1,.06,b-a,4.6,'x','Dark bronze','East entrance double-door wall',not aged,.90,4)
    # End corridors retain plan-supported route only; baths and hidden services
    # remain unmodeled. No cabins, shafts or below-track passage is invented.
    for ya,yb,label in [(c['north_approach_limit_y_m'],yn,'north Study approach'),(ys,c['south_approach_limit_y_m'],'south exit-ramp connector')]:
        xa,xb=(xe,north[0][0]) if label.startswith('north') else (-45.5,-42.6)
        if label.startswith('south'):
            # Connect existing trial floor datums continuously. Post_p36 shows
            # no abrupt threshold riser; this interpolated slope is NOT a
            # measurement of the actual modern corridor/ramp grade.
            def target_exit_z(x):return .06+.45*(-29.4894-x)/(-29.4894+45.1)
            v=[(xa,ya,zf),(xb,ya,zf),(xb,yb,target_exit_z(xb)),(xa,yb,target_exit_z(xa))]
            v += [(x,y,z-.16) for x,y,z in v]
            f=[(0,1,2),(0,2,3),(7,6,5),(7,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
            emit(v,f,sf,'Elevator south connector interpolated continuous floor | grade unmeasured')
        else:slab([(xa,ya),(xb,ya),(xb,yb),(xa,yb)],zf,.16,sf,'Elevator lobby '+label+' floor')
        slab([(xa,ya),(xb,ya),(xb,yb),(xa,yb)],4.79,.18,plaster,'Elevator lobby '+label+' ceiling')
        if label.startswith('north'):
            # The independently checked HNS underlay has two lateral restroom
            # doors and an open west branch. A closed rectangular corridor is wrong.
            for xx,segments in [(xa,[(ya,yy(448)),(yy(461),yb)]),(xb,[(ya,yy(448)),(yy(461),yy(470)),(yy(494),yb)])]:
                for sy0,sy1 in segments:box((xx,(sy0+sy1)/2,2.35),(.18,sy1-sy0,4.7),plaster,'Elevator north approach wall with documented lateral gaps')
                g['sec_frame']((yy(448)+yy(461))/2,xx,zf,yy(461)-yy(448),2.45,'x','Dark bronze','North approach restroom doorway | fit-out unresolved',False,0,1)
                box((xx,(yy(448)+yy(461))/2,3.62),(.18,yy(461)-yy(448),2.16),plaster,'North approach restroom doorway header')
            # Only the observed branch mouth is constructed; the hall-side end
            # is an unresolved interface, not an invented finished room.
            slab([(xb,yy(470)),(xb+1.2,yy(470)),(xb+1.2,yy(494)),(xb,yy(494))],zf,.16,sf,'North approach west branch mouth floor | continuation unresolved')
        else:
            for xx in [xa,xb]:box((xx,(ya+yb)/2,2.35),(.18,yb-ya,4.7),plaster,'Elevator lobby '+label+' boundary shell')
    if not aged:
        for y in [30.4,35.1,40.0,45.2,49.3]:lamp(xc,y,H,.24,True)
    else:
        # Local lost cladding class inspired by pre_p14. Exact six-face state is
        # not established, so no source-perfect damage inventory is claimed.
        for a,b in [north,south]:
            t,n,L=basis(a,b)
            for u in [L*.12,L*.87]:
                panel(a,b,u-.12,u+.12,.40,H-.68,substrate,'2017 lobby interpreted removed facing strips',.025,.15)
                for k in range(8):panel(a,b,u-.115+k*.030,u-.107+k*.030,.41,H-.69,'Distress umber','2017 lobby ribbed substrate grooves',.008,.158)
    if aged:
        # Pre_p14 supports local peeling ceilings and loose plaster. These
        # newly authored outlines/positions are condition-class interpretations,
        # not transferred photographic damage polygons or a six-bank inventory.
        rr=random.Random(171401)
        def west_x_at(y):
            aa,bb=(north if y<north[1][1] else south if y>south[0][1] else [north[1],south[0]])
            t=max(0,min(1,(y-aa[1])/(bb[1]-aa[1])))
            return aa[0]+(bb[0]-aa[0])*t
        for idx,y in enumerate([30.1,32.8,35.5,42.2,45.5,48.0]):
            x=xe+(west_x_at(y)-xe)*(.37 if idx%2 else .63)
            poly=[]
            for k in range(15):
                th=2*math.pi*k/15;r=.50+rr.random()*.23
                poly.append((x+r*math.cos(th),y+.82*r*math.sin(th),H-.008))
            emit(poly,[tuple(reversed(range(15)))],substrate,'2017 lobby ceiling coating losses | original approximate outlines')
        for k in range(65):
            y=rr.uniform(yn+.5,ys-.5);x=west_x_at(y)-rr.uniform(.20,.80);r=rr.uniform(.012,.055)
            v=[(x-r,y-r*.3,zf+.009),(x+r,y-r*.6,zf+.014),(x+r*.2,y+r,zf+.017)]
            emit(v,[(0,1,2)],plaster,'2017 lobby sparse original plaster fragments')
    g['SEC_CAMERAS']['elevator_lobby']=((xe+.60,ys-.85,1.75),(xc,yn+1.5,2.35),23)
    for record in g['SEC_SPACES']:
        if record['id']=='east_elevator_lobby':
            record.update(extent_m=[xe,max(north[1][0],south[0][0]),yn,ys,zf,H],basis='HNS registered tapered six-lift XY topology; original 1914 lift plan corroboration; restored post_p35; dated2017 pre_p14 condition classes',precision='Raster controls ±0.3–0.6m; provisional door positions and unmeasured Z; no shaft/cabin reconstruction')
    meta=dict(controls=c,removed_batches=[list(k) for k in removed],door_schedule=door_records,old_width_m=8.5,new_nominal_width_range_m=[north[0][0]-xe,north[1][0]-xe],status='Isolated candidate, no source-perfect historic claim',unresolved=['Six door glyph centers are approximate; exact jamb widths and restoration subdivisions unresolved','Unmeasured vertical profiles and ceiling datum; shared .13m lobby/arcade floor trial with interpolated south connector, no claimed surveyed grade','Exact2017 facing losses, boards and debris distribution','North approach lateral gaps retained; restroom interiors and west branch continuation unresolved','Complete modern lift control hardware','Hidden shafts/cabins'])
    g['GROUP']=old_group
    return meta
