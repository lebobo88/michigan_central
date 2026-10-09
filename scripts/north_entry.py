"""Isolated north-entrance detail candidate NED2017-03.
Replace north_entry.py only after acceptance. Restored branch is a verbatim,
indented copy of the baseline component; no 2026 behavior change is intended.
All 2017 detail is original geometry and procedural material, not site scans.
"""
if not AGED:
    """Floor-reaching north center entrance, separate from upper arched light.
    Photo controls: center doorbank approximately upper-window width;1+3+1 modules.
    No door operability or precise hinge/sill dimensions are claimed from imagery.
    """
    _NE_GROUP=GROUP;GROUP='01 EXTERIOR | measured historic envelope'
    NORTH_ENTRY_CONTROLS=dict(doorbank_trial_width_m=6.4008,door_panel_trial_top_m=2.88,transom_trial_top_m=3.88,lintel_trial_top_m=4.32,era=ERA,evidence='May2017 Historic Detroit entry photo and July2026 CC0 front crop',dimension_status='Doorbank sizes are photo-proportioned, not printed or surveyed dimensions;21x40ft wording does not establish a measured composite center door height')
    _ne_w=NORTH_ENTRY_CONTROLS['doorbank_trial_width_m'];_ne_jamb=.12;_ne_narrow=(_ne_w-4*_ne_jamb)/6
    _ne_zones=[(-(_ne_w/2-_ne_jamb-_ne_narrow/2),_ne_narrow),(0,4*_ne_narrow),(_ne_w/2-_ne_jamb-_ne_narrow/2,_ne_narrow)]
    # Ratios describe clear shutters, after allowing for the four jamb/piers.
    box((0,-.04,4.10),(_ne_w,1.00,.44),stone,'north center entrance structural lintel')
    _ne_structural_x=[-_ne_w/2+_ne_jamb/2,-2*_ne_narrow-_ne_jamb/2,2*_ne_narrow+_ne_jamb/2,_ne_w/2-_ne_jamb/2]
    for _ne_x in _ne_structural_x:box((_ne_x,-.20,1.45),(_ne_jamb,.20,2.90),'Roof steel' if AGED else 'Dark bronze','north entrance principal jamb frames')
    if AGED:
     for _ne_c,_ne_width in _ne_zones:
      box((_ne_c,-.24,1.44),(_ne_width,.11,2.88),'Window cast iron','2017 north entrance closed roller shutter door leaves')
      for _ne_j in range(34):box((_ne_c,-.307,(_ne_j+.5)*2.88/34),(_ne_width,.04,.026),'Roof steel','2017 north entrance shutter slat profiles')
     box((0,-.20,3.38),(_ne_w,.09,1.00),'Glass tower dark','2017 north entrance transom glazing')
    else:
     _ne_cells=[_ne_zones[0]]+[(q*(4*_ne_narrow)/3,(4*_ne_narrow)/3) for q in [-1,0,1]]+[_ne_zones[2]]
     for _ne_c,_ne_width in _ne_cells:
      box((_ne_c,-.20,1.445),(_ne_width-.065,.02,2.73),'Glass clear','2026 north entrance glazed door panel modules')
      box((_ne_c,-.245,.23),(_ne_width-.06,.10,.34),'Dark bronze','2026 north entrance panel lower rails')
      for _ne_z in [.06,2.88]:box((_ne_c,-.23,_ne_z),(_ne_width,.17,.085),'Dark bronze','2026 north entrance threshold and panel head frames')
     for _ne_x in [-2*_ne_narrow/3,2*_ne_narrow/3]:box((_ne_x,-.23,1.45),(.075,.17,2.90),'Dark bronze','2026 north entrance central module mullions')
     box((0,-.20,3.38),(_ne_w,.02,1.00),'Glass clear','2026 north entrance transom glazing')
    for _ne_x in _ne_structural_x+[-2*_ne_narrow/3,2*_ne_narrow/3]:box((_ne_x,-.24,3.38),(.075,.17,1.00),'Window cast iron','north entrance transom vertical frames')
    for _ne_z in [2.88,3.88]:box((0,-.24,_ne_z),(_ne_w,.18,.095),'Window cast iron','north entrance transom horizontal frames')
    NORTH_ENTRY_CONTROLS['clear_shutter_ratio']=[1,4,1]
    NORTH_ENTRY_CONTROLS['current_visible_modules']='one narrow, three wider center modules, one narrow; operability unverified'
    scene['north_entry_controls']=json.dumps(NORTH_ENTRY_CONTROLS)
    NORTH_ENTRY_CAMERAS={'north_entry_detail':((11,-21,5.0),(0,0,4.0),45)}
    GROUP=_NE_GROUP
else:
    _NED_GROUP=GROUP
    GROUP='01 EXTERIOR | measured historic envelope'
    _ned_w=6.4008
    _ned_jamb=_ned_w*(1-635/775)/4
    _ned_narrow=(_ned_w-4*_ned_jamb)/6
    _ned_zones=[(-(_ned_w/2-_ned_jamb-_ned_narrow/2),_ned_narrow),(0,4*_ned_narrow),(_ned_w/2-_ned_jamb-_ned_narrow/2,_ned_narrow)]
    _ned_jamb_x=[-_ned_w/2+_ned_jamb/2,-2*_ned_narrow-_ned_jamb/2,2*_ned_narrow+_ned_jamb/2,_ned_w/2-_ned_jamb/2]
    NORTH_ENTRY_CONTROLS=dict(doorbank_trial_width_m=_ned_w,door_panel_trial_top_m=2.88,transom_trial_top_m=3.88,lintel_trial_top_m=4.32,era=ERA,clear_shutter_ratio=[1,4,1],clear_shutter_widths_m=[w for c,w in _ned_zones],jamb_trial_width_m=_ned_jamb,clear_width_fraction=635/775,material_class='Weathered brown coated frame; timber versus metal substrate unverified',source='May 2017 Bob Laperriere photograph, Historic Detroit image p12',evidence='Three unequal closed shutters; one broad shallow elliptical transom and two near-semicircular side heads; weathered brown paneled frames; 2001 plaque; shallow chipped stone lintel',dimension_status='All doorbank dimensions are photo-proportioned trial controls, not printed, rectified or surveyed measurements',candidate_status='Isolated candidate; not integrated or accepted',candidate_revision='NED2017-03',transom_topology='Three individually shaped capped glass lights, no rectangular backing glass',real_void='No masonry or glazing plane across the three shutter clear zones; shutters are the 2017 closure, not a hidden wall',ornament_status='Simplified paneled face strips and arched beads are photo-informed, not measured carving profiles',lintel_loss='Original shallow edge wear, <=24 mm; not a measured loss map')
    _ned_frame='2017 north entry weathered brown coating | substrate unverified'
    _ned_shutter='2017 north entry galvanized shutter | approximate finish'
    _ned_glass='2017 north entry dark transom glass'
    _ned_plaque='2017 north entry pale address plaque'
    _ned_letter='2017 north entry address numerals'
    for _nm,_col,_rough,_metal in [(_ned_frame,(.040,.0145,.0048),.76,0),(_ned_shutter,(.23,.25,.26),.62,.18),(_ned_glass,(.025,.032,.033),.48,0),(_ned_plaque,(.61,.60,.52),.79,0),(_ned_letter,(.018,.02,.018),.73,0)]:
        _mm=mat(_nm,_col,_rough,_metal);_mm['texture_repeat_m']=1.0
        _mm['material_limit']='Photograph-informed appearance, no measured physical-property or substrate claim'
    if not globals().get('NED_GEOMETRY_ONLY',False):
        _mm=M[_ned_frame];_nt=_mm.node_tree;_p=_nt.nodes.get('Principled BSDF')
        for _channel in ['basecolor','roughness','normal','height']:
            _tex=_nt.nodes.new('ShaderNodeTexImage');_tex.name=_channel
            _tex.image=bpy.data.images.load(str(ROOT/'assets/candidates/north_entry_detail_2017'/(_channel+'.png')),check_existing=True)
            _tex.image.colorspace_settings.name='sRGB' if _channel=='basecolor' else 'Non-Color'
            _tex.label='Original procedural coating; no reference image pixels'
            if _channel=='basecolor':_nt.links.new(_tex.outputs['Color'],_p.inputs['Base Color'])
            elif _channel=='roughness':_nt.links.new(_tex.outputs['Color'],_p.inputs['Roughness'])
            elif _channel=='normal':
                _normal=_nt.nodes.new('ShaderNodeNormalMap');_normal.inputs['Strength'].default_value=.38
                _nt.links.new(_tex.outputs['Color'],_normal.inputs['Color']);_nt.links.new(_normal.outputs['Normal'],_p.inputs['Normal'])
        _mm['texture_provenance']='Original mathematical brown coating, seed 20012017; no source pixels; substrate unresolved'
        _mm['physical_limit']='1 m tiling trial; micro-normal only; no displacement or registered loss'

    def _ned_area(poly):
        return .5*sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))

    def _ned_triangles(poly):
        """Deterministic ear clipping: explicit clean caps, no n-gon export dependency."""
        idx=list(range(len(poly)));out=[]
        def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        while len(idx)>3:
            found=False
            for j,b in enumerate(idx):
                a=idx[j-1];c=idx[(j+1)%len(idx)]
                if cross(poly[a],poly[b],poly[c])<=1e-12:continue
                if any(cross(poly[a],poly[b],poly[k])>=-1e-12 and cross(poly[b],poly[c],poly[k])>=-1e-12 and cross(poly[c],poly[a],poly[k])>=-1e-12 for k in idx if k not in (a,b,c)):continue
                out.append((a,b,c));idx.pop(j);found=True;break
            if not found:raise ValueError('Non-simple or degenerate north-entry cap')
        out.append(tuple(idx));return out

    def _ned_solid(poly,yfront,yback,material,name,swap_xy=False):
        """Extrude CCW XZ outline. Every UV is an explicit metric coordinate."""
        poly=list(poly)
        if _ned_area(poly)<0:poly.reverse()
        n=len(poly);v=[(x,y,z) for y in (yfront,yback) for x,z in poly]
        caps=_ned_triangles(poly);f=caps+[tuple(i+n for i in reversed(t)) for t in caps]
        uv=[[(v[i][0],v[i][2]) for i in face] for face in f]
        length=0
        for i in range(n):
            j=(i+1)%n;edge=math.hypot(poly[j][0]-poly[i][0],poly[j][1]-poly[i][1])
            f.append((i,i+n,j+n,j));uv.append([(length,yfront),(length,yback),(length+edge,yback),(length+edge,yfront)]);length+=edge
        if swap_xy:
            v=[(y,x,z) for x,y,z in v];f=[tuple(reversed(face)) for face in f];uv=[list(reversed(face)) for face in uv]
        addmesh(v,f,material,name,face_uv=uv)

    def _ned_box(c,s,material,name):
        x,y,z=c;dx,dy,dz=[a/2 for a in s]
        _ned_solid([(x-dx,z-dz),(x+dx,z-dz),(x+dx,z+dz),(x-dx,z+dz)],y-dy,y+dy,material,name)

    def _ned_strip(inner,outer,yfront,yback,material,name,closed=False):
        """One capped band mesh, without duplicate radial faces between segments."""
        n=len(inner);v=[(x,y,z) for y in (yfront,yback) for line in (inner,outer) for x,z in line]
        f=[];uv=[]
        count=n if closed else n-1;arclen=[0]
        for i in range(1,n):arclen.append(arclen[-1]+math.dist(inner[i-1],inner[i]))
        for i in range(count):
            j=(i+1)%n;a=arclen[i];b=a+math.dist(inner[i],inner[j])
            # Lines travel right to left over each head. Outer lies above inner.
            front=(i,n+i,n+j,j);back=tuple(k+2*n for k in reversed(front))
            f.extend([front,back]);uv.extend([[(v[k][0],v[k][2]) for k in face] for face in (front,back)])
            for face in [(i,j,2*n+j,2*n+i),(n+i,3*n+i,3*n+j,n+j)]:
                f.append(face);uv.append([(a,yfront),(b,yfront),(b,yback),(a,yback)] if face[0]<n else [(a,yfront),(a,yback),(b,yback),(b,yfront)])
        if not closed:
            for face in [(0,2*n,3*n,n),(n-1,2*n-1,4*n-1,3*n-1)]:
                f.append(face);uv.append([(v[k][0],v[k][1]) for k in face])
        addmesh(v,f,material,name,face_uv=uv)

    # Four substantial structural members, a photo-ratio trial rather than measured joinery.
    # Raised panel trims stand 1 mm clear of the core; no coplanar overlay faces.
    for _x in _ned_jamb_x:
        _ned_box((_x,-.292,1.44),(_ned_jamb,.286,2.88),_ned_frame,'2017 north entry substantial brown jamb cores')
        for _z,_h in [(.175,.344),(1.435,2.157),(2.727,.292)]:
            _ned_box((_x,-.447,_z),(_ned_jamb-.035,.020,_h),_ned_frame,'2017 north entry simplified raised panel faces')
        for _side in [-1,1]:
            _ned_box((_x+_side*(_ned_jamb/2-.039),-.464,1.441),(.020,.010,2.806),_ned_frame,'2017 north entry narrow panel edge beads')
    # One closed shared-vertex corrugated prism per shutter. Side caps are
    # short ruled quads, not a long skinny ear-clipped fan: stable float32 tangents.
    for _ci,(_cx,_width) in enumerate(_ned_zones):
        _h=2.878;_slats=34;_step=_h/_slats;_profile=[(-.222,0.)]
        for _j in range(_slats):
            _z=_j*_step
            _profile.extend([(-.222,_z+_step*.49),(-.231,_z+_step*.57),(-.231,_z+_step*.67),(-.222,_z+_step*.75),(-.222,_z+_step)])
        _v=[]
        for _yf,_z in _profile:
            _v.extend([(_cx-_width/2,_yf,_z),(_cx+_width/2,_yf,_z),(_cx+_width/2,-.115,_z),(_cx-_width/2,-.115,_z)])
        _f=[];_uv=[]
        for _j in range(len(_profile)-1):
            _k=4*_j
            for _side,_face in enumerate([(_k,_k+1,_k+5,_k+4),(_k+1,_k+2,_k+6,_k+5),(_k+2,_k+3,_k+7,_k+6),(_k+3,_k,_k+4,_k+7)]):
                _f.append(_face);_axes=(0,2) if _side in (0,2) else (1,2)
                _uv.append([(_v[i][_axes[0]],_v[i][_axes[1]]) for i in _face])
        _last=4*(len(_profile)-1)
        for _face in [(3,2,1,0),(_last,_last+1,_last+2,_last+3)]:
            _f.append(_face);_uv.append([(_v[i][0],_v[i][1]) for i in _face])
        addmesh(_v,_f,_ned_shutter,'2017 north entry closed corrugated shutter '+str(_ci+1),face_uv=_uv)
    _ned_box((0,-.328,2.936),(_ned_w,.250,.108),_ned_frame,'2017 north entry continuous shutter head rail')
    _ned_box((0,-.292,3.833),(_ned_w,.222,.094),_ned_frame,'2017 north entry top head board')
    for _x in _ned_jamb_x:
        _ned_box((_x,-.292,3.387),(_ned_jamb,.222,.780),_ned_frame,'2017 north entry transom separating jambs')
    # Every glass cap follows its own actual arch outline, recessed behind the band.
    _ned_lights=[]
    for _ci,(_cx,_width) in enumerate(_ned_zones):
        _a=_width/2-.045;_spring=3.025 if _ci==1 else 3.247;_rise=.645 if _ci==1 else _a
        _bottom=3.020;_N=72 if _ci==1 else 40
        _arc=[(_cx+_a*math.cos(math.pi*i/_N),_spring+_rise*math.sin(math.pi*i/_N)) for i in range(_N+1)]
        _shape=[(_cx-_a,_bottom),(_cx+_a,_bottom)]+_arc
        _ned_solid(_shape,-.267,-.257,_ned_glass,'2017 north entry shaped '+('central elliptical' if _ci==1 else 'side arched')+' transom light '+str(_ci+1))
        _outer=[(_cx+(_a+.039)*math.cos(math.pi*i/_N),_spring+(_rise+.039)*math.sin(math.pi*i/_N)) for i in range(_N+1)]
        _ned_strip(_arc,_outer,-.445,-.407,_ned_frame,'2017 north entry arched transom raised bands '+str(_ci+1))
        # Shared-vertex vertical quad strips avoid ill-conditioned skinny
        # spandrel cap fans while retaining the identical curved lower boundary.
        _line=[(_cx-_width/2,_spring)]
        _line += [(_cx+(_a+.041)*math.cos(math.pi*i/_N),_spring+(_rise+.041)*math.sin(math.pi*i/_N)) for i in range(_N,-1,-1)]
        _line += [(_cx+_width/2,_spring)]
        _sv=[]
        for _x,_z in _line:_sv.extend([(_x,-.403,_z),(_x,-.403,3.778),(_x,-.181,3.778),(_x,-.181,_z)])
        _sf=[];_su=[];_arc_length=0.
        for _j in range(len(_line)-1):
            _k=4*_j;_edge=math.dist(_line[_j],_line[_j+1])
            for _side,_face in enumerate([(_k,_k+4,_k+5,_k+1),(_k+1,_k+5,_k+6,_k+2),(_k+2,_k+6,_k+7,_k+3),(_k+3,_k+7,_k+4,_k)]):
                _sf.append(_face)
                if _side==3:_su.append([(_arc_length,-.181),(_arc_length+_edge,-.181),(_arc_length+_edge,-.403),(_arc_length,-.403)])
                else:
                    _axes=(0,2) if _side in (0,2) else (0,1)
                    _su.append([(_sv[i][_axes[0]],_sv[i][_axes[1]]) for i in _face])
            _arc_length+=_edge
        _last=4*(len(_line)-1)
        for _face in [(0,1,2,3),(_last+3,_last+2,_last+1,_last)]:
            _sf.append(_face);_su.append([(_sv[i][1],_sv[i][2]) for i in _face])
        addmesh(_sv,_sf,_ned_frame,'2017 north entry solid curved spandrel '+str(_ci+1),face_uv=_su)
        if _spring>_bottom+.02:
            for _sgn in [-1,1]:
                _ned_box((_cx+_sgn*(_a+.020),-.426,(_spring+_bottom)/2),(.036,.038,_spring-_bottom-.002),_ned_frame,'2017 north entry side-light short spring stiles')
        _ned_box((_cx,-.418,3.007),(_width-.006,.043,.021),_ned_frame,'2017 north entry individual transom sill bead')
        _panes=11 if _ci==1 else 3
        for _j in range(1,_panes):
            _dx=-_a+2*_a*_j/_panes;_bar=.025
            _top=_spring+_rise*math.sqrt(max(0,1-((abs(_dx)+_bar/2)/_a)**2))-.011
            _ned_box((_cx+_dx,-.409,(_bottom+_top)/2),(_bar,.028,_top-_bottom),_ned_frame,'2017 north entry slender transom vertical bars')
        _ned_lights.append(dict(center_x_m=_cx,clear_width_m=2*_a,spring_z_m=_spring,rise_m=_rise,crown_z_m=_spring+_rise,glass_bottom_z_m=_bottom,panes=_panes))
    NORTH_ENTRY_CONTROLS['transom_lights']=_ned_lights
    NORTH_ENTRY_CONTROLS['central_bar_count_evidence']=dict(internal_bars=10,panes=11,photo_native_width_px=933,approximate_bar_x_px=[309,341,371,410,448,487,524,563,594,626],limit='Native-pixel visual count; model uses regularized spacing rather than tracing unrectified pixel positions')
    # The address plaque is original geometry; simple authored glyphs, not a photo crop.
    _ned_box((0,-.479,3.531),(.362,.025,.201),_ned_plaque,'2017 north entry address plaque 2001')
    def _ned_num_solid(points,x):
        _ned_solid([(x+a,3.457+b) for a,b in points],-.500,-.494,_ned_letter,'2017 north entry original address numeral strokes')
    _glyphw=.063;_glyphh=.145;_stroke=.011
    _ned_num_solid([(0,0),(.063,0),(.063,.012),(.017,.012),(.061,.087),(.063,.113),(.050,.140),(.015,.145),(0,.128),(0,.112),(.010,.112),(.016,.133),(.043,.133),(.052,.111),(.049,.094),(0,.011)],-.147)
    for _x in [-.069,.010]:
        _outer=[(_x+.0315+.0315*math.cos(2*math.pi*i/40),3.5295+.0725*math.sin(2*math.pi*i/40)) for i in range(40)]
        _inner=[(_x+.0315+.021*math.cos(2*math.pi*i/40),3.5295+.061*math.sin(2*math.pi*i/40)) for i in range(40)]
        _ned_strip(_inner,_outer,-.500,-.494,_ned_letter,'2017 north entry original oval zero numeral',closed=True)
    _ned_num_solid([(.022,0),(.054,0),(.054,.010),(.043,.010),(.043,.145),(.033,.145),(.011,.127),(.017,.120),(.031,.131),(.031,.010),(.022,.010)],.089)
    # Shallow, original leading-edge wear. The structural envelope and top are unchanged.
    _N=48;_v=[];_bottom=3.88;_top=4.32
    for _i in range(_N+1):
        _x=-_ned_w/2+_ned_w*_i/_N
        _chip=(.007+.017*max(0,math.sin(_i*2.371))**4) if _i not in (0,_N) else 0
        _front=-.54+(.006+.014*max(0,math.sin(_i*1.731+.3))**5 if _i not in (0,_N) else 0)
        _v.extend([(_x,_front,_bottom+_chip),(_x,-.54,_top),(_x,.46,_top),(_x,.46,_bottom)])
    _f=[]
    for _i in range(_N):
        _k=4*_i
        _f.extend([(_k,_k+4,_k+5,_k+1),(_k+1,_k+5,_k+6,_k+2),(_k+2,_k+6,_k+7,_k+3),(_k+3,_k+7,_k+4,_k)])
    _f.extend([(0,1,2,3),(4*_N+3,4*_N+2,4*_N+1,4*_N)])
    _uv=[]
    for _fi,_face in enumerate(_f):
        _axes=(0,2) if _fi<4*_N and _fi%4 in (0,2) else ((0,1) if _fi<4*_N else (1,2))
        _uv.append([(_v[k][_axes[0]],_v[k][_axes[1]]) for k in _face])
    addmesh(_v,_f,stone,'2017 north center entrance conservatively weathered stone lintel',face_uv=_uv)
    NORTH_ENTRY_CONTROLS['current_visible_modules']='2017 three closed shutters; no door-operability claim'
    scene['north_entry_controls']=json.dumps(NORTH_ENTRY_CONTROLS)
    NORTH_ENTRY_CAMERAS={'north_entry_detail':((11,-21,5.0),(0,0,4.0),45),'north_entry_2017_front_study':((0,-16,2.18),(0,0,2.18),52),'north_entry_2017_oblique_study':((7,-13,4.5),(0,0,2.2),52)}
    GROUP=_NED_GROUP
