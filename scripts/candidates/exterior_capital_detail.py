"""Opt-in original exterior capital ornament; does nothing on import.

Only replaces the legacy 'Corinthian acanthus approximation' beam loops.
Do not replace column(), its bell/profile, shaft, base, square abacus or datum.
Local Z=0 is z+h in column(); nominal r=.56 m. Coordinates and UVs are meters.
Study references establish visible form, not exact carving dimensions/counts.
Circumferential repetitions, reverse faces and inner leaf structure are inferred.
No images, scan data, downloaded meshes, surface damage or material changes.

Call emit_exterior_capital_detail(addmesh,x,y,z,h,r,m) instead of the two
legacy decorative loops ONLY when explicitly enabled by the caller. In a bpy
workflow create_linked_capital() reuses the same mesh datablock at each column.
Face fleurons are an optional inferred detail level visible in restored photos.
Their 2017 condition is unknown; this is NOT evidence of a restoration addition
or a historic absence. The option may be used in either era, never auto-switched.
"""
from dataclasses import dataclass, asdict
from functools import lru_cache
import math

TAU=2*math.pi
GEOMETRY_REVISION="03"  # Bump after algorithm edits to avoid stale bpy mesh reuse.

@dataclass(frozen=True)
class CapitalControls:
    # Photo-proportioned trials; these are NOT measured carving dimensions.
    nominal_radius_m: float=.56
    lower_root_z_m: float=-.755
    lower_leaf_height_m: float=.355
    lower_leaf_width_m: float=.365
    lower_root_radius_m: float=.460
    lower_body_outset_m: float=.052
    lower_projection_m: float=.168
    upper_root_z_m: float=-.617
    upper_leaf_height_m: float=.422
    upper_leaf_width_m: float=.402
    upper_root_radius_m: float=.465
    upper_body_outset_m: float=.087
    upper_projection_m: float=.209
    leaf_thickness_m: float=.016
    leaf_rib_relief_m: float=.014
    leaf_fan_fold_m: float=.009
    leaf_lobe_depth: float=.34
    leaf_lobe_rhythm: float=4.1
    leaf_minor_cut_depth: float=.085
    leaf_tip_taper_start: float=.56
    leaf_tip_width_fraction: float=.07
    leaf_turn_factor: float=.685
    # Inferred around unseen circumference, deliberately editable as positions.
    lower_angles_deg: tuple=(0,45,90,135,180,225,270,315)
    upper_angles_deg: tuple=(22.5,67.5,112.5,157.5,202.5,247.5,292.5,337.5)
    scroll_face_radius_m: float=.618
    scroll_root_inset_m: float=.135
    scroll_eye_offset_m: float=.447
    scroll_eye_z_m: float=-.212
    scroll_outer_radius_m: float=.122
    scroll_inner_radius_m: float=.029
    scroll_turns: float=1.18
    scroll_section_halfwidth_m: float=.029
    scroll_section_depth_m: float=.031
    fleuron_radius_m: float=.112
    fleuron_center_z_m: float=-.154
    fleurons: bool=False
    leaf_length_steps: int=28
    leaf_width_steps: int=8
    scroll_steps: int=52
    scroll_section_steps: int=10

DEFAULT_CONTROLS=CapitalControls()

@dataclass(frozen=True)
class MeshPart:
    name: str
    role: str
    vertices: tuple
    faces: tuple
    face_uv_m: tuple
    smooth_faces: tuple
    inference: str


def _add(a,b):return tuple(x+y for x,y in zip(a,b))
def _sub(a,b):return tuple(x-y for x,y in zip(a,b))
def _mul(a,k):return tuple(x*k for x in a)
def _dot(a,b):return sum(x*y for x,y in zip(a,b))
def _cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def _norm(a):return math.sqrt(_dot(a,a))
def _unit(a):
    l=_norm(a)
    if l<1e-12:raise ValueError('Degenerate frame')
    return _mul(a,1/l)
def _bezier(p,t):
    return tuple((1-t)**3*p[0][i]+3*(1-t)**2*t*p[1][i]+3*(1-t)*t*t*p[2][i]+t**3*p[3][i] for i in range(len(p[0])))

def _finish(name,role,v,f,uv,smooth,inference):
    # Every piece is a closed solid. Use exact input face winding to establish
    # a single consistent outward orientation, without any Blender repair.
    vol=0
    for q in f:
        for k in range(1,len(q)-1):vol+=_dot(v[q[0]],_cross(v[q[k]],v[q[k+1]]))/6
    if vol<0:f=[tuple(reversed(q)) for q in f];uv=[tuple(reversed(q)) for q in uv]
    return MeshPart(name,role,tuple(v),tuple(f),tuple(tuple(a) for a in uv),tuple(smooth),inference)


def _leaf(name,angle,root_z,height,width,root_radius,reach,c,role='acanthus',phase=0,body_outset_m=0):
    """Closed, lobed, ribbed carved blade with recurved tip, no zero-width pole.

    UV V follows centerline arc distance; U is blade width at each station.
    The back and all rim faces have independent metric islands. Thickness,
    internal reverse shape and the chosen lobing rhythm are reconstruction.
    """
    n=c.leaf_length_steps;k=c.leaf_width_steps
    er=(math.cos(angle),math.sin(angle),0);et=(-math.sin(angle),math.cos(angle),0)
    centers=[];halfwidth=[];tangents=[]
    for j in range(n+1):
        t=j/n
        # The last 28% rolls outward/down rather than ending in a straight rod.
        z=root_z+height*math.sin(math.pi*c.leaf_turn_factor*t)
        rr=root_radius+body_outset_m*(1-math.exp(-10*t))+reach*(t*t*(3-2*t))-.018*max(0,(t-.91)/.09)**2
        centers.append((rr,z))
        # Four coarse lobes, each with smaller incisions. This is photo-led
        # relief character, not a claim that four lobes were counted in situ.
        # Broad integrated body; the narrow recurved tongue is only the end.
        # The first trial stayed broad at the turn and hid its body in the
        # unchanged bell, producing cup-tops on apparent stems. This body
        # stands outside that support and narrows BEFORE it turns downward.
        envelope=.42+.58*math.sin(math.pi*min(1,t/.90))**.72
        envelope*=1-(1-c.leaf_tip_width_fraction)*max(0,(t-c.leaf_tip_taper_start)/(1-c.leaf_tip_taper_start))**.86
        lobing=1-c.leaf_lobe_depth*(.5+.5*math.cos(TAU*(c.leaf_lobe_rhythm*t+phase)))**3
        lobing*=1-c.leaf_minor_cut_depth*(.5+.5*math.cos(TAU*(2*c.leaf_lobe_rhythm*t+phase)))**4
        halfwidth.append(.5*width*envelope*lobing)
    arc=[0]
    for a,b in zip(centers,centers[1:]):arc.append(arc[-1]+math.hypot(b[0]-a[0],b[1]-a[1]))
    v=[];baseuv=[]
    for back in [False,True]:
        for j in range(n+1):
            t=j/n;rr,z=centers[j];w=halfwidth[j]
            for i in range(k+1):
                u=-1+2*i/k
                # Continuous relief, with deep center ridge and branching folds.
                relief=c.leaf_rib_relief_m*(1-u*u)*(.35+.65*math.exp(-32*u*u))
                # Branching fan folds run from the fine central rib to the
                # broad lobes; they are sculpted form, not cylindrical sticks.
                relief+=c.leaf_fan_fold_m*(1-u*u)*math.cos(5*math.pi*(t-.58*abs(u)))
                relief+=.008*(1-u*u)
                relief*=math.sin(math.pi*(.08+.84*t))*max(.10,1-2.2*max(0,t-.46))
                ca=centers[max(0,j-1)];cb=centers[min(n,j+1)]
                dr=cb[0]-ca[0];dz=cb[1]-ca[1];cl=math.hypot(dr,dz)
                offset=relief-(c.leaf_thickness_m if back else 0)
                rr2=rr+offset*dz/cl
                # Thickness follows the curved blade normal even at rolled tip.
                zz=z-offset*dr/cl-.022*u*u*math.sin(math.pi*t)
                v.append(_add(_mul(er,rr2),_add(_mul(et,w*u),(0,0,zz))))
                baseuv.append((w*u,arc[j]))
    layer=(n+1)*(k+1);f=[];uv=[];smooth=[]
    def face(ids,tex,sm=True):f.append(tuple(ids));uv.append(tuple(tex));smooth.append(sm)
    for back in [False,True]:
        off=layer if back else 0
        for j in range(n):
            for i in range(k):
                a=off+j*(k+1)+i;ids=(a,a+1,a+k+2,a+k+1)
                if back:ids=tuple(reversed(ids))
                face(ids,[baseuv[a] for a in ids])
    # A single clockwise perimeter viewed in parameter space closes the shell.
    perimeter=list(range(k+1))+[j*(k+1)+k for j in range(1,n+1)]+[n*(k+1)+i for i in range(k-1,-1,-1)]+[j*(k+1) for j in range(n-1,0,-1)]
    edge_s=0
    for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]):
        length=_norm(_sub(v[b],v[a]));th_a=_norm(_sub(v[a+layer],v[a]));th_b=_norm(_sub(v[b+layer],v[b]))
        face((b,a,a+layer,b+layer),((edge_s+length,0),(edge_s,0),(edge_s,th_a),(edge_s+length,th_b)),False)
        edge_s+=length
    return _finish(name,role,v,f,uv,smooth,'Visible leaf/rolled-tip character; full leaf rhythm, backs and closed underside inferred')


def _sweep(name,points,depth_axis,halfwidth,depth,segments,role):
    """Closed elliptical curved carving with arclength/circumference metric UVs."""
    axis=_unit(depth_axis);centers=[tuple(p) for p in points];v=[];f=[];uv=[];smooth=[];arc=[0]
    for a,b in zip(centers,centers[1:]):arc.append(arc[-1]+_norm(_sub(b,a)))
    frames=[];ringuv=[]
    for j,p in enumerate(centers):
        tangent=_unit(_sub(centers[min(j+1,len(centers)-1)],centers[max(0,j-1)]))
        inplane=_unit(_cross(axis,tangent));frames.append((inplane,axis))
        circumference=[];ring=[]
        for i in range(segments):
            a=TAU*i/segments
            # The small three-lobe crosssection is modeled relief, not a normal map.
            q=_add(_mul(inplane,halfwidth*math.cos(a)),_mul(axis,depth*math.sin(a)))
            ring.append(q);v.append(_add(p,q))
        circumference=[0]
        for i in range(segments):circumference.append(circumference[-1]+_norm(_sub(ring[(i+1)%segments],ring[i])))
        ringuv.append(circumference)
    for j in range(len(centers)-1):
        for i in range(segments):
            ni=(i+1)%segments;a=j*segments+i;b=j*segments+ni;cc=(j+1)*segments+ni;d=(j+1)*segments+i
            f.append((a,b,cc,d));uv.append(((arc[j],ringuv[j][i]),(arc[j],ringuv[j][i+1]),(arc[j+1],ringuv[j+1][i+1]),(arc[j+1],ringuv[j+1][i])));smooth.append(True)
    for j in [0,len(centers)-1]:
        idx=len(v);v.append(centers[j]);uaxis,vaxis=frames[j]
        for i in range(segments):
            a=j*segments+i;b=j*segments+(i+1)%segments
            ids=(idx,b,a) if j==0 else (idx,a,b)
            f.append(ids);uv.append(tuple((_dot(_sub(v[a],centers[j]),uaxis),_dot(_sub(v[a],centers[j]),vaxis)) for a in ids));smooth.append(False)
    return _finish(name,role,v,f,uv,smooth,'Visible opposed upper scroll character; trajectory, cross section and hidden reverse inferred')


def _scrolls(c):
    parts=[]
    for face in range(4):
        a=-math.pi/2+face*math.pi/2;er=(math.cos(a),math.sin(a),0);et=(-math.sin(a),math.cos(a),0)
        for side in [-1,1]:
            rad=c.scroll_outer_radius_m;eye=c.scroll_eye_offset_m;z=c.scroll_eye_z_m
            # Curve starts among upper leaves, rises to the scroll shoulder,
            # then winds inward in the facade-facing plane.
            stem=((side*.19,z-.265),(side*.18,z+rad*.75),(side*(eye-.16),z+rad),(side*eye,z+rad))
            points=[_bezier(stem,i/16) for i in range(17)]
            for j in range(1,c.scroll_steps+1):
                t=j/c.scroll_steps;theta=math.pi/2-TAU*c.scroll_turns*t;r=rad*(1-t)+c.scroll_inner_radius_m*t
                points.append((side*(eye+r*math.cos(theta)),z+r*math.sin(theta)))
            world=[]
            for j,(u,zz) in enumerate(points):
                # The rising scroll root belongs inside the retained bell.
                # A face-plane vertical tube gave a false dangling rod in
                # earlier neutral views. Emerge smoothly only at the shoulder.
                t=min(1,j/16);ease=t*t*(3-2*t)
                face_radius=c.scroll_face_radius_m-c.scroll_root_inset_m*(1-ease)
                world.append(_add(_mul(er,face_radius),_add(_mul(et,u),(0,0,zz))))
            parts.append(_sweep(f'face {face+1} opposed scroll {side:+d}',world,er,c.scroll_section_halfwidth_m,c.scroll_section_depth_m,c.scroll_section_steps,'volute'))
    return parts


def _fleurons(c):
    # This optional photograph-led detail is a coarse four-lobed face flower.
    # Its exact botanical count/profile is NOT resolved. Front face establishes
    # the motif; repeating on other faces is qualified unobserved reconstruction.
    parts=[]
    for face in range(4):
        a=-math.pi/2+face*math.pi/2;er=(math.cos(a),math.sin(a),0);et=(-math.sin(a),math.cos(a),0)
        for petal in range(4):
            theta=TAU*petal/4+math.pi/4;rr=c.fleuron_radius_m
            # A short round-ended bent closed lobe, deliberately restrained.
            pts=[]
            for j in range(13):
                t=j/12;rad=rr*(.12+.76*t)
                pts.append(_add(_mul(er,.663+.017*math.sin(math.pi*t)),_add(_mul(et,rad*math.cos(theta)),(0,0,c.fleuron_center_z_m+rad*math.sin(theta)))))
            parts.append(_sweep(f'optional inferred fleuron {face+1} lobe {petal+1}',pts,er,.022,.016,8,'optional inferred fleuron'))
    return parts


@lru_cache(maxsize=12)
def capital_parts(radius_m=.56,controls=DEFAULT_CONTROLS):
    """Return immutable reusable mesh parts, never create scene objects."""
    if radius_m<=0:raise ValueError('Radius must be positive')
    if controls.leaf_length_steps<8 or controls.leaf_width_steps<4:raise ValueError('Leaf tessellation too low')
    parts=[]
    for j,a in enumerate(controls.lower_angles_deg):
        parts.append(_leaf(f'lower curved acanthus {j+1}',math.radians(a),controls.lower_root_z_m,controls.lower_leaf_height_m,controls.lower_leaf_width_m,controls.lower_root_radius_m,controls.lower_projection_m,controls,body_outset_m=controls.lower_body_outset_m))
    for j,a in enumerate(controls.upper_angles_deg):
        parts.append(_leaf(f'upper curved acanthus {j+1}',math.radians(a),controls.upper_root_z_m,controls.upper_leaf_height_m,controls.upper_leaf_width_m,controls.upper_root_radius_m,controls.upper_projection_m,controls,phase=.22,body_outset_m=controls.upper_body_outset_m))
    parts.extend(_scrolls(controls))
    if controls.fleurons:parts.extend(_fleurons(controls))
    scale=radius_m/controls.nominal_radius_m
    if scale!=1:
        parts=[MeshPart(p.name,p.role,tuple(_mul(v,scale) for v in p.vertices),p.faces,tuple(tuple(_mul(uv,scale) for uv in face) for face in p.face_uv_m),p.smooth_faces,p.inference) for p in parts]
    return tuple(parts)


def emit_exterior_capital_detail(addmesh,x,y,z,h,r=.56,m='Exterior Indiana limestone',controls=DEFAULT_CONTROLS):
    """Builder adapter: pass its existing addmesh; decorate only, no supports.

    The caller must explicitly omit only the legacy acanthus beam loops.
    Its own finalizer should divide face_uv meters by material repeat meters.
    """
    for p in capital_parts(r,controls):
        addmesh([_add(v,(x,y,z+h)) for v in p.vertices],p.faces,m,'Exterior capital detailed '+p.role,face_uv=p.face_uv_m)
    return dict(asset='original exterior capital ornament',controls=asdict(controls),inference='Shared idealized visible-form reconstruction; not 14 known identical 2017 conditions')


def emit_legacy_foliage(beam,x,y,z,h,r,m):
    """Recovery: the untouched low-detail decoration from revision13 column()."""
    for level in [0,1]:
        for j in range(12):
            t=TAU*j/12+level*.25;rr=r*(1.02+level*.09);p=(x+rr*math.cos(t),y+rr*math.sin(t),z+h-.74+level*.28)
            beam(p,(p[0]+.11*math.cos(t),p[1]+.11*math.sin(t),p[2]+.46),.095,m,'Corinthian acanthus approximation',6)


def create_linked_capital(collection,material,location=(0,0,0),radius_m=.56,controls=DEFAULT_CONTROLS,repeat_m=1.0):
    """Optional bpy adapter, local origin z+h. Shared mesh data across 14 copies.

    UVs are explicitly divided by repeat_m. No object is made unless called.
    Blender sources preserve curved leaf faces and per-face smooth/flat flags.
    """
    import bpy,hashlib,json
    key=hashlib.sha256(json.dumps([GEOMETRY_REVISION,radius_m,asdict(controls),repeat_m,material.name],sort_keys=True).encode()).hexdigest()[:14]
    name='ECD reusable ornament '+key;me=bpy.data.meshes.get(name)
    if me is None:
        v=[];f=[];uv=[];smooth=[]
        for p in capital_parts(radius_m,controls):
            off=len(v);v.extend(p.vertices);f.extend(tuple(i+off for i in face) for face in p.faces);uv.extend(p.face_uv_m);smooth.extend(p.smooth_faces)
        me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();layer=me.uv_layers.new(name='Metric UV')
        for poly,tex,sm in zip(me.polygons,uv,smooth):
            poly.use_smooth=sm
            for li,coord in zip(poly.loop_indices,tex):layer.data[li].uv=(coord[0]/repeat_m,coord[1]/repeat_m)
        me.materials.append(material)
        me['generator_revision']=GEOMETRY_REVISION;me['uv_repeat_m']=repeat_m;me['original_geometry_only']=True;me['controls_json']=json.dumps(asdict(controls))
    ob=bpy.data.objects.new('Original exterior capital ornament',me);collection.objects.link(ob);ob.location=location
    ob['scope']='Decoration only; all column supports, bell/profile and abacus retained by caller'
    ob['period_uncertainty']='Shared idealized carving; individual2017 damage/replacements unresolved'
    ob['inferred_fleurons_enabled']=controls.fleurons
    return ob
