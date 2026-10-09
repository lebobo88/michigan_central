"""Opt-in, original north-entry canopy study NEC-01; import is passive.

No live builder, door/window geometry, column, entablature, or asset is edited.
Use canopy_parts('2026') for the mixed opaque/glazed restored canopy, or
canopy_parts('2017') for the observed retained wall bosses ONLY. Dimensions,
pattern counts, glass divisions, fixtures and connection sections are trials.
See manifests/north_entry_canopy_detail/EVIDENCE_CONTROLS_PROVENANCE.md.
"""
from dataclasses import dataclass,asdict
import math

@dataclass(frozen=True)
class Controls:
    width:float=7.46
    front_y:float=-5.30
    back_y:float=-.55
    fascia_bottom:float=3.80
    fascia_top:float=4.16
    skylight_width:float=5.60
    skylight_front_y:float=-4.62
    skylight_back_y:float=-1.16
    anchor_x:float=3.57
    anchor_y:float=-1.067
    anchor_z:float=7.20
    roof_x_divisions:int=3
    roof_y_divisions:int=3
    front_fascia_modules:int=20
    side_fascia_modules:int=12
    front_bulbs_per_row:int=26
    side_bulbs_per_row:int=13

DEFAULT_CONTROLS=Controls()

@dataclass
class Part:
    name:str
    role:str
    material:str
    vertices:list
    faces:list
    face_uv_m:list

MATERIALS={
 'painted_metal':dict(name='Canopy pale painted metal | alloy unverified',color=(.43,.48,.46),roughness=.40,metallic=.08,transmission=0,emission=0),
 'roof_sheet':dict(name='Canopy opaque roof and soffit | layered build-up unknown',color=(.41,.46,.44),roughness=.48,metallic=.10,transmission=0,emission=0),
 'glass':dict(name='Canopy skylight glazing | optical properties approximate',color=(.84,.92,.94),roughness=.12,metallic=0,transmission=1,emission=0),
 'lamp_metal':dict(name='Canopy warm dark lamp fittings | finish approximate',color=(.11,.063,.024),roughness=.35,metallic=.65,transmission=0,emission=0),
 'lamp_globe':dict(name='Canopy warm frosted globes | nominal glow',color=(1,.79,.46),roughness=.34,metallic=0,transmission=0,emission=3),
 'rust':dict(name='2017 retained canopy hardware | original rust approximation',color=(.14,.060,.020),roughness=.82,metallic=.16,transmission=0,emission=0),
}

def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def mul(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def unit(a):return mul(a,1/math.sqrt(dot(a,a)))
def lerp(a,b,t):return add(a,mul(sub(b,a),t))

def _part(name,role,material,v,f,uv=None):
    # Planar face-local metric UVs avoid global-axis collapse on tiny hardware.
    if uv is None:
        uv=[]
        for face in f:
            origin=v[face[0]];u=unit(sub(v[face[1]],origin));normal=unit(cross(sub(v[face[1]],origin),sub(v[face[2]],origin)));w=cross(normal,u)
            uv.append([(dot(sub(v[i],origin),u),dot(sub(v[i],origin),w)) for i in face])
    return Part(name,role,material,v,f,uv)

def _box(name,role,material,c,s,basis=None):
    u,v,w=basis or ((1,0,0),(0,1,0),(0,0,1))
    verts=[add(c,add(add(mul(u,a*s[0]/2),mul(v,b*s[1]/2)),mul(w,d*s[2]/2))) for a,b,d in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
    return _part(name,role,material,verts,faces)

def _bar(name,role,material,p,q,width,depth=None,normal=(0,0,1)):
    u=unit(sub(q,p));w=unit(normal);v=unit(cross(w,u));w=cross(u,v)
    return _box(name,role,material,lerp(p,q,.5),(math.dist(p,q),width,depth or width),(u,v,w))

def _tube(name,role,material,p,q,r,n=16):
    axis=unit(sub(q,p));u=unit(cross(axis,(0,0,1) if abs(axis[2])<.9 else (1,0,0)));w=cross(axis,u)
    v=[add(c,add(mul(u,r*math.cos(2*math.pi*i/n)),mul(w,r*math.sin(2*math.pi*i/n)))) for c in (p,q) for i in range(n)]
    # Triangle-fan caps with center vertices keep tangent conditioning bounded.
    v.extend([p,q]);f=[(2*n,(i+1)%n,i) for i in range(n)]+[(2*n+1,n+i,n+(i+1)%n) for i in range(n)]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    return _part(name,role,material,v,f)

def _ring(name,role,material,c,normal,r,thickness,depth,n=32):
    axis=unit(normal);u=unit(cross(axis,(0,0,1) if abs(axis[2])<.9 else (1,0,0)));w=cross(axis,u)
    v=[add(add(c,mul(axis,z)),add(mul(u,rad*math.cos(2*math.pi*i/n)),mul(w,rad*math.sin(2*math.pi*i/n)))) for z in (-depth/2,depth/2) for rad in (r-thickness/2,r+thickness/2) for i in range(n)]
    f=[]
    for i in range(n):
        j=(i+1)%n
        f.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    return _part(name,role,material,v,f)

def _rect_ring(name,role,material,xout,yfront,yback,xin,frontin,backin,zbottom,ztop):
    outer=[(-xout,yfront),(xout,yfront),(xout,yback),(-xout,yback)]
    inner=[(-xin,frontin),(xin,frontin),(xin,backin),(-xin,backin)]
    v=[(x,y,z) for z in (zbottom,ztop) for line in (outer,inner) for x,y in line];f=[]
    for i in range(4):
        j=(i+1)%4
        f.extend([(i,j,8+j,8+i),(4+i,12+i,12+j,4+j),(8+i,8+j,12+j,12+i),(i,4+i,4+j,j)])
    return _part(name,role,material,v,f)

def _sphere(name,role,material,c,r,n=12,rings=6):
    v=[add(c,(0,0,-r))]
    for k in range(1,rings):
        t=-math.pi/2+math.pi*k/rings
        for i in range(n):v.append(add(c,(r*math.cos(t)*math.cos(2*math.pi*i/n),r*math.cos(t)*math.sin(2*math.pi*i/n),r*math.sin(t))))
    top=len(v);v.append(add(c,(0,0,r)));f=[]
    for i in range(n):f.append((0,1+(i+1)%n,1+i))
    for k in range(rings-2):
        a=1+k*n;b=a+n
        for i in range(n):j=(i+1)%n;f.append((a+i,a+j,b+j,b+i))
    for i in range(n):f.append((top,1+(rings-2)*n+i,1+(rings-2)*n+(i+1)%n))
    return _part(name,role,material,v,f)

def canopy_parts(era='2026',c=DEFAULT_CONTROLS):
    if era not in ('2017','2026'):raise ValueError('Era must be 2017 or 2026')
    parts=[];restored=era=='2026';metal='painted_metal' if restored else 'rust'
    def put(p):parts.append(p)
    # Visible round bosses and simple projecting attachment eye. No hidden bolts,
    # elaborate rosette relief, or rust-map claim is inferred from photographs.
    for side in (-1,1):
        x=side*c.anchor_x;center=(x,c.anchor_y,c.anchor_z)
        put(_tube(f'{era} wall boss backing {side}','anchor',metal,add(center,(0,.030,0)),add(center,(0,-.023,0)),.167,32))
        put(_ring(f'{era} wall boss rolled perimeter {side}','anchor',metal,add(center,(0,-.031,0)),(0,1,0),.146,.027,.031,32))
        put(_tube(f'{era} wall boss center boss {side}','anchor',metal,add(center,(0,-.060,0)),add(center,(0,-.019,0)),.084,24))
        put(_ring(f'{era} exposed attachment eye {side}','anchor',metal,add(center,(0,-.113,-.030)),(1,0,0),.064,.031,.038,24))
    if not restored:return parts
    x=c.width/2;fi=c.skylight_front_y;bi=c.skylight_back_y;xi=c.skylight_width/2
    # True annular opaque roof/soffit: no hidden full rectangle across the glazing.
    put(_rect_ring('Opaque perimeter roof and soffit','roof_opaque','roof_sheet',x,c.front_y,c.back_y,xi,fi,bi,3.88,4.105))
    put(_rect_ring('Raised narrow perimeter fascia body','fascia','painted_metal',x+.012,c.front_y-.012,c.back_y,x-.058,c.front_y+.058,c.back_y-.058,3.80,4.15))
    put(_rect_ring('Fascia upper stepped drip edge','edge','painted_metal',x+.030,c.front_y-.030,c.back_y,x-.070,c.front_y+.070,c.back_y-.070,4.142,4.198))
    put(_rect_ring('Fascia lower bead edge','edge','painted_metal',x+.020,c.front_y-.020,c.back_y,x-.061,c.front_y+.061,c.back_y-.061,3.791,3.817))
    put(_rect_ring('Fascia top face fillet','edge','painted_metal',x+.022,c.front_y-.022,c.back_y,x-.060,c.front_y+.060,c.back_y-.060,4.080,4.114))
    # Rectangular solid-panel relief, flat raised bars instead of copied imagery.
    # Pattern frequency is regularized; motifs follow visible crossed/diamond form.
    def relief_run(a,b,n,normal,label):
        along=unit(sub(b,a));depth=.013
        for i in range(n):
            left=lerp(a,b,(i+.07)/n);right=lerp(a,b,(i+.93)/n);z0=3.842;z1=4.058
            pts=[(left[0],left[1],z0),(right[0],right[1],z0),(right[0],right[1],z1),(left[0],left[1],z1)]
            for j in range(4):put(_bar(f'{label} panel border {i:02d}-{j}','fascia_relief',metal,pts[j],pts[(j+1)%4],.012,depth,normal))
            if i%5==1:
                mid=[lerp(pts[j],pts[(j+1)%4],.5) for j in range(4)]
                for j in range(4):put(_bar(f'{label} diamond {i:02d}-{j}','fascia_relief',metal,mid[j],mid[(j+1)%4],.012,depth,normal))
            else:
                for j,k in [(0,2),(1,3)]:put(_bar(f'{label} crossed diagonal {i:02d}-{j}','fascia_relief',metal,pts[j],pts[k],.012,depth,normal))
    relief_run((-x+.050,c.front_y-.022,0),(x-.050,c.front_y-.022,0),c.front_fascia_modules,(0,-1,0),'Front')
    for side in (-1,1):relief_run((side*(x+.022),c.front_y+.052,0),(side*(x+.022),c.back_y-.09,0),c.side_fascia_modules,(side,0,0),f'Side {side}')
    # Glazing panes remain separate transparent solids. All roof divisions are
    # original regularized trials: 3 by 3 is not a recovered fabrication schedule.
    xs=[-xi+i*2*xi/c.roof_x_divisions for i in range(c.roof_x_divisions+1)]
    ys=[fi+i*(bi-fi)/c.roof_y_divisions for i in range(c.roof_y_divisions+1)]
    def glass_z(y):return 4.121+.025*(y-fi)/(bi-fi)
    for i,(xa,xb) in enumerate(zip(xs,xs[1:])):
        for j,(ya,yb) in enumerate(zip(ys,ys[1:])):
            # Small nominal slope is explicitly a drainage trial, not measurement.
            ya+=.033;yb-=.033;xa0=xa+.034;xb0=xb-.034
            v=[(xx,yy,glass_z(yy)+zz) for zz in (-.009,.009) for xx,yy in [(xa0,ya),(xb0,ya),(xb0,yb),(xa0,yb)]]
            f=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
            put(_part(f'Skylight glazing trial cell {i+1}-{j+1}','glazing','glass',v,f))
    for i,xx in enumerate(xs):
        put(_box(f'Skylight longitudinal visible frame {i}','roof_frame',metal,(xx,(fi+bi)/2,4.020),(.078,bi-fi+.03,.195)))
        put(_bar(f'Skylight longitudinal top cap {i}','roof_frame',metal,(xx,fi,glass_z(fi)),(xx,bi,glass_z(bi)),.09,.027))
    for i,yy in enumerate(ys):
        put(_box(f'Skylight transverse visible frame {i}','roof_frame',metal,(0,yy,4.041),(2*xi,.061,.152)))
        put(_box(f'Skylight transverse glazing cap {i}','roof_frame',metal,(0,yy,glass_z(yy)),(2*xi,.085,.029)))
    # Two photograph-visible suspended rods with open-body turnbuckle analogues.
    for side in (-1,1):
        q=(side*c.anchor_x,c.anchor_y-.112,c.anchor_z-.035);p=(side*(x-.14),c.front_y+.18,4.225)
        axis=unit(sub(q,p));u=unit(cross(axis,(1,0,0)));a=lerp(p,q,.46);b=lerp(p,q,.54)
        put(_tube(f'Suspension lower rod {side}','suspension',metal,p,add(a,mul(axis,.024)),.020,12))
        put(_tube(f'Suspension upper rod {side}','suspension',metal,add(b,mul(axis,-.024)),q,.020,12))
        for name,point in [('low',a),('high',b)]:put(_tube(f'Turnbuckle {name} collar {side}','turnbuckle',metal,add(point,mul(axis,-.031)),add(point,mul(axis,.031)),.031,16))
        for sign in (-1,1):put(_tube(f'Open turnbuckle side {side}-{sign}','turnbuckle',metal,add(a,mul(u,sign*.046)),add(b,mul(u,sign*.046)),.014,12))
        for point in (a,b):put(_tube(f'Turnbuckle transverse end {side}-{point[2]:.2f}','turnbuckle',metal,add(point,mul(u,-.047)),add(point,mul(u,.047)),.014,12))
        put(_ring(f'Roof attachment eye {side}','suspension',metal,add(p,(0,-.010,-.010)),(1,0,0),.067,.029,.04,24))
        put(_box(f'Roof attachment foot {side}','suspension',metal,(p[0],p[1],4.167),(.095,.17,.035)))
    # Only the two clearly visible rear knee silhouettes are generalized.
    for side in (-1,1):
        # Curve follows a shallow quadrant from wall bearing up to soffit.
        for j in range(8):
            t0=j*math.pi/16;t1=(j+1)*math.pi/16
            p=(side*3.38,-1.035-.48*math.sin(t0),3.36+.50*(1-math.cos(t0)))
            q=(side*3.38,-1.035-.48*math.sin(t1),3.36+.50*(1-math.cos(t1)))
            put(_bar(f'Rear knee visible curved rib {side}-{j}','bracket',metal,p,q,.075,.052,(1,0,0)))
    # Double perimeter runs, not a full ceiling grid. Number and spacing are trials.
    lamp_points=[]
    for row in (0,1):
        y=c.front_y+.14+row*.27
        for j in range(c.front_bulbs_per_row):lamp_points.append((-x+.16+(2*x-.32)*j/(c.front_bulbs_per_row-1),y))
        for side in (-1,1):
            xx=side*(x-.14-row*.27)
            for j in range(c.side_bulbs_per_row):lamp_points.append((xx,c.front_y+.69+(c.back_y-c.front_y-.90)*j/(c.side_bulbs_per_row-1)))
    for i,(xx,yy) in enumerate(lamp_points):
        put(_tube(f'Lamp ceiling rose {i:03d}','lighting','lamp_metal',(xx,yy,3.844),(xx,yy,3.883),.076,12))
        put(_tube(f'Lamp holder {i:03d}','lighting','lamp_metal',(xx,yy,3.755),(xx,yy,3.849),.046,12))
        put(_sphere(f'Warm globe {i:03d}','lighting','lamp_globe',(xx,yy,3.705),.067,12,6))
    return parts


def create_blender_component(collection,era='2026',controls=DEFAULT_CONTROLS,normal_qa=False):
    """Explicit opt-in Blender adapter. No bpy work happens at module import."""
    import bpy,json
    mats={}
    for key,spec in MATERIALS.items():
        m=bpy.data.materials.new(spec['name']);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value=(*spec['color'],1);p.inputs['Roughness'].default_value=spec['roughness'];p.inputs['Metallic'].default_value=spec['metallic'];p.inputs['Transmission Weight'].default_value=spec['transmission'];p.inputs['IOR'].default_value=1.46
        if spec['emission']:p.inputs['Emission Color'].default_value=(*spec['color'],1);p.inputs['Emission Strength'].default_value=spec['emission']
        m['provenance']='Original constant material; no copyrighted pixels or third-party textures';m['limits']='Approximate appearance, not measured physical properties'
        if normal_qa:
            im=bpy.data.images.get('Canopy original flat tangent QA')
            if im is None:
                im=bpy.data.images.new('Canopy original flat tangent QA',width=4,height=4,alpha=True);im.colorspace_settings.name='Non-Color';im.pixels[:]=[.5,.5,1,1]*16;im.update();im.pack()
            tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;normal=m.node_tree.nodes.new('ShaderNodeNormalMap');m.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        mats[key]=m
    # Batch by material and role: original individual topologies remain disjoint.
    batches={}
    for part in canopy_parts(era,controls):
        key=(part.material,part.role)
        if key not in batches:batches[key]=[[],[],[]]
        vv,ff,uu=batches[key];off=len(vv);vv.extend(part.vertices);ff.extend([tuple(off+i for i in face) for face in part.faces]);uu.extend(part.face_uv_m)
    objects=[]
    for (material,role),(v,f,uvs) in batches.items():
        me=bpy.data.meshes.new(f'{era} north canopy {role}');me.from_pydata(v,[],f);me.update();me.materials.append(mats[material]);uv=me.uv_layers.new(name='Original metric face UV')
        for poly,coords in zip(me.polygons,uvs):
            for li,coord in zip(poly.loop_indices,coords):uv.data[li].uv=coord
        ob=bpy.data.objects.new(me.name,me);collection.objects.link(ob);ob['candidate_only']=True;ob['era']=era;ob['role']=role;ob['revision']='NEC-01';ob['controls']=json.dumps(asdict(controls));ob['dimension_status']='Photo-proportioned trials, no drawing or fabrication dimension claim';objects.append(ob)
    return objects
