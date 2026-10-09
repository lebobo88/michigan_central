"""Evidence-led Michigan Central period reconstruction, Blender 5.2 compatible.
Coordinate system: X = station west, Y = station south, Z = up, meters.
Historical plan dimensions are not a contemporary measured as-built survey.
Geometries are tagged by modeled space and material; inaccessible interiors omitted.
"""
import bpy, math, json, random, sys, argparse, hashlib
from pathlib import Path
from mathutils import Vector
from collections import defaultdict
from math import sin,cos,pi,sqrt
ROOT=Path(__file__).resolve().parents[1]
BUILD_CODE_HASH=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
COMPONENT_HASHES={'repair_glb_tangents.py':hashlib.sha256((ROOT/'scripts/repair_glb_tangents.py').read_bytes()).hexdigest()}
def execute_component(filename):
 path=ROOT/'scripts'/filename;code=path.read_bytes();COMPONENT_HASHES[filename]=hashlib.sha256(code).hexdigest();exec(compile(code,str(path),'exec'),globals())
def load_component_module(filename,key):
 # Keep definitions in their own namespace (and __file__) while hashing the
 # exact code bytes. This prevents candidate helper-name collisions.
 import types
 path=ROOT/'scripts'/filename;code=path.read_bytes();COMPONENT_HASHES[filename]=hashlib.sha256(code).hexdigest()
 module=types.ModuleType(key);module.__file__=str(path);sys.modules[key]=module
 exec(compile(code,str(path),'exec'),module.__dict__);return module

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ap=argparse.ArgumentParser();ap.add_argument('--era',choices=['2017','2026'],default='2026');ap.add_argument('--render',default='exterior');ap.add_argument('--samples',type=int,default=48);ap.add_argument('--width',type=int,default=1600);ap.add_argument('--no-export',action='store_true');ap.add_argument('--no-render',action='store_true');STATION_ARGS=ap.parse_args(args)
ERA=STATION_ARGS.era;AGED=ERA=='2017';SUFFIX='2017' if AGED else 'restored';rng=random.Random(2017)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for x in list(bpy.data.materials):bpy.data.materials.remove(x)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['project']='Michigan Central Station | evidence-led period reconstruction'
scene['build_code_sha256']=BUILD_CODE_HASH
scene['era']=ERA;scene['status']='WORK IN PROGRESS: interpretive reconstruction, not surveyed digital twin'
scene['coordinates']='meters; +X station west, +Y station south, +Z up; ground datum 0'
scene['evidence']='Original 1914 plan dimensions; 2017 dated photographs; 2023-2026 restoration sources. See manifests.'
scene['interior_limit']='Public documented rooms only. Tower fit-outs, basements, hidden service spaces unresolved and omitted.'
M={}
def mat(name,color,rough=.5,metal=0,trans=0,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Transmission Weight'].default_value=trans
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 M[name]=m;return m

def pbr(name,asset,scale):
 m=mat(name,(.5,.5,.5));nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
 for channel in ['basecolor','roughness','normal','height']:
  tex=nt.nodes.new('ShaderNodeTexImage');tex.name=channel;tex.label=f'Original procedural {channel}';tex.image=bpy.data.images.load(str(ROOT/'assets/textures'/asset/(channel+'.png')),check_existing=True)
  if channel!='basecolor':tex.image.colorspace_settings.name='Non-Color'
  if channel=='basecolor':nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
  if channel=='roughness':nt.links.new(tex.outputs['Color'],p.inputs['Roughness'])
  if channel=='normal':
   n=nt.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.45;nt.links.new(tex.outputs['Color'],n.inputs['Color']);nt.links.new(n.outputs['Normal'],p.inputs['Normal'])
  if channel=='height':
   tex.label='16-bit height map supplied; actual displacement disabled at this LOD'
 m['texture_repeat_m']=scale;m['texture_provenance']='Original imagegen color with conservatively inferred PBR support maps; not a site scan' if asset.startswith('generated_') else 'Original procedural material, not site scan';return m
pbr('Exterior Indiana limestone','limestone_'+SUFFIX,4);pbr('Warm Mankato column stone','mankato_2017' if AGED else 'generated_mankato_v1',4 if AGED else 1.5);pbr('Decorative plaster','plaster_'+SUFFIX,12 if AGED else 4);pbr('Guastavino buff tile','aged_vault_unique' if AGED else 'guastavino_restored',1 if AGED else 4)
pbr('Rose Tennessee marble','dust_concrete' if AGED else 'generated_rose_marble_v1',12 if AGED else 1.2);pbr('Pale rose marble','pale_marble',4);pbr('Terrazzo','terrazzo',4);pbr('Exposed masonry','brick_v2_common',1.7);pbr('Concourse buff brick','brick_v2_buff',1.7);pbr('Tower buff brick','brick_v2_buff',1.7);pbr('Lawn texture','grass',4);pbr('Weathered concrete','dust_concrete',4)
pbr('Grand Hall floor assembly','great_hall_floor_2017' if AGED else 'great_hall_floor_2026',1)
if AGED:pbr('Mixed 2017 hall backing','mixed_hall_backing_2017',6)
if not AGED:
 pbr('Hall scored decorative plaster','hall_scored_plaster',4.8)
 pbr('Historic walnut herringbone','generated_walnut_herringbone_v1',.65)
mat('Dark bronze',(.075,.057,.039),.35,.78);mat('Window cast iron',(.24,.27,.24),.32,.58);mat('Roof dark copper',(.035,.044,.040),.62,.45);mat('Roof steel',(.08,.075,.069),.5,.75)
mat('Glass clear',(.88,.94,.97),.008,0,.98);mat('Glass tower dark',(.11,.17,.18),.2,.35,.12);mat('Glass tower blue',(.24,.30,.31),.21,.4,.1)
mat('Warm lamp glass',(1,.76,.41),.24,0,0,7);mat('Dark void',(.015,.016,.014),.96);mat('Wood walnut',(.045,.018,.008),.38)
mat('Lawn',(.065,.105,.028),.93);mat('Fine gravel',(.26,.235,.195),.94);mat('Foliage',(.045,.085,.016),.96);mat('Tree bark',(.18,.105,.065),.93)
mat('Distress umber',(.085,.067,.037),.97);mat('Distress plaster loss',(.29,.21,.12),.99);mat('Interpretive graffiti blue',(.018,.028,.064),.97);mat('Interpretive graffiti ochre',(.14,.078,.017),.97)
execute_component('surface_materials_v2.py')
B={}; GROUP='00 SITE'
# Revision14 promotes separately inspected original details and the independently
# registered public lobby. Legacy code remains recoverable in revision13 snapshots.
NORTH_ARCH_ORNAMENT_ENABLED=True
ARCH_DETAIL=load_component_module('candidates/north_arch_ornament.py','station_arch_detail')
CAPITAL_DETAIL=load_component_module('candidates/exterior_capital_detail.py','station_capital_detail')
CANOPY_DETAIL=load_component_module('candidates/north_entry_canopy_detail.py','station_canopy_detail')
ELEVATOR_DETAIL=load_component_module('candidates/elevator_lobby_detail.py','station_elevator_detail')
GLASS_RULES=load_component_module('candidates/glass_shell_rules.py','station_glass_shell_rules')
PORTABLE_MATERIALS=load_component_module('candidates/material_portability.py','station_portable_materials')
CAPITAL_DETAIL_PLACEMENTS=[]

def addmesh(v,f,material,name=None,uv=None,face_uv=None):
 if globals().get('SWAP_XY',False):v=[(p[1],p[0],p[2]) for p in v]
 key=(GROUP,material,name or material)
 if key not in B:B[key]=[[],[],[]]
 vv,ff,uu=B[key];n=len(vv);vv.extend(v);ff.extend([tuple(n+i for i in face) for face in f]);uu.extend(face_uv if face_uv is not None else [[uv[i] for i in face] if uv is not None else None for face in f])

def box(c,s,m,name=None):
 if any(k<0 for k in s):raise ValueError('Negative box dimensions: '+str((name,c,s)))
 if any(k<1e-7 for k in s):return
 x,y,z=c;u,v,w=[k/2 for k in s]
 addmesh([(x+dx*u,y+dy*v,z+dz*w) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m,name)

def beam(p,q,r,m,name=None,n=8):
 p,q=Vector(p),Vector(q)
 if (q-p).length<1e-7:return
 d=(q-p).normalized();axis=Vector((0,0,1)) if abs(d.z)<.95 else Vector((1,0,0));u=d.cross(axis).normalized();v=d.cross(u).normalized();verts=[]
 for c in [p,q]:
  for i in range(n):verts.append(tuple(c+r*(u*cos(2*pi*i/n)+v*sin(2*pi*i/n))))
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 addmesh(verts,faces,m,name)

def lathe(c,profile,m,name=None,n=32,flutes=0,flute_depth=0.0,flute_z0=0.0,flute_z1=0.0):
 # A true single-vertex pole avoids collapsed quads and zero-area export triangles.
 x,y,z=c;verts=[];uv=[];rings=[];faces=[]
 for r,h in profile:
  if abs(r)<1e-8:
   rings.append([len(verts)]);verts.append((x,y,z+h));uv.append((0,z+h))
  else:
   ids=[]
   for i in range(n+1):
    ids.append(len(verts));theta=i*2*pi/n;rr=r
    if flutes:
     fade=min(1,max(0,(h-flute_z0)/.22))*min(1,max(0,(flute_z1-h)/.22))
     rr-=flute_depth*fade*max(0,cos(flutes*theta))**.60
    verts.append((x+rr*cos(theta),y+rr*sin(theta),z+h));uv.append((i/n*2*pi*r,z+h))
   rings.append(ids)
 for a0,b0 in zip(rings,rings[1:]):
  if len(a0)==1 and len(b0)==1:continue
  for i in range(n):
   if len(a0)==1:faces.append((a0[0],b0[i+1],b0[i]))
   elif len(b0)==1:faces.append((a0[i],a0[i+1],b0[0]))
   else:faces.append((a0[i],a0[i+1],b0[i+1],b0[i]))
 capfaces=[]
 if profile[0]!=profile[-1]:
  if len(rings[0])>1:capfaces.append(len(faces));faces.append(tuple(reversed(rings[0][:-1])))
  if len(rings[-1])>1:capfaces.append(len(faces));faces.append(tuple(rings[-1][:-1]))
 uvfaces=[[uv[i] for i in f] for f in faces]
 for fi,face in enumerate(faces):
  if fi in capfaces or max(verts[i][2] for i in face)-min(verts[i][2] for i in face)<1e-8:uvfaces[fi]=[(verts[i][0],verts[i][1]) for i in face]
 addmesh(verts,faces,m,name,face_uv=uvfaces)

def ring(c,r,t,m,name=None,n=40):
 x,y,z=c;lathe(c,[(r-t,0),(r-t,t),(r+t,t),(r+t,0),(r-t,0)],m,name,n)

def arch(cx,y,z,w,rise,thick,depth,m,name=None,n=40,orientation='front'):
 # Elliptical masonry arch band, vertical x-z plane; orientation side rotates into y-z.
 v=[]
 for yy in [y-depth/2,y+depth/2]:
  for radius,height in [(w/2,rise),(w/2+thick,rise+thick)]:
   for i in range(n+1):
    t=pi*i/n;p=(cx+radius*cos(t),yy,z+height*sin(t));v.append(p if orientation=='front' else (yy,p[0],p[2]))
 f=[];s=n+1
 for i in range(n):
  f.extend([(i,i+1,s+i+1,s+i),(2*s+i,3*s+i,3*s+i+1,2*s+i+1),(i,2*s+i,2*s+i+1,i+1),(s+i,s+i+1,3*s+i+1,3*s+i)])
 f.extend([(0,s,3*s,2*s),(n,2*s+n,3*s+n,s+n)])
 uv=[]
 for yy in [y-depth/2,y+depth/2]:
  for radius,height in [(w/2,rise),(w/2+thick,rise+thick)]:
   for i in range(n+1):uv.append((i/n*pi*(radius+height)/2,yy))
 uvfaces=[]
 for fi,face in enumerate(f):
  if fi>=4*n:
   uvfaces.append([(v[i][0],v[i][1]) for i in face])
  elif fi%4 in [0,1]:
   horizontal=0 if orientation=='front' else 1
   uvfaces.append([(v[i][horizontal],v[i][2]) for i in face])
  else:uvfaces.append([uv[i] for i in face])
 addmesh(v,f,m,name,face_uv=uvfaces)

def opening(cx,y,bottom,width,height,m='Window cast iron',glass='Glass clear',name='arched window',bars=10,hstep=.83,fanlight=True):
 radius=width/2;spring=bottom+height-radius
 verts=[(cx-radius,y,bottom),(cx+radius,y,bottom),(cx+radius,y,spring)]+[(cx+radius*cos(pi*i/40),y,spring+radius*sin(pi*i/40)) for i in range(1,41)]
 addmesh(verts,[tuple(range(len(verts)))],glass,name+' glazing')
 for xx in [-radius,radius]:box((cx+xx,y-.05,(bottom+spring)/2),(.11,.16,spring-bottom),m,name+' frame')
 arch(cx,y,spring,width,radius,.115,.17,m,name+' arch')
 for i in range(1,bars):
  dx=-radius+width*i/bars;top=spring+sqrt(max(0,radius*radius-dx*dx));box((cx+dx,y-.085,(bottom+top)/2),(.048,.14,top-bottom),m,name+' mullions')
 for zz in [bottom+i*hstep for i in range(1,int(height/hstep)+1)]:
  if zz>bottom+height:continue
  half=radius if zz<=spring else sqrt(max(0,radius*radius-(zz-spring)**2));box((cx,y-.09,zz),(half*2,.14,.045),m,name+' transoms')
 for i in (range(1,9) if fanlight else []):
  t=pi*i/9;beam((cx,y-.10,spring),(cx+radius*cos(t),y-.10,spring+radius*sin(t)),.026,m,name+' fanlight')

def wall_with_arch(cx,y,width,height,opwidth,opheight,base=0,matname='Exterior Indiana limestone',depth=1.05,bottomfill=True):
 rad=opwidth/2;spring=base+opheight-rad
 for sign in ([-1,1] if width>opwidth+.00001 else []):box((cx+sign*(width+opwidth)/4,y,height/2),((width-opwidth)/2,depth,height),matname)
 n=30;v=[];f=[]
 for i in range(n+1):
  xx=-rad+opwidth*i/n;bot=spring+sqrt(max(0,rad*rad-xx*xx))
  v.extend([(cx+xx,y-depth/2,bot),(cx+xx,y-depth/2,height),(cx+xx,y+depth/2,bot),(cx+xx,y+depth/2,height)])
 for i in range(n):k=4*i;f.extend([(k,k+4,k+5,k+1),(k+2,k+3,k+7,k+6),(k,k+2,k+6,k+4)])
 addmesh(v,f,matname)
 if base>0 and bottomfill:box((cx,y,base/2),(opwidth,depth,base),matname)

def wall_x_portals(x,ya,yb,height,portals,m,name,depth=.6):
 cursor=ya
 for center,width,top in sorted(portals):
  a=max(ya,center-width/2);b=min(yb,center+width/2)
  if a>cursor:box((x,(cursor+a)/2,height/2),(depth,a-cursor,height),m,name)
  if b>a and height>top:box((x,(a+b)/2,(height+top)/2),(depth,b-a,height-top),m,name+' headers')
  cursor=max(cursor,b)
 if cursor<yb:box((x,(cursor+yb)/2,height/2),(depth,yb-cursor,height),m,name)

def wall_y_portals(y,xa,xb,height,portals,m,name,depth=.6):
 cursor=xa
 for center,width,top in sorted(portals):
  a=max(xa,center-width/2);b=min(xb,center+width/2)
  if a>cursor:box(((cursor+a)/2,y,height/2),(a-cursor,depth,height),m,name)
  if b>a and height>top:box(((a+b)/2,y,(height+top)/2),(b-a,depth,height-top),m,name+' headers')
  cursor=max(cursor,b)
 if cursor<xb:box(((cursor+xb)/2,y,height/2),(xb-cursor,depth,height),m,name)

def cornice(cx,cy,width,depth,z,m='Exterior Indiana limestone',name='layered cornice'):
 for dz,extra,h in [(0,0,.20),(.20,.22,.14),(.34,.48,.18),(.52,.63,.13),(.65,.75,.16)]:box((cx,cy,z+dz),(width+extra,depth+extra,h),m,name)

def pediment(cx,y,z,width,rise,m='Exterior Indiana limestone',north_monumental=False):
 v=[(cx-width/2,y,z),(cx+width/2,y,z),(cx,y,z+rise),(cx-width/2,y+.7,z),(cx+width/2,y+.7,z),(cx,y+.7,z+rise)]
 addmesh(v,[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(0,2,5,3)],m,'pediment tympanum')
 for o in [0,.24,.43]:
  beam((cx-width/2-o,y-.05,z+o*.3),(cx,y-.05,z+rise+o),.12,m,'pediment raking molding',8);beam((cx,y-.05,z+rise+o),(cx+width/2+o,y-.05,z+o*.3),.12,m,'pediment raking molding',8)
 for xx in range(int(width*2)):
  xp=cx-width/2+xx*.5
  if not(north_monumental and NORTH_ARCH_ORNAMENT_ENABLED and ARCH_DETAIL.generic_dentil_in_arch_bay('monumental_pediment',xp,y-.18,z-.28)):
   box((xp,y-.18,z-.28),(.18,.28,.28),m,'pediment dentils')
 # Original simplified tympanum foliage only on the monumental exterior pediments.
 if width>8:
  for side in [-1,1]:
   for i in range(7):
    xx=cx+side*(.8+i*.74);zz=z+.5+(1-i/7)*.5
    lathe((xx,y-.24,zz),[(.12,0),(.28,.18),(.13,.38)],m,'interpreted foliate relief',8)


def column(x,y,z,h,r,corinthian=False,m='Warm Mankato column stone',paired=False):
 # Interior h is the base-to-abacus profile control. Exterior h is nominal:
 # separate z, plinth and abacus offsets define the actual envelope. Profiles are photo-led;
 # individual molding dimensions are photo-proportioned, not a measured carving survey.
 if corinthian or h<7:
  prof=[(r*1.3,0),(r*1.3,.22),(r*1.13,.25),(r*1.13,.36),(r,.46),(r*.94,.58),(r*.94,h*.2),(r*.86,h*.72),(r*.83,h-.62),(r*.96,h-.52),(r*1.02,h-.45),(r*1.07,h-.26),(r*1.18,h-.20),(r*1.18,h)]
  if corinthian:
   # Source photographs show fluted monumental exterior shafts.24 channels and
   # their depth are a qualified classical-profile trial, not a carving survey.
   oldprof=prof;zs=sorted({zz for rr,zz in oldprof}|{.57,.79,h-.90,h-.65})
   def radius_at(zz):
    for (ra,za),(rb,zb) in zip(oldprof,oldprof[1:]):
     if za<=zz<=zb:return ra+(rb-ra)*(zz-za)/(zb-za)
    return oldprof[-1][0]
   prof=[(radius_at(zz),zz) for zz in zs]
   lathe((x,y,z),prof,m,'exterior fluted column shafts and torus bases',192,flutes=24,flute_depth=r*.055,flute_z0=.57,flute_z1=h-.65)
  else:lathe((x,y,z),prof,m,'exterior column shafts and torus bases',48)
  # Ground the existing base at the common local foundation datum. The top,
  # shaft, capital and published nominal h control are unchanged. Paving covers
  # the bottom25-35mm; this closes an unintended~0.30m model air gap.
  plinth_bottom=0.0 if corinthian else z-.22;plinth_top=z+.08
  box((x,y,(plinth_bottom+plinth_top)/2),(r*2.8,r*2.8,plinth_top-plinth_bottom),m,'exterior column plinths');box((x,y,z+h+.06),(r*2.8,r*2.8,.22),m,'exterior capital abacus')
  if corinthian:CAPITAL_DETAIL_PLACEMENTS.append((GROUP,x,y,z,h,r,m))
 else:
  if not paired:box((x,y,z+.20),(r*2.90,r*2.90,.40),m,'interior column squared plinths')
  # Lower torus, concave scotia, upper torus, shaft fillets and tapered monolith.
  prof=[(r*1.27,.40),(r*1.31,.44),(r*1.34,.51),(r*1.31,.59),(r*1.22,.65),
        (r*1.09,.68),(r*1.01,.73),(r*.99,.79),(r*1.02,.85),(r*1.15,.89),
        (r*1.22,.94),(r*1.24,1.00),(r*1.20,1.06),(r*1.09,1.12),
        (r*1.02,1.13),(r*1.02,1.20),(r*.95,1.25),(r*.945,h*.25),
        (r*.89,h*.58),(r*.84,h-.75),(r*.86,h-.72),(r*.88,h-.68),
        (r*.99,h-.65),(r*1.04,h-.61),(r*1.04,h-.56),(r*.96,h-.52),
        (r*1.00,h-.46),(r*1.13,h-.39),(r*1.23,h-.31),(r*1.25,h-.25),
        (r*1.17,h-.21),(r*1.17,h-.18)]
  if paired:
   # Close pairs have a photographed shared pedestal; keep their flared moldings physically distinct.
   prof=[(r*.94+(rr-r*.94)*.775 if (hh<=1.20 or hh>=h-.70) and rr>r*.94 else rr,hh) for rr,hh in prof]
  lathe((x,y,z),prof,m,'interior column shafts double torus scotia and capital profiles',64)
  cap_width=r*(2.45 if paired else 2.86)
  box((x,y,z+h-.09),(cap_width,cap_width,.18),m,'interior capital abacus')

# SITE ----------------------------------------------------------
GROUP='00 SITE | neutral render context; dated landscape separate'
mat('Neutral context ground',(.19,.20,.185),.98)
for x0,x1,y0g,y1g in [(-4000,-12.8,-3982,4018),(12.8,4000,-3982,4018),(-12.8,12.8,-3982,74.5),(-12.8,12.8,88.7,4018)]:
 box(((x0+x1)/2,(y0g+y1g)/2,-.62),(x1-x0,y1g-y0g,1),'Neutral context ground','landscape context')
# Era-specific documented landscape is provided by north_plaza.py for2026.
# Historical2017grounds remain an explicit evidence/modeling gap.

# TERMINAL EXTERIOR ---------------------------------------------
GROUP='01 EXTERIOR | measured historic envelope'
stone='Exterior Indiana limestone';north_field_stone='2017 aged limestone wall fields' if AGED else stone;hallw=71.0184;halfd=31.6992;allw=105.2576;alld=79.8576;bay=20.0
for x0,x1,ya,yb in [(-allw/2,-12.8,39.8-alld/2,39.8+alld/2),(12.8,allw/2,39.8-alld/2,39.8+alld/2),(-12.8,12.8,39.8-alld/2,74.5)]:
 box(((x0+x1)/2,(ya+yb)/2,-.35),(x1-x0,yb-ya,.6),'Weathered concrete','terminal foundation datum')
# North facade: FOUR small arches and THREE monumental arches, corroborated in a July2026 CC0 photograph.
# Build a single non-overlapping perforated wall, not glass decals over closed masonry.
front_openings=[(-32.75,2.4384,6.096,.8),(-20,6.4008,12.192,1.3),(-10,2.4384,6.096,.8),(0,6.4008,9.172,4.32),(10,2.4384,6.096,.8),(20,6.4008,12.192,1.3),(32.75,2.4384,6.096,.8)]
cursor=-hallw/2
for cx,ww,hh,bb in front_openings:
 left=cx-ww/2;right=cx+ww/2
 if left>cursor:box(((cursor+left)/2,0,7.8),(left-cursor,1.05,15.6),north_field_stone,'north facade continuous stone piers')
 wall_with_arch(cx,0,ww,15.6,ww,hh,base=bb,matname=north_field_stone,bottomfill=(cx!=0))
 if ww>5:
  opening(cx,-.20,bb,ww,hh,name='north monumental window',bars=13,fanlight=False)
  if not NORTH_ARCH_ORNAMENT_ENABLED:arch(cx,-.64,bb+hh-ww/2,ww,ww/2,.62,1.12,stone,'monumental window stone arch')
  for sign in [-1,1]:box((cx+sign*(ww/2+.28),-.5,5.8),(.52,1.1,9.0),stone,'arch jambs')
  pediment(cx,-1.25,15.55,18.8,3.3,north_monumental=True)
 else:
  opening(cx,-.59,bb,ww,hh,name='north secondary arched window',bars=4)
  arch(cx,-.60,bb+hh-ww/2,ww,ww/2,.24,.28,stone,'small front archivolt')
 cursor=right
if cursor<hallw/2:box(((cursor+hallw/2)/2,0,7.8),(hallw/2-cursor,1.05,15.6),north_field_stone,'north facade end pier')
# fourteen forty-foot exterior columns
for xx in [-34.4,-27.0,-24.3,-15.7,-13.0,-7.0,-4.3,4.3,7.0,13.0,15.7,24.3,27.0,34.4]:column(xx,-1.18,.55,12.192,.56,True,stone)
# Photo-supported interrupted projecting entablature: the lower stack
# terminates/returns beside the three monumental outer archivolts. A higher
# recessed connection clears them. No perspective-derived Z hierarchy asserted.
_north_arch_half=6.4008/2+.62;_north_clearance=.015
_north_arch_gaps=[(c-_north_arch_half-_north_clearance,c+_north_arch_half+_north_clearance) for c in [-20,0,20]]
_north_spans=[];_cursor=-37.0
for _left,_right in _north_arch_gaps:
 _north_spans.append((_cursor,_left));_cursor=_right
_north_spans.append((_cursor,37.0))
for _left,_right in _north_spans:
 _cx=(_left+_right)/2;_width=_right-_left
 box((_cx,-.6,(12.912+13.425)/2),(_width,2.1,13.425-12.912),stone,'north interrupted entablature bearing architrave')
 box((_cx,-.6,14.2),(_width,2.1,.25),stone,'north interrupted entablature upper molding')
 box((_cx,-.6,15.0),(_width,2.1,.25),stone,'north upper entablature projecting connection')
 box((_cx,-.55,14.86),(_width,2.0,.24),stone,'north upper cornice dentil backing fascia')
for _left,_right in _north_arch_gaps:
 _cx=(_left+_right)/2;_width=_right-_left
 box((_cx,-.475,15.0),(_width,1.85,.25),stone,'north upper entablature recessed arch-bay connection')
 box((_cx,-.425,14.86),(_width,1.75,.24),stone,'north recessed cornice dentil backing fascia')
for xx in [i*.5-36.5 for i in range(147)]:
 _recess=any(a<xx<b for a,b in _north_arch_gaps)
 _dentil_y=-1.40 if _recess else -1.65
 if not(NORTH_ARCH_ORNAMENT_ENABLED and ARCH_DETAIL.generic_dentil_in_arch_bay('north_entablature',xx,_dentil_y,14.62)):
  box((xx,_dentil_y,14.62),(.20,.28,.28),stone,'north entablature dentils')
scene['north_entablature_controls']=json.dumps(dict(outer_arch_half_span_m=_north_arch_half,construction_clearance_each_side_m=_north_clearance,gaps_x_m=_north_arch_gaps,bearing_spans_x_m=_north_spans,low_bearing_bottom_z_m=12.912,existing_abacus_top_z_m=12.912,upper_connection_recess_m=.25,source='Architect Key Facts2024 p2; July2026 front photo; exactMay2017 entry image; see north_vertical_qa',limits='Return depth, fascia and molding profiles are original geometric trials. No measured height convention or exact carved profile is claimed. Glass/window heights and nominal column h are unchanged.'))
if NORTH_ARCH_ORNAMENT_ENABLED:
 ARCH_DETAIL.build_north_arch_ornament(addmesh)
 scene['north_arch_ornament_controls']=json.dumps(ARCH_DETAIL.NORTH_ARCH_ORNAMENT_CONTROLS)
# side wings, approximately located by 1914 plan
for side in [-1,1]:
 x=side*(hallw/2+(allw-hallw)/4);w=(allw-hallw)/2
 for j in range(3):
  cx=x+(j-1)*4.35;wall_with_arch(cx,4.4,4.35,10.7,2.4384,6.2484,base=1.0,matname=north_field_stone)
  opening(cx,3.79,1.0,2.4384,6.2484,name='north wing wood window',bars=2 if (side<0 and not AGED) else 4,hstep=1.35 if (side<0 and not AGED) else .83,fanlight=not(side<0 and not AGED))
 for sign in [-1,1]:
  outer=w/2;inner=6.525;box((x+sign*(outer+inner)/2,4.4,5.35),(outer-inner,1.05,10.7),north_field_stone,'north side-wing end infill')
 cornice(x,16.3,w,23.8,10.5)
 # Shared side-wall glazing; north/east positions use raster-registered plan controls.
 if side<0:
  centers=[9.98,13.94,17.94,21.94,25.94,30.13,34.09]
  cells=[4.4]+[(a+b)/2 for a,b in zip(centers,centers[1:])]+[38.13]
 else:
  centers=[6.84,10.34,13.69,17.81,21.55,26.26,30.79,34.45,38.18,41.98,45.71,49.45]
  cells=[4.4]+[(a+b)/2 for a,b in zip(centers,centers[1:])]+[51.45]
 SWAP_XY=True
 for k,yy in enumerate(centers):
  # Build just the opening envelope, then solid infill to the adjacent midpoint.
  ww=2.4384;left=yy-ww/2;right=yy+ww/2
  wall_with_arch(yy,side*allw/2,ww,10.4,ww,6.2484,base=1.0,depth=1.0)
  for a0,b0 in [(cells[k],left),(right,cells[k+1])]:
   if b0>a0:box(((a0+b0)/2,side*allw/2,5.2),(b0-a0,1.0,10.4),stone,'side perimeter continuous stone piers')
  opening(yy,side*allw/2+(-.56 if side<0 else .56),1.0,ww,6.2484,name='side wood arched window',bars=2 if (side<0 and k<3 and not AGED) else 4,hstep=1.35 if (side<0 and k<3 and not AGED) else .83,fanlight=not(side<0 and k<3 and not AGED))
 SWAP_XY=False
 if side==-1:
  # Actual HNS doorway void, distinguished from the solid jamb. Registered to +/-0.3–0.6m.
  SWAP_XY=True
  wall_with_arch(40.07,-allw/2,3.88,10.4,3.88,7.2484,base=0,depth=1.0)
  opening(40.07,-allw/2-.56,4.60,3.88,2.6484,name='east main entrance arched transom',bars=4,hstep=1.1,fanlight=False)
  # Original1914 eight southern apertures; datedAug2025 photo confirms three adjacent exit doors.
  # One near-entry window is tree-obscured in2025, retained from historic-plan evidence.
  south=[46.50,50.39,54.27,58.83,62.80,66.98,70.79,75.13]
  edges=[42.01]+[(aa+bb)/2 for aa,bb in zip(south,south[1:])]+[79.8576]
  for k,yy in enumerate(south):
   ww=2.4384;door=k in [3,4,5];bottom=0 if door else 1.0;hh=7.2484-bottom
   wall_with_arch(yy,-allw/2,ww,10.4,ww,hh,base=bottom,depth=1.0)
   for aa,bb in [(edges[k],yy-ww/2),(yy+ww/2,edges[k+1])]:
    if bb>aa:box(((aa+bb)/2,-allw/2,5.2),(bb-aa,1.0,10.4),stone,'east southern historical aperture piers')
   if door:
    opening(yy,-allw/2-.56,3.0,ww,4.2484,name='east exit door arched transoms',bars=3,hstep=1.35,fanlight=False)
   else:opening(yy,-allw/2-.56,bottom,ww,hh,name='east southern wood windows',bars=3,hstep=1.35,fanlight=False)
  SWAP_XY=False
 else:
  box((side*allw/2,(51.45+79.8576)/2,5.2),(1.0,79.8576-51.45,10.4),stone,'west rear carriage-adjacent perimeter')
# Hipped standing-seam hall roof, visible in the owner's2025 venue axon and exterior photos.
# Ridge elevation remains photo-proportioned; historical height datum conflict stays in ledger.
# Provisional roof profile:22.0m ridge clears the photo-compatible17.2m side-crown trial.
# Historical76ft assertion remains separate; neither value is a contemporary survey.
eave=16.1;ridge=22.0;rx=28.0
verts=[(-37,-1,eave),(37,-1,eave),(37,33,eave),(-37,33,eave),(-rx,16,ridge),(rx,16,ridge)]
addmesh(verts,[(0,1,5,4),(3,4,5,2),(0,4,3),(1,2,5)],'Roof dark copper','hall hipped copper roof')
for i in range(150):
 x=-37+i*.5;fraction=1 if abs(x)<=rx else (37-abs(x))/(37-rx);z=eave+(ridge-eave)*fraction+.02
 yfront=-1+17*fraction;yback=33-17*fraction
 beam((x,-1,eave+.02),(x,yfront,z),.018,'Roof dark copper','standing roof seams')
 beam((x,33,eave+.02),(x,yback,z),.018,'Roof dark copper','standing roof seams')
beam((-rx,16,ridge+.05),(rx,16,ridge+.05),.08,'Roof dark copper','hall roof ridge cap')
for side in [-1,1]:
 for j in range(36):
  yy=-1+j*34/35;beam((side*37,yy,eave+.03),(side*rx,16,ridge+.03),.016,'Roof dark copper','hip roof seams')
# Detailed mixed-glazing canopy / retained 2017 hardware is added after finalization.

execute_component('north_entry.py')
NORTH_ENTRY_CONTROLS.pop('candidate_status',None)
NORTH_ENTRY_CONTROLS['integration_status']='Integrated source-informed WIP; see actual full-scene checkpoint validation'
scene['north_entry_controls']=json.dumps(NORTH_ENTRY_CONTROLS)

if AGED:
 # Photo-proportioned protective mesh. The native2017 crop shows~8px cells
 # against~600px clear width; nominal6.4008m glass gives an inferred~0.085m pitch.
 # Wire diameter is an artistic4mm trial, not recoverable from blurred pixels.
 # Clip each straight wire analytically to the rectangle/semicircle envelope;
 # one closed beam avoids redundant segment caps and preserves the arch silhouette.
 def north_mesh_endpoints(slope,intercept,bottom,radius=3.2004,spring=10.2916):
  pts=[]
  for xx in [-radius,radius]:
   zz=slope*xx+intercept
   if bottom-1e-8<=zz<=spring+1e-8:pts.append((xx,zz))
  xx=(bottom-intercept)/slope
  if -radius-1e-8<=xx<=radius+1e-8:pts.append((xx,bottom))
  aa=1+slope*slope;bb=2*slope*(intercept-spring);cc=(intercept-spring)**2-radius*radius;disc=bb*bb-4*aa*cc
  if disc>=0:
   for xx in [(-bb-sqrt(disc))/(2*aa),(-bb+sqrt(disc))/(2*aa)]:
    zz=slope*xx+intercept
    if zz>=spring-1e-8 and -radius-1e-8<=xx<=radius+1e-8:pts.append((xx,zz))
  unique=[]
  for q in sorted(pts):
   if not any(math.dist(q,p)<1e-7 for p in unique):unique.append(q)
  return (unique[0],unique[-1]) if len(unique)>=2 and math.dist(unique[0],unique[-1])>.01 else None
 for center in [-bay,0,bay]:
  for direction in [-1,1]:
   for i in range(260):
    ends=north_mesh_endpoints(direction,i*.085-4,4.32 if center==0 else 1.3)
    if ends:
     p,q=ends;beam((center+p[0],-.47,p[1]),(center+q[0],-.47,q[1]),.002,'Roof steel','2017 protective diamond mesh',6)
 scene['north_2017_mesh_controls']=json.dumps(dict(pitch_m=.085,inferred_pitch_range_m=[.07,.105],wire_diameter_m=.004,source='ExactMay2017 HistoricDetroit exterior p12, native-pixel pattern study',limits='Photo-relative density; wire diameter, tension, weave and small losses unmeasured. Original geometric approximation; no photo pixels.'))

# TOWER ---------------------------------------------------------
execute_component('tower_facade_v2.py')
# Four third-level corner terraces: approximate footprints, documented positions and stone balustrades.
GROUP='10 TERRACES | publicly documented roof interfaces'
for side in [-1,1]:
 cx=side*(hallw/2+(allw-hallw)/4);ww=(allw-hallw)/2
 for ya,yb in [(4.4,27.1),(60.8,79.3)]:
  cyy=(ya+yb)/2;dd=yb-ya
  box((cx,cyy,11.05),(ww-.8,dd-.4,.24),'Weathered concrete','third-level terrace surface')
  if ya>50:cornice(cx,cyy,ww,dd,10.5)
  # Exposed front/back edge, with solid end dies and turned balusters in intermediate runs.
  edge=ya if ya<50 else yb
  box((cx,edge,11.35),(ww,.55,.35),stone,'terrace balustrade plinth')
  box((cx,edge,12.35),(ww,.65,.23),stone,'terrace balustrade coping')
  for k in range(int(ww/.42)):
   xx=cx-ww/2+.35+k*.42
   lathe((xx,edge,11.52),[(.065,0),(.095,.12),(.075,.25),(.04,.36),(.078,.52),(.06,.72)],stone,'terrace turned stone balusters',16)
  for xx in [cx-ww/2,cx+ww/2,cx]:box((xx,edge,11.85),(.65,.67,1.3),stone,'terrace stone pedestal dies')
  # Outboard return railing along the station's side elevation.
  xx=side*(allw/2-.20)
  box((xx,cyy,11.35),(.55,dd,.35),stone,'terrace return plinth')
  box((xx,cyy,12.35),(.65,dd,.23),stone,'terrace return coping')
  for k in range(int(dd/.42)):
   yy=ya+.30+k*.42;lathe((xx,yy,11.52),[(.065,0),(.095,.12),(.075,.25),(.04,.36),(.078,.52),(.06,.72)],stone,'terrace return balusters',16)
# MAIN WAITING ROOM / GREAT HALL ------------------------------
GROUP='03 GREAT HALL | three sail vaults and colonnades'
FLOOR='Rose Tennessee marble';PL='Decorative plaster';COL='Warm Mankato column stone';spring=9.55;apex=18.8976;y0=3.9;y1=27.7;ym=(y0+y1)/2
HALL_BOUNDARY_RISE=17.20-spring
HALL_WALL_PLASTER=PL if AGED else 'Hall scored decorative plaster'
# Side-crown17.20m is an explicit photo-compatible trial, not a measured datum.
def hall_sail_z(vx,vy):
 sx=sqrt(max(0,1-vx*vx));sy=sqrt(max(0,1-vy*vy))
 return spring+HALL_BOUNDARY_RISE*(sx+sy)+(apex-spring-2*HALL_BOUNDARY_RISE)*sx*sy
box((0,15.85,-.05),(hallw,31.7,.22),'Grand Hall floor assembly','historic rose marble floor')
# Restored flush diagonal marble and terrazzo inlays are in a unique full-room PBR assembly.
# Lower south alcoves and north flanking ceiling fragments.
execute_component('hall_alcoves.py')
for xx in [-hallw/2,hallw/2]:
 portals=[(16.2,2.4,3.65)] if xx<0 else [(10.1,2.4,3.65),(22.2,2.4,3.65)]
 wall_x_portals(xx,0,31.7,8.6,portals,'Mixed 2017 hall backing' if AGED else HALL_WALL_PLASTER,'hall end walls with documented portals',1.2)
 # Upper end arch rotates to y-z plane.
 arch(ym,xx,9.45,21.5,7.0,1.1,1.4,PL,'end wall archivolt',48,'side')
# 16 hall + 12 ticket-lobby columns. Raster-digitized1914 plan, not surveyed coordinates.
for x in [-24.2,-15.7,-4.2,4.2,15.7,24.2]:
 for y in [y0,y1]:column(x,y,.06,8.382,.62,False,COL)
for xx in [-31.8,31.8]:
 for yy in [11.3,20.3]:column(xx,yy,.06,8.382,.62,False,COL)
for x in [-10,10]:
 for y in [y0,y1]:
  face=1 if y<15 else -1;pm='Mixed 2017 hall backing' if AGED else HALL_WALL_PLASTER
  # Visible telephone/closet door recess. Unknown continuation is not invented.
  for dx in [-.975,.975]:box((x+dx,y,4.775),(.45,2.4,9.55),pm,'major arch pier door jamb cores')
  box((x,y,6.30),(1.50,2.4,6.50),pm,'major arch pier upper core')
  box((x,y-face*.35,1.525),(1.50,1.70,3.05),pm,'major arch pier recess backing')
  if AGED:
   # Surviving pale scored cladding is documented on lateral pier faces; its exact loss edge is inferred.
   for sx in [-1,1]:
    for row in range(18):
     zz=.25+row*.49
     for j in range(5):
      yy=y-1.17+(j+.5)*2.34/5
      field=sin(yy*1.7+zz*.7+x*.24)+.38*cos(yy*3.9-zz*1.1)
      if field<-.10:continue
      box((x+sx*1.213,yy,zz),(.045,.452,.471),PL,'2017 surviving scored pier cladding | photo-informed')
   # Original irregular plaster skin on documented masonry backing; not an exact loss survey.
   nu=15;nz=60;front=y+face*1.202
   for iz in range(nz):
    for ix in range(nu):
     ux=-1.2+(ix+.5)*2.4/nu;zz=(iz+.5)*9.55/nz
     if abs(ux)<.77 and zz<3.12:continue
     field=sin(ux*2.1+zz*1.4+x*.31)+.47*cos(ux*5.2-zz*.8+x*.7)
     if field<-.35 and zz<8.9:continue
     verts=[]
     for depth in [0,.048]:
      for ii,jj in [(ix,iz),(ix+1,iz),(ix+1,iz+1),(ix,iz+1)]:
       uu=-1.2+ii*2.4/nu;vz=jj*9.55/nz
       if ii not in [0,nu]:uu+=.025*sin(ii*13.3+jj*7.1+x)
       if jj not in [0,nz]:vz+=.025*cos(ii*8.1+jj*12.2+x)
       verts.append((x+uu,front+face*depth,vz))
     addmesh(verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],PL,'2017 fractured plaster skin | interpreted loss geometry')
# Continuous entablature bridges the photographed pairs of round columns.
# Overall column official27ft6in height controls the spring; profile dimensions remain inferred.
for yy in [y0,y1]:
 profiles=[(8.572,1.36,.26),(8.80,1.48,.20),(9.10,1.42,.42),(9.36,1.70,.14),(9.49,1.86,.12)]
 if AGED and yy==y1:profiles=[(8.58,1.48,.27),(9.04,1.54,.50)]
 spans=[(-31.8,-23.4),(-16.6,-3.4),(3.4,16.6),(23.4,31.8)] if yy==y0 else [(-31.8,31.8)]
 for z,d,h0 in profiles:
  em='Weathered concrete' if AGED and yy==y1 else COL if z<9.02 else PL
  for xa,xb in spans:box(((xa+xb)/2,yy,z),(xb-xa,d,h0),em,'hall colonnade entablature with north opening breaks')
  if yy==y0:
   # Exact butt joints avoid broad coplanar overlaps where the cornice turns
   # toward each north jamb. Return depths are photo-proportioned.
   for cx in [-20,0,20]:
    for side in [-1,1]:
     ya=.525;yb=yy-d/2;xx=cx+side*(3.4+d/2)
     box((xx,(ya+yb)/2,z),(d,yb-ya,h0),em,'north monumental opening entablature jamb returns')
 if not(AGED and yy==y1):
  for xx in [-30.9+i*.43 for i in range(145)]:
   if min(abs(xx-pp) for pp in [-10,10])<1.4:continue
   if yy==y0 and min(abs(xx-c) for c in [-20,0,20])<3.45:continue
   box((xx,yy+(1 if yy<15 else -1)*.77,9.26),(.19,.18,.16),PL,'hall entablature dentils')
for xx in [-31.8,31.8]:
 for z,d,h0 in [(8.572,1.36,.26),(8.80,1.48,.20),(9.10,1.42,.42),(9.36,1.70,.14),(9.49,1.86,.12)]:
  box((xx,ym,z),(d,y1-y0,h0),COL if z<9.02 else PL,'hall end colonnade entablature profiles')
# Three sail vault patches, all created with metric UVs.
for b,(xa,xb) in enumerate([(-31.8,-10),(-10,10),(10,31.8)]):
 cx=(xa+xb)/2;n=64;verts=[];faces=[];hx=(xb-xa)/2;hy=(y1-y0)/2
 for j in range(n+1):
  vy=-1+2*j/n
  for i in range(n+1):
   vx=-1+2*i/n;z=hall_sail_z(vx,vy)
   verts.append((cx+hx*vx,ym+hy*vy,z))
 for j in range(n):
  for i in range(n):k=j*(n+1)+i;faces.append((k,k+n+1,k+n+2,k+1))
 addmesh(verts,faces,'Guastavino buff tile',f'sail vault bay {b+1}')
# Decorated upper walls stand at the colonnades, with deep reveals to rear glazing.
execute_component('hall_cartouche.py')
execute_component('hall_window_tracery.py')
execute_component('hall_lunettes.py')
# End walls follow the tall nave arch, with documented high fanlights.
for xx in [-hallw/2+.15,hallw/2-.15]:
 vv=[];ff=[];nn=60
 for ii in range(nn+1):
  t=pi*ii/nn;yy=ym+10.76*cos(t);zz=spring+HALL_BOUNDARY_RISE*sin(t)
  dy=yy-ym
  topwin=10.6+sqrt(max(0,3.8*3.8-dy*dy)) if abs(dy)<3.8 else 10.6
  vv.extend([(xx,yy,8.5),(xx,yy,10.6),(xx,yy,topwin),(xx,yy,zz)])
 for ii in range(nn):
  k=ii*4;ff.extend([(k,k+4,k+5,k+1),(k+2,k+6,k+7,k+3)])
 addmesh(vv,ff,'Mixed 2017 hall backing' if AGED else HALL_WALL_PLASTER,'end wall upper infill')
 # Fanlight glazing viewed from nave, with stone archivolt.
 innerx=xx+(.04 if xx<0 else -.04);rr=3.8;zz=10.6
 v=[(innerx,ym-rr,zz),(innerx,ym+rr,zz)]+[(innerx,ym+rr*cos(pi*i/40),zz+rr*sin(pi*i/40)) for i in range(1,41)]
 addmesh(v,[tuple(range(len(v)))],'Glass tower blue','end wall fanlight glazing')
 arch(ym,innerx,zz,rr*2,rr,.38,.26,PL,'end wall fanlight molding',40,'side')
 for ii in range(-6,7):
  dy=ii*.52;hh=sqrt(max(0,rr*rr-dy*dy));box((innerx,ym+dy,zz+hh/2),(.12,.055,hh),'Window cast iron','end fanlight mullions')
 for z in [11.3,12.1,12.9]:
  hw=sqrt(max(0,rr*rr-(z-zz)**2));box((innerx,ym,z),(.12,hw*2,.05),'Window cast iron','end fanlight transoms')
 # Rectangular stone frame beneath fanlight, including low central doorway.
 # End colonnade uses the existing four columns in the measured 28-column total
 box((innerx,ym,8.8),(.8,10,.4),PL,'end wall portal entablature')
 # True end-door geometry is added from plan-derived portal positions below.
for xa,xb in [(-hallw/2,-31.8),(31.8,hallw/2)]:
 vv=[];ff=[]
 for xx in [xa,xb]:
  for j in range(41):
   t=pi*j/40;vv.append((xx,ym+(y1-y0)/2*cos(t),spring+HALL_BOUNDARY_RISE*sin(t)))
 for j in range(40):ff.append((j,j+1,j+42,j+41))
 addmesh(vv,ff,PL,'end aisle vault infill')
# Broad rib bands across nave with rosette coffers.
for x in [-31.8,-10,10,31.8]:
 arch(ym,x,spring,y1-y0,HALL_BOUNDARY_RISE,.8,1.38,PL,'transverse coffered arch',56,'side')
 # Twin raised fillets frame the photographed coffer band along its intrados.
 for dx in [-.66,-.52,.52,.66]:
  for ii in range(64):
   ta=pi*ii/64;tb=pi*(ii+1)/64
   pa=(x+dx,ym+(y1-y0)/2*cos(ta),spring+HALL_BOUNDARY_RISE*sin(ta)-.035)
   pb=(x+dx,ym+(y1-y0)/2*cos(tb),spring+HALL_BOUNDARY_RISE*sin(tb)-.035)
   beam(pa,pb,.036 if abs(dx)<.6 else .052,PL,'hall arch continuous molded fillets',8)
 for j in range(15):
  t=.10+(pi-.20)*j/14;yy=ym+(y1-y0)/2*cos(t);zz=spring+HALL_BOUNDARY_RISE*sin(t)-.025
  # Shallow eight-petal rosette and octagonal border on the arch intrados.
  tangent=Vector((0,-(y1-y0)/2*sin(t),HALL_BOUNDARY_RISE*cos(t))).normalized()
  normal=Vector((0,-cos(t),-sin(t)))
  center=Vector((x,yy,zz))+normal*.055
  # Layered rosette has real petal relief; motif is authored, not a scan of historic carving.
  vv=[];nf=48
  for rr,depth in [(.025,.11),(.115,.10),(.22,.035),(.32,.016)]:
   for k in range(nf):
    ang=k*2*pi/nf;rad=rr*(1+.09*cos(8*ang));height=depth+.029*sin(8*ang)**2
    pp=center+Vector((1,0,0))*rad*cos(ang)+tangent*rad*sin(ang)+normal*height
    vv.append(tuple(pp))
  ff=[tuple(range(nf-1,-1,-1))]
  for ir in range(3):
   for k in range(nf):j=ir*nf+k;jn=ir*nf+(k+1)%nf;ff.append((j,jn,jn+nf,j+nf))
  addmesh(vv,ff,PL,'hall layered eight-petal rosette relief | approximate carving')
  for k in range(8):
   t0=2*pi*k/8;t1=2*pi*(k+1)/8
   p=center+Vector((1,0,0))*.48*cos(t0)+tangent*.48*sin(t0)
   q=center+Vector((1,0,0))*.48*cos(t1)+tangent*.48*sin(t1)
   beam(p,q,.035,PL,'octagonal coffer border',6)
# Skirting stops at real floor-reaching portals, including the north entry.
for y in [.6,30.5]:
 gaps=[(-3.26,3.26)] if y<15 else [(-10.0,10.0)]
 if y>15 and not AGED:gaps += [(q-.80,q+.80) for q in [-28,-12,12,28]]
 cursor=-hallw/2
 for xa,xb in sorted(gaps):
  if xa>cursor:box(((cursor+xa)/2,y,.28),(xa-cursor,.24,.5),COL,'hall stone skirting interrupted at portals')
  cursor=max(cursor,xb)
 if cursor<hallw/2:box(((cursor+hallw/2)/2,y,.28),(hallw/2-cursor,.24,.5),COL,'hall stone skirting interrupted at portals')
# Historically reproduced hall chandeliers; absent in exact2017 photographs.
def chandelier(x,y,top,wide=3.2,drop=6.2):
 bottom=top-drop
 beam((x,y,top),(x,y,bottom+1.0),.024,'Dark bronze','chandelier suspension chain',8)
 lathe((x,y,bottom+.55),[(.15,0),(.35,.25),(.43,.45),(.23,.7)],'Dark bronze','chandelier central finial')
 ring((x,y,bottom+1),wide/2,.10,'Dark bronze','chandelier annular crown',64)
 ring((x,y,bottom+.8),wide/2-.08,.055,'Dark bronze','chandelier lower bronze ring',64)
 for j in range(24):
  t=2*pi*j/24;xx=x+wide/2*cos(t);yy=y+wide/2*sin(t)
  beam((x,y,bottom+.5),(xx,yy,bottom+1),.025,'Dark bronze','chandelier radial arms')
  lathe((xx,yy,bottom+.65),[(.065,0),(.10,.14),(.065,.26),(0,.32)],'Warm lamp glass','chandelier lamps',10)
 for j in range(12):
  t=j*2*pi/12;beam((x+.28*cos(t),y+.28*sin(t),bottom+.3),(x+wide/2*cos(t),y+wide/2*sin(t),bottom+.9),.027,'Dark bronze','chandelier basket ribs')
 if wide>2.4:
  # Detailed lower basket and pendant tier; original geometry based on visible fixture proportions.
  lathe((x,y,bottom-.62),[(.02,0),(.12,.12),(.22,.27),(.14,.39),(.31,.53),(.44,.86),(.26,1.20),(.15,1.43)],'Dark bronze','hall chandelier pendant vase',48)
  ring((x,y,bottom+.14),.59,.045,'Dark bronze','hall chandelier lower lamp tier',40)
  for k in range(12):
   t=k*2*pi/12;xx=x+.58*cos(t);yy=y+.58*sin(t)
   lathe((xx,yy,bottom-.02),[(0,0),(.085,.06),(.10,.17),(.065,.26),(0,.31)],'Warm lamp glass','hall chandelier pendant bulbs',16)
   beam((x+.20*cos(t),y+.20*sin(t),bottom+.53),(xx,yy,bottom+.25),.027,'Dark bronze','hall chandelier lower scrolling arms',8)
  for k in range(32):
   t=k*2*pi/32
   beam((x+wide/2*cos(t),y+wide/2*sin(t),bottom+.94),(x+(wide/2-.15)*cos(t),y+(wide/2-.15)*sin(t),bottom+1.3),.05,'Dark bronze','hall chandelier crown acanthus forms',7)
 light=bpy.data.lights.new('Chandelier warm bounce','AREA');light.energy=470;light.color=(1,.76,.44);light.shape='DISK';light.size=3;ob=bpy.data.objects.new('Chandelier warm bounce',light);scene.collection.objects.link(ob);ob.location=(x,y,bottom+.72)
if not AGED:
 for x in [-bay,0,bay]:chandelier(x,ym,apex-.15)
# Documented2017 decay, art-directed distribution, never asserted exact marks.
if AGED:
 def hall_wall_patch_allowed(x0,x1,z0,z1,north):
  if north:
   for cc,ww,hh,bb in front_openings:
    bottom=0 if cc==0 else bb
    if x1>cc-ww/2-.10 and x0<cc+ww/2+.10 and z1>bottom-.08 and z0<bb+hh+.08:return False
   return True
  return (x1<=-10.1 or x0>=10.1) and x0>=-31.7 and x1<=31.7
 for side in [-1,1]:
  for j in range(38):
   x=rng.uniform(-34,34);z=rng.uniform(.5,8);w=rng.uniform(.6,3.2);h=rng.uniform(.4,2.4)
   if not hall_wall_patch_allowed(x-w/2,x+w/2,z-h/2,z+h/2,side==-1):continue
   yy=.62 if side==-1 else 30.66
   vv=[]
   for k in range(12):
    t=k*2*pi/12;r=rng.uniform(.65,1.0);vv.append((x+w*r*cos(t)/2,yy,z+h*r*sin(t)/2))
   addmesh(vv,[tuple(range(12))],'Mixed 2017 hall backing','interpreted irregular plaster loss patches')
 # Original column-base marks, with cylindrical placement following documented reachable surfaces.
 for cx in [-24.2,-15.7,-4.2,4.2,15.7,24.2]:
  for cy in [y0,y1]:
   theta0=pi/2 if cy<15 else -pi/2
   for k in range(5):
    pts=[]
    for j in range(6):
     theta=theta0-.6+k*.23+rng.uniform(-.18,.18);zz=1.2+j*.15+rng.uniform(-.1,.12)
     pts.append((cx+.60*cos(theta),cy+.60*sin(theta),zz))
    for p,q in zip(pts,pts[1:]):beam(p,q,.009,'Interpretive graffiti blue','original column paint marks',5)
 # Original nonverbatim spray-like marks, placed at human reach; not traced historic graffiti.
 for j in range(38):
  x=rng.uniform(-33,33);y=rng.choice([.60,30.63]);z=rng.uniform(.5,2.4)
  if not hall_wall_patch_allowed(x-.12,x+1.02,z-.35,z+.35,y<15):continue
  for k in range(rng.randint(3,6)):
   pts=[(x+k*.15+rng.uniform(-.1,.12),y,z+rng.uniform(-.35,.35)) for _ in range(5)]
   for p,q in zip(pts,pts[1:]):beam(p,q,.012,rng.choice(['Interpretive graffiti blue','Interpretive graffiti ochre']),'original interpretive low-wall paint strokes',5)
 for j in range(600):
  x=rng.uniform(-34,34);y=rng.choice([rng.uniform(1,4),rng.uniform(28,30)])
  if abs(x)<3.4:continue
  box((x,y,.12+rng.random()*.12),(rng.uniform(.06,.45),rng.uniform(.05,.3),rng.uniform(.03,.18)),'Decorative plaster','2017 perimeter plaster rubble')

# Modeled door surrounds and low window frames; placement photo/plan-proportioned.
GROUP='03 GREAT HALL | three sail vaults and colonnades'
for wall_y in [5.12,26.48]:
 face=1 if wall_y<10 else -1
 for xx in [-bay/2,bay/2]:
  # A pedimented stone surround, with a filled glazed door rather than black void.
  for dx in [-.91,.91]:box((xx+dx,wall_y,1.65),(.28,.42,3.3),COL,'hall pedimented door jambs')
  box((xx,wall_y,3.30),(2.18,.48,.3),PL,'hall doorway lintel')
  pediment(xx,wall_y+face*.22,3.48,2.52,.60,PL)
  if not AGED:
   box((xx,wall_y+face*.23,1.48),(1.56,.09,2.96),'Wood walnut','hall restored door leaves')
   for dx in [-.36,.36]:
    box((xx+dx,wall_y+face*.30,1.65),(.57,.025,2.13),'Glass tower blue','hall restored door glazing')
    box((xx+dx,wall_y+face*.32,1.65),(.035,.035,2.2),'Dark bronze','hall restored door central bars')
  if not AGED:
   # Original simplified bronze wall fixtures, approximate proportions.
   beam((xx,wall_y+face*.3,5.6),(xx,wall_y+face*1.05,5.6),.043,'Dark bronze','hall sconce wall arms')
   beam((xx,wall_y+face*1.05,5.6),(xx,wall_y+face*1.05,4.5),.018,'Dark bronze','hall sconce chains')
   lathe((xx,wall_y+face*1.05,4.05),[(.05,0),(.23,.12),(.29,.4),(.17,.66),(.03,.73)],'Warm lamp glass','hall wall sconces',24)
   # Concealed warm restoration uplights follow clerestory ledges.
   l=bpy.data.lights.new('Clerestory warm uplight','AREA');l.energy=450;l.color=(1,.76,.50);l.shape='RECTANGLE';l.size=10;l.size_y=.2
   o=bpy.data.objects.new('Clerestory warm uplight',l);scene.collection.objects.link(o);o.location=(xx,wall_y+(.7 if wall_y<10 else -.7),9.0);o.rotation_euler=(pi,0,0)
# End wall doorway: timber and bronze infill, no fictional passage behind.
for xx in [-hallw/2+.72,hallw/2-.72]:
 for yy in ([16.2] if xx<0 else [10.1,22.2]):
  xxin=xx+(.04 if xx<0 else -.04)
  box((xxin,yy,1.50),(.06,2.28,3.50),'Wood walnut' if not AGED else 'Dark bronze','end door leaves')
  for dy in [-1.21,1.21]:box((xxin,yy+dy,1.5),(.35,.24,3.7),COL,'end doorway stone jambs')
  box((xxin,yy,3.72),(.4,2.65,.32),PL,'end doorway stone lintels')
# TICKET LOBBY --------------------------------------------------
GROUP='04 TICKET LOBBY | documented public architecture'
ly0=31.7;ly1=50.7;lx0=-11.89;lx1=8.1;lw=lx1-lx0;lcx=(lx0+lx1)/2
box((lcx,(ly0+ly1)/2,.03),(lw,ly1-ly0,.2),FLOOR,'ticket lobby floor')
if AGED:
 box((lx1,(ly0+ly1)/2,4.5),(.6,ly1-ly0,9),PL,'ticket-lobby west wall')
else:
 for ya,yb in [(ly0,34.25),(46.95,ly1)]:box((lx1,(ya+yb)/2,4.5),(.6,yb-ya,9),PL,'ticket-lobby west wall beyond documented retail cluster')
 box((lx1,40.6,(4.22+9)/2),(.6,12.7,9-4.22),PL,'ticket-lobby upper clock niche backing')
for ya,yb in ([(ly0,36.63),(43.36,ly1)] if AGED else [(ly0,36.63),(48.52,ly1)]):box((lx0,(ya+yb)/2,4.5),(.6,yb-ya,9),PL,'ticket-lobby east wall sections')
if not AGED:box((lx0,(43.36+48.52)/2,(6.75+9)/2),(.6,48.52-43.36,9-6.75),PL,'ticket-lobby upper Neighbor frontage backing')
box((lx0,39.995,7.9),(.6,6.73,2.2),PL,'arcade portal header')
for x in [-4.0,4.0]:
 for y in [31.7,34.7,36.2,43.25,44.75,48.3]:column(x,y,.13,8.382,.60,False,COL,paired=y not in [31.7,48.3])
 for cy in [35.45,44.0]:box((x,cy,.33),(1.74,3.24,.40),COL,'ticket lobby paired columns shared stone plinths')
# Shared pedestals are visible in exact2017pre_p1 and restoredpost_p19.
# The second close pair is symmetrized by0.05m within the raster-control uncertainty.
box((lcx,41.2,9.22),(lw,19.5,.45),PL,'coffered lobby ceiling slab')
for y in [33.1,38.2,44.1,49.2]:
 box((lcx,y,8.88),(lw,.68,.52),PL,'lobby cross beams')
for x in [-4.0,0,4.0]:box((x,41.2,8.812),(.6,19.5,.6),PL,'lobby longitudinal beams')
for x in [-2.7,2.7]:
 for y in [35.5,41.3,47]:
  for xx,yy,ww,dd in [(x,y-2.1,4.4,.16),(x,y+2.1,4.4,.16),(x-2.2,y,.16,4.2),(x+2.2,y,.16,4.2)]:box((xx,yy,8.73),(ww,dd,.15),PL,'coffer inset molding')
if not AGED:
 for y in [35.8,45.2]:chandelier(0,y,8.9,1.45,2.2)
# SOUTH CONCOURSE -----------------------------------------------
GROUP='05 CONCOURSE | restored glazing and structural roof'
cw=58.9788;cd=23.7744;cy=63.4;cz=9.5
box((0,cy,.02),(cw,cd,.24),'Weathered concrete' if AGED else 'Terrazzo','concourse floor')
for y in [cy-cd/2,cy+cd/2]:
 for j in range(8):
  x=-cw/2+(j+.5)*cw/8
  if y>cy and abs(x)<15:
   box((x,y,9.4),(cw/8,1,1.2),'Concourse buff brick','passenger ramp upper parapet')
   if abs(x)>8:
    outer=cw/4;inner=11.5824;mid=(outer+inner)/2*(1 if x>0 else -1)
    box((mid,y,2.35),(outer-inner,1,4.7),'Concourse buff brick','ramp opening flank masonry')
   continue
  if y<cy and abs(x)<8:
   box((x,y,9.4),(cw/8,1,1.2),'Concourse buff brick','ticket lobby concourse portal lintel')
   continue
  box((x,y,1.4),(cw/8,1,2.8),'Concourse buff brick','concourse brick sill walls')
  box((x-cw/16+.6,y,5),(1.2,1,10),'Concourse buff brick','concourse brick piers')
  box((x,y,9.4),(cw/8,1,1.2),'Concourse buff brick','concourse brick parapet')
  box((x,y,5.8),(cw/8-1.4,.12,5.4),'Glass clear','concourse original grid window')
  for dx in [-2,-1,0,1,2]:box((x+dx,y-.12,5.8),(.065,.16,5.4),'Roof steel','concourse window mullions')
  for z in [3.7,4.8,5.9,7,8.1]:box((x,y-.12,z),(cw/8-1.4,.16,.06),'Roof steel','concourse window transoms')
# Long east-west gabled steel/glass roof. Kept open2017 where roof loss is observed, not all exact.
for j in range(14):
 x=-cw/2+j*cw/13
 for side in [-1,1]:
  beam((x,cy+side*cd/2,cz),(x,cy,cz+4.2),.12,'Roof steel','concourse primary truss chords')
  beam((x,cy+side*cd/2,cz),(x,cy,cz),.105,'Roof steel','concourse truss tie')
  for k in range(4):
   yy=cy+side*cd/2*k/4;zz=cz+4.2*(1-k/4)
   beam((x,yy,cz),(x,yy,zz),.065,'Roof steel','concourse truss posts')
   if k<3:beam((x,yy,zz),(x,cy+side*cd/2*(k+1)/4,cz),.055,'Roof steel','concourse truss diagonals')
for side in [-1,1]:
 for k in range(7):
  y=cy+side*cd/2*k/6;z=cz+4.2*(1-k/6);beam((-cw/2,y,z),(cw/2,y,z),.07,'Roof steel','concourse roof purlins')
 if not AGED:
  addmesh([(-cw/2,cy,cz+4.23),(cw/2,cy,cz+4.23),(cw/2,cy+side*cd/2,cz+.03),(-cw/2,cy+side*cd/2,cz+.03)],[(0,1,2,3)],'Glass clear','restored glazed concourse roof')
box((cw/2,cy,4.6),(1,cd,9.2),'Concourse buff brick','concourse west end wall')
for ya,yb in [(cy-cd/2,59.4),(66.2,cy+cd/2)]:box((-cw/2,(ya+yb)/2,4.6),(1,yb-ya,9.2),'Concourse buff brick','concourse east wall sections')
box((-cw/2,62.8,7.0),(1,6.8,4.4),'Concourse buff brick','east-exit portal header')

execute_component('concourse_roof_detail.py')
scene['concourse_roof_metadata']=json.dumps(CONCOURSE_ROOF_METADATA)
execute_component('concourse_walls_detail.py')
scene['concourse_wall_metadata']=json.dumps(CONCOURSE_WALL_METADATA)
execute_component('concourse_floor_2017.py')

# EAST ARCADE --------------------------------------------------
GROUP='06 EAST ARCADE | HNS registered six bays and separate crosshall margins'
ax0=-39.5;ax1=-11.89;ay=39.995;aw=6.73;vn0=-36.26;vn1=-11.89
arcade_centers=[-34.16,-30.13,-26.05,-21.98,-17.90,-13.87]
arcade_axes=[-36.26,-32.30,-28.19,-24.15,-20.04,-16.08,-11.89]
box(((ax0+ax1)/2,ay,.03),(ax1-ax0,aw,.2),FLOOR,'arcade stone floor')
for y in [36.63,43.36]:
 if not AGED and y>ay:
  wall_y_portals(y,ax0,ax1,6.8,[(-34.13,2.32,4.30),(-30.165,2.31,4.30)],PL,'south arcade with registered Yellow Light openings',.45)
 else:box(((ax0+ax1)/2,y,3.4),(ax1-ax0,.45,6.8),PL,'arcade walls')
 for j,x in enumerate(arcade_centers):
  # Published south elevation E->W: glass,glass,solid,glass,glass,solid.
  if y>ay and j in [2,5]:continue
  if not AGED and y>ay and j in [0,1]:continue
  iy=y-.25 if y>ay else y+.25;ww=2.48
  box((x,iy,2.1),(ww,.16,4.2),'Wood walnut' if not AGED else 'Dark void','arcade historic storefront surrounds')
  if not AGED:
   box((x,iy+(-.10 if y>ay else .10),2.1),(ww-.24,.03,3.6),'Glass tower dark','arcade storefront glazed panels')
   for dx in [-ww/2,0,ww/2]:box((x+dx,iy,2.1),(.10,.22,4.2),'Wood walnut','arcade storefront mullions')
   for zz in [.30,3.91]:box((x,iy,zz),(ww,.22,.12),'Wood walnut','arcade storefront transoms')
  arch(x,iy,4.25,ww,ww/2,.16,.25,PL,'arcade storefront arched tympanum',28)
for x in arcade_axes:arch(ay,x,4.4,aw,2.4,.3,.4,PL,'arcade transverse arch',28,'side')
verts=[];faces=[]
for i in range(61):
 x=vn0+(vn1-vn0)*i/60
 for j in range(25):
  t=pi*j/24;verts.append((x,ay+aw/2*cos(t),4.4+2.4*sin(t)))
for i in range(60):
 for j in range(24):k=i*25+j;faces.append((k,k+25,k+26,k+1))
addmesh(verts,faces,PL,'arcade barrel vault')
for xa,xb in [(ax0,vn0),(vn1,ax1)]:box(((xa+xb)/2,ay,5.85),(xb-xa,aw,.22),PL,'arcade crosshall margin lower ceiling')
if not AGED:
 for x in arcade_centers:chandelier(x,ay,6.7,.58,1.4)

WEST_FACADE_WINDOWS=[(yy,2.4384,1.0,7.2484) for yy in [6.84,10.34,13.69,17.81,21.55,26.26,30.79,34.45,38.18,41.98,45.71,49.45]]
execute_component('west_public_rooms.py')
execute_component('secondary_spaces.py')
scene['elevator_lobby_metadata']=json.dumps(ELEVATOR_DETAIL.build_elevator_lobby_candidate(globals()))
execute_component('current_fitouts.py')
execute_component('study_lounge.py')
execute_component('ticket_retail.py')

execute_component('north_plaza.py')
execute_component('north_forecourt_2017.py')

# FINISH BATCHED GEOMETRY ---------------------------------------
print('Building',len(B),'named geometric batches',flush=True)
collections={};room_nodes={}
UNUSED_CONTROL_VERTEX_CLEANUP=[]
for (g,m,n),(verts,faces,custom_uvs) in B.items():
 used=sorted({i for face in faces for i in face})
 if len(used)!=len(verts):
  UNUSED_CONTROL_VERTEX_CLEANUP.append(dict(space=g,object=n,removed=len(verts)-len(used)))
  remap={old:new for new,old in enumerate(used)};verts=[verts[i] for i in used];faces=[tuple(remap[i] for i in f) for f in faces]
 if g not in collections:
  col=bpy.data.collections.new(g);scene.collection.children.link(col);collections[g]=col
  node=bpy.data.objects.new(g,None);col.objects.link(node);node['export_group']=True;node['space']=g;node['era']=ERA;node['accuracy']='See evidence and per-space completeness manifests';room_nodes[g]=node
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],faces);mesh.materials.append(M[m]);mesh.update()
 ob=bpy.data.objects.new(n,mesh);collections[g].objects.link(ob);ob.parent=room_nodes[g];ob['space']=g;ob['material_evidence']='Original procedural surface; photographed material class';ob['reconstruction_status']='approximate geometry, see coverage manifest'
 uv=mesh.uv_layers.new(name='MetricUV');scale=M[m].get('texture_repeat_m',4.0)
 for p in mesh.polygons:
  normal=p.normal;ax=max(range(3),key=lambda j:abs(normal[j]));ids=([1,2] if ax==0 else [0,2] if ax==1 else [0,1])
  if 'vault' in n or 'lunette' in n:ids=[0,1]
  for local_i,li in enumerate(p.loop_indices):
   if m=='Grand Hall floor assembly':
    co=mesh.vertices[mesh.loops[li].vertex_index].co
    uv.data[li].uv=(co[ids[0]]/71.0184+.5,co[ids[1]]/31.6992)
   elif AGED and m=='Guastavino buff tile':
    co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co.x/71.0184+.5,co.y/31.6992)
   elif custom_uvs[p.index] is not None:
    u,v=custom_uvs[p.index][local_i];uv.data[li].uv=(u/scale,v/scale)
   else:
    co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(co[ids[0]]/scale,co[ids[1]]/scale)
 if m=='Glass clear' and not GLASS_RULES.glass_mesh_topology(mesh)['closed']:
  sol=ob.modifiers.new('Physical glazing thickness 8mm','SOLIDIFY');sol.thickness=.008
 # Small edge bevels give masonry real highlights; export applies modifiers.
 if any(t in n for t in ['cornice','plinth','sills','entablature','coffer inset','capital abacus']):
  bevel=ob.modifiers.new('Physical edge bevel','BEVEL');bevel.width=.024;bevel.segments=2
 if g.startswith('07 THE STUDY') and any(k in n for k in ['upholstery','opal globe','palm trunks','curved stool backs']):
  for p in mesh.polygons:p.use_smooth=len(p.vertices)<5
 if g.startswith('08 WEST') and any(k in n for k in ['opal pear','rosette','ram-head','relief beads','curled horns','radial leaves','curled petals']):
  for p in mesh.polygons:p.use_smooth=len(p.vertices)<5
 # Triangulate n-gon caps after bevel/solidify so glTF receives portable tangents.
 if any(len(p.vertices)>4 for p in mesh.polygons) or any(md.type=='BEVEL' for md in ob.modifiers):
  tri=ob.modifiers.new('Portable tangent topology for n-gon caps','TRIANGULATE');tri.min_vertices=5
 # Curve-like stonework smooth shading, walls keep architectural planar normals.
 if 'piers' not in n and any(t in n for t in ['layered eight-petal','shaft','torus','archivolt','coffered arch','transverse arch','fanlight molding','sail vault','foliate','acanthus']):
  for p in mesh.polygons:p.use_smooth=True

 # Match the isolated original ornament's sharp-edge/smooth-surface contract.
 if n.startswith('north candidate'):
  for poly in mesh.polygons:poly.use_smooth=True
  mesh.set_sharp_from_angle(angle=.60)

# Fourteen ornamental placements share one mesh; supports/datums stay unchanged.
for g,x,y,z,h,r,m in CAPITAL_DETAIL_PLACEMENTS:
 ob=CAPITAL_DETAIL.create_linked_capital(collections[g],M[m],location=(x,y,z+h),radius_m=r,repeat_m=M[m].get('texture_repeat_m',4.0))
 ob.parent=room_nodes[g];ob['space']=g;ob['era']=ERA
 ob['reconstruction_status']='Original mid-detail carving; individual period losses and exact fine carving unresolved'
assert len(CAPITAL_DETAIL_PLACEMENTS)==14
scene['exterior_capital_detail']=json.dumps(dict(placements=14,shared_mesh_count=1,controls=CAPITAL_DETAIL.asdict(CAPITAL_DETAIL.DEFAULT_CONTROLS),fine_carving_fidelity='open'))
_exterior_group='01 EXTERIOR | measured historic envelope'
for ob in CANOPY_DETAIL.create_blender_component(collections[_exterior_group],ERA,normal_qa=False):
 ob.parent=room_nodes[_exterior_group];ob['space']=_exterior_group;ob['candidate_only']=False
 ob['reconstruction_status']='Source-led original canopy interpretation; fabrication dimensions/counts unresolved'
 for material in ob.data.materials:M[material.name]=material
scene['north_canopy_detail']=json.dumps(dict(era=ERA,controls=CANOPY_DETAIL.asdict(CANOPY_DETAIL.DEFAULT_CONTROLS),source_limits='Mixed opaque/glazed roof photo-supported; exact dimensions, lamp counts and hidden connections unmeasured'))
scene['clear_glass_optics']='Roughness0.008 photo-comparison trial improves clear-screen view; not measured optical data'
scene['glass_thickness_rule']='Open surface panes get 8 mm thickness; already-closed glass boxes retain their authored single solid skin'
scene['portable_material_changes']=json.dumps(PORTABLE_MATERIALS.apply_candidate_materials(bpy.data.materials,ERA,ROOT/'assets/portable_public_finishes'))
north_plaza_post_finalize(collections,room_nodes)
forecourt_2017_post_finalize(collections,room_nodes)
scene['component_sha256']=json.dumps(COMPONENT_HASHES)
scene['unused_control_vertex_cleanup']=json.dumps(UNUSED_CONTROL_VERTEX_CLEANUP)
scene['secondary_space_evidence']=json.dumps(globals().get('SEC_SPACES',[]))
# Coverage is visible in the editable source rather than silently inventing inaccessible rooms.
coverage_col=bpy.data.collections.new('90 COVERAGE | unresolved areas, no invented fit-out');scene.collection.children.link(coverage_col)
for name,loc,reason in [
 ('Tower private floors | unmodeled fit-out',(0,43.96,43),'Historical exterior and floor spacing known; current private partitions and tenant interiors are not established'),
 ('Basements and plant | unmodeled',(0,40,-4),'No complete dated room plans or systems inventory'),
 ('Mezz and 2026 tenant suites | no invented layout',(-42,40,12),'Current occupancy and selected photos documented; complete suite geometry remains unverified'),
 ('NoMad hotel | not a finished 2026 interior',(0,44,61),'2027 opening announcement does not establish finished 2026 rooms')]:
 ob=bpy.data.objects.new(name,None);coverage_col.objects.link(ob);ob.location=loc;ob.empty_display_type='PLAIN_AXES';ob.empty_display_size=1.5;ob['coverage_status']='unmodeled';ob['reason']=reason;ob['export_coverage_marker']=True
# Explicit labels for period-specific source gaps; these are metadata/viewport markers, not room geometry.
extra_coverage=[('Southern platform / replacement deck | UNALIGNED',(0,106,0),'Separate local2017study only; current concrete deck placement/elevation unresolved'),
 ('East public restroom fit-outs | UNOBSERVED',(-48,25,2),'HNS passage door locations retained; complete room finishes, fixtures and 2017 state unresolved'),
 ('North lift approach west branch | CONTINUATION UNRESOLVED',(-40.8,27.0,1.7),'Documented branch mouth kept open; no unverified continuation, threshold rise or level route is claimed')]

if AGED:
 extra_coverage += [('West reading and cafe | 2017 CONDITION UNOBSERVED',(44,15,4),'Restored room sources do not establish exact2017fabric'),('Historic restaurant | 2017 CONDITION UNOBSERVED',(44,39,4),'No fabricated dated damage or complete room inventory'),('Former women room | 2017 CONDITION UNOBSERVED',(-44,12,4),'2025Studyfit-out cannot be used as2017interior evidence')]
else:
 extra_coverage += [('The Shop unseen suite | UNRESOLVED',(18,41,3),'Only documented frontage and bounded single-view fixture fragment modeled'),('Neighbor unseen suite | UNRESOLVED',(-23,46,3),'Photographed doorway/view fragment is not a complete tenant floorplan'),('Yellow Light rear service fit-out | UNOBSERVED',(-31,50,2),'Published L-shaped shell only; unseen service equipment and partitions omitted')]
for c in globals().get('HALL_CARTOUCHE_COVERAGE',[]):
 if c['state'].startswith('unobserved'):
  extra_coverage.append(('2017 '+c['side']+' cartouche X'+str(c['center_x_m'])+' | EXTENT UNOBSERVED',(c['center_x_m'],3.9 if c['side']=='north' else 27.7,15.5),'Omitted due incomplete dated coverage; absence is not asserted'))
for c in globals().get('CONCOURSE_WALL_UNRESOLVED_CONTINUATIONS',[]):
 if 'location_m' in c:loc=c['location_m']
 elif 'plane_y_m' in c:loc=(sum(c['x_spans_m'][0])/2,c['plane_y_m'],1.7)
 else:loc=(sum(c['x_span_m'])/2,sum(c['y_span_m'])/2,1.7)
 extra_coverage.append(('Concourse '+c['id']+' | UNRESOLVED',loc,c['reason']))
for name,loc,reason in extra_coverage:
 ob=bpy.data.objects.new(name,None);coverage_col.objects.link(ob);ob.location=loc;ob.empty_display_type='CUBE';ob.empty_display_size=1.5;ob.show_name=True;ob.show_in_front=True;ob.color=(1,.35,.08,1);ob['coverage_status']='unmodeled / unobserved';ob['reason']=reason;ob['export_coverage_marker']=True
for ob in coverage_col.objects:
 ob.show_name=True;ob.show_in_front=True
for label,path in [('READ ME - reconstruction coverage',ROOT/'README.md'),('Evidence and modeled-space coverage',ROOT/'manifests/evidence_and_coverage.json')]:
 if path.exists():
  text_block=bpy.data.texts.new(label);text_block.write(path.read_text())

# Lighting and camera presets ---------------------------------
world=bpy.data.worlds.new('Generic daylight | CC0 lighting, neutral camera sky');world.use_nodes=True;scene.world=world
nt=world.node_tree
sky=nt.nodes.new('ShaderNodeTexEnvironment');sky.image=bpy.data.images.load(str(ROOT/'assets/environment/kloofendal_48d_partly_cloudy_4k.exr'),check_existing=True)
nt.links.new(sky.outputs['Color'],nt.nodes['Background'].inputs[0]);nt.nodes['Background'].inputs['Strength'].default_value=.65
# A neutral camera background prevents the non-Detroit HDRI landscape being represented as the site.
cam_bg=nt.nodes.new('ShaderNodeBackground');cam_bg.inputs['Color'].default_value=(.42,.52,.65,1);cam_bg.inputs['Strength'].default_value=.8
light_path=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader')
nt.links.new(light_path.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(nt.nodes['Background'].outputs[0],mix.inputs[1]);nt.links.new(cam_bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],nt.nodes['World Output'].inputs['Surface'])
world['environment_license']='CC0; Greg Zaal / Poly Haven; source-license.json'
world['environment_use']='Generic daylight illumination. South African horizon is replaced in camera rays by a neutral sky; not Detroit surroundings.'
sun=bpy.data.lights.new('Afternoon sun','SUN');sun.energy=1.2;sun.angle=math.radians(2.0);ob=bpy.data.objects.new('Afternoon sun',sun);scene.collection.objects.link(ob);ob.rotation_euler=(math.radians(33),math.radians(-26),math.radians(-30))
# Broad window daylight fills improve physically plausible room bounce on CPU path tracer.
for x in [-bay,0,bay]:
 l=bpy.data.lights.new('North-window daylight','AREA');l.energy=1100;l.specular_factor=0.0;l.shape='RECTANGLE';l.size=7;l.size_y=9;l.color=(.76,.86,1)
 ob=bpy.data.objects.new('North-window daylight',l);scene.collection.objects.link(ob);ob.location=(x,1.1,8);ob.rotation_euler=(pi/2,0,0)

for x,y,z,power,siz in [(0,41,8.8,1200,8),(-28,40,6.2,700,6),(-20,63,12.8,4000,12),(0,63,12.8,4000,12),(20,63,12.8,4000,12)]:
 l=bpy.data.lights.new('Public-room bounced daylight','AREA');l.energy=power;l.specular_factor=0.0;l.color=(.91,.94,1);l.size=siz
 ob=bpy.data.objects.new('Public-room bounced daylight',l);scene.collection.objects.link(ob);ob.location=(x,y,z)
if not AGED:
 for x in [-43.85,43.5]:
  l=bpy.data.lights.new('Reading-room north-window bounce','AREA');l.energy=2600;l.specular_factor=0.0;l.color=(.88,.94,1);l.shape='RECTANGLE';l.size=12;l.size_y=5
  o=bpy.data.objects.new('Reading-room north-window bounce',l);scene.collection.objects.link(o);o.location=(x,5.9,5);o.rotation_euler=(pi/2,0,0)
 l=bpy.data.lights.new('Restaurant broad daylight bounce','AREA');l.energy=3000;l.specular_factor=0.0;l.color=(.95,.97,1);l.size=14
 o=bpy.data.objects.new('Restaurant broad daylight bounce',l);scene.collection.objects.link(o);o.location=(43.4,40,6.8)
for name,loc,target,power,size,color in [
 ('Elevator lobby daylight east entrance',(-51.9,40.,2.8),(-42.,40.,2.6),700,(3.1,3.5),(.80,.88,1.)),
 ('Elevator lobby daylight arcade',(-38.8,40.,3.3),(-46.,40.,2.8),350,(5.,4.),(1.,.92,.81)),
 ('Elevator lobby daylight upper bounce',(-44.,39.,5.48),(-44.,39.,.1),220 if AGED else 320,(3.,17.),(1.,.97,.93))]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='RECTANGLE';l.size,l.size_y=size;l.color=color;l.specular_factor=0;l.transmission_factor=0
 o=bpy.data.objects.new(name,l);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
scene['elevator_lighting_limit']='Original daylight/bounce exposure aids, not measured fixture power or dated photometry'
cams={
 'exterior':((112,-163,61),(0,29,30),43),
 'front':((0,-180,34),(0,28,31),44),
 'hall':((-31,15.8,2.4),(30,15.8,7.1),22),
 'hall_reverse':((30,14.5,2.5),(-31,16,7),22),
 'lobby':((0,32.7,2.2),(0,49,4.7),20),
 'concourse':((-25,62.9,2.5),(25,63.4,6.4),24),
 'arcade':((-37.5,40,1.85),(-8,40,3.6),24),
 'womens_room':((-43.8,20,1.85),(-43.8,5.5,4.3),22),
 'mens_room':((43.5,20,1.85),(43.5,5.5,4.4),22),
 'restaurant':((37.1,31,1.7),(48,48,4.7),23),
 'aerial':((132,-124,113),(0,33,18),47),
}
cams.update(globals().get('SECONDARY_CAMERAS',{}))
if not AGED:
 cams.update(globals().get('FRONTEND_CAMERAS',{}))
 cams.update(globals().get('STUDY_CAMERAS',{}))
 cams.update(globals().get('WEST_ROOM_CAMERAS',{}))
 cams.update(globals().get('TICKET_RETAIL_CAMERAS',{}))
cams.update(globals().get('NORTH_ENTRY_CAMERAS',{}))
cams.update(globals().get('TOWER_V2_CAMERAS',{}))
cams.update(globals().get('NORTH_PLAZA_CAMERAS',{}))
cams.update(globals().get('FORECOURT_2017_CAMERAS',{}))
cams.update(globals().get('HALL_LUNETTE_CAMERAS',{}))
cams.update(globals().get('CONCOURSE_WALL_CAMERAS',{}))
cams.update({name:(control['location'],control['target'],control['lens_mm']) for name,control in globals().get('CONCOURSE_ROOF_CAMERAS',{}).items()})
for name,(pos,target,lens) in cams.items():
 d=bpy.data.cameras.new(name);d.lens=lens;d.clip_end=1000;ob=bpy.data.objects.new('Camera '+name,d);scene.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
scene.camera=bpy.data.objects['Camera '+STATION_ARGS.render]
execute_component('render_lighting.py')
apply_camera_fill_mode(scene,STATION_ARGS.render)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=STATION_ARGS.samples;scene.cycles.use_denoising=True;scene.cycles.denoising_use_gpu=False;scene.cycles.max_bounces=8;scene.cycles.transmission_bounces=6;scene.cycles.transparent_max_bounces=8
scene.render.resolution_x=STATION_ARGS.width;scene.render.resolution_y=int(STATION_ARGS.width*.68);scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0.40
apply_camera_fill_mode(scene,STATION_ARGS.render)
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.filepath=str(ROOT/'renders'/f'michigan_central_{ERA}_{STATION_ARGS.render}.png')
# Remove only unreferenced in-memory image datablocks superseded during material
# construction. External source assets stay intact; every live node/world image remains.
_unused_images=[]
for im in list(bpy.data.images):
 if im.source=='FILE' and im.users==0:
  _unused_images.append(dict(name=im.name,source=im.filepath,pixels=list(im.size)))
  bpy.data.images.remove(im)
scene['unreferenced_image_datablock_cleanup']=json.dumps(_unused_images)
# Pack authored live textures only. Research photographs are never loaded as assets.
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
# Useful initial modeling view. The giant render-only ground is excluded from interchange exports.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active;space.clip_end=20000;space.region_3d.view_distance=195;space.region_3d.view_location=(0,29,26);space.region_3d.view_rotation=bpy.data.objects['Camera exterior'].rotation_euler.to_quaternion()
scene['component_sha256']=json.dumps(COMPONENT_HASHES)
model=ROOT/'models'/f'michigan_central_{ERA}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(model))
def artifact_hash(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as fh:
  for chunk in iter(lambda:fh.read(8*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
metrics={'source_blend_sha256':artifact_hash(model),'glb_exported_in_this_build':False,'glb_status':'not updated by this build; earlier GLB may exist','era':ERA,'blender':bpy.app.version_string,'build_code_sha256':BUILD_CODE_HASH,'component_sha256':COMPONENT_HASHES,'mesh_objects':len([o for o in scene.objects if o.type=='MESH']),'vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH'),'materials':len(M),'status':'work in progress; see render QA and evidence limitations','source_blend':str(model.relative_to(ROOT))}
(ROOT/'manifests'/f'metrics_{ERA}.json').write_text(json.dumps(metrics,indent=2))
print('SCENE BUILT',json.dumps(metrics),flush=True)
if not STATION_ARGS.no_export:
 bpy.ops.object.select_all(action='DESELECT')
 for ob in scene.objects:
  if (ob.type=='MESH' and ob.name!='landscape context') or ob.get('export_group') or ob.get('export_coverage_marker'):ob.select_set(True)
 bpy.ops.export_scene.gltf(use_selection=True,filepath=str(ROOT/'exports'/f'michigan_central_{ERA}.glb'),export_format='GLB',export_apply=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True)
 sys.path.insert(0,str(ROOT/'scripts'))
 from repair_glb_tangents import repair_glb_tangents
 repair_glb_tangents(ROOT/'exports'/f'michigan_central_{ERA}.glb',ROOT/'manifests'/f'tangent_repair_{ERA}_full.json')
 metrics['glb_exported_in_this_build']=True;metrics['glb_status']='synchronized to this source build';metrics['full_glb_sha256']=artifact_hash(ROOT/'exports'/f'michigan_central_{ERA}.glb')
 (ROOT/'manifests'/f'metrics_{ERA}.json').write_text(json.dumps(metrics,indent=2))
 (ROOT/'manifests'/f'export_lineage_{ERA}.json').write_text(json.dumps(dict(era=ERA,source_blend_sha256=metrics['source_blend_sha256'],full_glb_sha256=metrics['full_glb_sha256'],build_code_sha256=BUILD_CODE_HASH,component_sha256=COMPONENT_HASHES),indent=2))
 print('GLB EXPORTED AND TANGENT BASIS CHECKED',flush=True)
if not STATION_ARGS.no_render:
 bpy.ops.render.render(write_still=True)
 print('RENDER COMPLETE',scene.render.filepath,flush=True)
