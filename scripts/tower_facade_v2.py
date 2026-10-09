"""Photo-led Michigan Central tower shell, batch-context component, both eras.

No research raster is used as a material. Dimensions remain historical-plan anchors
and explicitly identified photo-proportioned trials, not a surveyed 2026 as-built.
Execute before the core-owned four terraces, replacing the old TOWER block. Remove
its post-terrace glazing/corner-infill block too; this component owns those pieces.
Uses the main builder's addmesh/box/lathe/beam/material context. Restores GROUP.
"""
import math as _tv2_math

_TV2_PREVIOUS_GROUP = GROUP
_TV2_STONE = 'Tower muted ornamental terra cotta'
_TV2_BRICK = 'Tower buff brick'
_TV2_FRAME = 'Tower 2015 green gray painted frames'
_TV2_PANEL = 'Tower 2015 shallow green gray spandrels'
_TV2_GLASS = 'Tower 2015 replacement insulating glass'
_TV2_STOP = 'Tower unobserved interior optical stop'
_TV2_JOINT = 'Tower recessed dark joint'

# Width/depth and typical story height retain the original 1914 plan anchors.
TW=104.2416; TF=27.5; TD=32.9184; CORE=16.4592; WING=16.4592
PITCH=(TW-2*WING)/18; Z0=15.28; floorh=3.81; floors=12
# "floors" remains a compatibility alias for the old 12 facade slots, not a
# claim about station floor numbering. Slot 12 is now a distinct upper register.
topbase=Z0+floors*floorh
_TV2_CFG={
 'shaft_rows':11, 'register_height':floorh,
 'core_roof_top':topbase+9.11, 'pavilion_roof_top':topbase+9.11,
 'core_entablature_height':2.60, 'pavilion_entablature_height':2.85,
 'regular_clear_width_ratio':.535, 'regular_clear_height':2.73,
 'crown_clear_width_ratio':.635, 'wall_thickness':.52,
 'glazing_recess':.265, 'neutral_optical_stop_depth':1.15,
 'narrow_end_shaft_width_ratio':.23, 'narrow_end_crown_width_ratio':.24,
}
_TV2_CFG.update(globals().get('TOWER_V2_PARAMETERS',{}))
_TV2_REG_Z=Z0+_TV2_CFG['shaft_rows']*floorh
_TV2_CROWN_Z=_TV2_REG_Z+_TV2_CFG['register_height']
_TV2_DIAGNOSTICS={'regular_windows':0,'register_windows':0,'crown_windows':0,
                  'podium_windows':0,'crown_arched_windows':0,'crown_rectangular_end_stacks':0,
                  'crown_rectangular_end_windows':0,'narrow_shaft_windows':0,'facade_segments':[], 'opening_clearances':[]}

# Stable painted-metal appearance is common to both eras: tower replacements were
# installed in 2015. No windowless 2017 ruin and no invented blind/tenant inventory.
for _name,_color,_rough,_metal,_trans in [
 (_TV2_FRAME,(.275,.325,.305),.40,.28,0),
 (_TV2_PANEL,(.315,.365,.345),.47,.16,0),
 (_TV2_GLASS,(.61,.72,.71),.10 if AGED else .075,0,.86),
 (_TV2_STOP,(.019,.025,.025),.98,0,0),
 (_TV2_JOINT,(.065,.058,.047),.90,0,0),
]:
 if _name not in M:mat(_name,_color,_rough,_metal,_trans)
 M[_name]['texture_provenance']='Original material definition; no photograph or blind inventory'
 M[_name]['era_evidence']='2015 installed tower windows retained in 2017; 2026 photographed frame family'
M[_TV2_GLASS].node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.52
M[_TV2_GLASS]['physical_note']='Recessed 18mm modeled glazing; continuous tint; reflection changes come from scene and orientation'
M[_TV2_STOP]['scope']='Unmodeled private interior optical occlusion only; not a documented room partition or fit-out'
if _TV2_STONE not in M:
 # Reuse the existing original authored stone maps only. Material naming preserves
 # the documented ornamental terra-cotta class rather than calling the crown marble.
 _m=M['Exterior Indiana limestone'].copy();_m.name=_TV2_STONE;M[_TV2_STONE]=_m
 _m['material_class']='Muted stone-like ornamental terra cotta; source photographs establish appearance, not a material scan'
 _m['texture_provenance']='Existing original authored limestone-class support maps reused as terra-cotta appearance approximation'


def tv2_prism(xy,z0,z1,material,name):
 """Closed XY extrusion with explicit outward winding and metric face UVs."""
 if z1<=z0+1e-8:return
 pts=[tuple(q) for q in xy]
 signed=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(pts,pts[1:]+pts[:1]))
 if signed<0:pts.reverse()
 n=len(pts);v=[(x,y,z) for z in (z0,z1) for x,y in pts]
 f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 uv=[[(v[i][0],v[i][1]) for i in face] for face in f]
 for i in range(n):
  j=(i+1)%n;f.append((i,j,j+n,i+n));length=_tv2_math.dist(pts[i],pts[j])
  uv.append([(0,z0),(length,z0),(length,z1),(0,z1)])
 addmesh(v,f,material,name,face_uv=uv)


def tv2_xy(face,u,d):
 p=face['p'];t=face['t'];n=face['n']
 return (p[0]+t[0]*u+n[0]*d,p[1]+t[1]*u+n[1]*d)


def tv2_block(face,u0,u1,d0,d1,z0,z1,material,name,miter=False):
 """Face-local closed prism. Optional exact miters for whole perimeter strips."""
 if min(u1-u0,d1-d0,z1-z0)<=1e-7:return
 left=abs(u0)<1e-7 and miter;right=abs(u1-face['length'])<1e-7 and miter
 def edge(u,d,isleft,isright):
  return u+(face['left_miter']*d if isleft else face['right_miter']*d if isright else 0)
 xy=[tv2_xy(face,edge(u0,d0,left,False),d0),tv2_xy(face,edge(u1,d0,False,right),d0),
     tv2_xy(face,edge(u1,d1,False,right),d1),tv2_xy(face,edge(u0,d1,left,False),d1)]
 tv2_prism(xy,z0,z1,material,name)


def tv2_band(face,z0,z1,d0,d1,material,name):
 tv2_block(face,0,face['length'],d0,d1,z0,z1,material,name,True)


def tv2_local_poly(face,profile,d0,d1,material,name):
 """Closed polygon in U/Z extruded along the outward normal, metric UVs."""
 pts=[tuple(p) for p in profile];signed=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(pts,pts[1:]+pts[:1]))
 if signed<0:pts.reverse()
 n=len(pts);v=[(*tv2_xy(face,u,d),z) for d in (d0,d1) for u,z in pts]
 # U x Z points outward: t cross up = n, so front cap follows profile order.
 f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 uv=[[(pts[i%n][0],pts[i%n][1]) for i in faceids] for faceids in f]
 for i in range(n):
  j=(i+1)%n;f.append((i,j,j+n,i+n));length=_tv2_math.dist(pts[i],pts[j])
  uv.append([(0,d0),(length,d0),(length,d1),(0,d1)])
 addmesh(v,f,material,name,face_uv=uv)


def tv2_intervals(face,centers,halfwidth):
 last=0.0
 widths=halfwidth if isinstance(halfwidth,(list,tuple)) else [halfwidth]*len(centers)
 for c,hw in zip(centers,widths):
  if c-hw>last+1e-8:yield(last,c-hw)
  last=c+hw
 if face['length']>last+1e-8:yield(last,face['length'])


def tv2_bay_cells(face,kind):
 """Per-bay opening types; side end strips are narrow, never extra arches."""
 out=[]
 for c,style in zip(face['centers'],face['bay_types']):
  narrow=style=='narrow_rectangular_end'
  if kind=='crown':ratio=_TV2_CFG['narrow_end_crown_width_ratio'] if narrow else _TV2_CFG['crown_clear_width_ratio'];extra=.19
  elif kind=='register':ratio=_TV2_CFG['narrow_end_shaft_width_ratio'] if narrow else .51;extra=.26
  else:ratio=_TV2_CFG['narrow_end_shaft_width_ratio'] if narrow else _TV2_CFG['regular_clear_width_ratio'];extra=.20
  w=face['pitch']*ratio
  out.append({'center':c,'clear_width':w,'rough_width':w+extra,'style':style,'narrow':narrow})
 return out


def tv2_rectangle_frame(face,c,z0,w,h,prefix,stone_sill=False,center_mullion=True):
 """True recessed pane, seals, 65mm perimeter, one principal center mullion."""
 rr=_TV2_CFG['glazing_recess'];pane0=-rr-.009;pane1=-rr+.009
 tv2_block(face,c-w/2,c+w/2,pane0,pane1,z0,z0+h,_TV2_GLASS,prefix+' insulating glazing')
 # Black gaskets sit behind, narrower than the frame; no coplanar front overlays.
 for side in (-1,1):
  x=c+side*(w/2+.017)
  tv2_block(face,x-.026,x+.026,-rr-.028,-rr+.021,z0-.034,z0+h+.034,_TV2_JOINT,prefix+' recessed glazing seals')
  x=c+side*(w/2+.044)
  tv2_block(face,x-.0325,x+.0325,-rr-.055,-rr+.090,z0-.065,z0+h+.065,_TV2_FRAME,prefix+' perimeter jambs')
 for z in (z0-.0325,z0+h+.0325):
  tv2_block(face,c-w/2-.012,c+w/2+.012,-rr-.055,-rr+.090,z-.0325,z+.0325,_TV2_FRAME,prefix+' head and sill frames')
 if center_mullion:
  tv2_block(face,c-.025,c+.025,-rr+.013,-rr+.075,z0,z0+h,_TV2_FRAME,prefix+' central mullions')
 # Two simple sash portions, observed green-gray rails; no independent random blinds.
 z=z0+h*.39
 tv2_block(face,c-w/2,c+w/2,-rr+.010,-rr+.078,z-.021,z+.021,_TV2_FRAME,prefix+' sash meeting rails')
 tv2_block(face,c-w/2-.092,c+w/2+.092,-.52,-.06,z0-.19,z0-.083,
           _TV2_STONE if stone_sill else _TV2_PANEL,prefix+' projecting sills')
 # Deep, opaque optical termination conveys unobserved interiors without inventing fit-out.
 tv2_block(face,c-w/2-.09,c+w/2+.09,-_TV2_CFG['neutral_optical_stop_depth']-.025,
           -_TV2_CFG['neutral_optical_stop_depth'],z0-.08,z0+h+.08,_TV2_STOP,prefix+' unobserved interior optical stop')


def tv2_shaft(face):
 pitch=face['pitch'];cells=tv2_bay_cells(face,'shaft')
 ztop=_TV2_REG_Z;dep=_TV2_CFG['wall_thickness']
 for a,b in tv2_intervals(face,face['centers'],[q['rough_width']/2 for q in cells]):
  tv2_block(face,a,b,-dep,0,Z0,ztop,_TV2_BRICK,'tower continuous buff brick shaft piers',True)
 for cell in cells:
  c=cell['center'];clearw=cell['clear_width'];rough=cell['rough_width']
  for row in range(_TV2_CFG['shaft_rows']):
   zb=Z0+row*floorh;clearz=zb+.775;clearh=_TV2_CFG['regular_clear_height']
   tv2_rectangle_frame(face,c,clearz,clearw,clearh,'tower narrow end shaft replacement window' if cell['narrow'] else 'tower regular replacement window',center_mullion=not cell['narrow'])
   # Framed metal infill spans only the opening strip; each row shares the same
   # paint, and the masonry pier remains uninterrupted over all eleven rows.
   for zlo,zhi in ((zb,clearz-.078),(clearz+clearh+.078,zb+floorh)):
    tv2_block(face,c-rough/2,c+rough/2,-dep,-.087,zlo,zhi,_TV2_PANEL,'tower shallow opaque spandrel panels')
   # A recessed central field and narrow raised border make the panel physically legible.
   pz0=zb+.07;pz1=clearz-.13
   if pz1>pz0:
    for uu in (c-rough/2+.047,c+rough/2-.047):
     tv2_block(face,uu-.016,uu+.016,-.088,-.065,pz0,pz1,_TV2_FRAME,'tower spandrel perimeter beads')
   # Reveal returns close the actual masonry gap around the larger pane.
   for side in (-1,1):
    uu=c+side*(rough/2-.027)
    tv2_block(face,uu-.027,uu+.027,-dep,-.062,clearz-.077,clearz+clearh+.077,_TV2_FRAME,'tower recessed masonry opening returns')
   _TV2_DIAGNOSTICS['regular_windows']+=1
   if cell['narrow']:_TV2_DIAGNOSTICS['narrow_shaft_windows']+=1
   _TV2_DIAGNOSTICS['opening_clearances'].append({'kind':'regular','bay_type':cell['style'],'face':face['id'],'clear_width':clearw,'rough_width':rough,'clear_height':clearh,'pitch':pitch})
  # Modest terminal lintel and keystone mark the shaft-to-register transition.
  tv2_block(face,c-rough/2-.065,c+rough/2+.065,-dep,.09,ztop-.12,ztop+.11,_TV2_STONE,'tower shaft terminal lintels')
  tv2_local_poly(face,[(c-.135,ztop-.39),(c+.135,ztop-.39),(c+.205,ztop+.10),(c-.205,ztop+.10)],-.03,.13,_TV2_STONE,'tower shaft terminal keystones')


def tv2_register(face):
 """Distinct squat-window stone belt, framed panels, and continuous sill/header."""
 dep=_TV2_CFG['wall_thickness'];z0=_TV2_REG_Z;z1=_TV2_CROWN_Z
 h=1.87;clearz=z0+.58;cells=tv2_bay_cells(face,'register')
 tv2_band(face,z0,z0+.40,-dep,.085,_TV2_STONE,'tower upper register continuous sill band')
 tv2_band(face,z1-.62,z1-.28,-dep,.11,_TV2_STONE,'tower upper register continuous header band')
 tv2_band(face,z1-.28,z1-.07,-dep,.26,_TV2_STONE,'tower crown base stepped ledge lower molding')
 tv2_band(face,z1-.07,z1+.16,-dep,.49,_TV2_STONE,'tower crown base projecting ledge coping')
 for a,b in tv2_intervals(face,face['centers'],[q['rough_width']/2 for q in cells]):
  tv2_block(face,a,b,-dep,0,z0+.40,z1-.62,_TV2_STONE,'tower register stone framed piers',True)
  # Recessed rectangular stone relief fields are bounded by raised rails.
  mid=(a+b)/2;ww=max(.08,b-a-.24)
  if ww>.30:
   tv2_block(face,mid-ww/2,mid+ww/2,.009,.029,z0+.67,z1-.82,_TV2_STONE,'tower register recessed rectangular relief fields')
   for uu in (mid-ww/2,mid+ww/2):
    tv2_block(face,uu-.035,uu+.035,.030,.075,z0+.64,z1-.79,_TV2_STONE,'tower register relief frame stiles')
   for zz in (z0+.64,z1-.79):
    tv2_block(face,mid-ww/2,mid+ww/2,.030,.075,zz-.035,zz+.035,_TV2_STONE,'tower register relief frame rails')
 for cell in cells:
  c=cell['center'];w=cell['clear_width'];roughw=cell['rough_width']
  tv2_rectangle_frame(face,c,clearz,w,h,'tower narrow end register window' if cell['narrow'] else 'tower special upper register window',True,not cell['narrow'])
  for lo,hi in ((z0+.40,clearz-.09),(clearz+h+.09,z1-.62)):
   tv2_block(face,c-roughw/2,c+roughw/2,-dep,0,lo,hi,_TV2_STONE,'tower register window lintel and apron')
  for ss in (-1,1):
   u=c+ss*(w/2+.103)
   tv2_block(face,u-.04,u+.04,-dep,.075,clearz-.10,clearz+h+.10,_TV2_STONE,'tower register projecting stone jambs')
  _TV2_DIAGNOSTICS['register_windows']+=1
 # Small repeated dentils under the crown-base ledge; larger pavilion consoles
 # are concentrated at shared piers, not arbitrarily repeated within each window.
 for j in range(max(1,int(face['length']/.43))):
  u=(j+.5)*face['length']/max(1,int(face['length']/.43))
  tv2_block(face,u-.075,u+.075,.10,.37,z1-.39,z1-.12,_TV2_STONE,'tower crown base ledge dentils')
 if face['zone']!='core':
  mids=[(a+b)/2 for a,b in tv2_intervals(face,face['centers'],face['pitch']*.635/2+.10)]
  for u in mids:
   if .42<u<face['length']-.42:
    tv2_console(face,u,z1-.99,.31,.40,.94,'tower pavilion crown base carved consoles')


def tv2_console(face,u,z,width,projection,height,name):
 # The changing projection gives a true corbel shadow and scroll-like return.
 # Exact historical carving is unresolved; this is a bounded profile trial.
 steps=[(0,.09,.17),(.17,.14,.36),(.36,.24,.61),(.61,.35,.80),(.80,projection,1)]
 for a,p,b in steps:
  tv2_block(face,u-width/2,u+width/2,.045,p,z+a*height,z+b*height,_TV2_STONE,name)


def tv2_arch_piece(face,c,spring,r,thick,d0,d1,material,name,steps=32):
 v=[]
 for d in (d0,d1):
  for rad in (r,r+thick):
   for i in range(steps+1):
    a=_tv2_math.pi*i/steps;v.append((*tv2_xy(face,c+rad*_tv2_math.cos(a),d),spring+rad*_tv2_math.sin(a)))
 s=steps+1;f=[]
 for i in range(steps):
  f.extend([(i,s+i,s+i+1,i+1),(2*s+i,2*s+i+1,3*s+i+1,3*s+i),
            (i,i+1,2*s+i+1,2*s+i),(s+i,3*s+i,3*s+i+1,s+i+1)])
 f.extend([(0,2*s,3*s,s),(steps,s+steps,3*s+steps,2*s+steps)])
 f=[tuple(reversed(faceids)) for faceids in f]  # U/Z shell outward winding
 # Project front/back onto U/Z; curved intrados/extrados unwrap by arc length.
 uv=[]
 for fi,poly in enumerate(f):
  if fi<4*steps and fi%4 in (0,1):
   uv.append([(c+((r if (k//s)%2==0 else r+thick))*_tv2_math.cos(_tv2_math.pi*(k%s)/steps),v[k][2]) for k in poly])
  elif fi<4*steps:
   uv.append([((k%s)/steps*_tv2_math.pi*(r if fi%4==2 else r+thick),d0 if k<2*s else d1) for k in poly])
  else:
   uv.append([(d0 if k<2*s else d1,r if (k//s)%2==0 else r+thick) for k in poly])
 addmesh(v,f,material,name,face_uv=uv)


def tv2_arch_window(face,c,bottom,w,apex):
 r=w/2;spring=apex-r;d=-_TV2_CFG['glazing_recess']
 outline=[(c-r,bottom),(c+r,bottom),(c+r,spring)]
 outline += [(c+r*_tv2_math.cos(_tv2_math.pi*i/32),spring+r*_tv2_math.sin(_tv2_math.pi*i/32)) for i in range(1,33)]
 tv2_local_poly(face,outline,d-.009,d+.009,_TV2_GLASS,'tower crown arched replacement glazing')
 tv2_local_poly(face,outline,-_TV2_CFG['neutral_optical_stop_depth']-.025,-_TV2_CFG['neutral_optical_stop_depth'],_TV2_STOP,'tower crown unobserved interior optical stop')
 for ss in (-1,1):
  u=c+ss*(r+.040)
  tv2_block(face,u-.034,u+.034,d-.055,d+.093,bottom-.055,spring,_TV2_FRAME,'tower crown window perimeter jambs')
 tv2_arch_piece(face,c,spring,r,.073,d-.055,d+.093,_TV2_FRAME,'tower crown curved metal window heads')
 tv2_block(face,c-r,c+r,d-.045,d+.089,bottom-.065,bottom,_TV2_FRAME,'tower crown window lower rails')
 # The upper/lower split is opaque green-gray as in the source, not a forest of
 # horizontal grids or invented radial fanlight spokes.
 mid=bottom+(apex-bottom)*.52;bandh=.37
 tv2_block(face,c-r,c+r,-.47,-.14,mid-bandh/2,mid+bandh/2,_TV2_PANEL,'tower crown two-level opaque spandrel')
 for zz in (mid-bandh/2,mid+bandh/2):
  tv2_block(face,c-r,c+r,-.21,-.115,zz-.035,zz+.035,_TV2_FRAME,'tower crown intermediate spandrel edge rails')
 tv2_block(face,c-.027,c+.027,d+.012,d+.092,bottom,apex-.025,_TV2_FRAME,'tower crown central metal mullions')
 for zz in (bottom+(mid-bottom)*.48,spring):
  tv2_block(face,c-r,c+r,d+.012,d+.095,zz-.022,zz+.022,_TV2_FRAME,'tower crown sash and spring rails')
 # Three stepped archivolt bands with separately exposed intrados/reveals.
 for rr,tt,dd0,dd1 in [(r+.083,.077,-.35,.035),(r+.16,.12,-.06,.125),(r+.28,.095,.005,.17)]:
  tv2_arch_piece(face,c,spring,rr,tt,dd0,dd1,_TV2_STONE,'tower crown layered terra cotta archivolts')
 _TV2_DIAGNOSTICS['crown_windows']+=1
 _TV2_DIAGNOSTICS['crown_arched_windows']+=1


def tv2_fluted_column(face,u,z,h,r):
 xy=tv2_xy(face,u,.095);rings=[(r*1.29,0),(r*1.29,.14),(r*1.05,.20),
   (r*1.11,.25),(r*1.13,.32),(r,.39),(r,.47),(r*.93,h-.53),
   (r*1.02,h-.46),(r*1.13,h-.34),(r*1.19,h-.22),(r*1.35,h-.13),(r*1.35,h)]
 v=[];n=64
 for k,(rr,zz) in enumerate(rings):
  for j in range(n+1):
   a=j*2*_tv2_math.pi/n
   rad=rr*(1-.085*(.5+.5*_tv2_math.cos(16*a))) if k in (5,6,7) else rr
   v.append((xy[0]+rad*_tv2_math.cos(a),xy[1]+rad*_tv2_math.sin(a),z+zz))
 f=[];uv=[];s=n+1
 for k in range(len(rings)-1):
  for j in range(n):
   f.append((k*s+j,k*s+j+1,(k+1)*s+j+1,(k+1)*s+j))
   uv.append([(j/n*2*_tv2_math.pi*r,z+rings[k][1]),((j+1)/n*2*_tv2_math.pi*r,z+rings[k][1]),
              ((j+1)/n*2*_tv2_math.pi*r,z+rings[k+1][1]),(j/n*2*_tv2_math.pi*r,z+rings[k+1][1])])
 f.extend([tuple(range(n-1,-1,-1)),tuple((len(rings)-1)*s+j for j in range(n))])
 uv.extend([[(v[i][0],v[i][1]) for i in ids] for ids in f[-2:]])
 addmesh(v,f,_TV2_STONE,'tower crown engaged fluted shafts and capitals',face_uv=uv)
 tv2_block(face,u-r*1.42,u+r*1.42,-.02,.47,z+h-.04,z+h+.16,_TV2_STONE,'tower crown column capital abacus')
 # Restrained capital foliation: original low relief profiles, not a claim to
 # reproduce the photograph's individual acanthus carving inventory.
 for du in (-r*.76,0,r*.76):
  tv2_local_poly(face,[(u+du-r*.34,z+h-.42),(u+du+r*.34,z+h-.42),
                      (u+du+r*.22,z+h-.22),(u+du,z+h-.09),(u+du-r*.22,z+h-.22)],
                  .26,.42,_TV2_STONE,'tower crown interpreted capital leaf relief')


def tv2_balustrade(face,centers,w,z):
 widths=w if isinstance(w,(list,tuple)) else [w]*len(centers)
 for c,ww in zip(centers,widths):
  a=c-ww/2-.11;b=c+ww/2+.11
  tv2_block(face,a,b,.22,.48,z+.13,z+.25,_TV2_STONE,'tower crown balustrade plinth')
  tv2_block(face,a,b,.19,.52,z+.77,z+.90,_TV2_STONE,'tower crown balustrade rail coping')
  count=max(4,round((b-a)/.255))
  for i in range(count):
   u=a+(i+.5)*(b-a)/count;xy=tv2_xy(face,u,.36)
   lathe((*xy,z+.24),[(.052,0),(.063,.045),(.056,.12),(.034,.20),(.032,.29),(.053,.39),(.046,.48),(.058,.53)],_TV2_STONE,'tower crown small turned balusters',12)
 # Pedestal dies align with the shared columns and parapet breaks.
 pier_centers=[(a+b)/2 for a,b in tv2_intervals(face,centers,[ww/2+.105 for ww in widths])]
 for u in pier_centers:
  if .30<u<face['length']-.30:
   tv2_block(face,u-.29,u+.29,-.10,.50,z+.16,z+.88,_TV2_STONE,'tower crown balustrade pedestal dies')
   tv2_block(face,u-.34,u+.34,-.13,.54,z+.88,z+1.00,_TV2_STONE,'tower crown balustrade pedestal caps')


def tv2_narrow_crown_end_stack(face,cell,zbase,apex):
 """Photo-observed rectangular end stack: small upper light, pedimented lower.

 East: Michael Barera, 31 August 2025. West topology is historically corroborated
 by the 2017-published Dandelion presentation oblique, not a 2026 west survey.
 Opening/profile dimensions below are local photo-proportioned trials.
 """
 c=cell['center'];w=cell['clear_width'];rough=cell['rough_width'];dep=_TV2_CFG['wall_thickness']
 lower_bottom=zbase+.36;lower_height=2.16
 upper_top=apex-.07;upper_height=1.36;upper_bottom=upper_top-upper_height
 assert upper_bottom>lower_bottom+lower_height+.45
 ranges=[(zbase+.16,lower_bottom-.079),(lower_bottom+lower_height+.079,upper_bottom-.079),(upper_top+.079,apex+.32)]
 for lo,hi in ranges:
  tv2_block(face,c-rough/2,c+rough/2,-dep,0,lo,hi,_TV2_STONE,'tower narrow crown end stack masonry panels')
 for label,zz,hh in [('lower',lower_bottom,lower_height),('upper',upper_bottom,upper_height)]:
  tv2_rectangle_frame(face,c,zz,w,hh,'tower narrow crown end stack '+label+' window',True,False)
  for side in (-1,1):
   u=c+side*(w/2+.115)
   tv2_block(face,u-.052,u+.052,-.27,.14,zz-.16,zz+hh+.14,_TV2_STONE,'tower narrow crown end stack raised stone jambs')
  for z in (zz-.14,zz+hh+.14):
   tv2_block(face,c-w/2-.168,c+w/2+.168,.04,.18,z-.055,z+.055,_TV2_STONE,'tower narrow crown end stack framed lintels and sills')
 # The source shows a modest triangular hood above the lower end window.
 pedz=lower_bottom+lower_height+.22;half=w/2+.28;rise=.31
 tv2_local_poly(face,[(c-half,pedz),(c+half,pedz),(c,pedz+rise)],.035,.13,_TV2_STONE,'tower narrow crown end stack pediment tympanum')
 for a,b in [((c-half,pedz),(c,pedz+rise)),((c,pedz+rise),(c+half,pedz))]:
  aa=(*tv2_xy(face,a[0],.16),a[1]);bb=(*tv2_xy(face,b[0],.16),b[1])
  beam(aa,bb,.045,_TV2_STONE,'tower narrow crown end stack pediment raking molding',8)
 # Quiet recessed field between the two lights, with a shallow rectangular border.
 p0=pedz+rise+.17;p1=upper_bottom-.27
 if p1>p0+.08:
  for u in (c-w/2-.06,c+w/2+.06):
   tv2_block(face,u-.025,u+.025,.012,.060,p0,p1,_TV2_STONE,'tower narrow crown end stack intermediate panel stiles')
  for z in (p0,p1):
   tv2_block(face,c-w/2-.06,c+w/2+.06,.012,.060,z-.025,z+.025,_TV2_STONE,'tower narrow crown end stack intermediate panel rails')
 _TV2_DIAGNOSTICS['crown_windows']+=1
 _TV2_DIAGNOSTICS['crown_rectangular_end_stacks']+=1
 _TV2_DIAGNOSTICS['crown_rectangular_end_windows']+=2


def tv2_crown(face):
 dep=_TV2_CFG['wall_thickness'];zbase=_TV2_CROWN_Z;top=face['top']
 entab=_TV2_CFG['core_entablature_height'] if face['zone']=='core' else _TV2_CFG['pavilion_entablature_height']
 apex=top-entab;bottom=zbase+.30;cells=tv2_bay_cells(face,'crown')
 fullw=face['pitch']*_TV2_CFG['crown_clear_width_ratio']
 spring=apex-fullw/2
 assert spring>bottom+1.5,('Crown vertically over-constrained',face['id'],bottom,spring,top)
 halfwidths=[q['rough_width']/2 for q in cells]
 for a,b in tv2_intervals(face,face['centers'],halfwidths):
  tv2_block(face,a,b,-dep,0,zbase+.16,apex+.28,_TV2_STONE,'tower crown shared masonry piers',True)
 for cell in cells:
  c=cell['center'];w=cell['clear_width'];r=w/2;roughw=cell['rough_width'];spring=apex-r
  if cell['narrow']:
   tv2_narrow_crown_end_stack(face,cell,zbase,apex)
   continue
  tv2_arch_window(face,c,bottom,w,apex)
  # Fill above each true arch; narrow end stacks get their own solid panels.
  rr=r+.095
  for i in range(32):
   u0=-rr+2*rr*i/32;u1=-rr+2*rr*(i+1)/32
   z0=spring+_tv2_math.sqrt(max(0,rr*rr-u0*u0));z1=spring+_tv2_math.sqrt(max(0,rr*rr-u1*u1))
   tv2_local_poly(face,[(c+u0,z0),(c+u1,z1),(c+u1,apex+.32),(c+u0,apex+.32)],-dep,0,_TV2_STONE,'tower crown curved masonry spandrel infill')
  tv2_block(face,c-roughw/2,c+roughw/2,-dep,0,zbase+.16,bottom-.067,_TV2_STONE,'tower crown masonry under window sills')
 # Columns stay on the shared piers. End-stack outer margins are paneled corner
 # strips in the source, not extra thin round columns outside each small light.
 for a,b in tv2_intervals(face,face['centers'],halfwidths):
  u=(a+b)/2
  outside_narrow=(cells[0]['narrow'] and u<cells[0]['center']) or (cells[-1]['narrow'] and u>cells[-1]['center'])
  if .38<u<face['length']-.38 and not outside_narrow:
   rad=min(.295,(b-a)*.31)
   tv2_fluted_column(face,u,zbase+.92,apex-zbase-.64,rad)
 tv2_balustrade(face,face['centers'],[q['clear_width'] for q in cells],zbase)
 tv2_entablature(face,apex,top)
 _TV2_DIAGNOSTICS['facade_segments'].append({'face':face['id'],'zone':face['zone'],
  'bays':len(face['centers']),'bay_types':list(face['bay_types']),'bay_pitch_m':face['pitch'],'apex_m':apex,'coping_m':top,
  'crown_clear_height_m':apex-bottom,'crown_clear_width_m':fullw,'apex_to_coping_m':top-apex,
  'arched_crown_bays':sum(not q['narrow'] for q in cells),'rectangular_end_stacks':sum(q['narrow'] for q in cells)})


def tv2_entablature(face,apex,top):
 """A layered frieze, dentils, deep bracketed soffit, fascia and coping."""
 # The July2026 junction crops show connected coping, soffit and frieze.
 # At the shared roof datum all decorative strata use one vertical profile.
 # The pavilion's slightly lower arch apex remains unchanged; existing curved
 # masonry spandrel closes the short transition under this common architrave.
 if abs(_TV2_CFG['core_roof_top']-_TV2_CFG['pavilion_roof_top'])<1e-7:
  apex=top-min(_TV2_CFG['core_entablature_height'],_TV2_CFG['pavilion_entablature_height'])
 h=top-apex;dep=_TV2_CFG['wall_thickness']
 # Adjacent vertical sections meet by endpoints. Perimeter miters also continue
 # through returns, so closure does not rely on overlapping coplanar boxes.
 for aa,bb,projection,label in [
  (0,.105,.23,'crown capital-zone architrave'),(.105,.16,.32,'crown architrave stepped molding'),
  (.16,.40,.17,'crown carved frieze backing'),(.40,.46,.31,'crown frieze upper molding'),
  (.46,.52,.43,'crown dentil shelf'),(.52,.79,.27,'crown deep bracketed soffit backing'),
  (.79,.89,.90,'crown projecting fascia'),(.89,1.0,1.05,'crown roof coping')]:
  tv2_band(face,apex+h*aa,apex+h*bb,-dep,projection,_TV2_STONE,'tower '+label)
 # Long shallow frieze panels are framed by a restrained original egg/bead-like
 # low relief; exact terra-cotta motifs have not been measured.
 n=max(1,int(face['length']/.72))
 for i in range(n):
  u=(i+.5)*face['length']/n
  tv2_local_poly(face,[(u-.095,apex+h*.205),(u+.095,apex+h*.205),(u+.12,apex+h*.275),
                       (u+.06,apex+h*.35),(u-.06,apex+h*.35),(u-.12,apex+h*.275)],
                    .174,.224,_TV2_STONE,'tower crown interpreted frieze relief')
 nd=max(1,int(face['length']/.43))
 for i in range(nd):
  u=(i+.5)*face['length']/nd
  tv2_block(face,u-.078,u+.078,.32,.515,apex+h*.435,apex+h*.53,_TV2_STONE,'tower upper entablature dentils')
 # Deep paired soffit coffer rails surround a dark recess while substantial
 # brackets alternate. These are measured in meters in the exported UV stream.
 nb=max(1,round(face['length']/.92));bp=face['length']/nb
 for i in range(nb):
  u=(i+.5)*bp
  tv2_console(face,u,apex+h*.50,.20,.91,h*.32,'tower deep cornice profiled modillions')
  a=max(.015,u-bp/2+.10);b=min(face['length']-.015,u+bp/2-.10)
  if b>a:
   tv2_block(face,a,b,.34,.86,apex+h*.785-.043,apex+h*.785-.029,_TV2_JOINT,'tower cornice recessed soffit shadow fields')
   for uu in (a,b):
    tv2_block(face,uu-.033,uu+.033,.32,.89,apex+h*.785-.095,apex+h*.785-.039,_TV2_STONE,'tower cornice soffit panel end rails')


def tv2_podium(face):
 # Deliberately upper-only. The shell never adds walls below z10.40 through the
 # documented public rooms. Terrace floors/railings stay owned by the main file.
 if face['zone']=='core':return
 z0=10.40;z1=Z0;dep=_TV2_CFG['wall_thickness']
 if face['kind'] not in ('pavilion_front','pavilion_back'):
  tv2_band(face,z0,z1,-dep,0,_TV2_STONE,'tower podium upper-only return band')
  return
 w=face['pitch']*.535;h=2.73;clearz=11.355;rough=w+.20
 for a,b in tv2_intervals(face,face['centers'],rough/2):
  tv2_block(face,a,b,-dep,0,z0,z1,_TV2_STONE,'tower podium upper-only window piers',True)
 for c in face['centers']:
  tv2_rectangle_frame(face,c,clearz,w,h,'tower terrace-level replacement window',True)
  for a,b in ((z0,clearz-.08),(clearz+h+.08,z1)):
   tv2_block(face,c-rough/2,c+rough/2,-dep,0,a,b,_TV2_STONE,'tower podium upper-only window lintel and apron')
  _TV2_DIAGNOSTICS['podium_windows']+=1


# CCW I-plan perimeter. Outward normal is (t_y,-t_x); exact offset intersections
# give matching shell and cornice miters at convex and concave return junctions.
_H=TW/2;_I=_H-WING;_NF=TF+(TD-CORE)/2;_SB=TF+(TD+CORE)/2;_BY=TF+TD
_TV2_OUTLINE=[(-_H,TF),(-_I,TF),(-_I,_NF),(_I,_NF),(_I,TF),(_H,TF),(_H,_BY),(_I,_BY),(_I,_SB),(-_I,_SB),(-_I,_BY),(-_H,_BY)]
_TV2_FACES=[]
for _i,(_p,_q) in enumerate(zip(_TV2_OUTLINE,_TV2_OUTLINE[1:]+_TV2_OUTLINE[:1])):
 _dx=_q[0]-_p[0];_dy=_q[1]-_p[1];_ll=_tv2_math.hypot(_dx,_dy);_tt=(_dx/_ll,_dy/_ll);_nn=(_tt[1],-_tt[0])
 if _i in (2,8):_zone='core';_kind='core_front' if _i==2 else 'core_back';_count=18;_pitch=PITCH
 elif _i in (0,4,6,10):_zone='pavilion';_kind='pavilion_front' if _i in (0,4) else 'pavilion_back';_count=3;_pitch=4.6
 elif _i in (5,11):_zone='pavilion';_kind='outer_side';_count=8;_pitch=_ll/8
 else:_zone='pavilion';_kind='inner_return';_count=2;_pitch=_ll/2
 _cs=[_ll/2+(j-(_count-1)/2)*_pitch for j in range(_count)]
 _TV2_FACES.append({'id':f'{_i:02d}_{_kind}','p':_p,'q':_q,'t':_tt,'n':_nn,'length':_ll,'zone':_zone,'kind':_kind,
                    'count':_count,'pitch':_pitch,'centers':_cs,
                    'bay_types':(['narrow_rectangular_end']+['regular']*6+['narrow_rectangular_end']) if _kind=='outer_side' else ['regular']*_count,
                    'top':_TV2_CFG['core_roof_top'] if _zone=='core' else _TV2_CFG['pavilion_roof_top']})
for _i,_face in enumerate(_TV2_FACES):
 def _miter_along(_other):
  a,b=_face['n'];c,d=_other['n'];det=a*d-b*c
  vx=(d-b)/det;vy=(a-c)/det
  return vx*_face['t'][0]+vy*_face['t'][1]
 _face['left_miter']=_miter_along(_TV2_FACES[(_i-1)%len(_TV2_FACES)])
 _face['right_miter']=_miter_along(_TV2_FACES[(_i+1)%len(_TV2_FACES)])

try:
 GROUP='02 TOWER | photo-proportioned exterior shell'
 for _face in _TV2_FACES:
  tv2_podium(_face);tv2_shaft(_face);tv2_register(_face);tv2_crown(_face)
 # A common coping datum is inferred by following the connected moldings at
 # both July2026 return/core junctions, not by comparing arbitrary image Y.
 _rt=_TV2_CFG['core_roof_top'];_pt=_TV2_CFG['pavilion_roof_top'];_wt=_TV2_CFG['wall_thickness']
 _base_outline=[tv2_xy(f,f['left_miter']*(-_wt),-_wt) for f in _TV2_FACES]
 if abs(_rt-_pt)<1e-7:
  # One inset I-plan prism has no unclosed half-meter joins between former deck
  # rectangles and no false vertical step along the pavilion/core interface.
  tv2_prism(_base_outline,_rt-.28,_rt-.04,'Roof dark copper','tower closed continuous I-plan roof deck')
 else:
  # Optional research overrides retain the former separate-level mechanism.
  tv2_prism([(-_I,_NF+_wt),(_I,_NF+_wt),(_I,_SB-_wt),(-_I,_SB-_wt)],_rt-.28,_rt-.04,'Roof dark copper','tower closed central roof deck')
  for _side in (-1,1):
   _xa,_xb=sorted((_side*_I,_side*_H))
   tv2_prism([(_xa+_wt,TF+_wt),(_xb-_wt,TF+_wt),(_xb-_wt,_BY-_wt),(_xa+_wt,_BY-_wt)],_pt-.28,_pt-.04,'Roof dark copper','tower closed pavilion roof deck')
   if _pt>_rt:
    _bridge={'p':(_side*_I,_SB if _side>0 else _NF),
             't':(0,-1 if _side>0 else 1),'n':(-_side,0),'length':CORE,
             'left_miter':-1,'right_miter':1}
    tv2_block(_bridge,0,CORE,-_wt,0,_rt,_pt,_TV2_STONE,'tower pavilion roof step closure above core',True)
 # This inset base slab meets the shell at Z0 without duplicate facade skins.
 tv2_prism(_base_outline,Z0-.25,Z0,'Weathered concrete','tower I-plan base slab without private fit-out')
 # Stone corner quoin strips are narrow front-facing relief, not giant 52m solid
 # blocks masking an adjacent face. Their depth terminates at the masonry face.
 for _face in _TV2_FACES:
  if _face['kind'] in ('pavilion_front','pavilion_back','outer_side'):
   for _end in (0,_face['length']):
    _a=max(0,_end-.53);_b=min(_face['length'],_end+.53)
    tv2_block(_face,_a,_b,.003,.10,Z0,_TV2_REG_Z,_TV2_STONE,'tower pavilion corner quoin relief',True)
finally:
 GROUP=_TV2_PREVIOUS_GROUP

TOWER_V2_CAMERAS={
 'tower_front_detail':((0,-108,53),(0,38,53),59),
 'tower_crown_detail':((53,-47,68),(30,37,63.5),65),
 'tower_return_detail':((92,-12,46),(41,37,42),59),
 'tower_rear_detail':((-97,132,55),(-18,49,45),50),
}
TOWER_V2_METADATA={
 'component':'tower_facade_v2.py','status':'WIP photo-proportioned shell; neither photoreal certification nor as-built survey',
 'reference':'https://commons.wikimedia.org/wiki/File:Michigan_Central_Station_2026.jpg',
 'reference_date':'2026-07-19','reference_license':'CC0','research_pixels_used_as_material':False,
 'directly_inspected':['research/visual/michigan_central_2026_cc0_wmrapids.jpg','renders/review03/2026_front.png',
                      'research/tower_qa/photo_pavilion_bay_grid.png','research/tower_qa/photo_core_cornice.png',
                      'research/tower_qa/pavilion_crown_large.png','research/tower_qa/east_crown_2025_inspection.png',
                      'research/tower_qa/east_return_2025_inspection.png','research/south_structure/presentation_ref_08.jpg',
                      'research/tower_qa/photo_east_core_roof_junction.png','research/tower_qa/photo_west_core_roof_junction.png'],
 'continuous_coping_inference':{'datum_m':_TV2_CFG['core_roof_top'],
  'basis':'Connected coping/soffit/frieze/lower moldings turn continuously through both July2026 inner-return/core junctions; no visible vertical riser',
  'status':'Photo-supported common-level inference; absolute height remains inherited, not surveyed',
  'common_upper_molding_profile_height_m':min(_TV2_CFG['core_entablature_height'],_TV2_CFG['pavilion_entablature_height'])},
 'side_topology_evidence':{'east_current':{'url':'https://commons.wikimedia.org/wiki/File:Detroit_August_2025_23_(Michigan_Central_Station).jpg',
  'photographer':'Michael Barera','capture_date':'2025-08-31','license':'CC BY-SA 4.0; reference only; no photo distributed in component',
  'position':'X=-TW/2; east outer face'},
  'west_historical':{'url':'https://sketchfab.com/3d-models/michigan-central-station-17921c30b4134bf598b0cac817f00f1d',
  'published':'2017-08-03','position':'X=+TW/2; west outer face','status':'Six-plus-two topology historically corroborated and carried forward, not independently current-verified'}},
 'historical_plan_anchors_m':{'tower_width':TW,'pavilion_width':WING,'pavilion_depth':TD,'core_depth':CORE,'typical_floor_spacing':floorh},
 'vertical_datum_m':Z0,'vertical_datum_status':'Inherited working datum; source grade/roof/parapet convention unresolved',
 'counts':{'regular_shaft_rows':11,'special_horizontal_registers':1,'levels_inside_crown_arch':2,
           'core_front_bays':18,'pavilion_front_bays_each':3,'side_window_columns':8,'side_large_crown_arches':6,'side_narrow_rectangular_end_stacks':2,'each_short_return_bays_trial':2},
 'parameters':dict(_TV2_CFG),
 'observed_material_classes':['pale pressed brick shaft','green-gray replacement window/spandrel system','muted ornamental terra cotta crown'],
 'period_notes':['Tower replacement windows installed in 2015; both eras remain glazed',
                 'No invented 2017 missing-window inventory or 2026 private tenant fit-outs',
                 'Restrained 2017 glazing roughness is an appearance approximation, not condition mapping'],
 'limitations':['Shared coping datum is photo-supported, but absolute elevation remains inherited; core crown is6.21m and pavilion5.96m. Core apex-to-coping allocation remains below the approximate source ratio',
                'Outer-side six-large-plus-two-narrow topology is photo-supported; west2026 is historical carry-forward. Back and inner-return repetition still need independently counted dated elevations',
                'Frieze, console, flute and capital profiles are bounded original approximations, not surveyed carved ornament',
                'Existing authored stone support maps approximate terra-cotta appearance; no new generated raster or photographic projection',
                'Uniform physical glazing with dark neutral optical stops does not inventory actual room occupation or blinds',
                'Existing core-owned terrace floor/railings and all public-room interiors are outside component ownership'],
 'diagnostics':_TV2_DIAGNOSTICS,
}
scene['tower_v2_metadata']=json.dumps(TOWER_V2_METADATA)
