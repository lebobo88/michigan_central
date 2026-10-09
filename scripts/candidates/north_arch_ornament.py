"""Original photo-informed north arch molding and restrained keystone candidate.

Opt-in, no side effects on import/exec. Call build_north_arch_ornament(addmesh).
Coordinates are the existing station coordinates in metres. No photo textures,
image generation, source-mesh extraction, surveyed carving or exact historic
relief count is claimed. The exterior bracket is NOT the 11-foot interior
cartouche. See manifests/north_arch_ornament/README.md for integration.
"""
import math

NORTH_ARCH_ORNAMENT_CONTROLS = {
    'candidate_revision': 'north-arch-ornament-01',
    'centers_x_m': [-20.0, 0.0, 20.0],
    'glass_half_width_m': 3.2004,
    'spring_z_m': 10.2916,
    'glass_crown_z_m': 13.492,
    'arch_inner_radius_m': 3.2004,
    'arch_outer_radius_m': 3.8204,
    'arch_front_y_m': -1.2,
    'arch_back_y_m': -.08,
    'arch_outer_crown_z_m': 14.112,
    'return_half_width_m': 3.8354,
    'bearing_z_m': 12.912,
    'egg_row_z_m': 14.63,
    'bracket_z_range_m': [13.73, 15.59],
    'bracket_max_width_m': .92,
    'bracket_max_projection_y_m': -1.74,
    'bracket_exterior_dimensions': 'Original unmeasured proportional trial; NOT the documented 11ft INTERIOR cartouche',
    'surface_uv': 'Continuous metric swept/face charts, metric planar end caps; finalizer divides by material repeat',
    'evidence_status': 'Dated2017 topology, independent2024/2026 corroboration; no historic carving survey',
    'era_geometry': 'Identical surviving ornament interpretation in2017 and2026; no invented missing chunks or cracks',
    'limits': 'Exact egg/scallop counts, relief depth, returns and hidden faces are authored approximations. Pediment shield/crest and capital foliage are out of scope.',
}


def _nao_sub(a, b): return tuple(x-y for x, y in zip(a, b))
def _nao_dot(a, b): return sum(x*y for x, y in zip(a, b))
def _nao_cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def _nao_length(a): return math.sqrt(_nao_dot(a, a))
def _nao_norm(a):
    n = _nao_length(a)
    if n < 1e-12: raise ValueError('Zero length geometric direction')
    return tuple(x/n for x in a)


def _nao_emit(addmesh, verts, faces, material, name, face_uv=None):
    """Triangulate original polygon charts without changing their UV frame.

    Curved sweeps supply continuous metric charts; end caps and small convex
    relief use metric polygon-plane charts. Geometry remains shared/closed.
    """
    triangles=[];uvs=[]
    for fi,face in enumerate(faces):
        uv=face_uv[fi] if face_uv is not None else None
        if uv is None:
            pa,pb,pc=[verts[i] for i in face[:3]]
            ab,ac=_nao_sub(pb,pa),_nao_sub(pc,pa)
            u=_nao_norm(ab);n=_nao_norm(_nao_cross(ab,ac));v=_nao_cross(n,u)
            uv=[(_nao_dot(_nao_sub(verts[i],pa),u),_nao_dot(_nao_sub(verts[i],pa),v)) for i in face]
        for j in range(1,len(face)-1):
            triangles.append((face[0],face[j],face[j+1]));uvs.append([uv[0],uv[j],uv[j+1]])
    volume=sum(_nao_dot(verts[a],_nao_cross(verts[b],verts[c]))/6 for a,b,c in triangles)
    if volume<0:triangles=[tuple(reversed(f)) for f in triangles];uvs=[list(reversed(uv)) for uv in uvs]
    addmesh(verts,triangles,material,name,face_uv=uvs)


def _nao_sweep(addmesh, path, radius, material, name, sides=8):
    """Closed smoothly curving relief tube with explicit endpoint caps."""
    verts = []; rings = []; old_u = None
    for j, p in enumerate(path):
        direction = _nao_norm(_nao_sub(path[min(j+1, len(path)-1)], path[max(0, j-1)]))
        axis = (0, 1, 0) if abs(direction[1]) < .9 else (0, 0, 1)
        u = _nao_norm(_nao_cross(direction, axis)); v = _nao_cross(direction, u)
        if old_u is not None and _nao_dot(u, old_u) < 0: u=tuple(-q for q in u); v=tuple(-q for q in v)
        old_u = u; rings.append(list(range(len(verts), len(verts)+sides)))
        rr = radius[j] if isinstance(radius, (tuple, list)) else radius
        for i in range(sides):
            th=2*math.pi*i/sides
            verts.append(tuple(p[k]+rr*(math.cos(th)*u[k]+math.sin(th)*v[k]) for k in range(3)))
    faces=[];uvs=[];dist=[0.]
    for a,b in zip(path,path[1:]):dist.append(dist[-1]+_nao_length(_nao_sub(b,a)))
    for j,(aa,bb) in enumerate(zip(rings,rings[1:])):
        ra=radius[j] if isinstance(radius,(tuple,list)) else radius
        rb=radius[j+1] if isinstance(radius,(tuple,list)) else radius
        for i in range(sides):
            faces.append((aa[i],aa[(i+1)%sides],bb[(i+1)%sides],bb[i]))
            uvs.append([(dist[j],2*math.pi*ra*i/sides),(dist[j],2*math.pi*ra*(i+1)/sides),(dist[j+1],2*math.pi*rb*(i+1)/sides),(dist[j+1],2*math.pi*rb*i/sides)])
    # Fan caps use true distinct centroid vertices, not zero-radius rings.
    for ring, p in [(rings[0], path[0]), (rings[-1], path[-1])]:
        center=len(verts); verts.append(p)
        for i in range(sides):
            faces.append((center,ring[(i+1)%sides],ring[i]) if ring is rings[0] else (center,ring[i],ring[(i+1)%sides]));uvs.append(None)
    _nao_emit(addmesh,verts,faces,material,name,uvs)


def _nao_extrude_profile(addmesh, x0, x1, profile_yz, material, name):
    """Closed convex/beveled molding cross section, extruded in X."""
    n=len(profile_yz); verts=[(x,y,z) for x in (x0,x1) for y,z in profile_yz]
    faces=[]
    for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    # These profiles are convex. Explicit triangle fans avoid exporter n-gons.
    for side, x in [(0,x0),(1,x1)]:
        ci=len(verts); verts.append((x,sum(y for y,z in profile_yz)/n,sum(z for y,z in profile_yz)/n))
        ring=[side*n+i for i in range(n)]
        for i in range(n): faces.append((ci,ring[(i+1)%n],ring[i]) if side==0 else (ci,ring[i],ring[(i+1)%n]))
    _nao_emit(addmesh,verts,faces,material,name)


def _nao_archivolt(addmesh, cx, material):
    """Continuous profiled ring WITHIN the exact revision13 stone-arch bounds.

    Radius and front/back extents are not moved. This replaces the plain ring;
    it must never be layered over that ring's coplanar front faces.
    """
    ri=3.2004; ro=3.8204; spring=10.2916
    # Cross section: inner back -> inner front -> broad torus/cove/fillets -> outer back.
    profile=[(ri,-.08),(ri,-.98),(ri+.035,-1.025),(ri+.075,-1.04),
             (ri+.115,-1.045),(ri+.145,-1.080),(ri+.178,-1.115),(ri+.218,-1.13),
             (ri+.258,-1.115),(ri+.292,-1.08),(ri+.320,-1.035),
             (ri+.346,-1.02),(ri+.366,-1.095),(ri+.397,-1.115),
             (ri+.435,-1.145),(ri+.475,-1.175),(ri+.515,-1.20),
             (ri+.551,-1.19),(ri+.579,-1.145),(ri+.600,-1.13),(ro,-1.13),(ro,-.08)]
    segments=40; n=len(profile); verts=[]
    for j in range(segments+1):
        th=math.pi*j/segments
        verts.extend((cx+r*math.cos(th),y,spring+r*math.sin(th)) for r,y in profile)
    faces=[];uvs=[];perimeter=[0.]
    for a,b in zip(profile,profile[1:]+profile[:1]):perimeter.append(perimeter[-1]+math.hypot(b[0]-a[0],b[1]-a[1]))
    for j in range(segments):
        for i in range(n):
            ni=(i+1)%n;faces.append((j*n+i,j*n+ni,(j+1)*n+ni,(j+1)*n+i))
            uvs.append([(math.pi*j/segments*profile[i][0],perimeter[i]),(math.pi*j/segments*profile[ni][0],perimeter[i+1]),(math.pi*(j+1)/segments*profile[ni][0],perimeter[i+1]),(math.pi*(j+1)/segments*profile[i][0],perimeter[i])])
    # Concave radial profile caps are triangulated by a back-edge fan. All front
    # radii increase strictly and the two back points form a star-shaped cap.
    for j in [0,segments]:
        ids=[j*n+i for i in range(n)]
        cap=[(ids[0],ids[i],ids[i+1]) for i in range(1,n-1)]
        faces.extend(cap if j==segments else [tuple(reversed(t)) for t in cap]);uvs.extend([None]*len(cap))
    _nao_emit(addmesh,verts,faces,material,'north candidate continuous profiled archivolt',uvs)


def _nao_egg(addmesh, x, y, z, material):
    """A small original ovoid relief, not a scanned historic egg count/profile."""
    sides=10; levels=7; verts=[(x,y,z-.093)]; rings=[]
    for j in range(1,levels):
        th=math.pi*j/levels; width=.057*math.sin(th)*(1+.17*math.cos(th))
        ring=[]
        for i in range(sides):
            a=2*math.pi*i/sides; ring.append(len(verts));verts.append((x+width*math.cos(a),y+.028*math.sin(th)*math.sin(a),z-.093*math.cos(th)))
        rings.append(ring)
    top=len(verts);verts.append((x,y,z+.093));faces=[]
    for i in range(sides):faces.append((0,rings[0][(i+1)%sides],rings[0][i]))
    for a,b in zip(rings,rings[1:]):
        for i in range(sides):faces.append((a[i],a[(i+1)%sides],b[(i+1)%sides],b[i]))
    for i in range(sides):faces.append((rings[-1][i],rings[-1][(i+1)%sides],top))
    _nao_emit(addmesh,verts,faces,material,'north candidate original egg relief')


def _nao_bracket_shape(t):
    # Softly flared top and bottom with a waisted middle; all original dimensions.
    width=.31+.15*t+.034*math.sin(2*math.pi*t)
    front=-1.40-.24*math.sin(math.pi*t)-.045*t
    return width,front


def _nao_keystone(addmesh,cx,material):
    z0=13.73; height=1.86; nz=24; nx=16; verts=[]
    # Front/back sheets share side, top and bottom edges via closing strips.
    for back in [False,True]:
        for j in range(nz+1):
            t=j/nz; width,front=_nao_bracket_shape(t)
            for i in range(nx+1):
                u=-1+2*i/nx
                y=-.90 if back else front-.055*math.cos(u*math.pi/2)**2
                verts.append((cx+width*u,y,z0+height*t))
    stride=nx+1; sheet=(nz+1)*stride;faces=[];uvs=[]
    for j in range(nz):
        for i in range(nx):
            a=j*stride+i;new=[(a,a+1,a+stride+1,a+stride),(sheet+a+stride,sheet+a+stride+1,sheet+a+1,sheet+a)];faces.extend(new);uvs.extend([[(verts[k][0]-cx,verts[k][2]-z0) for k in f] for f in new])
    for j in range(nz):
        a=j*stride;b=(j+1)*stride;faces.append((a,b,sheet+b,sheet+a))
        a=j*stride+nx;b=(j+1)*stride+nx;faces.append((a,sheet+a,sheet+b,b))
    for i in range(nx):
        a=i;faces.append((a,sheet+a,sheet+a+1,a+1))
        a=nz*stride+i;faces.append((a,a+1,sheet+a+1,sheet+a))
    uvs.extend([None]*(len(faces)-len(uvs)))
    _nao_emit(addmesh,verts,faces,material,'north candidate curved exterior keystone body',uvs)
    # Two long soft-edged straps and restrained scallop lines; no capital foliage.
    for side in [-1,1]:
        path=[]
        for j in range(23):
            t=.06+.88*j/22;w,f=_nao_bracket_shape(t)
            path.append((cx+side*w*.83,f-.035,z0+height*t))
        _nao_sweep(addmesh,path,.026,material,'north candidate keystone rolled side straps',8)
    # Shallow overlapping scallops describe the photographed scale-like surface,
    # without pretending to recover the exact count or hidden carving.
    for row in range(5):
        t=.42+row*.10;w,f=_nao_bracket_shape(t)
        for col in [-1,0,1]:
            xp=cx+col*.155+(0.035 if row%2 else -.035);path=[]
            for j in range(13):
                a=math.pi*j/12
                xx=xp+.073*math.cos(a);zz=z0+height*t-.125*math.sin(a)
                tt=(zz-z0)/height;ww,ff=_nao_bracket_shape(tt);u=(xx-cx)/ww
                yy=ff-.055*math.cos(u*math.pi/2)**2-.005
                path.append((xx,yy,zz))
            _nao_sweep(addmesh,path,.016,material,'north candidate original shallow scallop relief',7)
    # A small fan of rounded lower folds preserves the clear glass envelope.
    for k in [-3,-2,-1,0,1,2,3]:
        path=[]
        for j in range(15):
            t=.075+.245*j/14;w,f=_nao_bracket_shape(t)
            xx=cx+k*.062*(.45+.55*j/14);u=(xx-cx)/w
            path.append((xx,f-.055*math.cos(u*math.pi/2)**2-.012,z0+height*t))
        _nao_sweep(addmesh,path,.018,material,'north candidate keystone lower curved folds',7)


def generic_dentil_in_arch_bay(kind, x, y, z, centers=(-20,0,20)):
    """Narrow opt-in predicate for builder-time cube omission, not mesh deletion.

    Apply ONLY at the two documented north cube-emission sites, never by name
    across an already batched full scene. Column bays are retained unchanged.
    """
    in_gap=any(abs(x-c)<3.8354 for c in centers)
    if kind=='north_entablature':return in_gap and abs(z-14.62)<1e-6 and abs(y+1.40)<1e-6
    if kind=='monumental_pediment':return in_gap and abs(z-15.27)<1e-6 and abs(y+1.43)<1e-6
    return False


def build_north_arch_ornament(addmesh, centers=(-20,0,20), material='Exterior Indiana limestone', include_archivolt=True):
    """Generate isolated component only; no live scene deletion or transforms."""
    for cx in centers:
        if include_archivolt:_nao_archivolt(addmesh,cx,material)
        left=cx-3.8354;right=cx+3.8354
        # Small recessed molding replaces the low block row, keeping its backing.
        # Segment around the bracket; deliberate small embed at bracket edges.
        for x0,x1 in [(left,cx-.38),(cx+.38,right)]:
            _nao_extrude_profile(addmesh,x0,x1,[(-1.265,14.495),(-1.34,14.495),(-1.390,14.525),(-1.410,14.725),(-1.36,14.755),(-1.265,14.755)],material,'north candidate recessed egg bed')
            count=max(1,int((x1-x0)/.18));pitch=(x1-x0)/count
            for i in range(count):
                x=x0+pitch*(i+.5);_nao_egg(addmesh,x,-1.423,14.63,material)
                # U-outline and pointed dart give small-scale continuous ornament.
                curve=[(x+.074*math.cos(a),-1.437,14.645-.103*math.sin(a)) for a in [math.pi*j/12 for j in range(13)]]
                _nao_sweep(addmesh,curve,.008,material,'north candidate fine egg surrounds',6)
                if i<count-1:
                    dx=x+pitch/2
                    _nao_sweep(addmesh,[(dx-.019,-1.417,14.703),(dx,-1.438,14.565),(dx+.019,-1.417,14.703)],.007,material,'north candidate original dart accents',6)
            # Smooth upper pediment bed in the recessed central bay, without cubes.
            _nao_extrude_profile(addmesh,x0,x1,[(-1.215,15.135),(-1.315,15.135),(-1.420,15.205),(-1.435,15.32),(-1.39,15.40),(-1.215,15.40)],material,'north candidate smooth recessed pediment bed')
        # Fine molding turns in depth at the existing bay boundary. No support
        # stone, abacus, lower bearing band or column-bay dentil is deleted.
        for side in [-1,1]:
            x=cx+side*3.812
            _nao_sweep(addmesh,[(x,-1.405,14.747),(x+side*.017,-1.46,14.747),(x+side*.017,-1.56,14.747)],.017,material,'north candidate rounded molding depth returns',8)
        _nao_keystone(addmesh,cx,material)
    return dict(NORTH_ARCH_ORNAMENT_CONTROLS,generated_centers_x_m=list(centers),archivolt_replaces_plain_ring=include_archivolt)
