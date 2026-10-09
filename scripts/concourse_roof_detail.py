"""Source-informed concourse roof replacement, two eras, metric authored geometry.

Execute in the main B-batch namespace AFTER the old concourse roof is emitted.
Only the six explicitly named former roof batches may be replaced. Walls, floors,
public-room interfaces and the separate south passenger-ramp roof are untouched.
This component never executes the main builder, loads a photograph, or reads CLI
arguments. All member sizes and attachment patterns are modeled approximations.
"""
import math as _cr_math
from copy import deepcopy as _cr_deepcopy

_CR_SAVED_GROUP = GROUP
_CR_OLD_GROUP = '05 CONCOURSE | restored glazing and structural roof'
_CR_GROUP = '05 CONCOURSE | source-informed roof structure'
_CR_OLD_NAMES = (
    'concourse primary truss chords', 'concourse truss tie',
    'concourse truss posts', 'concourse truss diagonals',
    'concourse roof purlins', 'restored glazed concourse roof',
)
CONCOURSE_ROOF_DEFAULTS = {
    'width_m': 58.9788, 'depth_m': 23.7744, 'center_y_m': 63.4,
    'eave_centerline_z_m': 9.5, 'rise_m': 4.2, 'truss_stations': 14,
    'half_span_panels': 4, 'purlin_intervals_per_slope': 6,
    'sash_subdivisions_per_truss_bay': 4,
    'opaque_eave_band_horizontal_width_m': 2.25,
    'chord_width_m': .26, 'chord_depth_m': .30,
    'chord_flange_m': .021, 'chord_web_m': .014,
    'tie_width_m': .22, 'tie_depth_m': .24,
    'tie_flange_m': .018, 'tie_web_m': .012,
    'web_angle_leg_m': .095, 'web_angle_thickness_m': .012,
    'web_angle_gap_m': .035,
    'purlin_width_m': .090, 'purlin_depth_m': .140,
    'purlin_flange_m': .012, 'purlin_web_m': .009,
    'purlin_axis_normal_offset_m': .193,
    'roof_skin_normal_offset_m': .285,
    'glazing_thickness_m': .008, 'deck_thickness_m': .040,
    'opaque_deck_rib_spacing_m': .22, 'opaque_deck_rib_width_m': .028,
    'opaque_deck_rib_depth_m': .018,
    'sash_width_m': .045, 'sash_depth_m': .048,
    'sash_cap_width_m': .068, 'sash_cap_thickness_m': .012,
    'gusset_thickness_m': .014, 'gusset_half_height_m': .22,
    'gusset_half_length_m': .30, 'fastener_radius_m': .020,
    'fastener_head_depth_m': .014,
    'include_2026_visible_light_fittings': False,
}
CONCOURSE_ROOF_CONTROLS = _cr_deepcopy(CONCOURSE_ROOF_DEFAULTS)
CONCOURSE_ROOF_CONTROLS.update(globals().get('CONCOURSE_ROOF_CONTROL_OVERRIDES', {}))


def cr_add(a,b): return tuple(x+y for x,y in zip(a,b))
def cr_sub(a,b): return tuple(x-y for x,y in zip(a,b))
def cr_mul(a,s): return tuple(x*s for x in a)
def cr_dot(a,b): return sum(x*y for x,y in zip(a,b))
def cr_cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def cr_length(a): return _cr_math.sqrt(cr_dot(a,a))
def cr_unit(a):
    length=cr_length(a)
    if length < 1e-9: raise ValueError('Zero length concourse roof member')
    return cr_mul(a,1/length)


def cr_triangulate_section(section):
    """Ear clipping in local metric2D, rejecting zero-area cap triangles."""
    def turn(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    polygon=list(range(len(section)));triangles=[];epsilon=1e-12
    while len(polygon)>3:
        found=False
        for j,b in enumerate(polygon):
            a=polygon[j-1];c=polygon[(j+1)%len(polygon)]
            if turn(section[a],section[b],section[c])<=epsilon:continue
            blocked=False
            for other in polygon:
                if other in (a,b,c):continue
                p=section[other]
                if min(turn(section[a],section[b],p),turn(section[b],section[c],p),turn(section[c],section[a],p))>=-epsilon:
                    blocked=True;break
            if blocked:continue
            triangles.append((a,b,c));del polygon[j];found=True;break
        if not found:raise ValueError('Could not triangulate concourse profile without zero-area caps')
    if turn(*(section[i] for i in polygon))<=epsilon:raise ValueError('Collapsed terminal profile cap')
    triangles.append(tuple(polygon));return triangles


def cr_profile_prism(p,q,section,material,label,reference=(1,0,0)):
    """Closed extrusion of a simple CCW section; explicit metric face-corner UVs.

    Side UV distance follows section perimeter and member length; caps use the
    section's actual metric coordinates. Concave profile caps are deterministically
    triangulated in local2D before global float32 conversion.
    """
    axis=cr_unit(cr_sub(q,p)); along=cr_length(cr_sub(q,p))
    u=cr_sub(reference,cr_mul(axis,cr_dot(reference,axis)))
    if cr_length(u)<1e-7:
        fallback=(0,1,0) if abs(axis[1])<.9 else (0,0,1)
        u=cr_sub(fallback,cr_mul(axis,cr_dot(fallback,axis)))
    u=cr_unit(u); v=cr_cross(axis,u)
    if v[2]<-.000001: u=cr_mul(u,-1); v=cr_mul(v,-1)
    signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(section,section[1:]+section[:1]))
    if signed<=1e-10: raise ValueError('Section must be nondegenerate and counter-clockwise: '+label)
    vv=[cr_add(c,cr_add(cr_mul(u,a),cr_mul(v,b))) for c in (p,q) for a,b in section]
    n=len(section);ff=[];fu=[]
    # Triangulate in the exact local2D section before conversion to global
    # float32 mesh coordinates. Blender's concave-ngon tessellation can produce
    # near-collinear slivers at long, rotated I-section caps.
    for tri in cr_triangulate_section(section):
        bottom=tuple(reversed(tri));top=tuple(i+n for i in tri)
        ff.extend([bottom,top]);fu.extend([[section[i] for i in bottom],[section[i] for i in tri]])
    distance=0.
    for i in range(n):
        j=(i+1)%n; edge=cr_length(cr_sub(section[j],section[i]))
        if edge<1e-8: raise ValueError('Duplicate profile corners')
        ff.append((i,j,j+n,i+n))
        fu.append([(distance,0),(distance+edge,0),(distance+edge,along),(distance,along)])
        distance+=edge
    addmesh(vv,ff,material,label,face_uv=fu)


def cr_rect(w,d): return [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
def cr_i(w,d,tf,tw):
    if not 0<tw<w or not 0<2*tf<d: raise ValueError('Invalid I-section proportions')
    return [(-w/2,-d/2),(w/2,-d/2),(w/2,-d/2+tf),(tw/2,-d/2+tf),
            (tw/2,d/2-tf),(w/2,d/2-tf),(w/2,d/2),(-w/2,d/2),
            (-w/2,d/2-tf),(-tw/2,d/2-tf),(-tw/2,-d/2+tf),(-w/2,-d/2+tf)]


def cr_double_angle(p,q,material,label,c):
    """Paired L silhouettes, a qualified built-up web-member interpretation."""
    leg=c['web_angle_leg_m'];t=c['web_angle_thickness_m'];gap=c['web_angle_gap_m']
    base=[(0,0),(leg,0),(leg,t),(t,t),(t,leg),(0,leg)]
    for side in (-1,1):
        section=[(side*(a+gap/2),b-leg/2) for a,b in base]
        if side<0: section=list(reversed(section))
        cr_profile_prism(p,q,section,material,label)


def cr_material_copy(name,source,color=None,roughness=None,metallic=None,transmission=None):
    """Clone an existing authored PBR; source material and maps stay read-only."""
    if name in M: return name
    m=M[source].copy();m.name=name;M[name]=m
    p=m.node_tree.nodes.get('Principled BSDF')
    if p is None: raise ValueError('Expected standard Principled PBR source')
    for socket,value in [('Base Color',(*color,1) if color is not None else None),
                         ('Roughness',roughness),('Metallic',metallic),
                         ('Transmission Weight',transmission)]:
        if value is not None:
            for link in list(p.inputs[socket].links):m.node_tree.links.remove(link)
            p.inputs[socket].default_value=value
    m['texture_repeat_m']=1.0
    m['texture_provenance']='Original authored constant PBR; photo-informed material class, no reference pixels'
    m['physical_limit']='Approximate appearance; no measured reflectance or coating/section survey'
    return name


def cr_gusset(x,y,z,material,c,label):
    # Regularized diamond-like plates; actual fabrication/fastener layout unresolved.
    w=c['gusset_half_length_m'];h=c['gusset_half_height_m'];t=c['gusset_thickness_m']
    section=[(-w*.65,-h),(w*.65,-h),(w,h*.25),(0,h),(-w,h*.25)]
    for side in (-1,1):
        xx=x+side*(c['chord_width_m']/2+.013)
        a=xx-side*t/2;b=xx+side*t/2
        # Y is section U, Z is section V for extrusion along +X.
        cr_profile_prism((min(a,b),y,z),(max(a,b),y,z),section,material,label+' inferred gusset plates',reference=(0,1,0))
        for dy,dz in [(-w*.41,-h*.38),(w*.41,-h*.38),(0,h*.37)]:
            start=xx+side*t/2;end=start+side*c['fastener_head_depth_m']
            r=c['fastener_radius_m']
            poly=[(r*_cr_math.cos(i*2*_cr_math.pi/8),r*_cr_math.sin(i*2*_cr_math.pi/8)) for i in range(8)]
            cr_profile_prism((min(start,end),y+dy,z+dz),(max(start,end),y+dy,z+dz),poly,material,
                             label+' regularized rivet bolt head approximations',reference=(0,1,0))


def cr_validate(c):
    unknown=set(c)-set(CONCOURSE_ROOF_DEFAULTS)
    if unknown:raise ValueError('Unknown roof control keys: '+str(sorted(unknown)))
    for k,v in c.items():
        if isinstance(v,bool):continue
        if not isinstance(v,(float,int)) or not _cr_math.isfinite(v):raise ValueError('Invalid roof control '+k)
        if k not in ('center_y_m','eave_centerline_z_m') and v<=0:raise ValueError('Nonpositive roof control '+k)
    for key in ('truss_stations','half_span_panels','purlin_intervals_per_slope','sash_subdivisions_per_truss_bay'):
        if not isinstance(c[key],int) or c[key]<2:raise ValueError('Integer count >=2 required: '+key)
    if c['opaque_eave_band_horizontal_width_m']>=c['depth_m']/2:raise ValueError('Opaque band consumes entire roof')
    if c['web_angle_thickness_m']>=c['web_angle_leg_m']:raise ValueError('Invalid angle section')
    if globals().get('SWAP_XY',False):raise ValueError('Concourse roof expects station-global coordinates, SWAP_XY must be false')
    if str(ERA) not in ('2017','2026'):raise ValueError('Unsupported roof era')
    if bool(AGED)!=(str(ERA)=='2017'):raise ValueError('ERA and AGED disagree')


def cr_build(c):
    global GROUP
    cr_validate(c);GROUP=_CR_GROUP
    aged=bool(AGED)
    steel=cr_material_copy('Concourse '+str(ERA)+' inferred structural steel','Roof steel',
        (.125,.066,.036) if aged else (.060,.064,.060),.82 if aged else .48,.30 if aged else .70)
    detail=cr_material_copy('Concourse '+str(ERA)+' inferred fastener steel','Roof steel',
        (.088,.045,.023) if aged else (.078,.081,.073),.80 if aged else .43,.30 if aged else .72)
    glass=cr_material_copy('Concourse restored roof glazing','Glass clear',(.88,.93,.95),.07,0.,.96) if not aged else None
    deck=cr_material_copy('Concourse restored opaque perimeter deck','Roof dark copper',(.050,.051,.047),.72,.25) if not aged else None
    half=c['depth_m']/2; x0=-c['width_m']/2; x1=-x0;cy=c['center_y_m'];z0=c['eave_centerline_z_m'];rise=c['rise_m']
    stations=[x0+(x1-x0)*j/(c['truss_stations']-1) for j in range(c['truss_stations'])]
    chord=cr_i(c['chord_width_m'],c['chord_depth_m'],c['chord_flange_m'],c['chord_web_m'])
    tie=cr_i(c['tie_width_m'],c['tie_depth_m'],c['tie_flange_m'],c['tie_web_m'])
    pn=c['half_span_panels']
    for x in stations:
        cr_profile_prism((x,cy-half,z0),(x,cy+half,z0),tie,steel,'concourse refined built-up tie flanges and webs')
        for side in (-1,1):
            cr_profile_prism((x,cy+side*half,z0),(x,cy,z0+rise),chord,steel,'concourse refined flanged upper chords')
            for k in range(1,pn):
                y=cy+side*half*k/pn;zt=z0+rise*(1-k/pn)
                cr_double_angle((x,y,z0),(x,y,zt),steel,'concourse refined paired angle posts',c)
            for k in range(pn-1):
                ya=cy+side*half*k/pn;za=z0+rise*(1-k/pn);yb=cy+side*half*(k+1)/pn
                cr_double_angle((x,ya,za),(x,yb,z0),steel,'concourse refined paired angle diagonals',c)
        cr_double_angle((x,cy,z0),(x,cy,z0+rise),steel,'concourse refined single central paired angle post',c)
        # Source-visible junctions are represented without claiming a fabrication drawing.
        nodes={(cy,z0),(cy,z0+rise),(cy-half,z0),(cy+half,z0)}
        for side in (-1,1):
            for k in range(1,pn):
                yy=cy+side*half*k/pn;nodes.add((yy,z0));nodes.add((yy,z0+rise*(1-k/pn)))
        for y,z in sorted(nodes):cr_gusset(x,y,z,detail,c,'concourse refined')
    purlin=cr_i(c['purlin_width_m'],c['purlin_depth_m'],c['purlin_flange_m'],c['purlin_web_m'])
    skin=c['roof_skin_normal_offset_m']; offset=c['purlin_axis_normal_offset_m']
    for side in (-1,1):
        normal=cr_unit((0,side*rise,half));slope_u=cr_unit((0,half,-side*rise))
        def point(x,d,off=0):return cr_add((x,cy+side*d,z0+rise*(1-d/half)),cr_mul(normal,off))
        # Ridge purlin exists once, not twice on top of itself.
        for k in range(c['purlin_intervals_per_slope']+1):
            if k==0 and side<0:continue
            d=half*k/c['purlin_intervals_per_slope']
            cr_profile_prism(point(x0,d,offset),point(x1,d,offset),purlin,steel,
                'concourse refined flanged longitudinal purlins',reference=slope_u)
        sx=[]
        for j in range(len(stations)-1):
            sx.extend(stations[j]+(stations[j+1]-stations[j])*k/c['sash_subdivisions_per_truss_bay']
                      for k in range(c['sash_subdivisions_per_truss_bay']))
        sx.append(x1)
        glass_edge=half-c['opaque_eave_band_horizontal_width_m']
        # Fine surviving secondary grid retained in2017; no residual-pane inventory.
        for x in sx:
            cr_profile_prism(point(x,0,skin),point(x,half,skin),cr_rect(c['sash_width_m'],c['sash_depth_m']),steel,
                'concourse refined secondary roof bars' if aged else 'concourse restored slope glazing bars')
            if not aged:
                cr_profile_prism(point(x,0,skin+c['sash_depth_m']/2),point(x,glass_edge,skin+c['sash_depth_m']/2),
                    cr_rect(c['sash_cap_width_m'],c['sash_cap_thickness_m']),detail,'concourse restored glazing pressure caps')
        if not aged:
            # Independent sealed panes, between sash rails, instead of a single
            # glass plane projected through every member. Pane count is regularized.
            cuts=sorted({0.,glass_edge}|{half*k/c['purlin_intervals_per_slope'] for k in range(1,c['purlin_intervals_per_slope']) if half*k/c['purlin_intervals_per_slope']<glass_edge})
            for d in cuts:
                cr_profile_prism(point(x0,d,skin),point(x1,d,skin),cr_rect(c['sash_width_m'],c['sash_depth_m']),steel,
                    'concourse restored longitudinal glazing rails',reference=slope_u)
                cr_profile_prism(point(x0,d,skin+c['sash_depth_m']/2),point(x1,d,skin+c['sash_depth_m']/2),
                    cr_rect(c['sash_cap_width_m'],c['sash_cap_thickness_m']),detail,'concourse restored longitudinal pressure caps',reference=slope_u)
            gap=c['sash_width_m']/2+.003
            for xa,xb in zip(sx,sx[1:]):
                for da,db in zip(cuts,cuts[1:]):
                    a=point(xa+gap,da+gap,skin);b=point(xb-gap,da+gap,skin)
                    slope_length=cr_length(cr_sub(point(xa,db-gap),point(xa,da+gap)))
                    midpoint=cr_add(a,cr_mul(cr_unit(cr_sub(point(xa,db-gap),point(xa,da+gap))),slope_length/2))
                    end=cr_add(midpoint,cr_sub(b,a))
                    cr_profile_prism(midpoint,end,cr_rect(slope_length,c['glazing_thickness_m']),glass,
                                     'concourse restored individual glazing panels',reference=slope_u)
            # Dark outer strips are directly visible in restored source photo.
            mid=(glass_edge+half)/2;bandlen=cr_length(cr_sub(point(0,half),point(0,glass_edge)))
            cr_profile_prism(point(x0,mid,skin),point(x1,mid,skin),cr_rect(bandlen,c['deck_thickness_m']),deck,
                'concourse restored opaque outer roof strips',reference=slope_u)
            # Source-visible ribbed deck underside, regularized and unmeasured.
            rib_count=max(1,int(c['opaque_eave_band_horizontal_width_m']/c['opaque_deck_rib_spacing_m']))
            for r in range(rib_count):
                rd=glass_edge+(half-glass_edge)*(r+.5)/rib_count
                roff=skin-c['deck_thickness_m']/2-c['opaque_deck_rib_depth_m']/2
                cr_profile_prism(point(x0,rd,roff),point(x1,rd,roff),
                    cr_rect(c['opaque_deck_rib_width_m'],c['opaque_deck_rib_depth_m']),deck,
                    'concourse restored inferred opaque deck underside ribs',reference=slope_u)
            # Coarse seams only: no claim about hidden deck buildup or fixings.
            for x in stations:
                cr_profile_prism(point(x,glass_edge,skin+c['deck_thickness_m']/2),point(x,half,skin+c['deck_thickness_m']/2),
                    cr_rect(.028,.012),detail,'concourse restored opaque strip seams')
    if not aged and c['include_2026_visible_light_fittings']:
        # Visible small downlights are optional; exact fixture count and service
        # routing are not recovered. Services stay absent.
        for x in stations[1:-1:2]:
            cr_profile_prism((x,cy,z0-.03),(x,cy,z0-.42),cr_rect(.024,.024),steel,'concourse optional inferred light stems')
            poly=[(.115*_cr_math.cos(i*2*_cr_math.pi/16),.115*_cr_math.sin(i*2*_cr_math.pi/16)) for i in range(16)]
            cr_profile_prism((x,cy,z0-.49),(x,cy,z0-.42),poly,detail,'concourse optional inferred downlight housings')
    return stations


_CR_REMOVED=[]
try:
    cr_validate(CONCOURSE_ROOF_CONTROLS)
    if globals().get('CONCOURSE_ROOF_REPLACE_LEGACY',True):
        for _cr_key in list(B):
            if _cr_key[0]==_CR_OLD_GROUP and _cr_key[2] in _CR_OLD_NAMES:
                _CR_REMOVED.append({'group':_cr_key[0],'material':_cr_key[1],'name':_cr_key[2],
                                    'vertices':len(B[_cr_key][0]),'faces':len(B[_cr_key][1]),
                                    'actual_mesh_bounds_m':{'min':[min(p[i] for p in B[_cr_key][0]) for i in range(3)],
                                                            'max':[max(p[i] for p in B[_cr_key][0]) for i in range(3)]}})
                del B[_cr_key]
    if any(k[0]==_CR_GROUP for k in B):raise ValueError('Concourse roof component already emitted; refuse duplicate integration')
    _CR_STATIONS=cr_build(CONCOURSE_ROOF_CONTROLS)
    _cr_points=[p for key,data in B.items() if key[0]==_CR_GROUP for p in data[0]]
    CONCOURSE_ROOF_REPLACEMENT = {
        'replace_only_group':_CR_OLD_GROUP,'replace_only_batch_names':list(_CR_OLD_NAMES),
        'removed_batches':_CR_REMOVED,'emitted_group':_CR_GROUP,
        'actual_mesh_bounds_m':{'min':[min(p[i] for p in _cr_points) for i in range(3)],
                                'max':[max(p[i] for p in _cr_points) for i in range(3)]},
        'unchanged':'Floor, walls, end walls, window grids, public-room interfaces, passenger-ramp projection, southern train-platform deck',
        'integration':'Execute once after old SOUTH CONCOURSE roof emission and before batch finalization; no main-script import',
    }
    CONCOURSE_ROOF_CAMERAS = {
        'concourse_roof_axial':{'location':(-27.5,63.4,4.0),'target':(10.,63.4,10.9),'lens_mm':24},
        'concourse_roof_connection':{'location':(-12.0,59.0,8.0),'target':(-6.805246,63.4,12.0),'lens_mm':48},
        'concourse_roof_exterior':{'location':(-48.,91.,39.),'target':(0.,63.4,10.8),'lens_mm':42},
    }
    CONCOURSE_ROOF_METADATA = {
        'era':str(ERA),'status':'Source-informed interpretive roof detail, not surveyed fabrication or as-built geometry',
        'controls':_cr_deepcopy(CONCOURSE_ROOF_CONTROLS),'stations_x_m':_CR_STATIONS,
        'historical_plan_anchors_m':{'width':58.9788,'depth':23.7744},
        'unmeasured_controls':'Absolute height/registration, station count/spacing, all member sizes, section construction, fastener patterns, sash subdivisions, opaque band extent',
        'source_observations':'Flanged/flat-edged structural members and connections, dense secondary grid; restored central glazing with opaque outer strips; no recreated lower laylight',
        'era_2017':'Open steel and secondary bars; no glazed skin, no assumed surviving pane inventory, no 2010 opaque-strip pattern imported',
        'era_2026':'Restored central panes and photo-visible opaque outer strips; current2026 use extrapolates documented post-renovation restoration character, no exact-day survey',
        'topology_limit':'Retains qualified14-station pitched transverse truss topology. Dated2024 oblique views reveal additional layered longitudinal bracing; its exact topology remains unresolved and is not fabricated by this refinement. Lower historical brass laylight is omitted as documented not recreated.',
        'copyright':'Source images remain private study references. No photograph is loaded, textured, projected or included.',
        'no_bush_train_shed_roof':True,'optional_lights_default':False,
        'evidence_manifest':'manifests/concourse_roof_detail/evidence_and_unknowns.json',
        'replacement':CONCOURSE_ROOF_REPLACEMENT,
    }
finally:
    GROUP=_CR_SAVED_GROUP
