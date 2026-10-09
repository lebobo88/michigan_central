"""Southern platform/undercroft: evidence-gated, era-separated original geometry.

Executed in build_station.py's globals before geometry finalization. This module
never guesses a hall-relative deck Z or treats the 1914/2009 cargo envelope as a
2026 survey. A documented placement_controls.json is required to emit geometry.
The default controls remain blocked until those observations are available.

Copyrighted study photographs are not loaded, projected or packaged. No public
photogrammetry mesh is used. The Bush train-shed roof was demolished in 2000 and
is deliberately absent from both supported eras.
"""
import copy as _ss_copy

_SS_SAVED_GROUP = GROUP
_SS_CONTROL_PATH = Path(globals().get('SOUTH_STRUCTURE_CONTROL_PATH', ROOT / 'manifests/south_structure/placement_controls.json'))
SOUTH_STRUCTURE_CAMERAS = {}
SOUTH_STRUCTURE_SPACES = []
SOUTH_STRUCTURE_EVIDENCE_PROPERTIES = {}


def ss_number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('South structure needs a finite numeric control: '+label)
    return float(value)


def ss_control_value(record, key):
    value = record.get(key)
    if not isinstance(value, dict) or 'value' not in value or not value.get('basis'):
        raise ValueError('South structure missing value/basis: '+key)
    if value.get('confidence') not in ('published', 'registered', 'photo_proportioned'):
        raise ValueError('South structure missing recognized confidence: '+key)
    if not value.get('source_ids'):
        raise ValueError('South structure missing source reference: '+key)
    return value['value']


def ss_validate_controls(record, era):
    """Reject partial placement instead of quietly anchoring to a false datum."""
    if record.get('status') != 'ready':
        return ['Placement status is '+str(record.get('status', 'missing'))] + record.get('blockers', [])
    errors = []
    required = ['footprint_xy_m', 'deck_top_z_m', 'deck_thickness_m', 'support_bottom_z_m']
    if era == '2017':
        required += ['platform_strips_y_m', 'platform_height_m', 'cargo_south_bays',
                     'north_facade_segments', 'steel_edge_beam_depth_m']
    elif era == '2026':
        required += ['observed_concrete_columns', 'visible_perimeter_parapets']
    else:
        return ['Unsupported era '+era]
    values = {}
    for key in required:
        try: values[key] = ss_control_value(record, key)
        except ValueError as exc: errors.append(str(exc))
    if errors:
        return errors
    try:
        poly = values['footprint_xy_m']
        if len(poly) < 3: raise ValueError('Footprint needs at least three points')
        for point in poly:
            if len(point) != 2: raise ValueError('Footprint must have XY point pairs')
            for value in point: ss_number(value, 'footprint_xy_m')
        twice_area = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly, poly[1:]+poly[:1]))
        if twice_area <= .001: raise ValueError('Footprint must have positive area and counter-clockwise points')
        top = ss_number(values['deck_top_z_m'], 'deck_top_z_m')
        thickness = ss_number(values['deck_thickness_m'], 'deck_thickness_m')
        bottom = ss_number(values['support_bottom_z_m'], 'support_bottom_z_m')
        if not 0 < thickness < top-bottom: raise ValueError('Deck thickness or support range is invalid')
        if era == '2017':
            if len(poly) != 4 or len({p[0] for p in poly}) != 2 or len({p[1] for p in poly}) != 2:
                raise ValueError('2017 cargo core requires a registered rectangular envelope; bridge is separate')
            for a,b in values['platform_strips_y_m']:
                if not ss_number(b,'platform end') > ss_number(a,'platform start'):
                    raise ValueError('Platform strips need increasing Y intervals')
            if not values['platform_strips_y_m']: raise ValueError('No photo-informed platform strips supplied')
            if not values['cargo_south_bays']: raise ValueError('No cargo facade bays supplied')
        else:
            if not values['observed_concrete_columns']:
                raise ValueError('Observed concrete support controls required; a floating slab is not enough')
    except (TypeError, ValueError, KeyError) as exc:
        errors.append(str(exc))
    return errors


def ss_material_copy(name, source, color=None, roughness=None, metallic=None):
    """Original project PBR, never a photographic projection or copied asset."""
    m = M[source].copy(); m.name = name; M[name] = m
    p = m.node_tree.nodes.get('Principled BSDF')
    for socket, value in [('Base Color', (*color,1) if color is not None else None),
                          ('Roughness', roughness), ('Metallic', metallic)]:
        if value is not None:
            for link in list(p.inputs[socket].links): m.node_tree.links.remove(link)
            p.inputs[socket].default_value = value
    m['texture_provenance'] = 'Original authored material; source observations establish material class only'
    return name


def ss_slab(poly, z0, z1, material, name):
    """CCW footprint, explicit closed faces; UVs use metric main-pipeline mapping."""
    if not z1 > z0: raise ValueError('Positive slab thickness required')
    count = len(poly)
    vv = [(x,y,z) for z in (z0,z1) for x,y in poly]
    ff = [tuple(range(count-1,-1,-1)), tuple(range(count,2*count))]
    ff += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    addmesh(vv, ff, material, name)


def ss_i_column(x, y, z0, z1, width, depth, material, name):
    """Visible built-up steel exterior column; dimensions photo-proportioned."""
    if z1 <= z0: raise ValueError('Column has no vertical extent')
    flange = min(.07, width*.15)
    web = min(.055, width*.10)
    for yy in [y-depth/2+flange/2, y+depth/2-flange/2]:
        box((x,yy,(z0+z1)/2),(width,flange,z1-z0),material,name+' flanges')
    box((x,y,(z0+z1)/2),(web,depth-2*flange,z1-z0),material,name+' web')


def ss_riveted_edge(x0, x1, y, z0, depth, material, prefix):
    length = x1-x0
    box(((x0+x1)/2,y,z0-depth/2),(length,.055,depth),material,prefix+' steel girder web')
    for z in [z0-.025,z0-depth+.025]:
        box(((x0+x1)/2,y,z),(length,.34,.05),material,prefix+' steel girder flanges')
    # Original interpretation of visible riveted fabrication, not a rivet survey.
    n=max(1,int(length/2.0))
    for k in range(n+1):
        x=x0+.13+(length-.26)*k/n
        box((x,y-.043,z0-depth/2),(.075,.035,depth-.12),material,prefix+' edge stiffeners')
        for z in [z0-.12,z0-depth+.12]:
            beam((x,y-.07,z),(x,y-.10,z),.025,material,prefix+' visible rivet heads',8)


def ss_build_2017(record):
    global GROUP
    v={key:value['value'] for key,value in record.items() if isinstance(value,dict) and 'value' in value}
    poly=v['footprint_xy_m'];x0=min(p[0] for p in poly);x1=max(p[0] for p in poly)
    y0=min(p[1] for p in poly);y1=max(p[1] for p in poly)
    top=v['deck_top_z_m'];t=v['deck_thickness_m'];bottom=v['support_bottom_z_m']
    concrete=ss_material_copy('South 2017 weathered concrete','Weathered concrete')
    steel=ss_material_copy('South 2017 corroded structural steel','Roof steel',(.105,.064,.036),.78,.38)
    shutter=ss_material_copy('South 2017 steel cargo shutters','Roof steel',(.065,.073,.064),.74,.46)
    tile=ss_material_copy('South 2017 exposed terra cotta','Exposed masonry')
    platform=ss_material_copy('South 2017 faded platform paving','Weathered concrete',(.32,.245,.19),.91,0)
    GROUP='30 SOUTH 2017 | uncovered historic platform and cargo exterior'
    ss_slab(poly,top-t,top,concrete,'South 2017 concrete track-support deck | no Bush roof')
    # Exterior side returns preserve the enclosed cargo form, without room divisions.
    for xx in [x0,x1]:
        box((xx,(y0+y1)/2,(bottom+top-t)/2),(.30,y1-y0,top-t-bottom),concrete,
            'South 2017 cargo core side return | local bounded study crop')
    # Raised long strips are regularized from a 2017 aerial and historical dimensions.
    ph=v['platform_height_m']
    for index,(a,b) in enumerate(v['platform_strips_y_m']):
        ss_slab([(x0,a),(x1,a),(x1,b),(x0,b)],top,top+ph,platform,
                'South 2017 platform '+str(index+1)+' | photo-informed regularized strip')
        for yy in [a+.08,b-.08]:
            box(((x0+x1)/2,yy,top+ph+.015),(x1-x0,.16,.03),concrete,'South 2017 platform coping edges')
        # Segmented patches give authored relief without copying the photographs.
        for k in range(int((x1-x0)/4.0)):
            xx=x0+2.0+4.0*k
            if xx+.018 < x1:
                box((xx,(a+b)/2,top+ph+.012),(.035,b-a-.34,.022),concrete,
                    'South 2017 platform slab joints | spacing interpretive')
    # Only positively identified remaining rails can be supplied; no original1914
    # rail roster is silently treated as a complete2017 track inventory.
    for track in v.get('observed_rail_centerlines',[]):
        for y in [track['y']-.7175,track['y']+.7175]:
            box(((track['x0']+track['x1'])/2,y,top+.09),
                (track['x1']-track['x0'],.07,.14),steel,'South 2017 observed remaining running rail')
    # The Newark frontage: closed shutters mark exterior bays. They do not claim
    # private room subdivisions, access, equipment or complete retained interiors.
    for i,bay in enumerate(v['cargo_south_bays']):
        a,b=bay['x0'],bay['x1'];baytop=bay['top_z'];dock=bay['bottom_z']
        box(((a+b)/2,y1-.065,(dock+baytop)/2),(b-a,.07,baytop-dock),shutter,
            'South 2017 Newark cargo bay '+str(i+1)+' closed shutter')
        for j in range(1,int((baytop-dock)/.13)):
            z=dock+j*.13
            box(((a+b)/2,y1-.113,z),(b-a,.035,.024),steel,'South 2017 cargo shutter horizontal ribs')
        if top-t > baytop:
            box(((a+b)/2,y1-.14,(baytop+top-t)/2),(b-a,.28,top-t-baytop),tile,
                'South 2017 exposed terra-cotta header')
        for xx in [a,b]:
            ss_i_column(xx,y1-.07,dock,top-t,.23,.36,steel,'South 2017 cargo frontage steel piers')
        box(((a+b)/2,y1+.47,dock-.13),(b-a,.94,.26),concrete,'South 2017 cargo loading dock edge')
    ss_riveted_edge(x0,x1,y1,top-t+.10,v['steel_edge_beam_depth_m'],steel,'South 2017 south exposed')
    # North elevation is represented only where source-registered segments exist.
    for segment in v['north_facade_segments']:
        a,b,z0,z1=segment['x0'],segment['x1'],segment['z0'],segment['z1']
        box(((a+b)/2,y0,(z0+z1)/2),(b-a,.32,z1-z0),'Concourse buff brick',
            'South 2017 observed north brick facade segment')
        box(((a+b)/2,y0,top+.15),(b-a,.48,.22),'Exterior Indiana limestone',
            'South 2017 north parapet limestone coping')
    for awning in v.get('north_awning_intervals',[]):
        a,b=awning['x0'],awning['x1'];z=awning['z'];projection=awning['projection']
        ss_slab([(a,y0-projection),(b,y0-projection),(b,y0),(a,y0)],z-.08,z,steel,
                'South 2017 observed north hanging cargo awning')
    # Partial broken terra-cotta parapet is visible in the2017south view. Heights
    # and break pattern below are authored controls, not copied damage geometry.
    for remnant in v.get('south_parapet_remnants',[]):
        a,b,h=remnant['x0'],remnant['x1'],remnant['height']
        n=max(1,int((b-a)/.58));w=(b-a)/n
        for k in range(n):
            x=a+(k+.5)*w
            layers=max(1,int(h/.22)-(1 if k%7 in [0,1] else 0))
            for j in range(layers):
                box((x,y1-.18,top+.11+j*.22),(w-.023,.30,.202),tile,
                    'South 2017 broken terra-cotta parapet courses | original damage pattern')
    # Vegetation locations are an original sparse distribution following the
    # weed bands in the aerial. Their individual placement is not surveyed.
    if v.get('interpretive_weed_bands',False):
        rr=random.Random(172017)
        for a,b in v['platform_strips_y_m']:
            for yy in [a-.24,b+.24]:
                for k in range(100):
                    xx=rr.uniform(x0+.5,x1-.5)
                    if rr.random()<.36:continue
                    zz=top+.01;h=rr.uniform(.16,.62);r=rr.uniform(.08,.23)
                    for j in range(3):
                        angle=rr.random()*pi;dx=r*cos(angle);dy=r*sin(angle)
                        addmesh([(xx-dx,yy-dy,zz),(xx+dx,yy+dy,zz),
                                 (xx+.35*dx,yy+.35*dy,zz+h),(xx-.35*dx,yy-.35*dy,zz+h*.91)],
                                [(0,1,2,3)],'Foliage','South 2017 weed bands | placement interpretive')
    SOUTH_STRUCTURE_CAMERAS['south_2017_overview']=((x1+45,y1+75,top+45),((x0+x1)/2,(y0+y1)/2,top),35)
    SOUTH_STRUCTURE_CAMERAS['south_2017_cargo']=((x1*.15,y1+32,bottom+2.2),((x0+x1)/2,y1,bottom+2.0),32)


def ss_build_2026(record):
    global GROUP
    v={key:value['value'] for key,value in record.items() if isinstance(value,dict) and 'value' in value}
    poly=v['footprint_xy_m'];top=v['deck_top_z_m'];t=v['deck_thickness_m']
    concrete=ss_material_copy('South 2026 replacement concrete','Weathered concrete',(.46,.455,.43),.78,0)
    GROUP='31 SOUTH 2026 | observed replacement concrete deck exterior'
    ss_slab(poly,top-t,top,concrete,'South 2026 replacement concrete deck | documented perimeter only')
    for column in v['observed_concrete_columns']:
        x,y,z0,z1=column['x'],column['y'],column['z0'],column['z1']
        box((x,y,(z0+z1)/2),(column['width'],column['depth'],z1-z0),concrete,
            'South 2026 photographed concrete support | no private parking layout')
    for rail in v['visible_perimeter_parapets']:
        a,b=Vector(rail['a']),Vector(rail['b']);width=rail['width'];height=rail['height']
        direction=(b-a).normalized();normal=Vector((-direction.y,direction.x))*width/2
        ss_slab([tuple(a-normal),tuple(b-normal),tuple(b+normal),tuple(a+normal)],
                top,top+height,concrete,'South 2026 observed concrete parapet')
    # Neither proposed greenery nor parking stalls/interior rooms are inferred.
    cx=sum(p[0] for p in poly)/len(poly);cy=sum(p[1] for p in poly)/len(poly)
    x1=max(p[0] for p in poly);y1=max(p[1] for p in poly)
    SOUTH_STRUCTURE_CAMERAS['south_2026_overview']=((x1+45,y1+75,top+45),(cx,cy,top),35)


try:
    _ss_all=json.loads(_SS_CONTROL_PATH.read_text()) if _SS_CONTROL_PATH.exists() else {}
    _ss_record=_ss_copy.deepcopy(_ss_all.get('eras',{}).get(ERA,{}))
    _ss_errors=ss_validate_controls(_ss_record,ERA)
    SOUTH_STRUCTURE_EVIDENCE_PROPERTIES={
        'era':ERA,'controls':str(_SS_CONTROL_PATH.relative_to(ROOT)),
        'status':'blocked' if _ss_errors else 'enabled',
        'coordinate_space':_ss_record.get('coordinate_space','unresolved global placement'),
        'extent_limit':_ss_record.get('extent_limit','Perimeter unresolved'),
        'blockers':_ss_errors,
        'no_bush_roof':True,
        'source_geometry':'Original parametric reconstruction; no extracted mesh or photographic projection',
        'private_interiors':'Omitted; exterior observations do not establish cargo/parking room plans',
        'reference_images':'Study only; excluded from Blender and distribution',
    }
    if not _ss_errors:
        (ss_build_2017 if ERA=='2017' else ss_build_2026)(_ss_record)
        SOUTH_STRUCTURE_SPACES.append(SOUTH_STRUCTURE_EVIDENCE_PROPERTIES)
    scene['south_structure_evidence']=json.dumps(SOUTH_STRUCTURE_EVIDENCE_PROPERTIES)
finally:
    GROUP=_SS_SAVED_GROUP
