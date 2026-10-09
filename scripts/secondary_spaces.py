"""Evidence-led secondary public spaces; executed in build_station.py globals.

Only new meshes/materials are added. Copyrighted study photographs are NEVER
loaded as Blender textures. Original procedural detail interprets visible fabric.
Measurements marked visual/plan-traced are not a contemporary as-built survey.
See manifests/secondary_spaces/evidence.json and QA.md for scope and omissions.
"""
_sec_old_group = GROUP
_sec_rng = random.Random(84219 + (1 if AGED else 0))
SEC_SPACES = []
SEC_CAMERAS = {}

# New materials remain procedural and independent of the project's texture files.
def sec_material(name, color, roughness=.55, metal=0, variation=.08, scale=7):
    m = mat(name, color, roughness, metal)
    nt = m.node_tree; p = nt.nodes.get('Principled BSDF')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = scale
    noise.inputs['Detail'].default_value = 3
    nt.links.new(tc.outputs['Generated'], noise.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    for element, factor in zip(ramp.color_ramp.elements, [1-variation, 1+variation]):
        element.color = (*[min(.99, max(.003,c*factor)) for c in color], 1)
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.15
    bump.inputs['Distance'].default_value=.018 if AGED else .002
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],p.inputs['Normal'])
    m['provenance']='Original procedural shader; no photographic texture'
    return name

SEC_BRONZE=sec_material('Secondary brushed bronze',(.24,.14,.055),.32,.78,.14,32)
SEC_IRON=sec_material('Secondary iron rust' if AGED else 'Secondary conserved iron',(.14,.071,.035) if AGED else (.037,.046,.043),.73 if AGED else .36,.40 if AGED else .76,.36 if AGED else .08,40)
SEC_PLY=sec_material('Secondary 2017 protective plywood',(.26,.14,.072),.91,0,.38,9)
SEC_TILE=sec_material('Secondary glazed white ceramic',(.72,.75,.71),.19,0,.035,15)
SEC_GROUT=sec_material('Secondary pale mineral grout',(.42,.45,.41),.9,0,.08,10)
SEC_HEX=sec_material('Secondary ivory hex tile',(.65,.66,.59),.51,0,.075,36)
SEC_SUBSTRATE=sec_material('Secondary exposed ribbed substrate',(.26,.23,.18),.95,0,.30,24)
SEC_DARK=sec_material('Secondary conservation grille',(.018,.020,.019),.45,.55,.08,20)
SEC_LIGHT='Warm lamp glass'
# A local finish variant prevents the lobby marble from reading as rough paving.
SEC_FLOOR='Secondary polished lobby marble'
_sf=M['Rose Tennessee marble'].copy();_sf.name=SEC_FLOOR;M[SEC_FLOOR]=_sf
if not AGED:
    _sp=_sf.node_tree.nodes.get('Principled BSDF')
    for _link in list(_sp.inputs['Roughness'].links):_sf.node_tree.links.remove(_link)
    _sp.inputs['Roughness'].default_value=.20
    for _node in _sf.node_tree.nodes:
        if _node.type=='NORMAL_MAP':_node.inputs['Strength'].default_value=.08
SEC_GRAFF=[]
for i,c in enumerate([(.016,.14,.24),(.51,.35,.035),(.35,.06,.022),(.09,.11,.12),(.14,.22,.22)]):
    SEC_GRAFF.append(sec_material('Secondary original abstract marking '+str(i+1),c,.95,0,.09,10))


def sec_u_box(c, width, depth, height, material, name, axis='y'):
    """Vertical panel; axis is its constant coordinate / outward normal."""
    box(c,(depth,width,height) if axis=='x' else (width,depth,height),material,name)


def sec_point(u, plane, z, axis='y'):
    return (plane,u,z) if axis=='x' else (u,plane,z)


def sec_frame(u, plane, bottom, width, height, axis='y', material='Dark bronze', name='Secondary opening', glazing=False, transom=.0, leaves=2):
    for d in [-width/2,width/2]:
        sec_u_box(sec_point(u+d,plane,bottom+height/2,axis),.12,.19,height,material,name+' jambs',axis)
    for z in [bottom,bottom+height]:
        sec_u_box(sec_point(u,plane,z,axis),width+.15,.19,.13,material,name+' sill and head',axis)
    if transom:
        sec_u_box(sec_point(u,plane,bottom+height-transom,axis),width,.20,.13,material,name+' transom',axis)
    if glazing:
        sec_u_box(sec_point(u,plane+.015,bottom+height/2,axis),width-.10,.014,height-.10,'Glass clear',name+' glazing',axis)
    for j in range(1,leaves):
        sec_u_box(sec_point(u-width/2+width*j/leaves,plane,bottom+(height-transom)/2,axis),.065,.19,height-transom,material,name+' vertical divisions',axis)


def sec_lamp(x,y,ceiling,drop=.38,cage=False):
    beam((x,y,ceiling-.03),(x,y,ceiling-drop),.021,'Dark bronze','Secondary pendant stems')
    lathe((x,y,ceiling-.07),[(.15,0),(.15,.055),(.105,.095)],SEC_BRONZE,'Secondary pendant ceiling roses',16)
    z=ceiling-drop-.42
    lathe((x,y,z),[(.0,0),(.12,.05),(.205,.17),(.225,.32),(.18,.48),(.08,.57),(.0,.59)],SEC_LIGHT,'Secondary pendant opal globes',24)
    lathe((x,y,z+.55),[(.12,0),(.16,.07),(.1,.13)],SEC_BRONZE,'Secondary pendant collars',20)
    if cage:
        for a in [0,pi/2,pi,3*pi/2]:
            points=[]
            for k in range(17):
                t=pi*k/16; r=.23*sin(t)
                points.append((x+r*cos(a),y+r*sin(a),z+.59*k/16))
            for p,q in zip(points,points[1:]):beam(p,q,.012,SEC_BRONZE,'Secondary lantern cage',6)
        ring((x,y,z+.31),.23,.014,SEC_BRONZE,'Secondary lantern equator',24)


def sec_wall_bands(plane, u0,u1,z0,z1,axis='y',material='Warm Mankato column stone',name='Secondary stone joints'):
    # Thin recessed original joint lines, not a photographic surface projection.
    for j in range(1,int((z1-z0)/.58)):
        zz=z0+j*.58
        sec_u_box(sec_point((u0+u1)/2,plane,zz,axis),u1-u0,.008,.007,'Distress umber',name,axis)
        for k in range(int((u1-u0)/1.2)):
            uu=u0+(k+.5*(j%2))*1.2
            if u0+.03 < uu < u1-.03:
                sec_u_box(sec_point(uu,plane,zz+.29,axis),.007,.008,.575,'Distress umber',name,axis)


def sec_slope_floor(x0,x1,y0,y1,z0,z1,material,name):
    # Closed thin inclined slab, z changes with Y.
    t=.16
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z1),(x0,y1,z1),
       (x0,y0,z0-t),(x1,y0,z0-t),(x1,y1,z1-t),(x0,y1,z1-t)]
    addmesh(v,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],material,name)


def sec_original_marks(plane,u0,u1,z0,z1,axis='y',seed=1,count=8):
    """Original non-lettering gestures: never copies the photographed artwork."""
    rr=random.Random(seed)
    for i in range(count):
        uc=rr.uniform(u0+.7,u1-.7); zc=rr.uniform(z0+.3,z1-.3)
        wr=rr.uniform(.40,1.10); hr=rr.uniform(.4,.94); material=SEC_GRAFF[i%len(SEC_GRAFF)]
        v=[]; f=[];n=30;phase=rr.random()*pi
        for j in range(n+1):
            a=2*pi*j/n
            u=uc+wr*cos(a)+.10*sin(3*a+phase); z=zc+hr*sin(a)+.08*cos(5*a+phase)
            w=.055+.025*sin(7*a)
            for offset in [-w,w]:v.append(sec_point(u+offset*cos(a),plane,z+offset*sin(a),axis))
        for j in range(n): k=2*j;f.append((k,k+2,k+3,k+1))
        addmesh(v,f,material,'Original abstract markings | arrangement interpretive, no copied artwork')


# 10: EAST ELEVATOR LOBBY -------------------------------------------------
GROUP='10 EAST ELEVATOR LOBBY | 2017 photo and restored 2024 baseline'
# Plan-traced arrangement, adapted to the established core-model room datums.
ex0=-48.; ex1=-39.5; ey0=24.8; ey1=52.4; ez=.08; eh=5.75
box(((ex0+ex1)/2,(ey0+ey1)/2,ez-.10),(ex1-ex0,ey1-ey0,.20),'Weathered concrete' if AGED else SEC_FLOOR,'Elevator lobby principal floor')
if not AGED:
    for xx in [ex0+.42,ex1-.42]:
        box((xx,(ey0+ey1)/2,ez+.006),(.50,ey1-ey0-.4,.018),'Pale rose marble','Elevator lobby pale perimeter floor bands')
    for yy in [ey0+.38,35.7,43.8,ey1-.38]:
        box(((ex0+ex1)/2,yy,ez+.012),(ex1-ex0-.45,.27,.014),'Pale rose marble','Elevator lobby cross floor bands')
    for yy in [ey0+1.5+i*1.8 for i in range(14)]:
        box(((ex0+ex1)/2,yy,ez+.006),(ex1-ex0-.95,.012,.011),'Pale rose marble','Elevator lobby marble slab seams')
# East wall leaves the broad east entrance open.
for ya,yb in [(ey0,38.13),(42.01,ey1)]:
    box((ex0,(ya+yb)/2,eh/2),(.34,yb-ya,eh),'Warm Mankato column stone','Elevator lobby east wall with entrance opening')
    sec_wall_bands(ex0+.175,ya,yb,.15,eh-.35,'x',name='Elevator lobby stone course joints')
# West wall has two three-elevator banks separated by the arcade opening.
for ya,yb in [(ey0,36.63),(43.36,ey1)]:
    box((ex1+.10,(ya+yb)/2,eh/2),(.35,yb-ya,eh),'Warm Mankato column stone','Elevator lobby west stone bank backing')
# Six restored elevator doors, split three-and-three by the arcade.
for number,yy in enumerate([27.0,30.6,34.2,44.6,47.65,50.7],1):
    width=1.75 if number<4 else 1.58; plane=ex1-.115
    sec_u_box(sec_point(yy,plane,.08+2.05,'x'),width+.30,.15,4.10,'Dark void','Elevator recess '+str(number),'x')
    sec_frame(yy,plane-.06,.09,width,4.02,'x',SEC_IRON if AGED else SEC_BRONZE,'Elevator '+str(number),False,.82,2)
    if AGED:
        sec_u_box(sec_point(yy,plane-.13,1.55,'x'),width-.08,.075,2.90,SEC_PLY,'2017 boarded elevator openings','x')
        for dz in [.48,1.35,2.31]:
            sec_u_box(sec_point(yy,plane-.17,dz,'x'),width-.08,.017,.025,'Distress umber','2017 plywood grain bands','x')
    else:
        sec_u_box(sec_point(yy,plane-.08,1.65,'x'),width-.10,.06,3.12,SEC_BRONZE,'Restored elevator metal door faces','x')
        for delta in [-width/4,width/4]:
            for z in [.5,1.37,2.24,2.98]:
                sec_u_box(sec_point(yy+delta,plane-.122,z,'x'),width/2-.17,.025,.018,'Dark bronze','Restored elevator divided panel rails','x')
            for d in [-width/4+.10,width/4-.10]:
                sec_u_box(sec_point(yy+delta+d,plane-.12,1.74,'x'),.014,.025,2.63,'Dark bronze','Restored elevator divided panel stiles','x')
        sec_u_box(sec_point(yy,plane-.133,1.66,'x'),.016,.024,3.08,'Dark bronze','Restored elevator central door seam','x')
        # Generic recreated dial motif; individual floor numbers are not invented.
        for k in range(17):
            t=pi*k/16
            beam(sec_point(yy+.50*cos(t),plane-.16,3.50+.33*sin(t),'x'),sec_point(yy+.55*cos(t),plane-.16,3.50+.365*sin(t),'x'),.009,SEC_BRONZE,'Restored elevator transom dial marks',5)
        beam(sec_point(yy,plane-.17,3.50,'x'),sec_point(yy-.24,plane-.17,3.73,'x'),.012,SEC_BRONZE,'Restored elevator dial hand',6)
        sec_u_box(sec_point(yy-width/2-.23,plane-.10,1.33,'x'),.18,.12,.34,'Dark bronze','Restored elevator call plates','x')
    # Stone pilasters and compact cap/base profiles.
    for uu in [yy-width/2-.23,yy+width/2+.23]:
        sec_u_box(sec_point(uu,plane-.01,2.65,'x'),.22,.29,5.28,'Warm Mankato column stone','Elevator bank stone pilasters','x')
        for z,w,h in [(.17,.35,.27),(.40,.28,.12),(5.10,.34,.11),(5.32,.43,.12)]:
            sec_u_box(sec_point(uu,plane-.07,z,'x'),w,.36,h,'Warm Mankato column stone','Elevator pilaster base and capital moldings','x')
# End portals connect to women's-room corridor and the east-exit connector.
for yy,label in [(ey0,'north women room approach'),(ey1,'south exit-ramp connection')]:
    for xa,xb in [(ex0,-45.5),(-42.6,ex1)]:
        box(((xa+xb)/2,yy,eh/2),(xb-xa,.30,eh),'Warm Mankato column stone','Elevator lobby '+label+' side infill')
    box((-44.05,yy,4.83),(2.9,.30,1.84),'Warm Mankato column stone','Elevator lobby '+label+' lintel')
    sec_frame(-44.05,yy,.08,2.9,3.86,'y','Dark bronze','Elevator lobby '+label,not AGED,.62,2)
# Ceiling and layered cornice; floorplan precision does not imply measured height.
box(((ex0+ex1)/2,(ey0+ey1)/2,eh+.10),(ex1-ex0,ey1-ey0,.20),PL,'Elevator lobby flat plaster ceiling')
for z,offset,thick in [(eh-.34,.0,.10),(eh-.23,.06,.11),(eh-.11,.15,.14)]:
    for xx in [ex0+.14+offset,ex1-.14-offset]:
        box((xx,(ey0+ey1)/2,z),(.25,ey1-ey0,thick),PL,'Elevator lobby cornice')
    for yy in [ey0+.14+offset,ey1-.14-offset]:
        box(((ex0+ex1)/2,yy,z),(ex1-ex0,.25,thick),PL,'Elevator lobby cornice')
if not AGED:
    for yy in [27.6,33.8,40.0,46.2,50.6]:sec_lamp(-44.0,yy,eh,.24,True)
else:
    # Selective rectangular cladding losses with ribbed backing and attachment pads.
    for yy in [25.4,32.3,45.8,49.0]:
        plane=ex1-.31
        sec_u_box(sec_point(yy,plane,2.30,'x'),.42,.042,3.80,SEC_SUBSTRATE,'2017 missing elevator stone facing','x')
        for d in range(12):sec_u_box(sec_point(yy-.205+d*.035,plane-.025,2.30,'x'),.013,.012,3.8,'Distress umber','2017 substrate parallel ribs','x')
        for j in range(7):
            z=.52+j*.5;u=yy+_sec_rng.uniform(-.14,.14)
            v=[sec_point(u+.075*cos(k*2*pi/8),plane-.035,z+.09*sin(k*2*pi/8),'x') for k in range(8)]
            addmesh(v,[tuple(range(8))],PL,'2017 remnants of stone attachment pads')
    for j in range(22):
        x=_sec_rng.uniform(ex0+.2,ex1-.2);y=_sec_rng.uniform(ey0+.4,ey1-.4);r=_sec_rng.uniform(.15,.60)
        vs=[(x+r*(.65+_sec_rng.random()*.35)*cos(k*2*pi/9),y+r*sin(k*2*pi/9),eh-.012) for k in range(9)]
        addmesh(vs,[tuple(range(9))],SEC_SUBSTRATE,'2017 irregular ceiling plaster-loss interpretation')
    for j in range(75):
        x=_sec_rng.choice([ex0+.3,ex1-.4])+_sec_rng.uniform(-.12,.15);y=_sec_rng.uniform(ey0,ey1);r=_sec_rng.uniform(.025,.11)
        addmesh([(x-r,y,ez+.008),(x+r,y-r,ez+.018),(x+r*.4,y+r,ez+.022)],[(0,1,2)],PL,'2017 sparse lobby edge debris interpretation')
# Modest entrance vestibule and south linking passage; no hidden rooms/shafts.
for ya,yb,xa,xb,label in [(38.13,42.01,-52.1,-48.,'east entrance vestibule'),(52.4,59.4,-45.5,-42.6,'south exit-ramp connector')]:
    box(((xa+xb)/2,(ya+yb)/2,.01),(xb-xa,yb-ya,.12),'Weathered concrete' if AGED else 'Terrazzo','Elevator lobby '+label+' floor')
    box(((xa+xb)/2,(ya+yb)/2,4.7),(xb-xa,yb-ya,.18),PL,'Elevator lobby '+label+' ceiling')
    if 'vestibule' in label:
        for yy in [ya,yb]:box(((xa+xb)/2,yy,2.35),(xb-xa,.22,4.7),'Warm Mankato column stone','Elevator lobby vestibule walls')
        sec_frame(40.07,xa,.06,3.88,4.6,'x','Dark bronze','East entrance double-door wall',not AGED,.90,4)
    else:
        for xx in [xa,xb]:box((xx,(ya+yb)/2,2.35),(.22,yb-ya,4.7),PL,'Elevator lobby exit connector walls')
SEC_CAMERAS['elevator_lobby']=((-45.9,50.2,1.75),(-42.2,28.0,2.5),22)
SEC_SPACES.append({'id':'east_elevator_lobby','extent_m':[ex0,ex1,ey0,ey1,0,eh],'era':ERA,'basis':'1914 plan and six-elevator February2024 photo; May2017 missing cladding and boarding','precision':'Plan-traced approximate footprint; visual-proportion heights/detail; no lift shafts or cabins'})


# 11: EAST EXIT RAMP -----------------------------------------------------
GROUP='11 EAST EXIT RAMP | retained graffiti passage, exact markings unmodeled'
rx0=-45.1;rx1=-29.4894;ry0=59.4;ry1=66.2;rcy=(ry0+ry1)/2;rh=5.4
# The current rise is not surveyed: use a modest 0.45m slope toward the east.
# Quoted 3.33% and 2.25ft in 1914 refer to the ARCADE, not this exit ramp.
def sec_exit_z(x):return .06+.45*(rx1-x)/(rx1-rx0)
v=[(rx0,ry0,sec_exit_z(rx0)),(rx1,ry0,sec_exit_z(rx1)),(rx1,ry1,sec_exit_z(rx1)),(rx0,ry1,sec_exit_z(rx0))]
addmesh(v,[(0,1,2,3)],'Weathered concrete' if AGED else 'Terrazzo','East exit ramp floor | visual slope approximation')
for yy in [ry0,ry1]:
    # North connector remains open at X[-45.5,-42.6].
    segments=[(rx0,rx1)] if yy==ry1 else [(rx0,-45.5),(-42.6,rx1)]
    for xa,xb in segments:
        if xb<=xa:continue
        box(((xa+xb)/2,yy,rh/2),(xb-xa,.36,rh),'Concourse buff brick','East exit ramp brick wall with connector opening')
        box(((xa+xb)/2,yy+(.19 if yy==ry0 else -.19),.64),(xb-xa,.10,1.15),'Warm Mankato column stone','East exit ramp stone dado')
    if yy==ry0:
        box((-44.05,yy,4.78),(2.9,.36,1.24),'Concourse buff brick','East ramp north connector brick lintel')
        sec_frame(-44.05,yy+.22,.28,2.9,3.84,'y','Dark bronze','East exit ramp north lobby portal',False,.0,1)
    for xx in [rx0+.45,-39.7,-34.8,rx1-.45]:
        if yy==ry0 and -45.8<xx<-42.3:continue
        box((xx,yy+(.20 if yy==ry0 else -.20),2.7),(.44,.16,5.25),'Warm Mankato column stone','East exit ramp dressed stone pilasters')
    if not AGED:
        intervals=[(rx0+.9,-46.1),(-42.0,rx1-.9)] if yy==ry0 else [(rx0+.9,rx1-.9)]
        for k,(u0,u1) in enumerate(intervals):
            if u1-u0<1.5:continue
            sec_original_marks(yy+(.195 if yy==ry0 else -.195),u0,u1,1.1,4.35,'y',38+k+(10 if yy==ry1 else 0),21)
        # Photos show two long handrails with regular vertical supports.
        for xx in [rx0+.8+i*(rx1-rx0-1.6)/11 for i in range(12)]:
            if yy==ry0 and -45.7<xx<-42.4:continue
            z=sec_exit_z(xx)
            beam((xx,yy+(.43 if yy==ry0 else -.43),z),(xx,yy+(.43 if yy==ry0 else -.43),z+1.0),.019,'Dark bronze','East exit ramp handrail posts')
        for xa,xb in ([(rx0+.8,-45.7),(-42.4,rx1-.8)] if yy==ry0 else [(rx0+.8,rx1-.8)]):
            if xb<=xa:continue
            beam((xa,yy+(.43 if yy==ry0 else -.43),sec_exit_z(xa)+1.0),(xb,yy+(.43 if yy==ry0 else -.43),sec_exit_z(xb)+1.0),.027,'Dark bronze','East exit ramp handrails')
# The south wall contains three dark conservation grilles visible in post38.
for xx in [-42.3,-37.7,-33.1]:
    sec_frame(xx,ry1-.20,1.15,3.4,3.10,'y','Dark bronze','East exit ramp conservation grille frame',False,0,1)
    box((xx,ry1-.213,2.70),(3.27,.035,2.94),SEC_DARK,'East exit ramp dark conservation grille')
    for k in range(56):box((xx-1.6+k*.058,ry1-.239,2.7),(.011,.016,2.94),'Window cast iron','East exit ramp fine grille bars')
box(((rx0+rx1)/2,rcy,rh+.09),(rx1-rx0,ry1-ry0,.18),PL,'East exit ramp flat ceiling')
for xx in [-39.7,-34.8]:
    box((xx,rcy,rh-.22),(.42,ry1-ry0,.45),PL,'East exit ramp transverse ceiling beams')
for yy in [ry0+.16,ry1-.16]:
    for z,w in [(rh-.26,.15),(rh-.15,.23),(rh-.04,.35)]:box(((rx0+rx1)/2,yy,z),(rx1-rx0,w,.1),PL,'East exit ramp cornice')
# Photographed glazed screens close the narrow corridor at its two ends.
for xx,label in [(rx0,'east vestibule screen'),(rx1,'west concourse connection')]:
    sec_frame(rcy,xx,.12,ry1-ry0-.30,4.65,'x','Dark bronze','East exit ramp '+label,not AGED,1.35,4)
    if not AGED and xx==rx1:
        for ya,yb in [(ry0+.15,rcy-1.65),(rcy+1.65,ry1-.15)]:
            box((xx-.115,(ya+yb)/2,1.63),(.16,yb-ya,3.02),'Wood walnut','East ramp west portal photographed solid lower side panels')
# Historical plan flares only at the east facade to the three observed exterior exit-door bays.
# Perimeter jogs are approximate raster controls; hidden adjacent rooms remain unmodeled.
evx0=-52.1288;evx1=rx0;evy0=57.2;evy1=69.1
box(((evx0+evx1)/2,(evy0+evy1)/2,.42),(evx1-evx0,evy1-evy0,.18),'Weathered concrete' if AGED else 'Terrazzo','East three-door vestibule floor | historical flared shell')
box(((evx0+evx1)/2,(evy0+evy1)/2,rh+.09),(evx1-evx0,evy1-evy0,.18),PL,'East three-door vestibule ceiling')
for yy in [evy0,evy1]:box(((evx0+evx1)/2,yy,rh/2),(evx1-evx0,.36,rh),'Concourse buff brick','East vestibule flared side walls')
for ya,yb in [(evy0,ry0),(ry1,evy1)]:box((rx0,(ya+yb)/2,rh/2),(.36,yb-ya,rh),'Concourse buff brick','East vestibule shoulders to narrow ramp')
for yy in [58.83,62.80,66.98]:sec_frame(yy,evx0,.51,2.4384,2.49,'x','Dark bronze','East exit exterior double-door bank',not AGED,.85,2)
if not AGED:
    for xx in [-43.0,-38.4,-33.8]:sec_lamp(xx,rcy,rh,.18,False)
SEC_CAMERAS['east_exit_ramp']=((-44.1,62.8,2.05),(-29.5,62.8,2.2),22)
SEC_CAMERAS['east_exit_lobby_portal']=((-44.1,62.5,1.9),(-44.05,45.5,2.0),25)
SEC_SPACES.append({'id':'east_exit_ramp','extent_m':[rx0,rx1,ry0,ry1,0,rh],'era':ERA,'basis':'1914 exit-ramp location; May2024 post36–38 finish observations','precision':'1914 polygon: narrowY59.4..66.2 ramp, east vestibuleY57.2..69.1, three doors; raster +/-0.5–0.8m. Current subdivision and .45m rise remain unverified; exact2017 condition unknown','artwork':'Original non-lettering gesture marks only; no copied historical graffiti'})


# 12: PASSENGER RAMP UPPER ROOM AND MEZZANINE BRIDGE ----------------------
GROUP='12 PASSENGER RAMP | observed upper segment and mezzanine bridge'
prx=11.5824;pry0=75.2872;pry1=87.8;prz0=.06;prz1=prz0-.07*(pry1-pry0)
sec_slope_floor(-prx,prx,pry0,pry1,prz0,prz1,'Weathered concrete','Passenger ramp historic 7 percent upper segment | current slope unverified')
# Three entrances are separated by substantial buff brick piers.
for xx in [-prx,-prx/3,prx/3,prx]:
    box((xx,pry0,5.05),(.85,1.12,10.10),'Concourse buff brick','Passenger ramp entrance brick piers')
    box((xx,pry0,.70),(.98,1.20,1.36),'Warm Mankato column stone','Passenger ramp entrance pier stone bases')
# Continuous observed bridge, supported by shallow curved steel haunches.
box((0,pry0+.85,4.90),(2*prx,2.7,.22),SEC_IRON,'Passenger ramp mezzanine bridge deck')
for yy in [pry0-.53,pry0+2.23]:
    box((0,yy,4.72),(2*prx,.22,.82),SEC_IRON,'Passenger ramp mezzanine riveted fascia')
    for xx in [-prx+1.0+k*1.65 for k in range(14)]:
        box((xx,yy-.125,4.74),(1.43,.045,.50),SEC_IRON,'Passenger ramp bridge raised fascia panels')
        for dx in [-.65,.65]:
            for zz in [4.48,4.98]:beam((xx+dx,yy-.15,zz),(xx+dx,yy-.20,zz),.035,SEC_IRON,'Passenger ramp bridge rivets',8)
    for baycenter in [-2*prx/3,0,2*prx/3]:
        for side in [-1,1]:
            start=baycenter+side*(prx/3-.48)
            for k in range(11):
                t=k/11*pi/2;t2=(k+1)/11*pi/2
                p=(start-side*1.22*(1-cos(t)),yy,3.06+1.35*sin(t))
                q=(start-side*1.22*(1-cos(t2)),yy,3.06+1.35*sin(t2))
                beam(p,q,.11,SEC_IRON,'Passenger ramp curved bridge haunches',8)
# Upper bridge glazing: the old corroded frames survive, restored glazing added.
for xc in [-2*prx/3,0,2*prx/3]:
    sec_frame(xc,pry0-.03,5.14,2*prx/3-.92,4.65,'y',SEC_IRON,'Passenger ramp high bridge grid',not AGED,0,7)
    for zz in [6.05,7.0,7.95,8.9]:box((xc,pry0-.03,zz),(2*prx/3-.90,.15,.065),SEC_IRON,'Passenger ramp high transoms')
# Shallow room south of the entrance; windows and upper brick frieze observed.
for xx in [-prx,prx]:
    box((xx,(pry0+pry1)/2,.725),(.70,pry1-pry0,3.15),'Concourse buff brick','Passenger ramp side lower wall')
    for yy in [pry0+.8,pry0+6.3,pry1-.45]:
        box((xx,yy,5.25),(.92,.76,9.1),'Concourse buff brick','Passenger ramp side window piers')
    for yy in [pry0+3.5,pry0+9.2]:
        sec_frame(yy,xx,2.45,4.7,5.58,'x',SEC_IRON,'Passenger ramp side grid windows',not AGED,1.45,6)
    box((xx,(pry0+pry1)/2,9.28),(.82,pry1-pry0,1.45),'Concourse buff brick','Passenger ramp side brick frieze')
# Observed back-wall window bank; lower exact modern intervention incomplete.
box((0,pry1,.725),(2*prx,.70,3.15),'Concourse buff brick','Passenger ramp back lower masonry shell')
for xx in [-prx,-prx/3,prx/3,prx]:box((xx,pry1,5.13),(.83,.86,9.82),'Concourse buff brick','Passenger ramp back window piers')
for xx in [-2*prx/3,0,2*prx/3]:
    sec_frame(xx,pry1-.04,2.10,2*prx/3-1.,5.65,'y',SEC_IRON,'Passenger ramp back grid windows',not AGED,1.48,7)
    for zz in [3.60,4.7,5.8,6.9]:box((xx,pry1-.05,zz),(2*prx/3-.94,.14,.06),SEC_IRON,'Passenger ramp back-window transoms')
    # Circular brick medallion, original geometry guided by the photo.
    for k in range(24):
        t=2*pi*k/24;u=xx+.36*cos(t);z=8.66+.36*sin(t)
        beam((u,pry1-.47,z),(xx+.47*cos(t),pry1-.47,8.66+.47*sin(t)),.036,'Warm Mankato column stone','Passenger ramp radial brick medallions',6)
box((0,pry1,9.03),(2*prx,.82,1.60),'Concourse buff brick','Passenger ramp back frieze')
for zz in [8.16,9.70,9.94]:box((0,pry1-.42,zz),(2*prx,.22,.13),'Warm Mankato column stone','Passenger ramp back cornice')
# Transparent roof only in the restored baseline; pre2017 coverage does not
# establish exact intact panel count, so there is no fabricated breakage map.
midy=(pry0+pry1)/2;eave=10.04;rise=2.05
for xx in [-prx+i*(2*prx)/8 for i in range(9)]:
    for yy in [pry0,pry1]:
        beam((xx,yy,eave),(xx,midy,eave+rise),.075,SEC_IRON,'Passenger ramp roof chords')
        beam((xx,yy,eave),(xx,midy,eave),.055,SEC_IRON,'Passenger ramp roof ties')
    beam((xx,midy,eave),(xx,midy,eave+rise),.05,SEC_IRON,'Passenger ramp roof king posts')
for yy,zz in [(pry0,eave),(midy,eave+rise),(pry1,eave)]:beam((-prx,yy,zz),(prx,yy,zz),.08,SEC_IRON,'Passenger ramp roof purlins')
if not AGED:
    for yy in [pry0,pry1]:addmesh([(-prx,yy,eave+.025),(prx,yy,eave+.025),(prx,midy,eave+rise+.025),(-prx,midy,eave+rise+.025)],[(0,1,2,3)],'Glass clear','Passenger ramp restored glazed roof')
else:
    for yy in [pry0+.64,pry0+1.37]:
        box((0,yy,4.75),(2*prx,.10,.12),SEC_IRON,'2017 corroded bridge cross members')
    sec_original_marks(pry1-.361,-prx+.8,prx-.8,-.30,1.6,'y',201728,16)
SEC_CAMERAS['passenger_ramp']=((-7.5,78.2,1.4),(2.5,86.2,5.3),24)
SEC_CAMERAS['passenger_bridge']=((2.3,81.0,1.3),(-6.1,75.3,6.4),23)
SEC_SPACES.append({'id':'passenger_ramp_upper','extent_m':[-prx,prx,pry0,pry1,prz1,12.1],'era':ERA,'basis':'1914 76ft three-opening entry and approximately7percent grade; exactMay2017 pre28; February2024 post43/45','precision':'Entry total width published; segment length, heights, and current pitch visual approximations','limit':'No subway, train-platform stairs, or below-track hidden connections; 2017 roof panels omitted because count unknown'})


# 13: WEST CONNECTING CORRIDOR AND OBSERVED PRESERVED STAIR ---------------
# No reliable exact2017 photograph of this identified location is available.
# It is therefore a restored-baseline shell only, never invented 2017 decay.
if not AGED:
    GROUP='13 WEST CONNECTING CORRIDOR | 2023 observed shell and stair fragment'
    wx0=35.8;wx1=51.4;wy0=23.5;wy1=28.85;wh=5.55
    box(((wx0+wx1)/2,(wy0+wy1)/2,.018),(wx1-wx0,wy1-wy0,.12),SEC_GROUT,'West connecting corridor hex-tile grout bed')
    # Original hex-grid geometry; approximate module is not a measured tile count.
    hr=.07;dx=1.5*hr;dy=sqrt(3)*hr
    for ix in range(int((wx1-wx0)/dx)):
        xx=wx0+.10+ix*dx
        for iy in range(int((wy1-wy0)/dy)-1):
            yy=wy0+.13+iy*dy+(ix%2)*dy/2
            if yy>wy1-.10:continue
            vv=[(xx+(hr-.002)*cos(k*pi/3),yy+(hr-.002)*sin(k*pi/3),.083) for k in range(6)]
            addmesh(vv,[tuple(range(6))],SEC_HEX,'West connecting corridor original hex-tile geometry')
    for yy in [wy0,wy1]:
        # Keep a door in each adjoining room wall near the central corridor.
        for xa,xb in [(wx0,42.6),(45.6,wx1)]:
            box(((xa+xb)/2,yy,wh/2),(xb-xa,.23,wh),PL,'West connecting corridor plaster walls with room portals')
            box(((xa+xb)/2,yy+(.125 if yy==wy0 else -.125),1.35),(xb-xa,.028,2.5),SEC_GROUT,'West corridor glazed-tile wainscot bed')
            for row in range(22):
                for col in range(int((xb-xa)/.23)):
                    xx=xa+.12+col*.23+(.115 if row%2 else 0)
                    if xx>xb-.07:continue
                    box((xx,yy+(.146 if yy==wy0 else -.146),.17+row*.11),(.221,.018,.102),SEC_TILE,'West corridor glazed white subway tiles')
        box((44.1,yy,4.58),(3.0,.23,1.95),PL,'West corridor room portal lintels')
        sec_frame(44.1,yy,.08,3.0,3.52,'y','Wood walnut','West corridor reading room or restaurant portal',True,.60,2)
    box(((wx0+wx1)/2,(wy0+wy1)/2,wh+.08),(wx1-wx0,wy1-wy0,.16),PL,'West connecting corridor flat ceiling')
    box((wx1,(wy0+wy1)/2,wh/2),(.20,wy1-wy0,wh),PL,'West corridor stair-end plaster wall')
    for xx in [38.3,42.4,46.5,49.8]:sec_lamp(xx,25.3,wh,.46)
    # Photographed preserved rusted stair at the WEST corridor end. Only two
    # visible flights and their landing; no inferred full stairwell continuation.
    # The actual profile is not copied vertex-for-vertex from any photograph.
    stairx=48.9;stairy=25.75;stairw=1.13;run=2.9;rise=2.05;n=12
    stairmetal=sec_material('Secondary preserved west stair iron',(.12,.092,.065),.83,.35,.32,24)
    for i in range(n):
        xx=stairx-run/2+(i+.5)*run/n;zz=.10+(i+1)*rise/n
        box((xx,stairy,zz-.045),(run/n+.035,stairw,.09),stairmetal,'West preserved stair first flight treads')
        box((xx-run/n/2,stairy,zz-rise/n/2),(.035,stairw,rise/n),stairmetal,'West preserved stair first flight risers')
    box((stairx+run/2+.37,stairy,.10+rise-.07),(.74,stairw,.14),stairmetal,'West preserved stair intermediate landing')
    for side in [-1,1]:
        yy=stairy+side*(stairw/2+.04)
        beam((stairx-run/2,yy,.02),(stairx+run/2,yy,rise+.02),.06,stairmetal,'West preserved stair sloped stringers')
        beam((stairx-run/2,yy,1.06),(stairx+run/2,yy,rise+1.06),.035,'Wood walnut','West preserved stair handrails')
        for i in range(n+1):
            xx=stairx-run/2+i*run/n;zz=.10+i*rise/n
            beam((xx,yy,zz),(xx,yy,zz+.93),.016,stairmetal,'West preserved stair slim balusters')
    # Return flight visible above first. It ends at the documented-fragment limit.
    for i in range(n):
        xx=stairx+run/2-(i+.5)*run/n;zz=.10+rise+(i+1)*rise/n
        box((xx,stairy+1.32,zz-.045),(run/n+.035,stairw,.09),stairmetal,'West preserved stair return-flight treads')
        box((xx+run/n/2,stairy+1.32,zz-rise/n/2),(.035,stairw,rise/n),stairmetal,'West preserved stair return-flight risers')
    box((stairx+run/2+.37,stairy+.66,.10+rise-.07),(.74,2.45,.14),stairmetal,'West preserved stair turning landing')
    for side in [-1,1]:
        yy=stairy+1.32+side*(stairw/2+.04)
        beam((stairx+run/2,yy,rise+.02),(stairx-run/2,yy,2*rise+.02),.06,stairmetal,'West preserved stair return stringers')
        beam((stairx+run/2,yy,rise+1.06),(stairx-run/2,yy,2*rise+1.06),.035,'Wood walnut','West preserved stair return handrails')
        for i in range(n+1):
            xx=stairx+run/2-i*run/n;zz=.10+rise+i*rise/n
            beam((xx,yy,zz),(xx,yy,zz+.93),.016,stairmetal,'West preserved stair return balusters')
    # Close the visible undersides and give the observed fragment a terminal landing.
    for xa,xb,ya,yb,za,zb in [(stairx-run/2,stairx+run/2,stairy-stairw/2,stairy+stairw/2,.03,rise+.03),(stairx+run/2,stairx-run/2,stairy+1.32-stairw/2,stairy+1.32+stairw/2,rise+.03,2*rise+.03)]:
        addmesh([(xa,ya,za),(xb,ya,zb),(xb,yb,zb),(xa,yb,za)],[(0,1,2,3)],stairmetal,'West preserved stair continuous visible underside')
    box((stairx-run/2-.32,(stairy+1.32-stairw/2+wy1)/2,2*rise+.03),(.64,wy1-(stairy+1.32-stairw/2),.14),stairmetal,'West preserved stair upper wall-connected fragment landing')
    SEC_CAMERAS['west_corridor']=((37.0,25.7,1.68),(49.2,26.2,2.3),24)
    SEC_CAMERAS['west_preserved_stair']=((45.4,23.4,1.8),(49.0,26.3,2.5),23)
    SEC_SPACES.append({'id':'west_connecting_corridor','extent_m':[wx0,wx1,wy0,wy1,0,wh],'era':ERA,'basis':'1914 service/cafe adjacency and August2023 post55–58','precision':'Visible finishes and two-flight stair interpreted; approximate room bounds and stair orientation; no lower rooms or hidden continuation','limit':'Not included in2017 because exactdated matching source absent; lower stair descent and basement omitted'})


# 14: WEST CARRIAGE ENCLOSURE --------------------------------------------
GROUP='14 WEST CARRIAGE ENCLOSURE | historic footprint, 2025 observed structure'
cx0=52.6288;cx1=cx0+19.5072;cy1=79.8576;cy0=cy1-26.2128
ccx=(cx0+cx1)/2;ccy=(cy0+cy1)/2;cwidth=cx1-cx0;cdepth=cy1-cy0
box((ccx,ccy,-.02),(cwidth,cdepth,.16),'Weathered concrete','Carriage enclosure historic 64 by 86 foot footprint')
# Masonry pylons are visible in the real 2025 photograph, not design renderings.
for xx in [cx0+.72,cx1-.72]:
    for yy in [cy0+.74,cy1-.74]:
        box((xx,yy,3.9),(1.75,1.90,7.8),'Exterior Indiana limestone','Carriage enclosure corner masonry pylons')
        for z,w,d,h in [(.24,2.0,2.14,.35),(.54,1.94,2.07,.15),(6.95,1.94,2.06,.14),(7.24,2.13,2.25,.23),(7.48,2.32,2.41,.20),(7.73,1.95,2.02,.28)]:
            box((xx,yy,z),(w,d,h),'Exterior Indiana limestone','Carriage enclosure pylon cornice and plinth')
        sec_wall_bands(xx+(.882 if xx>ccx else -.882),yy-.94,yy+.94,.7,6.95,'x',name='Carriage enclosure pylon stone joints')
# Low west parapet; no invented finished cocktail-lounge curtain wall.
box((cx1,ccy,.58),(.45,cdepth-3.35,1.16),'Exterior Indiana limestone','Carriage enclosure west low masonry parapet')
box((cx1,ccy,1.20),(.64,cdepth-3.35,.18),'Exterior Indiana limestone','Carriage enclosure west parapet coping')
# Three shallow wrought-iron arches along west elevation.
span=(cdepth-3.3)/3;u0=cy0+1.65
for j in range(3):
    uy=u0+(j+.5)*span
    arch(uy,cx1-.1,5.40,span-.42,1.01,.15,.26,SEC_IRON,'Carriage west iron arcade arch',32,'side')
    box((cx1-.1,uy,6.85),(.26,span,.37),SEC_IRON,'Carriage west lattice spandrel rail')
    # Diagonal lattice lies above the shallow curved main arch.
    for k in range(8):
        ua=uy-span/2+.1+k*(span-.2)/8;ub=ua+(span-.2)/8
        beam((cx1-.12,ua,6.30),(cx1-.12,ub,6.66),.033,SEC_IRON,'Carriage west spandrel lattice')
        beam((cx1-.12,ua,6.66),(cx1-.12,ub,6.30),.033,SEC_IRON,'Carriage west spandrel lattice')
for yy in [u0+span,u0+2*span]:
    box((cx1-.1,yy,3.96),(.32,.38,5.52),SEC_IRON,'Carriage intermediate iron piers')
    for z in [1.30+i*.55 for i in range(10)]:
        beam((cx1-.28,yy-.15,z),(cx1-.28,yy+.15,z+.49),.025,SEC_IRON,'Carriage iron pier crossed lattice')
        beam((cx1-.28,yy+.15,z),(cx1-.28,yy-.15,z+.49),.025,SEC_IRON,'Carriage iron pier crossed lattice')
# North/south returns: structural span only, approximate division, open-sided.
for yy in [cy0+.65,cy1-.65]:
    arch(ccx,yy,5.42,cwidth-3.5,1.12,.16,.31,SEC_IRON,'Carriage return shallow iron arch',48)
    box((ccx,yy,7.09),(cwidth-2,.30,.50),SEC_IRON,'Carriage return entablature')
for xx in [cx0+.65,cx1-.1]:box((xx,ccy,7.10),(.38,cdepth-2,.49),SEC_IRON,'Carriage long iron entablature')
# Roof system: historic shell with modern 2025 observed raised glazed lantern.
for k in range(9):
    yy=cy0+1.2+k*(cdepth-2.4)/8
    for xx in [cx0+.7,cx1-.7]:beam((xx,yy,7.31),(ccx,yy,8.38),.07,SEC_IRON,'Carriage roof transverse iron members')
for xx in [cx0+.7,cx1-.7]:
    inner=ccx+(-3.8 if xx<ccx else 3.8)
    addmesh([(xx,cy0+.7,7.36),(xx,cy1-.7,7.36),(inner,cy1-.7,8.0),(inner,cy0+.7,8.0)],[(0,1,2,3)],'Roof dark copper','Carriage dark roof shoulder | roof cover approximate')
if not AGED:
    lx0=ccx-3.8;lx1=ccx+3.8;ly0=cy0+1.40;ly1=cy1-1.40;lz=8.0;peak=9.38
    for xx in [lx0,lx1]:
        addmesh([(xx,ly0,lz),(xx,ly1,lz),(xx,ly1,lz+.60),(xx,ly0,lz+.60)],[(0,1,2,3)],'Glass tower blue','Carriage 2025 observed roof-lantern side glazing')
        addmesh([(xx,ly0,lz+.60),(xx,ly1,lz+.60),(ccx,ly1,peak),(ccx,ly0,peak)],[(0,1,2,3)],'Glass clear','Carriage 2025 observed roof-lantern sloped glazing')
        beam((xx,ly0,lz),(xx,ly1,lz),.065,SEC_IRON,'Carriage roof-lantern lower rails')
        beam((xx,ly0,lz+.60),(xx,ly1,lz+.60),.055,SEC_IRON,'Carriage roof-lantern eave rails')
    for k in range(13):
        yy=ly0+k*(ly1-ly0)/12
        for xx in [lx0,lx1]:
            beam((xx,yy,lz),(xx,yy,lz+.60),.046,SEC_IRON,'Carriage roof-lantern mullions')
            beam((xx,yy,lz+.60),(ccx,yy,peak),.046,SEC_IRON,'Carriage roof-lantern sloped bars')
    beam((ccx,ly0,peak),(ccx,ly1,peak),.065,SEC_IRON,'Carriage roof-lantern ridge')
SEC_CAMERAS['carriage_house']=((101.0,38.2,7.3),(61.7,66.1,4.6),35)
SEC_CAMERAS['carriage_detail']=((85.0,66.2,3.2),(65.7,67.0,4.7),30)
SEC_SPACES.append({'id':'west_carriage_enclosure','extent_m':[cx0,cx1,cy0,cy1,0,9.38],'era':ERA,'basis':'Published1914 64x86ft footprint; August2025 real west-elevation photo','precision':'Footprint published; placement plan-traced; height/profile/bay dimensions visually approximated','limit':'No unverified2026 side glazing, lounge/hotel fit-out, or asserted completion;2017 roof-lantern and exact damage unknown'})

# A side-effect-free integration hook: the parent can apply these records after
# converting geometry batches to Blender collections/objects.
SEC_EVIDENCE_PROPERTIES={s['id']:s for s in SEC_SPACES}
GROUP=_sec_old_group
SECONDARY_CAMERAS=SEC_CAMERAS
