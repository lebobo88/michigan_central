"""Bounded period-informed north forecourt, original authored geometry and PBR.

Execute before core batch finalization; call forecourt_2017_post_finalize once
AFTER batches. Add FORECOURT_2017_CAMERAS to the camera registry. Strictly emits
nothing in other eras. Dimensions, grade, inventories and condition patterns are
photo-fit approximations. Main visual evidence is a project PUBLISHED in 2017;
its individual photograph capture dates are not documented. No complete 2017
park, site survey, exact landscaping inventory or street engineering is claimed.
"""
from mathutils.geometry import tessellate_polygon as _f17_tessellate, delaunay_2d_cdt as _f17_cdt

FORECOURT_2017_CAMERAS = {}
FORECOURT_2017_INSTANCE_REQUESTS = []
FORECOURT_2017_STATS = {}
FORECOURT_2017_GROUPS = {
 'apron':'00F 2017 FORECOURT | 2017-published photo topology; approximate dimensions',
 'road':'00G 2017 FRONTAGE ROAD | bounded divided-road shell; approximate dimensions',
 'details':'00H 2017 FORECOURT DETAILS | observed classes; approximate detail and inventory',
 'shrubs':'00I 2017 FORECOURT SHRUBS | original shared meshes; approximate count and placement',
 'coverage':'90F 2017 NORTH SITE COVERAGE | beyond documented module boundary',
}
FORECOURT_2017_CONTROLS = {
 'coordinate_system':'meters; +X west, +Y south, +Z up',
 'station_front_glazing_y_m':0.0,
 'station_width_reference_m':105.2576,
 'dimensional_status':'PHOTO_FIT_APPROXIMATE, NOT SURVEYED',
 'source_date_status':'Dandelion Air creator photographs published in 2017; exact capture dates undocumented',
 'modeled_boundary_xy_m':[[-64,-49],[64,-49],[64,-.16],[-64,-.16]],
 'paired_bed_outer_extent_x_m':52.8,
 'paired_bed_station_edge_y_m':-9.4,
 'paired_bed_road_edge_y_m':-19.0,
 'central_opening_halfwidth_m':12.0,
 'central_side_lobe_radius_m':3.8,
 'sidewalk_north_edge_y_m':-23.0,
 'south_carriageway_north_edge_y_m':-35.5,
 'median_north_edge_y_m':-38.0,
 'bounded_north_carriageway_north_edge_y_m':-49.0,
 'median_extent_x_m':[-44.0,44.0],
 'surface_levels_local_m':{'apron':.035,'soil':.035,'sidewalk':.035,'road':-.085,'median':.08,'curb_top':.065},
 'flagpole_height_m':17.0,
 'vertical_caution':'Interpretive flat local datum. No measured curb height, crossfall, drainage or absolute elevation.',
 'inventory_caution':'Shrub, baluster, fence and light counts and positions are illustrative photo fits; species and exact fixtures unverified.',
 'coverage_limit':'Apron, paired beds, central pole/gate, sidewalk and bounded divided frontage road only. Broader park and junctions omitted.',
}
FORECOURT_2017_SOURCES = [
 {'id':'DAND2017_OBLIQUE','url':'https://spark.adobe.com/page/OMI5cVvEGgqxk/','local_reference':'research/south_structure/presentation_ref_12.jpg','creator':'Aleksey Bochkovsky / Dandelion Air','date_class':'Project published by 2017-09-15; capture date not stated','supports':'Paved apron; two planted beds; balustrades on station-facing edges and outer returns; inner low-curb lobes; pole, US flag and thin fencing'},
 {'id':'DAND2017_OVERHEAD','url':'https://spark.adobe.com/page/OMI5cVvEGgqxk/','local_reference':'research/south_structure/presentation_ref_13.jpg','creator':'Aleksey Bochkovsky / Dandelion Air','date_class':'Project published by 2017-09-15; capture date not stated','supports':'Near-facade-width paired beds; low separate shrubs and exposed soil; sidewalk; divided road with a narrow paved streetlight median'},
 {'id':'PIX4D_PUBLICATION','url':'https://community.pix4d.com/t/michigan-central-station-by-aleksey-bochkovsky-dandelion-air/3356','date_class':'Showcase publication dated 2017-09-15','supports':'2017 publication of linked creator presentation, not an exact image capture date'},
 {'id':'HD_UNDATED_CONTEXT','url':'https://historicdetroit.org/galleries/michigan-central-station-pre-restoration-exterior#p10','local_reference':'research/reference_only_copyrighted/hd_pre_10.jpg','creator':'Bob Laperriere / Historic Detroit','date_class':'Undated capture; filename is not dating evidence','supports':'Corroborative pre-restoration context only; broader park not reconstructed here'},
]


def f17_clean(poly):
 out=[]
 for p in poly:
  p=tuple(p[:2])
  if not out or math.dist(p,out[-1])>1e-7:out.append(p)
 if len(out)>2 and math.dist(out[0],out[-1])<1e-7:out.pop()
 return out


def f17_area(poly):
 return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))*.5


def f17_ccw(poly):
 p=f17_clean(poly)
 return p if f17_area(p)>0 else p[::-1]


def f17_inside(point,poly):
 x,y=point;inside=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside


def f17_slab(poly,z,depth,material,name):
 p=f17_ccw(poly);n=len(p)
 if n<3 or f17_area(p)<1e-7:return
 vertices=[(x,y,z) for x,y in p]+[(x,y,z-depth) for x,y in p]
 lookup={tuple(round(c,7) for c in (x,y,0)):i for i,(x,y) in enumerate(p)};faces=[]
 for triangle in _f17_tessellate([[Vector((x,y,0)) for x,y in p]]):
  ids=tuple(int(v) if isinstance(v,int) else lookup[tuple(round(c,7) for c in v)] for v in triangle)
  faces.extend([ids,tuple(n+i for i in ids[::-1])])
 for i in range(n):j=(i+1)%n;faces.append((i,n+i,n+j,j))
 addmesh(vertices,faces,material,name)


def f17_ribbon(points,width):
 p=f17_clean(points);left=[];right=[]
 for i,pt in enumerate(p):
  a=Vector(p[max(0,i-1)]);b=Vector(p[min(len(p)-1,i+1)]);d=(b-a).normalized();normal=Vector((-d.y,d.x))*width*.5
  left.append(tuple(Vector(pt)+normal));right.append(tuple(Vector(pt)-normal))
 return f17_ccw(left+right[::-1])


def f17_strip(points,width,z,depth,material,name):
 f17_slab(f17_ribbon(points,width),z,depth,material,name)


def f17_samples(points,spacing):
 lengths=[0.0]
 for a,b in zip(points,points[1:]):lengths.append(lengths[-1]+math.dist(a,b))
 count=max(1,round(lengths[-1]/spacing));result=[];j=0
 for i in range(count+1):
  t=lengths[-1]*i/count
  while j<len(points)-2 and lengths[j+1]<t:j+=1
  u=(t-lengths[j])/(lengths[j+1]-lengths[j]);result.append(tuple(a*(1-u)+b*u for a,b in zip(points[j],points[j+1])))
 return result


def f17_bed(sign):
 # Independently photo-fit. Do not substitute the 2026 footprint.
 outer=[(43.6+9.2*cos(pi/2-i*pi/2/24),-18.6+9.2*sin(pi/2-i*pi/2/24)) for i in range(25)]
 inner=[(12+3.8*cos(pi/2-i*pi/32),-14.6+3.8*sin(pi/2-i*pi/32)) for i in range(33)]
 rail=[(12,-9.4),(43.6,-9.4)]+outer[1:]
 poly=[(12,-19),(52.8,-19)]+outer[::-1]+[(12,-9.4),(12,-10.8)]+inner[1:]
 return f17_ccw([(sign*x,y) for x,y in poly]),[(sign*x,y) for x,y in rail],[(sign*x,y) for x,y in inner]


def f17_central_polygon():
 right=[(12+3.8*cos(pi/2-i*pi/32),-14.6+3.8*sin(pi/2-i*pi/32)) for i in range(33)]
 return f17_ccw([(-12,-.16),(12,-.16)]+right+[(12,-23),(-12,-23)]+[(-x,y) for x,y in right[::-1]])


def f17_partition_surfaces(boundary,polygons,z,classes,default):
 """Constrained planar partition: all soil/apron/paving tops are disjoint."""
 verts=[];edges=[];lookup={}
 for poly in [boundary]+polygons:
  ids=[]
  for x,y in f17_ccw(poly):
   key=(round(x,7),round(y,7))
   if key not in lookup:lookup[key]=len(verts);verts.append(Vector((x,y)))
   ids.append(lookup[key])
  edges.extend([(a,b) for a,b in zip(ids,ids[1:]+ids[:1]) if a!=b])
 cv,ce,cf,*_=_f17_cdt(verts,edges,[],0,1e-7,False)
 counts={};v=[(p.x,p.y,z) for p in cv]
 for face in cf:
  if len(face)!=3:raise AssertionError('Constrained partition must output triangles')
  center=tuple(sum(cv[i][j] for i in face)/3 for j in range(2))
  if not f17_inside(center,boundary):continue
  item=default
  for poly,matname,label in classes:
   if f17_inside(center,poly):item=(matname,label);break
  points=[v[i] for i in face]
  if (Vector(points[1])-Vector(points[0])).cross(Vector(points[2])-Vector(points[0])).z<0:points.reverse()
  addmesh(points,[(0,1,2)],item[0],item[1]);counts[item[1]]=counts.get(item[1],0)+1
 return counts


def f17_rail(points):
 f17_strip(points,.41,.23,.20,'F17 aged pale stone','2017 stone balustrade continuous base')
 f17_strip(points,.43,1.09,.14,'F17 aged pale stone','2017 stone balustrade upper rail')
 f17_strip(points,.34,.955,.065,'F17 aged pale stone','2017 stone balustrade rail bead')
 piers=f17_samples(points,5.5)
 for x,y in f17_samples(points,.46):
  if min(math.dist((x,y),p) for p in piers)<.42:continue
  lathe((x,y,.23),[(.10,0),(.106,.065),(.07,.13),(.058,.21),(.085,.31),(.104,.38),(.084,.46),(.063,.55),(.096,.65),(.096,.72)],'F17 aged pale stone','2017 original modeled turned balusters',12)
 for i,(x,y) in enumerate(piers):
  box((x,y,.57),(.68,.68,1.08),'F17 aged pale stone','2017 square balustrade piers')
  box((x,y,1.115),(.82,.81,.12),'F17 aged pale stone','2017 stone pier cap slabs')
 # Pier and profile counts are not measured inventories.


def f17_fence(x0,x1,y,gate=False):
 for x,_ in f17_samples([(x0,y),(x1,y)],2.6):
  beam((x,y,.14),(x,y,1.2),.014,'F17 weathered iron','2017 thin north fence posts',7)
 for z in [.29,1.17]:beam((x0,y,z),(x1,y,z),.008,'F17 weathered iron','2017 thin north fence horizontal wires',6)
 if gate:
  # Simplified low gate frame. Mesh gauge and actual lock/signs unverified.
  for a,b in [(x0,(x0+x1)/2),((x0+x1)/2,x1)]:
   for x in [a,b]:beam((x,y,.23),(x,y,1.17),.017,'F17 weathered iron','2017 central two-leaf gate frame',7)
   beam((a,y,.23),(b,y,1.17),.009,'F17 weathered iron','2017 gate diagonal brace',6)


def f17_lamp(x,y):
 # Thin pole with simple curved outreach. Not a manufacturer-certified fixture.
 lathe((x,y,.08),[(.16,0),(.16,.15),(.10,.29),(.079,4.7),(.063,9.7)],'F17 road pole','2017 median tapered streetlight poles',12)
 points=[]
 for j in range(17):
  t=j/16;points.append((x,y+1.35*t,9.78+.62*sin(t*pi/2)))
 for a,b in zip(points,points[1:]):beam(a,b,.049,'F17 road pole','2017 median curved light outreach',10)
 box((x,y+1.54,10.38),(.23,.57,.105),'F17 road pole','2017 approximate road luminaire housings')
 box((x,y+1.56,10.322),(.175,.46,.02),'F17 pale lamp glass','2017 road luminaire underside')


def f17_flag():
 height=FORECOURT_2017_CONTROLS['flagpole_height_m'];x,y=0,-16.2
 box((x,y,.15),(.78,.78,.23),'F17 aged pale stone','2017 central flagpole footing approximate')
 lathe((x,y,.24),[(.072,0),(.069,5),(.052,height-.35),(.032,height-.24)],'F17 flagpole metal','2017 central flagpole',16)
 lathe((x,y,height),[(0,-.055),(.073,-.02),(.09,.025),(.067,.081),(0,.10)],'F17 flagpole metal','2017 flagpole finial approximate',16)
 # A symbolic original flag with approximate wind shape, physically separate front/back faces.
 w,h=2.65,1.395;nx,ny=40,20;vertices=[];uv=[]
 for j in range(ny+1):
  v=j/ny
  for i in range(nx+1):
   u=i/nx;vertices.append((x+.05+w*u,y+(.19*sin(u*pi*3-v*.55)+.06*sin(u*pi*7+v))*u,height-.35-h*v-.20*u*u));uv.append((u,1-v))
 faces=[]
 for j in range(ny):
  for i in range(nx):
   a=j*(nx+1)+i;b=a+1;c=b+nx+1;d=a+nx+1;faces.extend([(a,b,c),(a,c,d)])
 addmesh(vertices,faces,'F17 authored US flag','2017 US flag original cloth mesh',uv=uv)
 beam((x+.083,y,.4),(x+.083,y,height-.17),.005,'F17 flagpole metal','2017 flagpole halyard',5)


def f17_request_shrubs(bed,sign):
 r=random.Random(17009+sign);count=0
 for row,y in enumerate([-11.0,-13.30,-15.60,-17.75]):
  for col in range(17):
   x=16.2+col*2.02+(row%2)*.64
   q=(sign*(x+r.uniform(-.16,.16)),y+r.uniform(-.19,.19))
   if not f17_inside(q,bed):continue
   if any(not f17_inside((q[0]+dx,q[1]+dy),bed) for dx,dy in [(.63,0),(-.63,0),(0,.58),(0,-.58)]):continue
   FORECOURT_2017_INSTANCE_REQUESTS.append({'location':(q[0],q[1],.025),'scale':r.uniform(.76,1.12),'rotation':r.random()*2*pi,'variant':r.randrange(4)})
   count+=1
 return count


def f17_original_shrub(variant):
 """Four low-memory shared original shrub meshes; no external plant assets."""
 import bmesh as _f17_bmesh
 global B,GROUP
 oldb,oldg=B,GROUP;B={};GROUP='F17 prototype';r=random.Random(81700+variant)
 try:
  lathe((0,0,.01),[(.033,0),(.024,.20),(.014,.44)],'F17 woody stem','original low shrub stem',7)
  for j in range(10):
   t=j*pi/5+r.random()*.3;tip=(.31*cos(t),.31*sin(t),r.uniform(.32,.60));beam((0,0,.12),tip,.012,'F17 woody stem','original shrub small branches',6)
  # Slightly irregular ovoid envelope, individual modeled leaves and open soil.
  for j in range(1200):
   az=r.random()*2*pi;zz=r.uniform(-1,1);rr=(r.random()**.36)*sqrt(1-zz*zz)
   p=Vector((.57*rr*cos(az),.52*rr*sin(az),.36+.34*zz))
   t=r.random()*2*pi;length=r.uniform(.034,.067);u=Vector((cos(t),sin(t),r.uniform(-.60,.55))).normalized()*length;v=Vector((-sin(t),cos(t),r.uniform(-.25,.25))).normalized()*length*.46
   points=[p-u,p-u*.28+v,p+u*.55+v*.7,p+u,p+u*.55-v*.7,p-u*.28-v,p+Vector((0,0,length*.12))]
   addmesh([tuple(a) for a in points],[(6,k,(k+1)%6) for k in range(6)],'F17 shrub leaf '+str(r.choices([0,1,2],[.45,.38,.17])[0]),'original explicit low shrub leaves',uv=[(0,.5),(.36,1),(.76,.84),(1,.5),(.76,.16),(.36,0),(.5,.5)])
  batches=B
 finally:B,GROUP=oldb,oldg
 vv=[];ff=[];uvfaces=[];mi=[];materials=[]
 for (group,material,label),(verts,faces,uvs) in batches.items():
  if material not in materials:materials.append(material)
  offset=len(vv);vv.extend(verts);ff.extend(tuple(offset+i for i in f) for f in faces);mi.extend([materials.index(material)]*len(faces))
  for f,u in zip(faces,uvs):
   if u is not None:uvfaces.append(u)
   else:
    a,b,c=[Vector(verts[i]) for i in f[:3]];normal=(b-a).cross(c-a);ax=max(range(3),key=lambda k:abs(normal[k]));ids=[1,2] if ax==0 else [0,2] if ax==1 else [0,1];uvfaces.append([(verts[i][ids[0]],verts[i][ids[1]]) for i in f])
 mesh=bpy.data.meshes.new('F17 shared original shrub '+str(variant));mesh.from_pydata(vv,[],ff);mesh.update()
 for material in materials:mesh.materials.append(M[material])
 uv=mesh.uv_layers.new(name='MetricUV')
 for p,index,xy in zip(mesh.polygons,mi,uvfaces):
  p.material_index=index;p.use_smooth=not materials[index].startswith('F17 shrub leaf')
  scale=M[materials[index]].get('texture_repeat_m',1)
  for li,q in zip(p.loop_indices,xy):uv.data[li].uv=(q[0]/scale,q[1]/scale)
 bm=_f17_bmesh.new();bm.from_mesh(mesh);caps=[f for f in bm.faces if len(f.verts)>4]
 if caps:_f17_bmesh.ops.triangulate(bm,faces=caps)
 bm.to_mesh(mesh);bm.free();mesh.update();mesh['provenance']='Original seeded explicit stems and 1200 polygon leaves; no external vegetation geometry'
 return mesh


def forecourt_2017_post_finalize(collections=None,room_nodes=None):
 """Link shared plant Mesh datablocks and non-rendering coverage marker empties."""
 if ERA!='2017' or scene.get('forecourt_2017_post_finalized',False):return
 group=FORECOURT_2017_GROUPS['shrubs'];col=bpy.data.collections.new(group);scene.collection.children.link(col)
 parent=bpy.data.objects.new(group,None);col.objects.link(parent);parent['export_group']=True;parent['space']=group;parent['era']=ERA
 cache={}
 for i,req in enumerate(FORECOURT_2017_INSTANCE_REQUESTS):
  v=req['variant']
  if v not in cache:cache[v]=f17_original_shrub(v)
  ob=bpy.data.objects.new('2017 forecourt shrub '+str(i).zfill(3),cache[v]);col.objects.link(ob);ob.parent=parent;ob.location=req['location'];ob.rotation_euler.z=req['rotation'];s=req['scale'];ob.scale=(s,s,s);ob['original_shared_mesh']=True;ob['era']=ERA;ob['space']=group;ob['evidence_status']='Low shrubs in roughly regular rows visible; exact count, species and placement unverified'
 if collections is not None:collections[group]=col
 if room_nodes is not None:room_nodes[group]=parent
 cover=bpy.data.collections.new(FORECOURT_2017_GROUPS['coverage']);scene.collection.children.link(cover)
 for name,location,reason in [
  ('2017 north park beyond frontage road | UNMODELED',(0,-51,0),'Broader park context is from an undated photograph; no precise 2017 park inventory or layout asserted. Crescent island, divided boulevard, lawns, paths and trees are omitted.'),
  ('2017 east junction | UNVERIFIED',(-65,-29,0),'Local curb island fragments are visible; junction extents, turns and traffic controls are not dimensioned and not reconstructed.'),
  ('2017 west junction | UNVERIFIED',(65,-29,0),'Local curb island fragments are visible; junction extents, turns and traffic controls are not dimensioned and not reconstructed.'),
  ('2017 apron markings | PARTIAL EVIDENCE',(0,-5,0),'Faint angled stripes are visible but full layout/use is unknown; no parking-bay inventory or road lane-use plan fabricated.'),
  ('2017 site grading | UNMEASURED',(58,-20,0),'All surface levels are an interpretive flat local datum; no survey, drainage or accessibility compliance implied.'),
 ]:
  ob=bpy.data.objects.new(name,None);cover.objects.link(ob);ob.location=location;ob.empty_display_type='PLAIN_AXES';ob.empty_display_size=1.8;ob['coverage_status']='unmodeled or unverified';ob['reason']=reason;ob['era']=ERA;ob['export_coverage_marker']=True
 for ob in scene.objects:
  if ob.type=='MESH' and ob.get('space','') in list(FORECOURT_2017_GROUPS.values()):
   ob['era']=ERA;ob['source_date_status']=FORECOURT_2017_CONTROLS['source_date_status'];ob['dimensional_status']='Photo-fit approximate; not surveyed'
 scene['forecourt_2017_post_finalized']=True;scene['forecourt_2017_shared_mesh_count']=len(cache);scene['forecourt_2017_instance_count']=len(FORECOURT_2017_INSTANCE_REQUESTS)
 scene['forecourt_2017_unique_prototype_vertices']=sum(len(me.vertices) for me in cache.values())


def f17_build():
 global GROUP
 saved_group=GROUP
 try:
  for name,asset,repeat in [('F17 worn gray apron','weathered_apron',4),('F17 exposed brown soil','exposed_soil',2),('F17 pale sidewalk','pale_sidewalk',3),('F17 median concrete','median_concrete',3)]:
   pbr(name,'../forecourt_2017/textures/'+asset,repeat)
  pbr('F17 asphalt','../north_plaza/textures/np_asphalt',2)
  m=M['Exterior Indiana limestone'].copy();m.name='F17 aged pale stone';M[m.name]=m;m['texture_provenance']='Reused original project limestone_2017 PBR, never source photograph pixels'
  for name,color,rough,metal in [('F17 weathered iron',(.08,.085,.073),.72,.50),('F17 flagpole metal',(.34,.33,.27),.52,.7),('F17 road pole',(.14,.15,.135),.70,.48),('F17 pale lamp glass',(.54,.53,.45),.55,.05),('F17 joint',(.14,.139,.123),.98,0),('F17 crack',(.095,.093,.081),.99,0),('F17 woody stem',(.14,.105,.061),.96,0),('F17 shrub leaf 0',(.026,.050,.012),.88,0),('F17 shrub leaf 1',(.044,.074,.018),.85,0),('F17 shrub leaf 2',(.069,.103,.025),.83,0)]:mat(name,color,rough,metal)
  for name in ['F17 shrub leaf 0','F17 shrub leaf 1','F17 shrub leaf 2']:M[name].use_backface_culling=False
  m=mat('F17 authored US flag',(.8,.8,.75),.88);m['texture_repeat_m']=1;m['texture_provenance']='Original geometric drawing, 13 stripes and 50 stars; not a downloaded flag photograph';tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'assets/forecourt_2017/textures/authored_us_flag/basecolor.png'),check_existing=True);m.node_tree.links.new(tex.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);m.use_backface_culling=False
  GROUP=FORECOURT_2017_GROUPS['apron'];boundary=[(-64,-23),(64,-23),(64,-.16),(-64,-.16)];central=f17_central_polygon();beditems=[f17_bed(s) for s in [-1,1]];beds=[p[0] for p in beditems];sidewalk=[(-64,-23),(64,-23),(64,-19),(-64,-19)]
  classes=[(p,'F17 exposed brown soil','2017 paired low-shrub soil beds') for p in beds]+[(sidewalk,'F17 pale sidewalk','2017 station-side sidewalk'),(central,'F17 pale sidewalk','2017 central flagpole plaza and side lobes')]
  FORECOURT_2017_STATS['surface_partition']=f17_partition_surfaces(boundary,beds+[central,sidewalk],.035,classes,('F17 worn gray apron','2017 broad paved station apron'))
  # Vertical bounded shell fascia only, not an overlapping plane under the partition.
  for a,b in zip(boundary,boundary[1:]+boundary[:1]):addmesh([(a[0],a[1],.035),(b[0],b[1],.035),(b[0],b[1],-.14),(a[0],a[1],-.14)],[(0,3,2,1)],'F17 worn gray apron','2017 bounded apron edge shell')
  shrub_counts=[]
  for sign,(bed,rail,inner) in zip([-1,1],beditems):
   f17_rail(rail);f17_strip(inner,.20,.19,.155,'F17 aged pale stone','2017 low-curb central side lobe')
   f17_strip([(sign*12,-19),(sign*52.8,-19)],.23,.17,.15,'F17 aged pale stone','2017 low road-facing bed edging')
   f17_fence(sign*12,sign*52.8,-19.025);shrub_counts.append(f17_request_shrubs(bed,sign))
  # Sparse paving joints, plus restrained original, non-source-traced crack paths.
  for x in range(-60,61,3):
   if abs(x)<12:continue
   box((x,-4.9,.037),(.012,9.35,.003),'F17 joint','2017 apron interpretive expansion joints')
  for y in [-3.2,-6.25]:
   for a,b in [(-63,-12),(12,63)]:box(((a+b)/2,y,.037),(b-a,.012,.003),'F17 joint','2017 apron transverse joint segments')
  for x in range(-60,61,3):box((x,-21,.037),(.012,3.72,.003),'F17 joint','2017 sidewalk interpretive joints')
  for x in [-9,-6,-3,0,3,6,9]:box((x,-11.2,.037),(.009,21.4,.003),'F17 joint','2017 central paving interpretive joints')
  for y in [-2.3,-5.0,-7.7,-10.4,-13.1,-15.8,-18.5,-21.2]:box((0,y,.037),(23.7,.009,.003),'F17 joint','2017 central plaza joint segments')
  crack_rng=random.Random(201709)
  for j in range(45):
   x=crack_rng.uniform(-61,60);y=crack_rng.uniform(-8.9,-.65)
   if abs(x)<12.5:continue
   points=[(x,y)]
   for k in range(crack_rng.randrange(2,5)):
    points.append((max(-63,min(63,points[-1][0]+crack_rng.uniform(.18,.60))),max(-9.0,min(-.4,points[-1][1]+crack_rng.uniform(-.60,.60)))))
   f17_strip(points,.009,.038,.002,'F17 crack','2017 non-source-traced apron wear cracks')
  GROUP=FORECOURT_2017_GROUPS['details'];f17_flag()
  for a,b in [(-12,-1.8),(1.8,12)]:f17_fence(a,b,-19.025)
  f17_fence(-1.8,1.8,-19.025,True)
  GROUP=FORECOURT_2017_GROUPS['road']
  # Both asphalt carriageways are separated by a genuine slender paved median.
  f17_slab([(-64,-35.5),(64,-35.5),(64,-23),(-64,-23)],-.085,.22,'F17 asphalt','2017 bounded southern frontage carriageway')
  f17_slab([(-64,-49),(64,-49),(64,-38),(-64,-38)],-.085,.22,'F17 asphalt','2017 bounded northern frontage carriageway')
  for a,b in [(-64,-44),(44,64)]:f17_slab([(a,-38),(b,-38),(b,-35.5),(a,-35.5)],-.085,.22,'F17 asphalt','2017 bounded median-end asphalt continuity')
  median=[(-42.75,-38),(42.75,-38)]+[(42.75+1.25*cos(-pi/2+i*pi/16),-36.75+1.25*sin(-pi/2+i*pi/16)) for i in range(1,17)]+[(-42.75,-35.5)]+[(-42.75+1.25*cos(pi/2+i*pi/16),-36.75+1.25*sin(pi/2+i*pi/16)) for i in range(1,17)]
  f17_slab(median,.08,.195,'F17 median concrete','2017 narrow paved streetlight median')
  # Fill the four small corners outside rounded median ends; no overlapping asphalt top.
  for sign in [-1,1]:
   for north in [True,False]:
    cy=-36.75;angles=[(-pi/2+i*pi/16) if north else (i*pi/16) for i in range(9)];arc=[(sign*(42.75+1.25*cos(t)),cy+1.25*sin(t)) for t in angles]
    corners=[(sign*44,cy-1.25 if north else cy+1.25),(sign*42.75,cy-1.25 if north else cy+1.25)]
    # Original arc order differs by corner; convex hull would overwrite median. Triangle fans are avoided.
    poly=([arc[0],*arc[1:],(sign*44,cy-1.25)] if north else [arc[0],(sign*44,cy+1.25),*arc[:0:-1]])
    f17_slab(poly,-.085,.22,'F17 asphalt','2017 asphalt around rounded median tips')
  f17_strip([(-64,-23),(64,-23)],.22,.065,.21,'F17 pale sidewalk','2017 station-side road curb')
  for x in range(-39,40,3):box((x,-36.75,.0815),(.012,2.46,.003),'F17 joint','2017 median slab joints')
  GROUP=FORECOURT_2017_GROUPS['details']
  for x in [-40,0,40]:f17_lamp(x,-36.75)
  FORECOURT_2017_STATS.update({'shrubs_per_bed':shrub_counts,'instance_requests':len(FORECOURT_2017_INSTANCE_REQUESTS),'bed_polygons_xy_m':beds,'central_polygon_xy_m':central,'coverage_markers':5,'streetlight_count_approximate':3,'trees_in_beds':0})
  scene['forecourt_2017_status']='Bounded period-informed shell. 2017-published photographs, capture dates undocumented; dimensions and grades approximate.'
  scene['forecourt_2017_controls']=json.dumps(FORECOURT_2017_CONTROLS);scene['forecourt_2017_source_metadata']=json.dumps(FORECOURT_2017_SOURCES)
  scene['forecourt_2017_rights']='Only original authored/procedural geometry and textures. Reference photographs remain reference-only and are never embedded.'
  scene['forecourt_2017_beyond_boundary']='No complete precise 2017 Roosevelt Park reconstruction: north park, junctions and site grading remain gaps.'
 finally:GROUP=saved_group


if ERA=='2017':
 f17_build()
 FORECOURT_2017_CAMERAS={
  'forecourt_2017_oblique':((92,-106,59),(0,-22,1.6),40),
  'forecourt_2017_overhead':((0,-25,155),(0,-25,0),38),
  'forecourt_2017_axis':((0,-47,2.1),(0,-3,6.0),36),
 }
