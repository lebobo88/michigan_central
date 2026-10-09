"""2026 north forecourt, Lacombe Drive and Roosevelt Park, original geometry.

Execute before core batch finalization. Then call north_plaza_post_finalize()
once AFTER core finalization to link shared-mesh vegetation instances. Update
cameras with NORTH_PLAZA_CAMERAS. GROUP is restored. Nothing is emitted in 2017.

Design/built-photo topology is supported; all local distances, radii, furniture
positions, tree counts and local grades below are APPROXIMATE drawing/photo fits.
Legal ROW dimensions are not pavement dimensions. Detroit datum is NOT local Z0.
No reference photograph or plan pixels are used by this module.
"""
from mathutils.geometry import tessellate_polygon as _np_tessellate, delaunay_2d_cdt as _np_cdt

_NP_SAVED_GROUP = GROUP
_NP_RNG = random.Random(20260719)
NORTH_PLAZA_CAMERAS = {}
NORTH_PLAZA_INSTANCE_REQUESTS = []
NORTH_PLAZA_STATS = {}
NORTH_PLAZA_GROUPS = {
    'forecourt':'00A NORTH FORECOURT | 2026 photo-supported topology, approximate dimensions',
    'road':'00B LACOMBE DRIVE | 2026 asphalt roadway and central crossing',
    'park':'00C ROOSEVELT PARK | 2023 completed topology, 2026 approximate context',
    'furnishing':'00D NORTH LANDSCAPE FURNISHINGS | observed types, approximate placement',
    'plants':'00E NORTH LANDSCAPE VEGETATION | original shared meshes, approximate inventory',
}
NORTH_PLAZA_CONTROLS = {
    'coordinate_system':'meters; +X station west, +Y station south, +Z up',
    'front_glazing_y_m':0.0,
    'building_width_reference_m':105.2576,
    'dimensional_status':'PHOTO_FIT_APPROXIMATE; not surveyed/current as-built',
    'road_station_edge_y_m':-20.0,
    'road_park_edge_y_m':-29.0,
    'apron_top_local_z_m':0.025,
    'road_nominal_local_z_m':-0.10,
    'crossing_top_local_z_m':-0.025,
    'park_top_local_z_m':0.015,
    'promenade_width_m':7.2,
    'circular_lawn_center_xy_m':[32.0,-130.0],
    'circular_lawn_radius_m':27.5,
    'park_scope':'Main north park only; southwest annex, Michigan Avenue road and distant blocks omitted',
    'vertical_caution':'Local flat interpretive datum only; NAD83/Detroit road-survey elevations not imported',
}


def np_clean(poly):
    out=[]
    for p in poly:
        p=tuple(p[:2])
        if not out or math.dist(p,out[-1])>1e-6:out.append(p)
    if len(out)>2 and math.dist(out[0],out[-1])<1e-6:out.pop()
    return out


def np_area(poly):
    return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))*.5


def np_ccw(poly):
    p=np_clean(poly)
    return p if np_area(p)>0 else p[::-1]


def np_slab(poly,z,depth,material,name):
    """Triangulated planar top and genuine vertical edges, no overlapping fan faces."""
    p=np_ccw(poly)
    if len(p)<3 or np_area(p)<1e-6:return
    verts=[(x,y,z) for x,y in p]+[(x,y,z-depth) for x,y in p]
    n=len(p);tri=_np_tessellate([[Vector((x,y,0)) for x,y in p]])
    lookup={tuple(round(c,6) for c in (x,y,0)):i for i,(x,y) in enumerate(p)}
    faces=[]
    for t in tri:
        ids=tuple(int(v) if isinstance(v,int) else lookup[tuple(round(c,6) for c in v)] for v in t)
        faces.append(ids);faces.append(tuple(n+i for i in ids[::-1]))
    for i in range(n):j=(i+1)%n;faces.append((i,n+i,n+j,j))
    addmesh(verts,faces,material,name)


def np_ribbon(points,width):
    p=np_clean(points);left=[];right=[]
    for i,pt in enumerate(p):
        a=Vector(p[max(0,i-1)]);b=Vector(p[min(len(p)-1,i+1)])
        d=(b-a).normalized();normal=Vector((-d.y,d.x))*width*.5
        left.append(tuple(Vector(pt)+normal));right.append(tuple(Vector(pt)-normal))
    return np_ccw(left+right[::-1])


def np_catmull(points,steps=9):
    out=[];pts=[points[0]]+list(points)+[points[-1]]
    for j in range(1,len(pts)-2):
        a,b,c,d=[Vector(v) for v in pts[j-1:j+3]]
        for i in range(steps):
            t=i/steps
            q=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
            out.append(tuple(q))
    return np_clean(out+[points[-1]])


def np_circle(cx,cy,r,n=100):
    return [(cx+r*cos(i*2*pi/n),cy+r*sin(i*2*pi/n)) for i in range(n)]


def np_inside(point,poly):
    x,y=point;inside=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
    return inside


def np_path_samples(points,spacing):
    distances=[0.0]
    for a,b in zip(points,points[1:]):distances.append(distances[-1]+math.dist(a,b))
    count=max(1,int(distances[-1]/spacing));out=[];j=0
    for i in range(count+1):
        t=distances[-1]*i/count
        while j<len(points)-2 and distances[j+1]<t:j+=1
        span=distances[j+1]-distances[j];u=(t-distances[j])/span if span else 0
        out.append(tuple((1-u)*a+u*b for a,b in zip(points[j],points[j+1])))
    return out


def np_strip(points,width,z,depth,material,name):
    np_slab(np_ribbon(points,width),z,depth,material,name)


def np_bed_rail(points):
    # Rear and curved ends only. The road-facing edge is a low curb, not a fourth rail.
    np_strip(points,.39,.24,.25,'NP forecourt stone','forecourt balustrade continuous stone plinth')
    np_strip(points,.42,1.04,.13,'NP forecourt stone','forecourt balustrade shaped coping')
    np_strip(points,.33,.93,.065,'NP forecourt stone','forecourt balustrade lower coping bead')
    for x,y in np_path_samples(points,.43):
        lathe((x,y,.24),[(.095,0),(.105,.07),(.069,.13),(.055,.21),(.083,.30),(.105,.37),(.084,.45),(.062,.55),(.093,.62),(.093,.67)],'NP forecourt stone','forecourt turned stone balusters',12)
    for x,y in [points[0],points[-1]]:
        box((x,y,.51),(.73,.72,1.02),'NP forecourt stone','forecourt balustrade terminal piers')
        box((x,y,1.045),(.87,.85,.12),'NP forecourt stone','forecourt terminal pier caps')


def np_bench(x,y,angle=0,swing=False):
    """Observed black metal slatted family, not a claimed manufacturer model."""
    ca,sa=cos(angle),sin(angle)
    def q(u,v,z):return(x+u*ca-v*sa,y+u*sa+v*ca,z)
    for xx in [-.83,.83]:
        beam(q(xx,-.23,.04),q(xx,-.23,.48),.025,'NP black metal','park bench cast legs')
        beam(q(xx,.27,.04),q(xx,.31,.86),.026,'NP black metal','park bench back supports')
        beam(q(xx,-.24,.45),q(xx,.30,.45),.025,'NP black metal','park bench underframe')
        beam(q(xx,-.24,.70),q(xx,.26,.70),.024,'NP black metal','park bench arms')
    for j in range(8):beam(q(-1.03,-.23+j*.069,.48),q(1.03,-.23+j*.069,.48),.017,'NP black metal','park bench seat slats',6)
    for j in range(7):beam(q(-1.03,.30+j*.016,.55+j*.049),q(1.03,.30+j*.016,.55+j*.049),.017,'NP black metal','park bench back slats',6)
    if swing:
        for xx in [-1.35,1.35]:beam(q(xx,0,.0),q(xx,0,2.38),.042,'NP black metal','park swing frame',10)
        beam(q(-1.35,0,2.38),q(1.35,0,2.38),.042,'NP black metal','park swing crossbar',10)
        for xx in [-.88,.88]:
            for yy in [-.20,.27]:beam(q(xx,yy,.52),q(xx,0,2.30),.007,'NP black metal','park swing suspension',5)


def np_lamp(x,y,height=5.25,modern=False):
    lathe((x,y,.0),[(.24,0),(.25,.08),(.20,.17),(.18,.31),(.145,.36),(.13,.85),(.095,1.02),(.073,height-.60)],'NP black metal','decorative park lamp bases and poles',16)
    if modern:
        beam((x,y,height-.60),(x,y,height),.075,'NP black metal','forecourt contemporary light pole',12)
        box((x,y,height),(.38,.16,.085),'NP black metal','forecourt contemporary light head')
    else:
        lathe((x,y,height-.61),[(.10,0),(.23,.12),(.25,.19),(.22,.61),(.31,.64),(.19,.79),(.03,.89)],'NP black metal','park lamp lantern metal',16)
        lathe((x,y,height-.39),[(.187,0),(.165,.35)],'NP frosted lamp','park lamp translucent panes',12)
        for a in range(6):
            t=a*pi/3;beam((x+.21*cos(t),y+.21*sin(t),height-.39),(x+.18*cos(t),y+.18*sin(t),height-.04),.012,'NP black metal','park lamp lantern ribs',6)


def np_bin(x,y):
    lathe((x,y,.03),[(.24,0),(.28,.72),(.28,.80)],'NP black metal','park bin inner shell',16)
    for i in range(24):
        t=i*pi/12;beam((x+.3*cos(t),y+.3*sin(t),.05),(x+.36*cos(t),y+.36*sin(t),.79),.014,'NP black metal','park bin vertical slats',5)
    lathe((x,y,.79),[(.27,0),(.37,.0),(.37,.05),(.27,.05),(.27,0)],'NP black metal','park bin rim',24)


def np_request(kind,x,y,z=.02,scale=1,rotation=None):
    NORTH_PLAZA_INSTANCE_REQUESTS.append({'kind':kind,'location':(x,y,z),'scale':scale,'rotation':_NP_RNG.random()*2*pi if rotation is None else rotation,'variant':_NP_RNG.randrange(4)})


def np_scatter_bed(poly,spacing=.84,density=1.0):
    lo=[min(p[k] for p in poly) for k in range(2)];hi=[max(p[k] for p in poly) for k in range(2)]
    y=lo[1]+spacing*.3
    while y<hi[1]:
        x=lo[0]+spacing*.3
        while x<hi[0]:
            q=(x+_NP_RNG.uniform(-.18,.18),y+_NP_RNG.uniform(-.18,.18))
            if np_inside(q,poly) and _NP_RNG.random()<density:
                np_request('perennial' if _NP_RNG.random()<.7 else 'grass',*q,z=.10,scale=_NP_RNG.uniform(.65,1.15))
            x+=spacing
        y+=spacing


def np_build_park():
    """CDT partitions path intersections into non-overlapping triangles.
    No lawn/path rectangle overlaps or invented symmetry. Dimensions are editable
    approximate controls, not digitized engineering coordinates.
    """
    global GROUP
    GROUP=NORTH_PLAZA_GROUPS['park']
    boundary=np_ccw([(62,-32),(91,-192),(82,-204),(-64,-204),(-85,-41),(-78,-32)])
    paths=[];pads=[];beds=[]
    # Straight north-south axis. Major circle is WEST (+X), distinctly off axis.
    paths.append(np_ribbon([(0,-30),(0,-204)],7.2))
    boundary_closed=boundary+[boundary[0]]
    paths.append(np_ribbon(boundary_closed,3.2))
    ringouter=np_circle(32,-130,31.2);ringinner=np_circle(32,-130,27.5)
    # Rounded station-facing event lawn; center promenade bisects it.
    fan=np_catmull([(-34,-33),(-31,-48),(-20,-60),(0,-65),(22,-59),(34,-46),(34,-33)],12)
    paths.append(np_ribbon(fan,3.2))
    # Main diagonal and asymmetrical east radial/curving routes from observed topology.
    for pts,w in [
      ([(88,-195),(60,-177),(34,-164),(4,-157)],3.0),
      ([(73,-92),(56,-101),(45,-102),(32,-99)],3.0),
      ([(18,-102),(10,-100),(0,-86)],3.0),
      ([(62,-35),(53,-60),(47,-77),(34,-91),(18,-103)],3.0),
      ([(0,-65),(-27,-61),(-45,-78),(-50,-104),(-31,-127),(-15,-153),(-25,-178),(-40,-204)],3.3),
      ([(0,-88),(-27,-90),(-52,-77),(-80,-47)],2.8),
      ([(0,-151),(-24,-137),(-56,-123),(-75,-117)],3.0),
      ([(-4,-167),(-29,-163),(-59,-180),(-64,-196)],2.7),
      ([(0,-195),(0,-171),(5,-159)],3.0),
    ]:paths.append(np_ribbon(np_catmull(pts,9),w))
    for x,y,w,h in [(7,-77,7,10),(-7,-81,7,12),(7,-103,7,13),(-8,-115,8,11),(7,-150,7,12),(-8,-155,8,10),(7,-185,7,11)]:
        pads.append([(x-w/2,y-h/2),(x+w/2,y-h/2),(x+w/2,y+h/2),(x-w/2,y+h/2)])
    # Warm aggregate seating segments outside the circular lawn, not a mirrored ring.
    for start,end in [(105,146),(175,208),(224,260),(290,319),(336,358)]:
        a=[(32+34.3*cos(t*pi/180),-130+34.3*sin(t*pi/180)) for t in range(start,end+1,2)]
        if len(a)>1:pads.append(np_ribbon(a,3.2))
    for x,y,w,h in [(7,-66,6,7),(-7,-67,6,8),(8,-92,7,6),(-8,-99,7,6),(8,-139,7,5),(-8,-141,7,7),(8,-174,7,7),(-8,-185,7,7)]:
        beds.append(np_ccw([(x-w/2,y-h/2),(x+w/2,y-h/2),(x+w/2,y+h/2),(x-w/2,y+h/2)]))
    # Make all boundary intersections exact once. All visible faces have exactly one class.
    verts=[];edges=[];loops=[boundary]+paths+pads+beds+[ringouter,ringinner]
    for loop in loops:
        p=np_clean(loop);start=len(verts);verts.extend(Vector(v) for v in p)
        edges.extend((start+i,start+(i+1)%len(p)) for i in range(len(p)))
    vv,ee,ff,ov,oe,of=_np_cdt(verts,edges,[],0,1e-5)
    classes={'NP pale concrete':[],'NP warm aggregate':[],'NP turf':[],'NP mulch':[]}
    for face in ff:
        center=tuple(sum(vv[j][k] for j in face)/len(face) for k in [0,1])
        if not np_inside(center,boundary):continue
        r=math.dist(center,(32,-130))
        ispath=any(np_inside(center,p) for p in paths) or 27.5<r<31.2
        material='NP pale concrete' if ispath else 'NP mulch' if any(np_inside(center,p) for p in beds) else 'NP warm aggregate' if any(np_inside(center,p) for p in pads) else 'NP turf'
        classes[material].append(face)
    for material,faces in classes.items():
        z=.031 if material in ('NP pale concrete','NP warm aggregate') else .021 if material=='NP mulch' else .016
        v=[(p.x,p.y,z) for p in vv]
        addmesh(v,faces,material,'Roosevelt Park '+material[3:]+' nonoverlapping surface')
    np_strip(boundary_closed,.19,.11,.24,'NP pale concrete','park perimeter concrete curb')
    # Crosswise saw cuts on the promenade. Very shallow physically narrow dark seams.
    for y in range(-34,-203,-3):box((0,y,.0328),(7.18,.012,.0015),'NP joint','promenade contraction joints')
    for x in [-1.2,1.2]:box((x,-118,.0328),(.01,167,.0015),'NP joint','promenade longitudinal joints')
    for bed in beds:np_scatter_bed(bed,.85,.80)
    # Original tree massing at source-supported classes and broad zones; no exact inventory claim.
    mature=[(32,-127,1.18),(35,-139,.94),(62,-181,1.03),(40,-178,1.1),(21,-179,.90),(73,-162,.88),(-25,-177,.96),(-31,-147,1.04),(-40,-120,1.06),(-59,-105,.95),(-62,-79,.92),(-37,-50,.88),(31,-82,.88),(48,-89,.95)]
    for x,y,s in mature:np_request('mature_tree',x,y,scale=s)
    # Flowering-tree class is in leaf in the July-based reconstruction.
    for i in range(15):
        t=(i/15*2*pi)+.15;x=32+35.9*cos(t);y=-130+35.9*sin(t)
        if x>8:np_request('young_tree',x,y,scale=_NP_RNG.uniform(.9,1.14))
    for x,y in [(12,-74),(-12,-79),(12,-102),(-13,-115),(12,-151),(-13,-155),(12,-183),(-13,-185),(79,-188),(76,-174),(72,-157),(69,-140),(65,-121),(61,-105),(57,-86),(51,-67),(-69,-192),(-71,-177),(-73,-160),(-76,-143),(-79,-126),(-82,-108),(-84,-91),(-82,-72)]:
        # Some east perimeter nominal points fall outside the sloped boundary; pull them inward.
        while not np_inside((x,y),boundary):x*=.96
        np_request('young_tree',x,y,scale=_NP_RNG.uniform(.86,1.17))
    GROUP=NORTH_PLAZA_GROUPS['furnishing']
    for y in [-58,-86,-112,-145,-175,-198]:
        for x in [-5.05,5.05]:np_lamp(x,y)
    for x,y,a in [(8,-79,pi/2),(-8,-80,-pi/2),(8,-104,pi/2),(-9,-115,-pi/2),(8,-151,pi/2),(-9,-155,-pi/2),(8,-186,pi/2),(51,-100,.35),(62,-136,pi/2),(32,-165,0),(-32,-91,-.4),(-50,-122,.8)]:np_bench(x,y,a)
    for x,y in [(23,-97),(-38,-83)]:np_bench(x,y,0,True)
    for x,y in [(6,-71),(-6,-90),(6,-157),(-6,-190),(59,-113)]:np_bin(x,y)
    return {'boundary':boundary,'path_polygons':paths,'planting_polygons':beds,'circular_lawn':{'center':[32,-130],'radius':27.5},'surface_triangles':{k:len(v) for k,v in classes.items()}}


def np_build_forecourt():
    global GROUP
    GROUP=NORTH_PLAZA_GROUPS['forecourt']
    apron=[(-76,-20),(76,-20),(72,-.16),(-71,-.16)]
    np_slab(apron,.025,.19,'NP forecourt paving','north forecourt gray paved apron')
    # Central lighter entrance apron, widening in curved notches at the two bed ends.
    central=[(-10.8,-20),(10.8,-20),(10.7,-18),(8.9,-16.5),(9.2,-13.4),(12,-10),(13,-7),(13,-.2),(-13,-.2),(-13,-7),(-12,-10),(-9.2,-13.4),(-8.9,-16.5),(-10.7,-18)]
    np_slab(central,.030,.09,'NP pale concrete','central entrance apron with curved side notches')
    base=[(10.8,-17.8),(9.4,-15.8),(9.8,-12.6),(13,-10.0),(44.5,-10.0),(49.1,-11.0),(52.3,-13.7),(53.2,-17.8)]
    for sign in [-1,1]:
        rail=np_catmull([(sign*x,y) for x,y in base],8)
        bed=np_ccw(rail)
        np_slab(bed,.17,.25,'NP mulch','paired long ornamental forecourt bed')
        np_bed_rail(rail)
        np_strip([rail[0],rail[-1]],.24,.20,.29,'NP forecourt stone','road-facing low bed curb')
        np_scatter_bed(bed,.8,.91)
        # Front wing base planting stays below the window sills.
        strip=[(sign*36.9,-2.0),(sign*51.1,-2),(sign*51.1,-.30),(sign*36.9,-.30)]
        np_slab(strip,.08,.18,'NP mulch','outer wing low foundation planting')
        np_scatter_bed(strip,.82,.87)
    # Paving joints through the unobstructed apron; bed masks hide irrelevant portions.
    for x in range(-72,73,3):
        box((x,-5.0,.027),(.012,9.5,.002),'NP joint','forecourt paving expansion joints')
    for y in [-2.5,-5,-7.5]:box((0,y,.027),(142,.012,.002),'NP joint','forecourt transverse paving joints')
    for x in [-8,-5.33,-2.67,0,2.67,5.33,8]:
        lathe((x,-18.55,.025),[(.055,0),(.055,.92),(.049,.95)],'NP bollard metal','entry approach slim metal bollards',12)
        lathe((x,-18.55,.86),[(.056,0),(.056,.055)],'NP pale concrete','bollard narrow reflective band',12)
    # Potted seasonal plants and smaller trees on outer plazas, preserving the central vista.
    GROUP=NORTH_PLAZA_GROUPS['furnishing']
    for x,y in [(-11.5,-18.8),(11.5,-18.8),(-57,-17.8),(57,-17.8),(-65,-12),(65,-12),(-70,-10),(70,-10)]:
        lathe((x,y,.025),[(.35,0),(.40,.12),(.48,.71),(.46,.78),(.36,.78),(.34,.68)],'NP planter','movable dark flower planters',24)
        np_request('perennial',x,y,z=.56,scale=1.15)
    for x,y in [(-55,-19.2),(-16.5,-19.2),(16.5,-19.2),(55,-19.2),(-57,-30),(57,-30)]:np_lamp(x,y)
    for x,y in [(-30,-6),(30,-6),(-45,-5),(45,-5)]:np_lamp(x,y,5.4,True)
    for sign in [-1,1]:
        for x,y,s in [(60,-11,1.0),(64,-7,.86),(67,-14,.94),(71,-8,.9)]:
            np_request('young_tree',sign*x,y,scale=s)
            lathe((sign*x,y,.03),[(.85,0),(.85,.03)],'NP mulch','outer plaza circular tree pit',36)
    GROUP=NORTH_PLAZA_GROUPS['road']
    for xa,xb in [(-94,-10.8),(10.8,94)]:
        np_slab([(xa,-29),(xb,-29),(xb,-20),(xa,-20)],-.10,.24,'NP asphalt','Lacombe Drive actual asphalt carriageway')
    np_slab([(-10.8,-29),(10.8,-29),(10.8,-20),(-10.8,-20)],-.025,.20,'NP pale concrete','Lacombe central pale crossing approximate grade')
    for y in [-20.14,-28.86]:box((0,y,-.023),(21.6,.20,.025),'NP warm aggregate','Lacombe crossing reddish edge bands')
    for sign in [-1,1]:
        # No invented centerline lane markings; central crossing and sparse utility details only.
        np_strip([(sign*11.15,-29),(sign*11.15,-20)],.7,-.071,.11,'NP asphalt','crossing shallow transition strips')
    np_slab([(-92,-32),(92,-32),(92,-29),(-92,-29)],.021,.20,'NP pale concrete','Lacombe park-side sidewalk')
    for y in [-20,-29]:
        for xa,xb in [(-93,-11.2),(11.2,93)]:
            np_strip([(xa,y),(xb,y)],.20,.045,.26,'NP pale concrete','Lacombe roadway curbs')
    for x in range(-90,91,3):box((x,-30.5,.0225),(.013,2.95,.0015),'NP joint','Lacombe sidewalk joints')
    for x,y in [(-40,-28.85),(41,-20.15),(-64,-20.15),(70,-28.85)]:
        box((x,y,-.095),(.64,.39,.022),'NP black metal','road storm drain grates')
        for j in range(9):box((x-.26+j*.064,y,-.081),(.025,.35,.006),'NP joint','storm drain slot openings')
    GROUP=NORTH_PLAZA_GROUPS['furnishing']
    for x,y in [(-43,-30.5),(72,-30.5)]:
        lathe((x,y,.02),[(.085,0),(.085,.39),(.13,.43),(.10,.55),(.035,.61)],'NP hydrant','observed-type small hydrants',12)
        beam((x-.19,y,.39),(x+.19,y,.39),.06,'NP hydrant','hydrant side outlets',10)
    return {'paired_bed_rail_control_xy_m':base,'apron_outline_xy_m':apron}


def np_original_prototype(kind,variant):
    """A compact shared mesh; leaves are original solid-color portable geometry.
    Full leaf size is 5-14cm. Leaf translucency is conservative BSDF subsurface.
    Species are intentionally not asserted. Templates are never exported as stray
    prototype objects: instantiated objects share their Mesh datablock directly.
    """
    global B,GROUP
    old_b,old_g=B,GROUP;B={};GROUP='np prototype';r=random.Random(84201+variant*91+len(kind)*11)
    if kind in ('mature_tree','young_tree'):
        mature=kind=='mature_tree';height=10.4 if mature else 4.3;radius=4.65 if mature else 1.65
        trunk=.33 if mature else .075
        lathe((0,0,0),[(trunk*1.55,0),(trunk*1.1,.30),(trunk,.9),(trunk*.83,height*.35),(trunk*.57,height*.60),(trunk*.18,height*.78)],'NP bark','tree trunk',12)
        tips=[]
        for j in range(11 if mature else 8):
            t=j*2*pi/(11 if mature else 8)+r.uniform(-.27,.27);z=height*r.uniform(.30,.58)
            end=(radius*r.uniform(.5,.82)*cos(t),radius*r.uniform(.5,.82)*sin(t),height*r.uniform(.64,.84))
            beam((0,0,z),end,trunk*r.uniform(.27,.42),'NP bark','tree scaffold branch',9)
            for k in range(4):
                tt=t+(k-1.5)*.37;tip=(end[0]+radius*.26*cos(tt),end[1]+radius*.26*sin(tt),end[2]+r.uniform(.40,height*.19))
                beam(end,tip,trunk*.11,'NP bark','tree secondary branch',6);tips.append(tip)
                for n in range(2):
                    twig=(tip[0]+r.uniform(-.45,.45),tip[1]+r.uniform(-.45,.45),tip[2]+r.uniform(-.2,.40))
                    beam(tip,twig,trunk*.025,'NP bark','tree twigs',5)
        # Individual petiole-connected leaf clusters. Mature crowns stay broad and opaque enough.
        leaves=29000 if mature else 5400
        for i in range(leaves):
            tip=tips[i%len(tips)] if i%4 else (r.uniform(-radius*.17,radius*.17),r.uniform(-radius*.17,radius*.17),height*.93)
            ang=r.random()*2*pi;rr=sqrt(r.random())*(radius*.37)
            dz=r.uniform(-1,1)*(1.55 if mature else .68)
            p=Vector((tip[0]+rr*cos(ang),tip[1]+rr*sin(ang),tip[2]+dz))
            angle=r.random()*2*pi;length=r.uniform(.105,.185) if mature else r.uniform(.072,.125)
            u=Vector((cos(angle),sin(angle),r.uniform(-.7,.7))).normalized()*length
            v=Vector((-sin(angle),cos(angle),r.uniform(-.6,.6))).normalized()*length*.43
            mid=p+Vector((0,0,length*.17))
            vv=[tuple(p-u),tuple(p-u*.35+v),tuple(p+u*.6+v*.65),tuple(p+u),tuple(p+u*.6-v*.65),tuple(p-u*.35-v),tuple(mid)]
            ff=[(6,j,(j+1)%6) for j in range(6)]
            leafmat='NP leaf '+str(r.choices([0,1,2],[.35,.45,.2])[0])
            addmesh(vv,ff,leafmat,'individual deciduous leaves',uv=[(0,.5),(.32,1),(.74,.83),(1,.5),(.74,.17),(.32,0),(.5,.5)])
    elif kind=='grass':
        for j in range(36):
            t=r.random()*2*pi;length=r.uniform(.33,.86);rr=r.uniform(.01,.11)
            p=Vector((rr*cos(t),rr*sin(t),0));tip=p+Vector((cos(t)*length*.45,sin(t)*length*.45,length));mid=(p+tip)*.5+Vector((0,0,.08));side=Vector((-sin(t),cos(t),0))*r.uniform(.007,.014)
            addmesh([tuple(p-side),tuple(p+side),tuple(mid+side*.5),tuple(tip),tuple(mid-side*.5)],[(0,1,2),(0,2,4),(4,2,3)],'NP grass blade','ornamental grass blade',uv=[(0,0),(1,0),(1,.5),(.5,1),(0,.5)])
            if j%5==0:beam(tuple(tip),(tip.x,tip.y,tip.z+.15),.017,'NP grass plume','ornamental grass seed plume',5)
    else:
        # Mixed broad-leaf perennial clump with restrained seasonal flower heads.
        for j in range(16):
            t=j*pi*2/16+r.random()*.4;h=r.uniform(.24,.62);base=Vector((r.uniform(-.15,.15),r.uniform(-.15,.15),0));top=base+Vector((.20*cos(t),.20*sin(t),h))
            beam(tuple(base),tuple(top),.005,'NP grass blade','perennial stems',5)
            for k in range(5):
                z=(k+1)/7;pt=base.lerp(top,z);tt=t+(k%2)*pi;u=Vector((cos(tt),sin(tt),.30))*r.uniform(.12,.21);v=Vector((-sin(tt),cos(tt),0))*.065
                addmesh([tuple(pt),tuple(pt+u*.4+v),tuple(pt+u),tuple(pt+u*.4-v)],[(0,1,2),(0,2,3)],'NP leaf '+str(j%3),'broad perennial leaves',uv=[(0,.5),(.4,1),(1,.5),(.4,0)])
            if j%8==0:
                for k in range(7):
                    a=k*pi*2/7;c=top+Vector((cos(a)*.04,sin(a)*.04,.012*(k%2)))
                    lathe(tuple(c),[(.018,-.015),(.042,0),(.014,.023)],'NP flower '+str((j+variant)%3),'small seasonal perennial flower heads',5)
        for j in range(220):
            t=r.random()*2*pi;rr=sqrt(r.random())*.46
            p=Vector((rr*cos(t),rr*sin(t),r.uniform(.13,.48)))
            a=r.random()*2*pi;u=Vector((cos(a),sin(a),r.uniform(-.25,.45)))*r.uniform(.105,.17)
            v=Vector((-sin(a),cos(a),.12))*r.uniform(.046,.073)
            addmesh([tuple(p-u),tuple(p+v),tuple(p+u),tuple(p-v)],[(0,1,2),(0,2,3)],'NP leaf '+str(j%3),'dense lower perennial foliage',uv=[(0,.5),(.5,1),(1,.5),(.5,0)])
    batches=B;B,GROUP=old_b,old_g
    mesh=bpy.data.meshes.new('NP shared original '+kind+' '+str(variant));vv=[];ff=[];mi=[];uvfaces=[];materials=[]
    for (g,m,n),(verts,faces,uvs) in batches.items():
        if m not in materials:materials.append(m)
        materialindex=materials.index(m);start=len(vv);vv.extend(verts);ff.extend(tuple(start+i for i in face) for face in faces);mi.extend([materialindex]*len(faces))
        for f,u in zip(faces,uvs):
            if u is not None:uvfaces.append(u)
            else:
                tri=[Vector(verts[i]) for i in f[:3]];normal=(tri[1]-tri[0]).cross(tri[2]-tri[0]);ax=max(range(3),key=lambda j:abs(normal[j]));ids=[1,2] if ax==0 else [0,2] if ax==1 else [0,1]
                uvfaces.append([(verts[i][ids[0]],verts[i][ids[1]]) for i in f])
    mesh.from_pydata(vv,[],ff);mesh.update()
    for m in materials:mesh.materials.append(M[m])
    uv=mesh.uv_layers.new(name='MetricUV')
    for p,index,u in zip(mesh.polygons,mi,uvfaces):
        p.material_index=index;p.use_smooth=not materials[index].startswith('NP flower')
        scale=M[materials[index]].get('texture_repeat_m',1)
        for li,xy in zip(p.loop_indices,u):uv.data[li].uv=(xy[0]/scale,xy[1]/scale)
    # Triangulate polygon caps once on the shared datablock, preserving loop UVs.
    # glTF tangents stay portable without realizing each placed instance.
    import bmesh as _np_bmesh
    bm=_np_bmesh.new();bm.from_mesh(mesh)
    caps=[f for f in bm.faces if len(f.verts)>4]
    if caps:_np_bmesh.ops.triangulate(bm,faces=caps)
    bm.to_mesh(mesh);bm.free();mesh.update()
    mesh['provenance']='Original deterministic branching/leaf geometry, no external vegetation assets'
    mesh['tree_class']='Retained mature deciduous' if kind=='mature_tree' else 'Young deciduous/flowering class in leaf' if kind=='young_tree' else kind
    return mesh


def north_plaza_post_finalize(collections=None,room_nodes=None):
    """Call exactly once after main batches, before export selection/save.
    glTF reuses Mesh datablocks across standard object transforms. No collection
    instances, GN, alpha cards, particles or conversion into global B is needed.
    """
    if ERA!='2026' or scene.get('north_plaza_instances_created',False):return
    group=NORTH_PLAZA_GROUPS['plants'];col=bpy.data.collections.get(group)
    if not col:col=bpy.data.collections.new(group);scene.collection.children.link(col)
    parent=bpy.data.objects.new(group,None);col.objects.link(parent);parent['export_group']=True;parent['era']=ERA;parent['space']=group
    parent['evidence']='Observed vegetation classes; exact species, inventory and placement are approximate'
    cache={}
    for i,req in enumerate(NORTH_PLAZA_INSTANCE_REQUESTS):
        key=(req['kind'],req['variant'])
        if key not in cache:cache[key]=np_original_prototype(*key)
        ob=bpy.data.objects.new('North plaza '+req['kind']+' '+str(i).zfill(4),cache[key]);col.objects.link(ob);ob.parent=parent;ob.location=req['location'];ob.rotation_euler.z=req['rotation'];s=req['scale'];ob.scale=(s,s,s)
        ob['space']=group;ob['era']=ERA;ob['evidence_status']='Class and broad zone supported; placement and inventory approximate';ob['original_shared_mesh']=True
    if collections is not None:collections[group]=col
    if room_nodes is not None:room_nodes[group]=parent
    for ob in scene.objects:
        if ob.type=='MESH' and ob.get('space','').startswith(('00A','00B','00C','00D')):
            ob['source_scope']='2026 photo / 2023 completed north park topology; dimensions and elevations approximate'
    scene['north_plaza_instances_created']=True
    scene['north_plaza_shared_mesh_count']=len(cache)
    scene['north_plaza_instance_count']=len(NORTH_PLAZA_INSTANCE_REQUESTS)
    scene['north_plaza_unique_prototype_vertices']=sum(len(m.vertices) for m in cache.values())


if ERA=='2026':
    for name,asset,repeat in [('NP pale concrete','np_pale_concrete',3),('NP warm aggregate','np_warm_aggregate',2),('NP asphalt','np_asphalt',2),('NP turf','np_turf',2),('NP mulch','np_mulch',1),('NP bark','np_bark',1),('NP forecourt paving','np_forecourt_gray',3)]:pbr(name,'../north_plaza/textures/'+asset,repeat)
    m=M['Exterior Indiana limestone'].copy();m.name='NP forecourt stone';M['NP forecourt stone']=m
    m['texture_provenance']='Original project material; photo-supported stone class, not a site scan'
    for name,color,rough,metal in [('NP black metal',(.027,.034,.029),.43,.65),('NP bollard metal',(.28,.29,.27),.37,.78),('NP planter',(.045,.047,.038),.72,.15),('NP joint',(.115,.112,.100),.95,0),('NP leaf 0',(.040,.085,.012),.76,0),('NP leaf 1',(.061,.126,.019),.74,0),('NP leaf 2',(.094,.151,.028),.73,0),('NP grass blade',(.101,.170,.024),.89,0),('NP grass plume',(.29,.26,.15),.95,0),('NP flower 0',(.65,.61,.48),.80,0),('NP flower 1',(.38,.19,.34),.80,0),('NP flower 2',(.33,.30,.52),.80,0),('NP hydrant',(.24,.075,.050),.58,.45)]:mat(name,color,rough,metal)
    mat('NP frosted lamp',(.62,.63,.54),.45,0,.08)
    for name in ['NP leaf 0','NP leaf 1','NP leaf 2','NP grass blade']:
        M[name].node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.035
        M[name]['provenance']='Original restrained July leaf colors; no species or exact planting inventory assertion'
    NORTH_PLAZA_STATS['forecourt']=np_build_forecourt()
    NORTH_PLAZA_STATS['park']=np_build_park()
    NORTH_PLAZA_STATS['instance_requests']=len(NORTH_PLAZA_INSTANCE_REQUESTS)
    scene['north_plaza_status']='Source-led draft: three distinct zones; current topology supported, dimensions/grades approximate'
    scene['north_plaza_controls']=json.dumps(NORTH_PLAZA_CONTROLS)
    scene['north_plaza_rights']='Original procedural geometry/materials. OHM/ASLA images reference-only, never embedded.'
    scene['north_plaza_2017_limit']='Current 2023 park layout is absent from 2017; no old park layout claimed'
    NORTH_PLAZA_CAMERAS={
        'north_forecourt_detail':((67,-64,30),(0,-12,1.5),43),
        'north_plaza_axis':((0,-64,2.0),(0,-4,5.0),38),
        'north_park_aerial':((150,-240,168),(0,-100,0),44),
        'north_park_path':((4,-109,1.8),(0,-38,2.2),33),
    }
else:
    scene['north_plaza_status']='Disabled for 2017: post-2023 park topology is not period evidence'

GROUP=_NP_SAVED_GROUP
